# from apprentice.agents.ModularAgent import ModularAgent
# from apprentice.agents.RHS_LHS_Agent import RHS_LHS_Agent
# from apprentice.agents.WhereWhenHowNoFoa import WhereWhenHowNoFoa
import apprentice
from apprentice.working_memory.representation import Sai

# from tutorgym.env_classes.misc.fraction_arith.fractions import FractionArithmetic
from tutorgym.trainer import Trainer, AuthorTrainer
from tutorgym.utils import DataShopLogger


from tutorgym.env_classes.apprentice.apprentice_tutor import ApprenticeTutor





def run_training(agent, typ='arith', logger_name=None, n=30, n_fracs=2, demo_args=False):
    # logger_name, problem_types = resolve_type(typ, logger_name)
    logger = DataShopLogger(logger_name, extra_kcs=['field'], output_dir='log_al')
    
    env = ApprenticeTutor(domain="solve_triangle")
                             # demo_args=False)
    trainer = Trainer(agent, env, logger=logger, n_problems=n)
    trainer.start()

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
    feature_set = ['Equals']

    
    logger_name = f'frac_{args.env_type}_{args.agent_type}_{args.n_fracs}frac_{args.n_problems}probs'
    
    for _ in range(args.n_agents):
        if(True):
            from apprentice.agents.cre_agents.cre_agent import CREAgent
            import tutorgym.helpers.ai2t_helpers # Registers SkillApplication -> Action

            agent_args = {
                # "function_set": ['AcrossMultiply','Multiply', 'Add'],
                "function_set": ['classify_triangle'],
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
