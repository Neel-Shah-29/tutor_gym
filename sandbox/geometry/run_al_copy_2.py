import os
import sys
import json
import re
import argparse
from pathlib import Path

import numpy as np

# CRE structrefs require numba's JIT; force it on even if the env disables it.
if os.environ.get("NUMBA_DISABLE_JIT") == "1":
    print("[run_al_copy_2] NUMBA_DISABLE_JIT=1 detected; enabling JIT for CRE.")
os.environ["NUMBA_DISABLE_JIT"] = "0"

# Prefer the in-repo Cognitive-Rule-Engine over any installed version.
repo_root = Path(__file__).resolve().parents[2]
local_cre = repo_root / "Cognitive-Rule-Engine"
if local_cre.exists():
    sys.path.insert(0, str(local_cre))

from apprentice.agents.cre_agents.hint_nlp import build_hf_llm_call
from apprentice.agents.cre_agents.environment import TextField, Label, Button, Component

from cre import MemSet
from cre.gval import gval as gval_type, new_gval
from cre.transform import Vectorizer
from numba.types import f8, string, boolean
from numba import njit

from tutorgym.env_classes.apprentice.apprentice_tutor import ApprenticeTutor
from tutorgym.envs.apprentice.cognitive_models.solve_triangle.htn_geometry_solve_triangle import (
    htn_geometry_solve_triangle_intermediate_hints,
)


def _extract_predicates(flat_feat_state):
    preds = []
    gvals = []
    if hasattr(flat_feat_state, "get_facts"):
        try:
            facts_iter = flat_feat_state.get_facts(gval_type)
        except Exception:
            facts_iter = flat_feat_state.get_facts()
        for fact in facts_iter:
            preds.append(str(fact))
            gvals.append(fact)
    elif isinstance(flat_feat_state, (list, tuple)):
        for fact in flat_feat_state:
            preds.append(str(fact))
            gvals.append(fact)
    return preds, gvals


def _build_prompt(predicates, hint):
    lines = [
        "You are selecting the minimal set of predicates relevant to the hint.",
        "Return ONLY a JSON array of indices, e.g. [0, 3, 9].",
        "If none apply, return [].",
        "",
        "Predicates:",
    ]
    for i, pred in enumerate(predicates):
        lines.append(f"{i}: {pred}")
    lines.extend(["", f"Hint: {hint}", "Indices:"])
    return "\n".join(lines)


def _parse_indices(text, max_index):
    text = text.strip()
    if not text:
        return []
    if "llm_error" in text.lower() or "bad request" in text.lower():
        return []
    # Try JSON array first.
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return sorted({int(x) for x in data if isinstance(x, (int, float)) and 0 <= int(x) < max_index})
    except Exception:
        pass
    # Fallback: extract integers from the response.
    found = [int(x) for x in re.findall(r"\d+", text)]
    return sorted({x for x in found if 0 <= x < max_index})


def _heuristic_indices(predicates, hint, max_count=5):
    hint_tokens = {tok.lower() for tok in re.sub(r"[^A-Za-z0-9_]+", " ", hint).split() if tok}
    scores = []
    for i, pred in enumerate(predicates):
        score = sum(1 for tok in hint_tokens if tok in pred.lower())
        if score > 0:
            scores.append((score, i))
    scores.sort(reverse=True)
    return sorted([i for _, i in scores[:max_count]])


def _select_predicate_indices(predicates, hint, llm_call):
    prompt = _build_prompt(predicates, hint)
    try:
        response = llm_call(prompt)
    except Exception as exc:
        print("[run_al_copy_2] LLM call failed:", exc)
        response = ""
    response_text = str(response)
    indices = _parse_indices(response_text, len(predicates))
    if not indices:
        indices = _heuristic_indices(predicates, hint)
    return indices, response_text


@njit(cache=True)
def _vector_index_for_gval(vectorizer, gval):
    slot = vectorizer.slot_map[gval.head]
    if vectorizer.one_hot_nominals:
        return vectorizer.one_hot_map[(slot, gval.nom)]
    return slot


def _vectorize_and_weight(flat_feat_state, selected_gvals, one_hot=True, encode_missing=True, upweight=5.0):
    vectorizer = Vectorizer([f8, string, boolean], one_hot, encode_missing)
    continuous, nominal = vectorizer(flat_feat_state)

    vec_indices = []
    for gval in selected_gvals:
        try:
            vec_ind = int(_vector_index_for_gval(vectorizer, gval))
            vec_indices.append(vec_ind)
        except Exception:
            continue

    weights = np.ones(len(nominal), dtype=np.float64)
    for idx in vec_indices:
        if 0 <= idx < len(weights):
            weights[idx] = upweight

    return vectorizer, continuous, nominal, vec_indices, weights


