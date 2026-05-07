from tutorgym.shared import Action, ProblemState
from tutorgym.utils import DataShopLogger
from colorama import Back, Fore, Style
import colorama
from colorama import init
from pprint import pprint
import json
from pathlib import Path

# init(autoreset=True)

class ProblemIterator:
    def __init__(self, problem_set=None, n_problems=None, **kwargs):
        # print("problem_set", problem_set)
        # raise ValueError()
        if(problem_set is not None):
            n_problems = 0 if n_problems is None else n_problems
            self.n_problems = max(n_problems, len(problem_set))
            self.problem_set = problem_set
        else:   
            self.n_problems = n_problems
            self.problem_set = []

        self.p = 0

    def __iter__(self):
        return self

    def __next__(self):
        p = self.p
        if(p >= self.n_problems):
            raise StopIteration
        self.p += 1
        if(p < len(self.problem_set)):
            prob_args = self.problem_set[p]
            return prob_args
        else:
            return None

class Trainer:
    def __init__(self, agent, env, logger=None,
                 num_incorrect_force_demo=-1,
                 evaluators=[],
                 problem_end_callbacks = [],
                 step_end_callbacks = [],
                 train_end_callbacks = [],
                 agent_action_repr = "action",
                 agent_state_repr = "obj_dicts",
                 hint_llm_call=None,
                 **kwargs):
        self.agent = agent
        self.env = env
        if(logger is None or isinstance(logger, str)):
            logger_name = logger
            if(logger_name is None):
                logger_name = type(self.env).__name__
            self.logger = DataShopLogger(logger_name, extra_kcs=['field'])
        else:
            self.logger = logger
        self.num_incorrect_force_demo = num_incorrect_force_demo
        self.always_update_state = kwargs.get('always_update_state', False)
        self.train_next_state = kwargs.get('train_next_state', False)
        self.total_incorrect = 0
        self.total_correct = 0
        self.total_hints = 0
        self.agent_action_repr = agent_action_repr
        self.agent_state_repr = agent_state_repr
        self.hint_llm_call = hint_llm_call

        self.training_framework = str(kwargs.get("training_framework", "feedback_and_nl_hint")).strip().lower()
        if self.training_framework not in {
            "feedback_only",
            "nl_hint_only",
            "feedback_and_nl_hint",
        }:
            self.training_framework = "feedback_and_nl_hint"
        self.nl_hint_delivery = str(kwargs.get("nl_hint_delivery", "demo_only")).strip().lower()
        if self.nl_hint_delivery not in {
            "off",
            "demo_only",
            "feedback_only",
            "demo_and_feedback",
        }:
            self.nl_hint_delivery = "demo_only"
        self._interpret_nl_hint = self.training_framework in {"feedback_and_nl_hint", "nl_hint_only"}
        self.student_id = kwargs.get("student_id")
        self.holdout_problem_set = list(kwargs.get("holdout_problem_set", []) or [])
        self.holdout_logger = kwargs.get("holdout_logger")
        self.holdout_eval_mode = str(kwargs.get("holdout_eval_mode", "stepwise")).strip().lower()
        if self.holdout_eval_mode not in {"off", "next_problem", "stepwise"}:
            self.holdout_eval_mode = "stepwise"
        self.holdout_total_incorrect = 0
        self.holdout_total_correct = 0

        if('problem_set' not in kwargs and
           'n_problems' not in kwargs and 
           'outer_loop_controller' not in kwargs):
            raise ValueError("Trainer Be Given either a 'problem_set', 'n_problems', or an 'outer_loop_controller'")

        if('outer_loop_controller' in kwargs):
            self.outer_loop_controller = kwargs['outer_loop_controller']
            self.problem_iterator = self.outer_loop_controller
        else:
            self.problem_iterator = ProblemIterator(**kwargs)

        self.step_end_evaluators = []
        self.problem_end_evaluators = []
        self.train_end_evaluators = []

        for ev in evaluators:
            ev.initialize(self, agent, env)
            if(ev.eval_freq == "step_end"):
                self.step_end_evaluators.append(ev)
            elif(ev.eval_freq == "problem_end"):
                self.problem_end_evaluators.append(ev)
            elif(ev.eval_freq == "train_end"):
                self.train_end_evaluators.append(ev)
            else:
                raise ValueError(f"Unrecognized eval_freq: {ev.eval_freq}.")

        self.problem_end_callbacks = problem_end_callbacks
        self.step_end_callbacks = step_end_callbacks
        self.train_end_callbacks = train_end_callbacks

    def _should_use_nl_hint(self, outcome_kind):
        if not self._interpret_nl_hint:
            return False
        if self.nl_hint_delivery == "off":
            return False
        if outcome_kind == "HINT":
            return self.nl_hint_delivery in {"demo_only", "demo_and_feedback"}
        if outcome_kind in {"CORRECT", "INCORRECT"}:
            return self.nl_hint_delivery in {"feedback_only", "demo_and_feedback"}
        return False

    def _resolve_hint_text(self, action):
        if isinstance(action, Action):
            hint_txt = action.annotations.get("hint")
            if isinstance(hint_txt, str) and hint_txt.strip():
                return hint_txt.strip()
            sel = action.selection
        else:
            sel = getattr(action, "selection", None)

        if not sel:
            return None

        hint_map = getattr(self.env, "intermediate_hints", {}) or {}
        hint_values = hint_map.get(sel)
        if isinstance(hint_values, str) and hint_values.strip():
            return hint_values.strip()
        if isinstance(hint_values, (list, tuple)):
            for hint_txt in hint_values:
                if isinstance(hint_txt, str) and hint_txt.strip():
                    return hint_txt.strip()
        return None

    def _annotate_nl_hint(self, state, action, train_kwargs, outcome_kind):
        if not self._should_use_nl_hint(outcome_kind):
            return None

        hint_txt = self._resolve_hint_text(action)
        if not hint_txt:
            return None

        print(f"[Trainer] NL hint ({outcome_kind.lower()}): {hint_txt}")
        hint_precond = None
        try:
            try:
                from apprentice.agents.cre_agents.hint_nlp import interpret_hint, interpret_hint_with_llm
            except ImportError:
                from AL_Core.apprentice.agents.cre_agents.hint_nlp import interpret_hint, interpret_hint_with_llm
            if self.hint_llm_call:
                hint_precond = interpret_hint_with_llm(state, action, hint_txt, self.hint_llm_call)
            else:
                hint_precond = interpret_hint(state, action, hint_txt)
            if hint_precond:
                print(f"[Trainer] Hint precondition ({outcome_kind.lower()}): {hint_precond}")
        except Exception as exc:
            print(f"[Trainer] hint interpretation failed: {exc}")
            hint_precond = None

        if isinstance(action, Action):
            action.annotations["hint"] = hint_txt
            if hint_precond:
                action.annotations["hint_precond"] = hint_precond
            train_kwargs["action"] = self._sanitize_action(action)
        if hint_precond:
            train_kwargs["hint_precond"] = hint_precond
        return hint_precond


    def _canonicalize_str(self, value):
        if not isinstance(value, str):
            return value
        try:
            cleaned = value.encode('utf-8', 'surrogatepass').decode('utf-8', 'surrogatepass')
        except Exception:
            cleaned = str(value)
        return cleaned

    def _json_clone(self, obj):
        try:
            return json.loads(json.dumps(obj, ensure_ascii=False))
        except (TypeError, ValueError):
            return obj

    def _sanitize_structure(self, obj):
        if isinstance(obj, str):
            return self._canonicalize_str(obj)
        if isinstance(obj, dict):
            return {self._sanitize_structure(k): self._sanitize_structure(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._sanitize_structure(x) for x in obj]
        if isinstance(obj, tuple):
            return tuple(self._sanitize_structure(x) for x in obj)
        return obj

    def _sanitize_problem_state(self, state: ProblemState) -> ProblemState:
        objs = self._sanitize_structure(state.objs)
        annotations = self._sanitize_structure(state.annotations)
        if objs is state.objs and annotations is state.annotations:
            return state
        return ProblemState(objs, [*state.action_hist], **annotations)

    def _sanitize_action(self, action: Action) -> Action:
        sel, act_type, inp = action.as_tuple()
        sanitized_sel = self._sanitize_structure(sel)
        sanitized_act_type = self._sanitize_structure(act_type)
        sanitized_inp = self._sanitize_structure(inp)
        sanitized_annotations = {
            self._sanitize_structure(k): self._sanitize_structure(v)
            for k, v in action.annotations.items()
        }
        return Action(
            (sanitized_sel, sanitized_act_type, sanitized_inp),
            **sanitized_annotations
        )

    def _state_to_kwargs(self, state, is_start=None):
        sanitized_state = self._sanitize_problem_state(state)
        if(self.agent_state_repr == "obj_dicts"):
            state_payload = self._json_clone(sanitized_state.objs)
            anno_payload = self._json_clone(sanitized_state.annotations)
            s = {"state" : state_payload, **anno_payload, "is_start" : is_start,}
        else:
            s = {"state" : sanitized_state, "is_start" : is_start}
        return s

    def _to_train_kwargs(self, state, action, reward, is_demo=False, is_start=None):

        s = self._state_to_kwargs(state, is_start)

        if(isinstance(action, Action)):
            sanitized_action = self._sanitize_action(action)
            a = {"action" : sanitized_action,
                 **sanitized_action.annotations}
        else:
            a = {"action" : action}

        # if(self.agent_action_repr == "skill_app" and not is_demo):
        #     print("A")
            
        # elif(self.agent_action_repr == "action"):
        #     print("B", self.agent_action_repr)
        #     a = {"action" : action,
        #          **action.annotations}
        # else:
        #     print("C")
        #     a = action.as_train_kwargs()

        d = {**s, 
            **a,
            "reward": reward,
            "is_demo" : is_demo
            }
        # if('how_str' in d):
        #     d['how_help'] = d.get('how_str', None)

        return d
        # # if(self.agent_action_repr == "skill_app" and not is_demo):
        #     return {"state" : state,
        #             "skill_app" : action,
        #             "is_start" : is_start,
        #             "reward" : reward}
        # # else:
        #     return {"state" : state,
        #             "reward" : reward,
        #             "is_start" : is_start,
        #             **action.as_train_kwargs(),
        #             "is_demo" : is_demo}

    def print_outcome(self, action, outcome_kind):
        extra = ""
        
        if(isinstance(action, Action)):
            sel, at, inp = action.as_tuple()
            extra = ','.join([f"{k}={v}" for k,v in action.annotations.items()])
        # elif('sai' in action):
        #     sai = Action(action['sai']).as_tuple()
        #     # print(action)
        #     arg_foci = action.get('arg_foci',['???'])
        #     if(arg_foci is None):
        #         arg_foci = ['???']
        #     extra = f"{getattr(action,'how_str','???')}({','.join(arg_foci)})"
        # elif('skill_app' in action):
        #     print("ACTION", action)
        #     skill_app = action['skill_app']
        #     sai = Action(skill_app.sai).as_tuple()        
        #     extra = f'{skill_app.__repr__(add_sai=False)}'
            # how_part = getattr(getattr(skill_app,'skill'),'how_part', "???")
            # arg_foci = getattr(skill_app,'arg_foci',['???'])
            # print("arg_foci", arg_foci)
            # if(arg_foci is None):
            #     arg_foci = []
            # extra = f"{how_part}({','.join(arg_foci)})"

        if(outcome_kind == "CORRECT"):
            print(Back.GREEN + Fore.BLACK  + f"CORRECT: {sel} -> {inp} {extra}" + Style.RESET_ALL)
        elif(outcome_kind == "INCORRECT"):            
            print(Back.RED + Fore.BLACK + f"INCORRECT: {sel} -> {inp} {extra}" + Style.RESET_ALL)
        elif(outcome_kind == "HINT"):
            print(Back.BLUE + Fore.YELLOW + f"HINT: {sel} -> {inp} {extra}" + Style.RESET_ALL)

    def tutor_train_state(self, state, is_start=False, force_demo=False):
        ''' Tutor-train (i.e. train one action at a time) on 'state'.'''

        if(not force_demo):
            # actions = self.agent.act_all(
            action = self.agent.act(**self._state_to_kwargs(state, is_start),
                return_kind=self.agent_action_repr)
        else:
            action = None

        
        outcome_kind = None

        if(action):
            conv_action = Action(action)
            reward = self.env.check(conv_action)
            if(reward > 0):
                outcome_kind = "CORRECT"
                self.total_correct += 1
            else:
                outcome_kind = "INCORRECT"
                self.total_incorrect += 1
        else:
            action = self.env.get_demo()
            conv_action = Action(action)
            reward = 1
            outcome_kind = "HINT"
            self.total_hints += 1

        # print("A ACTION:", action)

        s,a,inp = action.as_tuple()
        self.logger.log_step(s, a, inp, outcome_kind, step_name=s, kcs=[s])

        train_kwargs = self._to_train_kwargs(state, action, reward, 
             is_start=is_start,
             is_demo=outcome_kind=="HINT")
        self._annotate_nl_hint(state, conv_action, train_kwargs, outcome_kind)

        if self.training_framework == "nl_hint_only":
            train_kwargs["hint_only_mode"] = True
            if outcome_kind != "HINT":
                train_kwargs["attempted_action"] = self._sanitize_action(conv_action)
                train_kwargs["attempted_reward"] = reward

        try:
            self.agent.train(**train_kwargs)
        except AssertionError as exc:
            if "PY_UNICODE_WCHAR_KIND unsupported" in str(exc):
                extra = {}
                for k,v in train_kwargs.items():
                    if k in ("state","action","reward","is_demo","is_start"):
                        continue
                    try:
                        json.dumps(v, ensure_ascii=False)
                        extra[k] = v
                    except TypeError:
                        extra[k] = repr(v)
                debug_payload = {
                    "state": train_kwargs.get("state"),
                    "action": str(train_kwargs.get("action")),
                    "reward": train_kwargs.get("reward"),
                    "is_demo": train_kwargs.get("is_demo"),
                    "is_start": train_kwargs.get("is_start"),
                    "extra": extra,
                }
                debug_file = Path("log_al") / "unicode_debug.json"
                try:
                    debug_file.parent.mkdir(exist_ok=True)
                    with open(debug_file, "w", encoding="utf-8") as fh:
                        json.dump(debug_payload, fh, ensure_ascii=False, indent=2)
                    print(f"[Trainer] Wrote unicode debug snapshot to {debug_file}")
                except Exception as log_exc:
                    print(f"[Trainer] Failed to write unicode debug snapshot: {log_exc}")
            raise
        self.print_outcome(conv_action, outcome_kind)

        # Change the state by applying the action
        if(reward > 0 or self.always_update_state):
            self.env.apply(conv_action)

        return reward                

    def _print_holdout_outcome(self, action, outcome_kind):
        prefix = "[Holdout] "
        if isinstance(action, Action):
            sel, _, inp = action.as_tuple()
            print(f"{prefix}{outcome_kind}: {sel} -> {inp}")
        else:
            print(f"{prefix}{outcome_kind}")

    def holdout_eval_state(self, state, is_start=False):
        action = self.agent.act(
            **self._state_to_kwargs(state, is_start),
            return_kind=self.agent_action_repr,
        )

        conv_action = Action(action) if action else None
        reward = None
        outcome_kind = None

        if conv_action is not None:
            reward = self.env.check(conv_action)
            if reward > 0:
                outcome_kind = "CORRECT"
                self.holdout_total_correct += 1
            else:
                outcome_kind = "INCORRECT"
                self.holdout_total_incorrect += 1
        else:
            outcome_kind = "INCORRECT"
            self.holdout_total_incorrect += 1
            reward = -1

        log_action = conv_action if conv_action is not None else self.env.get_demo()
        if log_action is not None and self.holdout_logger is not None:
            s, a, inp = log_action.as_tuple()
            self.holdout_logger.log_step(s, a, inp, outcome_kind, step_name=s, kcs=[s])

        self._print_holdout_outcome(log_action, outcome_kind)

        if reward > 0 and conv_action is not None:
            self.env.apply(conv_action)
            return reward

        if self.holdout_eval_mode == "stepwise":
            demo = self.env.get_demo()
            if demo is not None:
                self.env.apply(demo)
        return reward

    def run_holdout(self):
        if not self.holdout_problem_set or self.holdout_eval_mode == "off":
            return

        if self.holdout_logger is not None:
            holdout_student_id = self.student_id
            if holdout_student_id:
                holdout_student_id = f"{holdout_student_id}_holdout"
            self.holdout_logger.set_student(holdout_student_id)

        print("=" * 100)
        print(f"STARTING HOLDOUT EVAL ({len(self.holdout_problem_set)} problems, mode={self.holdout_eval_mode})")

        for idx, prob_args in enumerate(self.holdout_problem_set, start=1):
            self.env.set_problem(**prob_args)
            if self.holdout_logger is not None:
                self.holdout_logger.set_problem(self.env.problem_name)

            print(Back.WHITE + Fore.BLACK + f"HOLDOUT PROBLEM {idx} of {len(self.holdout_problem_set)}: {self.env.problem_name}" + Style.RESET_ALL)

            is_start = True
            while True:
                state = self.env.get_state()
                if state.get_annotation("is_done") is True:
                    break

                rew = self.holdout_eval_state(state, is_start=is_start)
                if rew > 0:
                    is_start = False
                    continue
                if self.holdout_eval_mode == "next_problem":
                    break
                is_start = False

        total = self.holdout_total_correct + self.holdout_total_incorrect
        print("=" * 100)
        print(
            f"HOLDOUT TOTALS (correct:{self.holdout_total_correct}, incorrect:{self.holdout_total_incorrect})"
        )
        if total > 0:
            print(
                f"HOLDOUT PERCENTS(correct:{100*self.holdout_total_correct/total:.2f}%, "
                f"incorrect:{100*self.holdout_total_incorrect/total:.2f}%)"
            )

    def start(self):
        self.logger.set_student(self.student_id)
        p = 1
        p_iter = self.problem_iterator
        for prob_args in p_iter:
            if(prob_args is None):
                prob_args = self.env.set_random_problem()
            else:
                self.env.set_problem(**prob_args)
            self.logger.set_problem(self.env.problem_name)

            print(Back.WHITE + Fore.BLACK + f"STARTING PROBLEM {self.env.problem_name}"  + Style.RESET_ALL)

            is_start = True
            incorr_streak = 0
            while True:#(not self.env.is_done):
                state = self.env.get_state()
                if(state.get_annotation("is_done") == True):
                    break

                force_demo = False
                if(self.num_incorrect_force_demo >= 0 and 
                   incorr_streak >= self.num_incorrect_force_demo):
                    force_demo = True
                
                rew = self.tutor_train_state(state, is_start=is_start, force_demo=force_demo)
                if(rew > 0):
                    incorr_streak = 0
                    is_start = False
                else:
                    incorr_streak += 1

            print("+" * 100)
            print(f"Finished problem {p} of {getattr(p_iter, 'n_problems', '??')}")

            p += 1
        total = (self.total_hints+self.total_incorrect+self.total_correct)
        print(f'TOTALS  (correct:{self.total_correct}, incorrect:{self.total_incorrect}, hint:{self.total_hints}, assistance:{self.total_hints+self.total_incorrect})')
        print(f'PERCENTS(correct:{100*(self.total_correct)/total:.2f}%, incorrect:{100*(self.total_incorrect)/total:.2f}%, hint:{100*(self.total_hints)/total:.2f}%, assistance:{100*(self.total_hints+self.total_incorrect)/total:.2f}%)')
        self.run_holdout()

class AuthorTrainer(Trainer):
    def __init__(self, *args, **kwargs):
        # Author trainer defaults return kind to 'skill_app'
        kwargs['agent_action_repr'] = kwargs.get('agent_action_repr', 'action')
        super(AuthorTrainer, self).__init__(*args, **kwargs)
        self.states_trained = 0
        self.problem_jumps = 0

    def author_train_state(self, state, is_start=None):
        ''' Author-train (i.e. all proposed actions + available demos at once) on 'state'.'''
        actions = self.agent.act_all(**self._state_to_kwargs(state, is_start), #, is_start=is_start,
            return_kind=self.agent_action_repr)
        demos = self.env.get_all_demos(state)

        # print("demos:", len(demos))
        # for demo in demos:
        #     print(demo)

        # print("actions:", len(actions))
        # for action in actions:
        #     print(action)

        # print("state: ")
        # for k,v in state.items():
        #     print("[L]" if v.get('locked',False) else "[ ]", k, v.get('value',""))

        # Annotate each proposed action with reward and add to training set
        train_set = []
        covered_demos = [False] * len(demos)
        for action in actions:
            conv_action = Action(action)
            reward = -1
            for j, demo in enumerate(demos):
                if(demo.is_equal(conv_action,
                    check_annotations=self.env.check_annotations
                    )):

                    reward = 1
                    covered_demos[j] = action
                    break

            train_set.append(self._to_train_kwargs(state, action, reward, is_start=is_start))

            if(reward == 1):
                self.print_outcome(conv_action, "CORRECT")
                self.total_correct += 1
            else:
                self.print_outcome(conv_action, "INCORRECT")
                self.total_incorrect += 1
                
        # Add any next demos not covered by the actions into the training set
        for i, action in enumerate(covered_demos):
            if(not action):
                self.print_outcome(demos[i], "HINT")
                self.total_hints += 1
                train_set.append(
                    self._to_train_kwargs(state, demos[i], 
                        reward=1, is_demo=True, is_start=is_start)
                )

        # print("train_set", train_set)

        # Apply Training Set
        self.agent.train_all(train_set)

        
        # Change the state by applying the first demo 
        #  (or the action that covered it)
        demo = covered_demos[0]
        if(not demo):
            demo = demos[0]
        # self.env.apply(demo)
        print(Back.WHITE + Fore.BLACK + f"APPLY: {demo.selection} -> {demo.input}" + Style.RESET_ALL)
        return demos#[1:]

    def train_prob_start_to_end(self):

        is_start = True
        unapplied = []

        
        while True:#(not self.env.is_done):
            state = self.env.get_state()
            if(state.get_annotation("is_done") == True):
                break
            # print("########")
            # for key, obj in state.items():
            #     print(key, obj)
            # print("########")
            demos = self.author_train_state(state, is_start)
            unapplied.append((state, unused_demos))
            is_start = False
        return unapplied

    # def train_rollout_skipped_states(self):
    #     self.env.reset()
    #     start_state = self.env.get_state()
    #     rollout = self.agent.act_rollout(start_state, json_friendly=True)
    #     print(rollout)
    #     raise ValueError()

    def train_unapplied_demo_states(self, unapplied):
        for state, demos in unapplied:
            orig_state = state
            for demo in demos:
                self.env.set_state(orig_state)
                self.env.apply(demo)
                state = self.env.get_state()
                self.author_train_state(state)


    def start(self):
        p_iter = self.problem_iterator
        p = 1

        problems_so_far = []
        for prob_args in p_iter:
            print("P ITER", prob_args)
            if(prob_args is None):
                prob_args = self.env.set_random_problem()
            else:
                self.env.set_problem(**prob_args)

            problem = getattr(self.env, 'problem_name', self.env.problem_config)
            print(Back.WHITE + Fore.BLACK + f"STARTING PROBLEM {problem}" + Style.RESET_ALL)

            
            # Begin with the start state
            states = [self.env.get_state()]
            cov = set([str(states[0])])
            is_start = True

            while len(states) > 0:
                new_states = []

                # Go through all states
                for state in states:
                    # Train on state
                    self.env.set_state(state)
                    demos = self.author_train_state(state, is_start)

                    callback_context = {
                        "trainer": self, 
                        "problem_num" : p, "problem" : problem
                        # TODO: Some kind of state info
                    }
                    for ev in self.step_end_evaluators:
                        ev.do_eval(callback_context)
                    for callback in self.step_end_callbacks:
                        callback(callback_context);

                    # Follow the states after the next correct actions
                    for demo in demos:
                        self.env.set_state(state)
                        self.env.apply(demo)
                        n_state = self.env.get_state()

                        # Don't bother repeating states
                        s_str = str(n_state)
                        if(s_str in cov or 
                           n_state.get_annotation("is_done") == True):
                            continue
                        else:
                            cov.add(s_str)

                        new_states.append(n_state)
                states = new_states
                is_start = False

            print("L_COV:", len(cov))

                    
                #     for demo in demos:
                #         # Prep State after demo
                #         self.env.set_state(orig_state)
                #         self.env.apply(demo)

                #         # Don't bother repeating states
                #         aft_state = self.env.get_state()
                #         a_str = str(aft_state)
                #         if(a_str in cov):
                #             continue
                #         cov.add(a_str)

                #         # Train from state after demo to end
                #         # NOTE: there will be some redundancy (should fix?)
                #         st_unapp = self.train_prob_start_to_end()
                #         for s,d in st_unapp:
                #             if(str(s) not in cov):
                #                 new_unapp.append((s,d))

                #     cov.add(s_str)
                # unapplied = new_unapp

            print("+" * 100)
            print(f"Finished problem {p} of {getattr(p_iter, 'n_problems', '??')}")
                
            problems_so_far.append(prob_args)

            callback_context = {"trainer": self, "problem_num" : p, "problem" : problem}
            for ev in self.problem_end_evaluators:
                ev.do_eval(callback_context)
            for callback in self.problem_end_callbacks:
                callback(callback_context);

            p += 1
        total = (self.total_hints+self.total_incorrect+self.total_correct)
        print(f'TOTALS  (correct:{self.total_correct}, incorrect:{self.total_incorrect}, hint:{self.total_hints}, assistance:{self.total_hints+self.total_incorrect})')
        print(f'PERCENTS(correct:{100*(self.total_correct)/total:.2f}%, incorrect:{100*(self.total_incorrect)/total:.2f}%, hint:{100*(self.total_hints)/total:.2f}%, assistance:{100*(self.total_hints+self.total_incorrect)/total:.2f}%)')

        callback_context = {"trainer": self}
        for ev in self.train_end_evaluators:
            ev.do_eval(callback_context)
        for callback in self.train_end_callbacks:
            callback(callback_context);
