#!/usr/bin/env python3
import argparse
import json
import os
import random
import re
import sys
from pathlib import Path

import numpy as np

# CRE structrefs require numba's JIT; force it on even if the env disables it.
if os.environ.get("NUMBA_DISABLE_JIT") == "1":
    print("[run_al_copy_2] NUMBA_DISABLE_JIT=1 detected; enabling JIT for CRE.")
os.environ["NUMBA_DISABLE_JIT"] = "0"

# Ensure local package paths work when running directly from the geometry folder.
script_path = Path(__file__).resolve()
workspace_root = script_path.parents[3]

# Keep CRE/Numba caches inside the workspace so generated modules stay writable and reproducible.
local_cache_root = workspace_root / ".codex_geometry_cache"
os.environ.setdefault("XDG_CACHE_HOME", str(local_cache_root))
os.environ.setdefault("NUMBA_CACHE_DIR", str(local_cache_root / "numba"))

for p in [
    str(workspace_root / "AL_Core"),
    str(workspace_root / "tutor_gym"),
    str(workspace_root / "STAND"),
    str(workspace_root / "tutor_gym" / "Cognitive-Rule-Engine"),
]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Prefer the in-repo Cognitive-Rule-Engine over any installed version.
local_cre = workspace_root / "tutor_gym" / "Cognitive-Rule-Engine"
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
    htn_geometry_solve_triangle_problem_pool,
    htn_geometry_solve_triangle_intermediate_hints,
)
from tutorgym.trainer import Trainer
from tutorgym.utils import DataShopLogger


def _get_debug_mode():
    return os.environ.get("CRE_STAND_WEIGHT_DEBUG", "0") == "1"