def _subset_factset(selected_gvals):
    subset_ms = MemSet()
    for gval in selected_gvals:
        try:
            clone = new_gval(gval.head, gval.val, gval.flt, gval.nom)
            subset_ms.declare(clone)
        except Exception:
            subset_ms.declare(gval)
    return subset_ms


def run_once(agent, one_hot=True, encode_missing=True, upweight=5.0):
    env = ApprenticeTutor(domain="solve_triangle")
    env.set_random_problem()
    demo = env.get_demo()

    hint_key = demo.selection if hasattr(demo, "selection") and demo.selection else None
    if not hint_key:
        hint_key = "apply_pythagorean" if "apply_pythagorean" in agent.function_set else agent.function_set[0]

    hints = htn_geometry_solve_triangle_intermediate_hints()
    hint_candidates = hints.get(hint_key, []) if hints else []
    hint = hint_candidates[0] if hint_candidates else "Use the Pythagorean theorem."

    state = env.get_state()
    agent_state = agent.standardize_state(state.objs, False)
    flat_feat_state = agent_state.get("flat_featurized")

    predicates, gvals = _extract_predicates(flat_feat_state)
    if not predicates:
        print("[run_al_copy_2] No predicates found in flat_featurized state.")
        return []

    try:
        llm_call = build_hf_llm_call()
    except RuntimeError as exc:
        print("[run_al_copy_2] LLM unavailable:", exc)
        llm_call = None

    if llm_call is None:
        indices = _heuristic_indices(predicates, hint)
        llm_response = ""
    else:
        indices, llm_response = _select_predicate_indices(predicates, hint, llm_call)

    selected_gvals = [gvals[i] for i in indices]
    vectorizer, continuous, nominal, vec_indices, weights = _vectorize_and_weight(
        flat_feat_state,
        selected_gvals,
        one_hot=one_hot,
        encode_missing=encode_missing,
        upweight=upweight,
    )

    # Optionally create a gated factset.
    subset_ms = _subset_factset(selected_gvals)
    subset_vectorizer = Vectorizer([f8, string, boolean], one_hot, encode_missing)
    subset_vectorizer(subset_ms)

    print("\n" + "=" * 40)
    print(f"HINT: {hint}")
    if llm_response:
        print("LLM RESPONSE:", llm_response.strip())
    print(f"TOTAL PREDICATES: {len(predicates)}")
    print("SELECTED PREDICATE INDICES:", indices)
    for i in indices:
        print(f"  {i}: {predicates[i]}")
    print("VECTOR INDICES:", vec_indices)
    print("WEIGHTS LEN:", len(weights))
    print("=" * 40 + "\n")

    # Required output: indices of predicates associated with the hint.
    print(json.dumps(indices))
    return indices


if __name__ == "__main__":
    import tutorgym.helpers.ai2t_helpers  # Registers SkillApplication -> Action
    from apprentice.agents.cre_agents.cre_agent import CREAgent

    parser = argparse.ArgumentParser(description="Hint-gated predicate selection")
    parser.add_argument("--runs", type=int, default=1, help="number of runs")
    parser.add_argument("--upweight", type=float, default=5.0, help="upweight factor for selected predicates")
    parser.add_argument("--one-hot", action="store_true", default=True, help="use one-hot encoding for nominals")
    parser.add_argument("--no-one-hot", dest="one_hot", action="store_false", help="disable one-hot encoding")
    parser.add_argument("--encode-missing", action="store_true", default=True, help="encode missing values")
    parser.add_argument("--no-encode-missing", dest="encode_missing", action="store_false", help="disable missing encoding")

    args = parser.parse_args()

    agent_args = {
        "function_set": [
            "normalize_inputs",
            "classify_triangle",
            "apply_pythagorean",
            "use_trig_ratios",
            "resolve_ssa_ambiguity",
            "compute_missing_angles",
            "compute_missing_sides",
            "compute_unknown_by_cosine",
            "map_correspondence",
            "scale_sides_angles",
            "select_area_formula",
            "compute_area",
            "consistency_checks",
        ],
        "feature_set": ["Equals"],
        "planner": "set_chaining",
        "explanation_choice": "least_operations",
        "search_depth": 2,
        "where_learner": "mostspecific",
        "when_learner": "decision_tree",
        "which_learner": "when_prediction",
        "action_chooser": "max_which_utility",
        "suggest_uncert_neg": True,
        "error_on_bottom_out": False,
        "extra_features": ["Match"],
        "when_args": {"encode_relative": True, "one_hot": True},
        "should_find_neighbors": True,
    }

    agent = CREAgent(**agent_args)

    for _ in range(max(1, args.runs)):
        run_once(
            agent,
            one_hot=args.one_hot,
            encode_missing=args.encode_missing,
            upweight=args.upweight,
        )
