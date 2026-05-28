import os
import random
import sys
from pathlib import Path

import numpy as np

script_path = Path(__file__).resolve()
workspace_root = script_path.parents[3]

for p in [
    str(workspace_root / "AL_Core"),
    str(workspace_root / "tutor_gym"),
    str(workspace_root / "STAND"),
    str(workspace_root / "tutor_gym" / "Cognitive-Rule-Engine"),
]:
    if p not in sys.path:
        sys.path.insert(0, p)

if os.environ.get("NUMBA_DISABLE_JIT") == "1":
    print("[run_al_norf] NUMBA_DISABLE_JIT=1 detected; enabling JIT for CRE.")
os.environ["NUMBA_DISABLE_JIT"] = "0"

from tutorgym.env_classes.apprentice.apprentice_tutor import ApprenticeTutor
from tutorgym.envs.apprentice.cognitive_models.multicolumn.htn_multicolumn_addition import (
    htn_multicolumn_addition_intermediate_hints,
    htn_multicolumn_addition_problem_pool,
)
from tutorgym.trainer import Trainer
from tutorgym.utils import DataShopLogger


def _cycle_problem_pool(pool, n, seed=None):
    if n <= 0:
        return []

    rng = random.Random(seed)
    ordered = list(pool)
    rng.shuffle(ordered)

    problems = []
    while len(problems) < n:
        batch = list(ordered)
        rng.shuffle(batch)
        problems.extend(batch)
    return problems[:n]


def build_problem_set(n_problems, seed=None):
    return [
        {"domain": "multicolumn_addition", "initial_problem": problem}
        for problem in _cycle_problem_pool(
            htn_multicolumn_addition_problem_pool("train"),
            int(n_problems),
            seed=seed,
        )
    ]


def run_training(agent, logger_name='MulticolumnAddition', n=10,
                 n_columns=3, author_train=True, carry_zero=False, seed=None):
    if n_columns != 3:
        raise ValueError(
            "The ApprenticeTutor multicolumn_addition domain currently supports fixed 3-column problems."
        )

    logger = DataShopLogger(logger_name, extra_kcs=['field'], output_dir='log_al_norf')
    env = ApprenticeTutor(domain="multicolumn_addition")

    trainer = Trainer(
        agent,
        env,
        logger=logger,
        problem_set=build_problem_set(n, seed=seed),
        n_problems=n,
        training_framework="feedback_and_nl_hint",
        nl_hint_delivery="demo_only",
    )
    trainer.start()


if __name__ == "__main__":
    import faulthandler; faulthandler.enable()

    np.set_printoptions(edgeitems=30, linewidth=100000,
        formatter=dict(float=lambda x: "%.3g" % x))

    import argparse
    parser = argparse.ArgumentParser(
        description='Runs AL agents on multi-column addition')
    parser.add_argument('--n-agents', default=50, type=int, metavar="<n_agents>",
                        dest="n_agents", help="number of agents")
    parser.add_argument('--n-problems', default=500, type=int, metavar="<n_problems>",
                        dest="n_problems", help="number of problems")
    parser.add_argument('--n-columns', default=3, type=int, metavar="<n_columns>",
                        dest="n_columns", help="number of columns")
    parser.add_argument('--agent-type', default='DIPL',metavar="<agent_type>",
                        dest="agent_type", help="agent type; DIPL is supported for this HTN runner")
    parser.add_argument('--agent-seed-base', default=1000, type=int,
                        dest="agent_seed_base", help="base random seed for agents/problems")

    args = parser.parse_args(sys.argv[1:])

    logger_name = f'mc_addition_{args.agent_type}_{args.n_columns}col_{args.n_problems}probs'
    for agent_index in range(args.n_agents):
        agent_seed = args.agent_seed_base + agent_index
        random.seed(agent_seed)
        np.random.seed(agent_seed)

        if(args.agent_type.upper() == "DIPL"):
            from apprentice.agents.cre_agents.cre_agent import CREAgent
            agent_args = {
                "search_depth" : 2,
                "where_learner": "mostspecific",
                "when_learner": "stand",
                "which_learner": "when_prediction",
                "action_chooser" : "max_which_utility",
                "suggest_uncert_neg" : True,
                "explanation_choice" : "least_operations",
                "planner" : "set_chaining",
                "function_set" : [
                    "out1", "carry1", "out2", "carry2", "out3", "carry3", "out4",
                ],
                "feature_set" : ["Equals"],
                "extra_features" : ["Match"],
                "should_find_neighbors" : True,
                "when_args": {
                    "encode_relative" : True,
                    "one_hot": True,
                    "gated_hints": True,
                    "gated_hint_map": htn_multicolumn_addition_intermediate_hints(),
                },
                "process_learner": "htnlearner",
                "track_rollout_preseqs": True,
            }
            agent = CREAgent(**agent_args)
        else:
            raise ValueError(
                f"Unrecognized or unsupported agent type {args.agent_type!r}; "
                "use DIPL for the ApprenticeTutor HTN multicolumn runner."
            )

        run_training(
            agent,
            logger_name=logger_name,
            n=int(args.n_problems),
            n_columns=args.n_columns,
            seed=agent_seed,
        )