def _to_bool(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    return str(v).lower() in {"1", "true", "yes", "on"}


def _process_learning_enabled(process_learner):
    if process_learner is None:
        return False
    if not str(process_learner).strip():
        return False
    return str(process_learner).strip().lower() not in {"none", "off", "disable", "disabled"}


def set_global_seed(seed):
    if seed is None:
        return
    random.seed(seed)
    np.random.seed(seed)


def _cycle_problem_pool(pool, n, seed):
    if n <= 0:
        return []
    rng = random.Random(seed)
    ordered = list(pool)
    if not ordered:
        return []
    rng.shuffle(ordered)
    problem_texts = []
    while len(problem_texts) < n:
        batch = list(ordered)
        rng.shuffle(batch)
        problem_texts.extend(batch)
    return problem_texts[:n]


def build_problem_sets(n_problems, seed=None, holdout_count=0):
    train_pool = htn_geometry_solve_triangle_problem_pool("train")
    holdout_pool = htn_geometry_solve_triangle_problem_pool("holdout")

    train_problem_texts = _cycle_problem_pool(train_pool, int(n_problems), seed)
    train_problem_set = [
        {"domain": "solve_triangle", "initial_problem": problem_text}
        for problem_text in train_problem_texts
    ]

    holdout_problem_set = []
    if holdout_count > 0:
        holdout_problem_texts = _cycle_problem_pool(holdout_pool, int(holdout_count), None if seed is None else seed + 9973)
        holdout_problem_set = [
            {"domain": "solve_triangle", "initial_problem": problem_text}
            for problem_text in holdout_problem_texts
        ]

    return train_problem_set, holdout_problem_set


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


# Keep legacy underscore-prefixed names for any internal call sites.
extract_predicates = _extract_predicates


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
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return sorted({int(x) for x in data if isinstance(x, (int, float)) and 0 <= int(x) < max_index})
    except Exception:
        pass
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


def select_hint_predicates(
    predicates,
    hint,
    hint_key=None,
    preferred_terms=None,
    llm_call=None,
    filter_labels=True,
    max_count=5,
    debug_label="input change",
):
    if not predicates:
        return []

    candidates = list(range(len(predicates)))
    if filter_labels:
        candidates = [
            i
            for i, pred in enumerate(predicates)
            if "label_of_" not in pred
        ]
    if not candidates:
        candidates = list(range(len(predicates)))

    selected = []
    preferred_terms = [str(term).lower() for term in (preferred_terms or []) if term]
    if hint_key:
        preferred_terms.append(str(hint_key).lower())

    if preferred_terms:
        direct_scored = []
        for i in candidates:
            pred_l = predicates[i].lower()
            score = 0
            for term in preferred_terms:
                if f"{term}.value" in pred_l:
                    score += 6
                if f"field={term}" in pred_l:
                    score += 4
                if term in pred_l:
                    score += 2
                if "label_of_" in pred_l and term in pred_l:
                    score -= 1
            if score > 0:
                direct_scored.append((score, i, len(predicates[i])))
        if direct_scored:
            direct_scored.sort(key=lambda item: (-item[0], item[2], item[1]))
            selected = [i for _, i, _ in direct_scored[:max_count]]

    prompt = _build_prompt([predicates[i] for i in candidates], hint)
    response = ""
    if not selected:
        try:
            response = llm_call(prompt) if callable(llm_call) else ""
        except Exception as exc:
            print(f"[run_al_copy_2] LLM call failed: {exc}")
            response = ""

        indices = _parse_indices(str(response), len(candidates))
        if indices:
            selected = [candidates[i] for i in indices[:max_count]]

    if not selected:
        selected = [
            candidates[i]
            for i in _heuristic_indices(
                [predicates[i] for i in candidates],
                hint,
                max_count=max_count,
            )
        ]

    selected = sorted(set(selected))[:max_count]
    if _get_debug_mode():
        print(f"[run_al_copy_2:{debug_label}] prompt_hint={hint!r}")
        print(f"[run_al_copy_2:{debug_label}] llm_response={response!r}")
        print(f"[run_al_copy_2:{debug_label}] selected_predicates={selected}")
        for i in selected:
            if 0 <= i < len(predicates):
                print(f"  - {i}: {predicates[i]}")
    return selected


def resolve_hint_text(hint_key, hint_map=None):
    if not hint_key:
        return ""

    hint_map = hint_map or {}
    if isinstance(hint_map, dict):
        hint_values = hint_map.get(hint_key)
        if isinstance(hint_values, str):
            hints = [hint_values]
        elif isinstance(hint_values, (list, tuple)):
            hints = [h for h in hint_values if isinstance(h, str)]
        else:
            hints = []
        if hints:
            if _get_debug_mode():
                print(f"[run_al_copy_2] Resolved hint from map for key={hint_key!r}: {hints[0]!r}")
            return hints[0]

    try:
        hint_candidates = htn_geometry_solve_triangle_intermediate_hints().get(hint_key, [])
        if hint_candidates:
            if _get_debug_mode():
                print(f"[run_al_copy_2] Resolved hint from model map for key={hint_key!r}: {hint_candidates[0]!r}")
            return hint_candidates[0]
    except Exception:
        pass

    if _get_debug_mode():
        print(f"[run_al_copy_2] No hint text found for key={hint_key!r}")
    return ""


@njit(cache=True)
def _vector_index_for_gval(vectorizer, gval):
    slot = vectorizer.slot_map[gval.head]
    if vectorizer.one_hot_nominals:
        return vectorizer.one_hot_map[(slot, gval.nom)]
    return slot


def _subset_factset(selected_gvals):
    subset_ms = MemSet()
    for gval in selected_gvals:
        try:
            subset_ms.declare(new_gval(gval.head, gval.val, gval.flt, gval.nom))
        except Exception:
            subset_ms.declare(gval)
    return subset_ms


def build_weight_vector(vectorizer, selected_gvals, upweight=5.0):
    subset_ms = _subset_factset(selected_gvals)
    _, nominal = vectorizer(subset_ms)

    weights = np.ones(len(nominal), dtype=np.float64)
    for gval in selected_gvals:
        try:
            idx = int(_vector_index_for_gval(vectorizer, gval))
            if 0 <= idx < len(weights):
                weights[idx] = upweight
        except Exception:
            continue

    return nominal, weights


def run_once(agent, one_hot=True, encode_missing=True, upweight=5.0):
    env = ApprenticeTutor(domain="solve_triangle")
    env.set_random_problem()
    demo = env.get_demo()

    hint_key = demo.selection if hasattr(demo, "selection") and demo.selection else None
    if not hint_key:
        hint_key = "apply_pythagorean" if "apply_pythagorean" in agent.function_set else agent.function_set[0]

    hint = resolve_hint_text(hint_key)
    if not hint:
        hint = "Use the Pythagorean theorem."

    state = env.get_state()
    agent_state = agent.standardize_state(state.objs, False)
    flat_feat_state = agent_state.get("flat_featurized")

    predicates, gvals = extract_predicates(flat_feat_state)
    if not predicates:
        print("[run_al_copy_2] No predicates found in flat_featurized state.")
        return []

    try:
        llm_call = build_hf_llm_call()
    except Exception:
        llm_call = None

    indices = select_hint_predicates(predicates, hint, llm_call=llm_call)
    selected_gvals = [gvals[i] for i in indices]

    _, nominal = build_weight_vector(agent.vectorizer if hasattr(agent, "vectorizer") else Vectorizer([f8, string, boolean], one_hot, encode_missing), selected_gvals)

    print("\n" + "=" * 40)
    print(f"HINT: {hint}")
    print(f"TOTAL PREDICATES: {len(predicates)}")
    print("SELECTED PREDICATE INDICES:", indices)
    for i in indices:
        print(f"  {i}: {predicates[i]}")
    print("WEIGHTS LEN:", len(nominal))
    print("=" * 40 + "\n")

    print(json.dumps(indices))
    return indices



def _collect_framework_options(training_framework, args):
    framework = training_framework
    when_args = {
        "encode_relative": True,
        "one_hot": True,
        "gated_hints": framework != "feedback_only",
        "gated_filter_labels": True,
        "gated_use_llm": False,
        "gated_max_predicates": args.predicate_threshold,
        "gated_upweight": 5.0,
        "gated_hint_map": htn_geometry_solve_triangle_intermediate_hints(),
        "predict_with_weight_only": framework == "nl_hint_only",
        "weight_debug": _get_debug_mode(),
        "tree_debug": getattr(args, "stand_tree_debug", False),
    }

    if framework == "feedback_and_nl_hint":
        when_args["gated_hints"] = True
    if framework == "nl_hint_only":
        when_args["gated_hints"] = True

    base_args = {
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
        "when_learner": args.when_learner,
        "which_learner": "when_prediction",
        "action_chooser": "max_which_utility",
        "suggest_uncert_neg": True,
        "error_on_bottom_out": False,
        "extra_features": ["Match"],
        "when_args": when_args,
        "should_find_neighbors": True,
    }

    if _process_learning_enabled(args.process_learner):
        base_args["process_learner"] = args.process_learner
        base_args["process_args"] = {}
        base_args["track_rollout_preseqs"] = args.track_rollout_preseqs

    if framework == "nl_hint_only":
        base_args["hint_only_ignore_reward"] = True
        base_args["hint_only_default_reward"] = 1.0

    return base_args


def run_training(agent, typ="arith", logger_name=None, n=30, n_fracs=2,
                training_framework="feedback_and_nl_hint", log_dir="log_al",
                num_incorrect_force_demo=-1, use_hint_llm=False,
                problem_set=None, holdout_problem_set=None, holdout_log_dir=None,
                nl_hint_delivery="demo_only", student_id=None,
                holdout_eval_mode="stepwise"):
    logger = DataShopLogger(logger_name, extra_kcs=["field"], output_dir=log_dir)
    holdout_logger = None
    if holdout_problem_set and holdout_log_dir:
        holdout_logger = DataShopLogger(
            f"{logger_name}_holdout",
            extra_kcs=["field"],
            output_dir=holdout_log_dir,
        )

    env = ApprenticeTutor(domain="solve_triangle")

    trainer_kwargs = {
        "num_incorrect_force_demo": num_incorrect_force_demo,
        "training_framework": training_framework,
        "nl_hint_delivery": nl_hint_delivery,
        "student_id": student_id,
        "holdout_problem_set": holdout_problem_set,
        "holdout_logger": holdout_logger,
        "holdout_eval_mode": holdout_eval_mode,
    }

    if use_hint_llm:
        trainer_kwargs["hint_llm_call"] = build_hf_llm_call()

    trainer_kwargs["problem_set"] = problem_set
    trainer_kwargs["n_problems"] = n

    trainer = Trainer(agent, env, logger=logger, **trainer_kwargs)
    trainer.start()


if __name__ == "__main__":
    from tutorgym.env_classes.apprentice.apprentice_tutor import ApprenticeTutor
    from tutorgym.shared import Action
    import tutorgym.helpers.ai2t_helpers  # Registers SkillApplication -> Action

    parser = argparse.ArgumentParser(description="Run AL agents on triangle geometry")
    parser.add_argument("--train", action="store_true")
    parser.add_argument("--train-only", action="store_true", dest="train_only")
    parser.add_argument("--n-agents", type=int, default=1, dest="n_agents")
    parser.add_argument("--n-problems", type=int, default=15, dest="n_problems")
    parser.add_argument("--n-fracs", type=int, default=2, dest="n_fracs")
    parser.add_argument("--agent-type", default="DIPL", dest="agent_type")
    parser.add_argument("-t", default="arith", dest="env_type")
    parser.add_argument("--training-framework", default="feedback_and_nl_hint", choices=["feedback_only", "nl_hint_only", "feedback_and_nl_hint"],
                        dest="training_framework")
    parser.add_argument(
        "--nl-hint-delivery",
        default="demo_only",
        choices=["off", "demo_only", "feedback_only", "demo_and_feedback"],
        dest="nl_hint_delivery",
        help="When to attach/interpret NL hints for hint-enabled frameworks.",
    )
    parser.add_argument("--when-learner", default="stand", dest="when_learner")
    parser.add_argument("--process-learner", default="htnlearner", dest="process_learner")
    parser.add_argument("--track-rollout-preseqs", default=True, action="store_true", dest="track_rollout_preseqs")
    parser.add_argument("--num-incorrect-force-demo", type=int, default=-1, dest="num_incorrect_force_demo")
    parser.add_argument("--log-dir", default=str(Path(__file__).resolve().parent / "log_al"), dest="log_dir")
    parser.add_argument("--holdout-log-dir", default="", dest="holdout_log_dir")
    parser.add_argument("--holdout-count", type=int, default=0, dest="holdout_count")
    parser.add_argument(
        "--holdout-eval-mode",
        default="stepwise",
        choices=["off", "next_problem", "stepwise"],
        dest="holdout_eval_mode",
    )
    parser.add_argument("--predicate-threshold", type=int, default=5, dest="predicate_threshold")
    parser.add_argument("--agent-seed", type=int, default=None, dest="agent_seed")
    parser.add_argument("--agent-seed-base", type=int, default=1000, dest="agent_seed_base")
    parser.add_argument("--agent-seed-step", type=int, default=1, dest="agent_seed_step")
    parser.add_argument("--agent-index-base", type=int, default=0, dest="agent_index_base")

    parser.add_argument("--safe-train", action="store_true")
    parser.add_argument("--unicode-fallback", action="store_true")
    parser.add_argument("--unicode-wchar-patch", action="store_true", dest="unicode_wchar_patch", default=True)
    parser.add_argument("--no-unicode-wchar-patch", action="store_false", dest="unicode_wchar_patch")
    parser.add_argument("--when-weight-debug", action="store_true", dest="when_weight_debug")
    parser.add_argument("--stand-tree-debug", action="store_true", dest="stand_tree_debug")
    parser.add_argument("--use-hf-llm", action="store_true")
    parser.add_argument("--llm-seed", type=int, default=None, dest="llm_seed")
    parser.add_argument("--llm-temperature", type=float, default=None, dest="llm_temperature")
    parser.add_argument("--llm-cache-dir", default="", dest="llm_cache_dir")
    parser.add_argument(
        "--openai-api-key",
        default=os.environ.get("OPENAI_API_KEY", ""),
        help="Optional OpenAI API key used by hint interpreter (overrides OPENAI_API_KEY env var).",
    )

    args = parser.parse_args()

    if args.safe_train:
        # Keep interface compatibility with older launch scripts.
        pass

    if args.unicode_wchar_patch:
        os.environ.setdefault("PYTHONUNBUFFERED", "1")

    if args.when_weight_debug:
        os.environ["CRE_STAND_WEIGHT_DEBUG"] = "1"
    if args.stand_tree_debug:
        os.environ["CRE_STAND_TREE_DEBUG"] = "1"
    if args.openai_api_key:
        os.environ["OPENAI_API_KEY"] = args.openai_api_key
    if args.llm_temperature is not None:
        os.environ["CRE_HINT_LLM_TEMPERATURE"] = str(args.llm_temperature)
    if args.llm_cache_dir:
        os.environ["CRE_HINT_LLM_CACHE_DIR"] = args.llm_cache_dir

    if args.training_framework not in {"feedback_only", "nl_hint_only", "feedback_and_nl_hint"}:
        raise ValueError(f"Unsupported training framework: {args.training_framework}")

    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    holdout_log_dir = None
    if args.holdout_count > 0:
        holdout_log_dir = Path(args.holdout_log_dir) if args.holdout_log_dir else (log_dir / "holdout")
        holdout_log_dir.mkdir(parents=True, exist_ok=True)

    for agent_index in range(args.n_agents):
        effective_agent_index = args.agent_index_base + agent_index
        agent_seed = args.agent_seed
        if agent_seed is None:
            agent_seed = args.agent_seed_base + (agent_index * args.agent_seed_step)
        set_global_seed(agent_seed)

        agent_llm_seed = (
            args.llm_seed + (agent_index * args.agent_seed_step)
            if args.llm_seed is not None
            else agent_seed
        )
        if agent_llm_seed is not None:
            os.environ["CRE_HINT_LLM_SEED"] = str(agent_llm_seed)

        from apprentice.agents.cre_agents.cre_agent import CREAgent

        agent_args = _collect_framework_options(args.training_framework, args)
        # Use explicit learner selection for every run.
        agent_args["when_learner"] = args.when_learner
        if _process_learning_enabled(args.process_learner):
            agent_args["process_learner"] = args.process_learner

        if args.unicode_wchar_patch and args.training_framework:
            os.environ["PYTHONUTF8"] = "1"

        agent = CREAgent(**agent_args)

        train_problem_set, holdout_problem_set = build_problem_sets(
            args.n_problems,
            seed=agent_seed,
            holdout_count=args.holdout_count,
        )

        agent_tag = f"agent{effective_agent_index:02d}_seed{agent_seed}"
        logger_name = (
            f"frac_{args.env_type}_{args.agent_type}_{args.n_fracs}frac_"
            f"{args.n_probs if hasattr(args, 'n_probs') else args.n_problems}probs_"
            f"{args.training_framework}_{args.nl_hint_delivery}_{agent_tag}"
        )
        student_id = agent_tag

        run_training(
            agent,
            args.env_type,
            logger_name=logger_name,
            n=int(args.n_problems),
            n_fracs=args.n_fracs,
            training_framework=args.training_framework,
            log_dir=str(log_dir),
            num_incorrect_force_demo=args.num_incorrect_force_demo,
            use_hint_llm=args.use_hf_llm,
            problem_set=train_problem_set,
            holdout_problem_set=holdout_problem_set,
            holdout_log_dir=str(holdout_log_dir) if holdout_log_dir is not None else None,
            nl_hint_delivery=args.nl_hint_delivery,
            student_id=student_id,
            holdout_eval_mode=args.holdout_eval_mode,
        )
