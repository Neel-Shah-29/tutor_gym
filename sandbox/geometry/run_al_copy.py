import os
import sys
from pathlib import Path

# CRE structrefs require numba's JIT; force it on even if the env disables it.
if os.environ.get("NUMBA_DISABLE_JIT") == "1":
    print("[run_al_copy] NUMBA_DISABLE_JIT=1 detected; enabling JIT for CRE.")
os.environ["NUMBA_DISABLE_JIT"] = "0"

# Prefer the in-repo Cognitive-Rule-Engine over any installed version to avoid numba cache locator issues.
repo_root = Path(__file__).resolve().parents[2]
local_cre = repo_root / "Cognitive-Rule-Engine"
if local_cre.exists():
    sys.path.insert(0, str(local_cre))

from apprentice.agents.cre_agents.hint_nlp import interpret_hint_with_llm, build_hf_llm_call
from apprentice.agents.cre_agents.environment import TextField, Label, Button, Component

# Import CRE components for type checking (Var and Fact)
from cre import Var, Fact
from numba.types import string as string_type

# from apprentice.agents.ModularAgent import ModularAgent
# from apprentice.agents.RHS_LHS_Agent import RHS_LHS_Agent
# from apprentice.agents.WhereWhenHowNoFoa import WhereWhenHowNoFoa
import apprentice
from apprentice.working_memory.representation import Sai

# from tutorgym.env_classes.misc.fraction_arith.fractions import FractionArithmetic
from tutorgym.trainer import Trainer, AuthorTrainer
from tutorgym.utils import DataShopLogger


from tutorgym.env_classes.apprentice.apprentice_tutor import ApprenticeTutor
from tutorgym.envs.apprentice.cognitive_models.solve_triangle.htn_geometry_solve_triangle import (
    htn_geometry_solve_triangle_intermediate_hints,
)





def run_training(agent, typ='arith', logger_name=None, n=30, n_fracs=2, demo_args=False):
    # logger_name, problem_types = resolve_type(typ, logger_name)
    logger = DataShopLogger(logger_name, extra_kcs=['field'], output_dir='log_al')
    
    env = ApprenticeTutor(domain="solve_triangle")
                             # demo_args=False)
    env.set_random_problem()
    demo1 = env.get_demo()
    print("DEMO 1:", demo1)
    # Pull an interactive hint from the geometry cognitive model so we stay aligned
    # with the official hint text instead of inventing ad-hoc phrasing.
    # Extract hint_key dynamically from the demo action
    if hasattr(demo1, 'selection') and demo1.selection:
        hint_key = demo1.selection
    else:
        hint_key = "apply_pythagorean" if "apply_pythagorean" in agent.function_set else agent.function_set[0]
    print(f"DEBUG: Extracted hint_key from demo: {hint_key}")
    geom_hints = htn_geometry_solve_triangle_intermediate_hints()
    hint_candidates = geom_hints.get(hint_key, []) if geom_hints else []
    hint = hint_candidates[0] if hint_candidates else "Use the Pythagorean theorem."
    print(f"Using interactive hint for {hint_key}: {hint}")
    state = env.get_state()
    agent_state = agent.standardize_state(state.objs, False)
    flat_feat_state = agent_state.get("flat_featurized")

    # Use a HuggingFace text-generation model if available; otherwise fall back to a simple heuristic.
    use_hf_llm = os.environ.get("USE_HF_LLM", "0") == "1"
    
    # FORCE LLM usage for this task if available, or warn user
    try:
        hf_llm_call = build_hf_llm_call()
        llm_call = hf_llm_call
        print("[run_al_copy] Using HF LLM for hint interpretation.")
        use_hf_llm = True
    except RuntimeError as exc:
        print("[run_al_copy] HF LLM unavailable:", exc)
        print("[run_al_copy] Falling back to heuristic LLM call.")
        use_hf_llm = False

    if not use_hf_llm:
        def llm_call(prompt: str) -> str:
            # crude filter: keep predicates that mention tokens from the hint
            if hasattr(flat_feat_state, "get_facts"):
                preds = [str(fact) for fact in flat_feat_state.get_facts()]
            elif isinstance(flat_feat_state, (list, tuple)):
                preds = list(flat_feat_state)
            else:
                preds = []
            hint_tokens = {tok.lower() for tok in hint.replace("'", "").split()}
            kept = [p for p in preds if any(tok in str(p).lower() for tok in hint_tokens)]
            return " && ".join(map(str, kept[:3])) or "True"
        print("[run_al_copy] Using heuristic LLM call (HF disabled or unavailable).")

    # print("Featurized state:", flat_feat_state)
    print("Using LLM to interpret hint:", hint)
    
    # Pass both predicates and raw state objects for richer hint interpretation.
    predicates = []
    if hasattr(flat_feat_state, "get_facts"):
        predicates = [str(fact) for fact in flat_feat_state.get_facts()]
    state_for_llm = {
        "_predicates": predicates,
        "_objs": state.objs if hasattr(state, "objs") else state, # try with both with and without objs
    }
    
    
    some_string = interpret_hint_with_llm(state_for_llm, demo1, hint, llm_call)
    print("\n" + "="*40)
    print(f"HINT: {hint}")
    print(f"LLM GENERATED CODE:\n{some_string}")
    
    # --- Evaluate CRE Conditions against working_memory ---
    def eval_cre_conditions(cond_code, agent_state):
        """Execute LLM-generated CRE Conditions code and evaluate against working_memory."""
        if not cond_code or "llm_error" in cond_code:
            return "ERROR"
        if isinstance(cond_code, str) and cond_code.strip().lower() in ("true", "false"):
            return cond_code.strip().lower() == "true"
        
        # Extract code from markdown if present
        if "```python" in cond_code:
            start = cond_code.find("```python") + len("```python")
            end = cond_code.find("```", start)
            cond_code = cond_code[start:end].strip()
        elif "```" in cond_code:
            start = cond_code.find("```") + 3
            end = cond_code.find("```", start)
            cond_code = cond_code[start:end].strip()
        
        print(f"DEBUG: Extracted code:\n{cond_code}\n")
        
        # Build execution context with CRE imports
        exec_context = {"__builtins__": __builtins__}
        
        # Import CRE components and fact types for execution.
        from cre import Var
        from cre.conditions import AND, OR

        exec_context["Var"] = Var
        exec_context["AND"] = AND
        exec_context["OR"] = OR
        exec_context["TextField"] = TextField
        exec_context["Label"] = Label
        exec_context["Button"] = Button
        exec_context["Component"] = Component
        
        # Execute the generated code
        try:
            exec(cond_code, exec_context)
            conds = exec_context.get("conds")
            if conds is None:
                return "ERROR: Generated code did not create 'conds' variable"
            print(f"DEBUG: Created CRE Conditions: {conds}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Exec Failed: {e}"
        
        # Evaluate against working_memory
        try:
            wm = agent_state.get("working_memory")
            if wm is None:
                return "ERROR: No working_memory in agent_state"
            
            # Get matches from working_memory using CRE's matching system
            if isinstance(conds, bool):
                return conds
            matches = list(conds.get_matches(wm))
            
            result = len(matches) > 0
            print(f"DEBUG: Found {len(matches)} matches in working_memory")
            return result
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Match Failed: {e}"

    eval_result = eval_cre_conditions(some_string, agent_state)
    print(f"EVALUATION RESULT: {eval_result}")
    print("="*40 + "\n")
    # trainer = Trainer(agent, env, logger=logger, n_problems=n)

    # trainer.start()

if __name__ == "__main__":
    import sys, argparse
    import faulthandler; faulthandler.enable()
    
    parser = argparse.ArgumentParser(
        description='Runs AL agents on multi-column addition')
    parser.add_argument('--n-agents', default=50, type=int, metavar="<n_agents>",
                        dest="n_agents", help="number of agents")
    parser.add_argument('--n-problems', default=500, type=int, metavar="<n_problems>",
                        dest="n_problems", help="number of problems")
    parser.add_argument('--n-fracs', default=2, type=int, metavar="<n_fracs>",
                        dest="n_fracs", help="number of fractions")
    parser.add_argument('--agent-type', default='DIPL',metavar="<agent_type>",
                        dest="agent_type", help="type of agents DIPL or RHS_LHS")
    parser.add_argument('-t', default='arith',metavar="<env_type>",
                        dest="env_type", help="'arith' (i.e. mult & addition), 'mult' or 'addition'")


    args = parser.parse_args(sys.argv[1:])

    print("n_agents", args.n_agents)
    # function_set = ['RipFloatValue','Add','Multiply','Subtract','ConvertNumerator']
                    # 'Divide',
                    # 'DivideRound',
                    #, 'Add3', 'Add4', 'Add5', 
                    #, 'Multiply3', 'Multiply4', 'Multiply5', 
                    # ]
    # feature_set = ['Equals']
    feature_set = []
    
    logger_name = f'frac_{args.env_type}_{args.agent_type}_{args.n_fracs}frac_{args.n_problems}probs'
    
    for _ in range(args.n_agents):
        if(True):
            from apprentice.agents.cre_agents.cre_agent import CREAgent
            import tutorgym.helpers.ai2t_helpers # Registers SkillApplication -> Action

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
                "feature_set": ['Equals'],
                "planner":'set_chaining',
                "explanation_choice" : "least_operations",
                "search_depth": 2,

                # "where_learner" : "antiunify",
                "where_learner": "mostspecific",

                # For STAND
                "when_learner": "decision_tree",
                "which_learner": "when_prediction",
                "action_chooser" : "max_which_utility",
                "suggest_uncert_neg" : True,

                "error_on_bottom_out" : False,

                # "when_learner" : 'sklearndecisiontree',
                # "when_learner" : 'decisiontree',
                
                "extra_features" : ["Match"],
                "when_args" : {"encode_relative" : True, "one_hot" : True},
                
                "should_find_neighbors" : True
            }

            agent = CREAgent(**agent_args)
        elif(args.agent_type.upper() == "MODULAR"):
            from apprentice.agents.ModularAgent import ModularAgent

            agent_args = dict(
                function_set=['RipFloatValue','Add','Multiply','Subtract','ConvertNumerator'],

                feature_set=['Equals'],
                planner='numba',
                explanation_choice = "least_operations",
                search_depth=3,
                when_learner='decisiontree2',
                # where_learner='FastMostSpecific',
                where_learner="mostspecific",
                # where_learner="version_space",
                # state_variablization='whereswap',
                state_variablization = "metaskill",
                strip_attrs=["to_left","to_right","above","below","type","id","offsetParent", "dom_class"],
                should_find_neighbors=True
            )

            agent = ModularAgent(**agent_args)
        elif(args.agent_type.upper() == "RHS_LHS"):
            from apprentice.agents.RHS_LHS_Agent import RHS_LHS_Agent
            agent = RHS_LHS_Agent(**agent_args)
        else:
            raise ValueError(f"Unrecognized agent type {args.agent_type!r}.")

        run_training(agent, args.env_type, logger_name=logger_name,  n=int(args.n_problems), n_fracs=args.n_fracs)


    # for i in range(100):
    #     agent = ModularAgent(**agent_args)
    #     # agent = RHS_LHS_Agent(**agent_args)
    #     # agent = WhereWhenHowNoFoa('fraction arith', 'fraction arith',
    #     #                       search_depth=1)

    #     run_training(agent, n=20, demo_args=True)
