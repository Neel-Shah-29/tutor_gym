from pathlib import Path
from bs4 import BeautifulSoup
from tutorgym.shared import ProblemState, Action
from shop2.fact import Fact # type: ignore
from .planner import planner
import sympy as sp
from sympy.parsing.latex._parse_latex_antlr import parse_latex
from tutorgym.env_classes.env_base import TutorEnvBase
import re
import os
import inspect

# from tutorgym.shared import ProblemState
# from tutorgym.env_classes.apprentice_tutor import ApprenticeTutor, HTNCognitiveModel
from shop2.domain import Task
from copy import deepcopy
from shop2.conditions import AND, OR
from random import choice



# TODO

def make_next_state(state, action, reward=1):
    next_state = state.copy()
    selection, action_type, inp = action.as_tuple()
    if(action_type == "UpdateTextField" or action_type == "input change"):
        next_state[selection] = next_state.objs.get(selection, {})
        next_state[selection]['value'] = "" if inp is None else str(inp)
        if(reward == 1):
            next_state[selection]['locked'] = True
        else:
            next_state[selection]['locked'] = False
    return next_state


def check_effect_match(effect, answer, verbosity=1):
    value = answer['value']

    if(effect['field'] != answer['field']):
        if(verbosity >= 1):
            print("NOMATCH(FIELD) :",  answer['field'], "->", f"{value}", f"{answer['field']}!={effect['field']}")
        return False

    val_match = False

    # EDGE CASE: Pressing done, it doesn't matter what the input value is, just field.
    if(effect['field'] == "done"):
        return True

    for evalue in effect['value']:
        val_match = False
        # Check if the hint demo (which is usually a fixed latex string) equals the answer value
        if(len(evalue) >= 2):
            val_match = evalue[1] == value

        # Otherwise convert from latex to a standard sympy string and see if either 
        # matcher string (which is usually a regex over sympy strings) or the regex matches         
        if(not val_match):
            sympy_value = re.sub(r'sqrt(\d+)', r'sqrt{\1}', value)
            sympy_value = sp.sstr(parse_latex(sympy_value), order='grlex')
            sympy_value = sympy_value.replace('-1*s', '-s').replace('-1*l', '-l').replace('-1*e', '-e')

            val_match = (evalue[0] == sympy_value or 
                         evalue[0].match(sympy_value) is not None)

        if(val_match):
            return True
        else:
            #print("EVALUE[0]", evalue[0], evalue[0].match(value) is not None)
            #print("EVALUE[1]", effect['field'], "->", evalue[1], evalue[1] == value)
            if(verbosity >= 1):
                print("NOMATCH(VALUE):",  answer['field'], "->", f"{sympy_value}", evalue[0])
    return val_match


def effect_to_action(effect):
    if effect['field'] == 'done':
        action = Action(
                ('done', 'PressButton', -1), 
                how_help="-1")
            
    else:
        #value = str(parse_latex(effect['value'][0][1]))
        value = str(effect['value'][0][1])

        action = Action(
            (f'{effect["field"]}', 'input change', value), 
            arg_foci=[effect['arg_foci']] if 'arg_foci' in effect else [''],
            how_help=effect['how'] if 'how' in effect else '',
        )

    return action

def action_to_answer(action):
    selection, action_type, inp = action.as_tuple()

    if selection == 'done':
        answer = {
            "field" : "done",
            "action" : "button click",
            "value" : "x"
        }
    else:
        #value = str(parse_latex(effect['value'][0][1]))
        answer = {
            "field" : selection,
            "action" : action_type,
            "value" : inp
        }
    return answer
            



class HTNCognitiveModel:
    def __init__(self, start_state, task, domain, scaffold="all", problem_fact_field='equation'):
        self.start_state = ProblemState(start_state)
        self.task = task
        self.domain = domain
        self.scaffold = scaffold
        self.problem_fact_field = problem_fact_field

    def get_expected_effects(self, state):
        def task_order_for_state():
            """Return an ordered list of task names that matches the current branch."""
            root_val = str(state.objs.get(self.problem_fact_field, {}).get('value', '')).lower()
            marker = {
                'right': 'apply_pythagorean',
                'sines': 'resolve_ssa_ambiguity',
                'cosines': 'compute_unknown_by_cosine',
                'similarity': 'map_correspondence',
                'area': 'select_area_formula',
            }.get(root_val)

            subtasks = getattr(self.domain.get('solve'), 'subtasks', []) or []
            for branch in subtasks:
                names = [task.name for task in branch if task.name != 'done']
                if marker and marker in names:
                    return names
            if subtasks:
                return [task.name for task in subtasks[0] if task.name != 'done']
            return []

        order = {name: i for i, name in enumerate(task_order_for_state())}
        # NOTE: Momin's version sorted by y value, (which Danny got rid so that bounds could,
        #   be omitted in the state). Shouldn't cause bug sice dicts are ordered. 
        state_list = sorted(list(state.objs.values()), key=lambda obj: order.get(obj['id'], len(order)))
        # state_list: list[dict] = sorted(list(state.objs.values()), key=lambda x: x['y'])
        fact_state: Fact = Fact(start=True)  

        # print(">>>", self.domain['solve'])

        if(self.scaffold == "all"):
            # print("SCAFFOLD", self.scaffold)
            fact_state = (fact_state 
             & Fact(scaffold='level_0') & Fact(scaffold='level_1')
             & Fact(scaffold='level_2') & Fact(scaffold='level_3') 
             & Fact(scaffold='level_4') & Fact(scaffold='level_5') 
             & Fact(scaffold='level_6')
            )
        elif self.scaffold is not None:
            fact_state = fact_state & Fact(scaffold=self.scaffold)
        

        answers: list[Fact] = []
        for value in state_list:
            if value['id'] == 'done' or 'label' in value['id']:
                continue
            
            if value['id'] != self.problem_fact_field and value['locked']:
                answers.append(Fact(field=value['id'], value=value['value'], answer=value['locked']))
            else:
                fact_state = fact_state & Fact(field=value['id'], value=value['value'], answer=False)
        
        # print("FS", fact_state)

        plan = planner(fact_state, self.task, self.domain)        
        effect, fact_state = plan.send(None)
        # fail = False
        
        # Get the planner caught up with the previous answers
        for answer in answers:            
            i = 0
            while True:                
                if effect and check_effect_match(effect, answer):
                    effect['value'] = answer['value']
                    effect, fact_state = plan.send((fact_state, True, effect))
                    break

                # NOTE: Danny's kludgey fail-safe, not clear why planner
                #  gets stuck in infinite loop here
                i += 1
                effect_order = order.get(effect.get('field')) if effect else None
                answer_order = order.get(answer.get('field'))
                # If planner is proposing an earlier step than the answered field, don't loop forever.
                if i >= 3 or (effect_order is not None and answer_order is not None and effect_order < answer_order):
                    break
                    #raise RuntimeError()

                # print("EEE", effect)
                # print(fact_state)
                next_effect, fact_state = plan.send((fact_state, False, effect))
                if next_effect == effect:
                    break
                # if(next_effect and effect and next_effect == effect):
                #     break
                effect = next_effect
        
        expected: set[Fact] = set()
        seen_effects: set[Fact] = set()
        max_expected_iters = 50

        # while not fail:            
        iter_count = 0
        while True:
            iter_count += 1
            if iter_count > max_expected_iters:
                print(f"[ApprenticeTutor] Breaking expected-effect loop after {max_expected_iters} iterations.")
                break
            effect, fact_state = plan.send((fact_state, False, expected))
            # print("EFFECT", effect)
            if not effect:
                break
            if effect in seen_effects:
                # Avoid infinite loops if planner keeps proposing the same effect.
                break
            expected.add(effect)
            seen_effects.add(effect)

        return list(expected)

    

    

    def get_next_actions(self, state):
        expected = self.get_expected_effects(state)
        
        next_actions = []
        for effect in expected:
            action = effect_to_action(effect)
            hint_txt = None
            try:
                field = effect.get('field')
                if field in getattr(self, "intermediate_hints", {}):
                    hints = self.intermediate_hints[field]
                    if isinstance(hints, (list, tuple)) and hints:
                        hint_txt = hints[0]
                    elif isinstance(hints, str):
                        hint_txt = hints
            except Exception:
                pass
            if hint_txt:
                action = Action(action.as_tuple(), hint=hint_txt)
            next_actions.append(action)

        return next_actions


class ApprenticeTutor(TutorEnvBase):
    def __init__(self, domain=None, initial_problem=None, scaffold="first",
                      include_obj_bounds=False,
                     **kwargs):
        super().__init__(**kwargs)        

        self.problem_fact_field = 'equation'
        self.default_domain = domain
        self.default_scaffold = scaffold
        self.include_obj_bounds = include_obj_bounds
        # if(isinstance())
        # self.problem_types = problem_types
        if(initial_problem is None):
            self.set_random_problem()
        else:
            self.set_problem(domain, initial_problem, scaffold)
        
    def _resolve_scaffold_options(self):
        self.scaffold_options = []
        for precond in self.domain_model['solve'].preconditions:
            if(not isinstance(precond, AND)):
                precond = AND(precond)
        
            scaffold = None
            for cond in precond:
                scaffold = cond.get('scaffold', None)
                if(scaffold is not None):
                    break
            self.scaffold_options.append(scaffold)
        #print("scaffold_options", self.scaffold_options)
        return self.scaffold_options

    @staticmethod
    def _ensure_str(value, fallback=""):
        if value is None:
            return fallback
        if isinstance(value, str):
            return str(value)
        return str(value)

    def _extract_fact_field(self, condition):
        if isinstance(condition, Fact):
            field_name = condition.get('field')
            if isinstance(field_name, str):
                return field_name
        elif isinstance(condition, (AND, OR)):
            for sub_condition in condition:
                field_name = self._extract_fact_field(sub_condition)
                if field_name:
                    return field_name
        return None

    def _determine_problem_fact_field(self):
        meta_key = '__problem_fact_field__'
        field_name = None

        if isinstance(self.domain_model.get(meta_key), str):
            field_name = self.domain_model.pop(meta_key)

        if field_name is None:
            solve_method = self.domain_model.get('solve')
            if solve_method is not None:
                for precond in solve_method.preconditions:
                    field_name = self._extract_fact_field(precond)
                    if field_name:
                        break

        if not field_name:
            field_name = getattr(self, 'problem_fact_field', 'equation')

        print(f"[ApprenticeTutor] Using problem fact field '{field_name}'")
        return field_name

    def _collect_state_overrides(self, initial_problem):
        overrides = {}
        if isinstance(initial_problem, dict):
            for key in ('state_overrides', 'state', 'state_values'):
                values = initial_problem.get(key)
                if isinstance(values, dict):
                    overrides.update(values)
            explicit = initial_problem.get(self.problem_fact_field)
            if explicit is not None:
                overrides.setdefault(self.problem_fact_field, explicit)
        return overrides

    def _infer_problem_fact_value_from_text(self, initial_problem):
        if isinstance(initial_problem, dict):
            problem_text = (initial_problem.get('prompt')
                            or initial_problem.get('problem')
                            or initial_problem.get('text')
                            or initial_problem.get('description')
                            or initial_problem.get('problem_name'))
        else:
            problem_text = initial_problem

        if not isinstance(problem_text, str):
            return self._ensure_str(problem_text)

        normalized = problem_text.strip().lower()
        if self.problem_fact_field == 'triangle_type':
            if normalized.startswith('right'):
                return 'Right'
            if normalized.startswith(('asa', 'aas')) or 'ssa' in normalized:
                return 'Sines'
            if normalized.startswith(('sas', 'sss')):
                return 'Cosines'
            if normalized.startswith('sim'):
                return 'Similarity'
            if normalized.startswith('area'):
                return 'Area'
            print(f"[ApprenticeTutor] Unable to infer triangle_type from '{problem_text}'")
            return ''

        return self._ensure_str(problem_text)

    def _apply_state_overrides(self, state, overrides):
        for field, override in overrides.items():
            if field not in state:
                print(f"[ApprenticeTutor] Skipping override for missing field '{field}'")
                continue

            if isinstance(override, dict):
                if 'value' in override:
                    state[field]['value'] = self._ensure_str(override['value'])
                if 'locked' in override:
                    state[field]['locked'] = override['locked']
                for attr in ('x', 'y', 'width', 'height', 'id', 'type'):
                    if attr in override:
                        if attr in ('id', 'type'):
                            state[field][attr] = self._ensure_str(override[attr])
                        else:
                            state[field][attr] = override[attr]
            else:
                state[field]['value'] = self._ensure_str(override)

    def _initialize_problem_state_field(self, state, initial_problem):
        overrides = self._collect_state_overrides(initial_problem)
        root_value = overrides.pop(self.problem_fact_field, None)
        if root_value is None:
            root_value = self._infer_problem_fact_value_from_text(initial_problem)

        if root_value is None:
            root_value = ""

        if self.problem_fact_field not in state:
            state[self.problem_fact_field] = {'type': 'TextField', 'value': "", 'locked': True}

        state[self.problem_fact_field]['value'] = self._ensure_str(root_value)
        state[self.problem_fact_field]['locked'] = True

        self._apply_state_overrides(state, overrides)
        print(f"[ApprenticeTutor] Initialized '{self.problem_fact_field}' with '{root_value}'")

    def _resolve_problem_label(self, initial_problem):
        if isinstance(initial_problem, dict):
            for key in ('problem_name', 'name', 'prompt', 'problem', 'text', 'description'):
                if key in initial_problem and initial_problem[key]:
                    return self._ensure_str(initial_problem[key])
        return self._ensure_str(initial_problem)

    def _blank_state(self):
        current_dir = Path(__file__).parent.parent

        html_path = os.path.join(
            current_dir, 
            f"../envs/apprentice/static_html/{self.domain}.html"
        )
        with open(html_path, 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')
            
        field_params = {'type': 'TextField', 'value' : "", 'width' : 100, 'height' : 50,  }
        label_params = {'type': 'Label', 'width' : 100, 'height' : 50, 'locked': True, }
        button_params = {'x': 0, 'type': 'Button', 'width' : 100, 'height' : 50, }

        solve_method = self.domain_model['solve']
        field_names = []
        seen_fields = set()

        def append_unique(tasks):
            for task in tasks:
                name = task.name
                if name == 'done' or name in seen_fields:
                    continue
                seen_fields.add(name)
                field_names.append(name)

        # Keep the ordering of the first branch, then append new fields from others.
        if solve_method.subtasks:
            append_unique(solve_method.subtasks[0])
            for subtasks in solve_method.subtasks[1:]:
                append_unique(subtasks)

        # Always place the done button last if the domain defines it.
        has_done = any(task.name == 'done' for sub in solve_method.subtasks for task in sub)
        if has_done:
            field_names.append('done')

        # assert field_names.index('done') == len(field_names)-1

        state: dict = {self.problem_fact_field: {'y': 10, 'locked': True,  **field_params}}
        row_count: dict[str, int] = {'factor_1_b': 1, 'factor_2_b': 1, 'sum_factor': 1, 'sum_c': 1}
        for idx, field in enumerate(field_names):            
            if field == 'done':
                state[field] = {'y': 10 + (idx + 1) * 100, **button_params}
            else:
                # Check if field matches special patterns that need row count
                if (field.startswith(('factor_1_b', 'factor_2_b', 'sum_factor', 'sum_c'))):
                    field_id = f'{field}_{row_count[field]}'
                    label_elem = soup.find(id=field_id).find_previous_sibling('label')
                    if not label_elem:
                        label_elem = soup.find(id=field_id).find_previous_sibling('p')
                    row_count[field] += 1
                else:
                    field_id = field
                    label_elem = soup.find(id=field).find_previous_sibling('label')
                    if not label_elem:
                        label_elem = soup.find(id=field).find_previous_sibling('p')
                
                label_text = label_elem.text if label_elem else field
                label_text = self._ensure_str(label_text)
                state[f'label_of_{field}'] = {'x': 0, 'y': 10 + (idx + 1) * 100, 'value': label_text, **label_params}
                state[field] = {'x': 200, 'y': 10 + (idx + 1) * 100, 'locked': False,  **field_params}
        for key, value in state.items():
            state[key]['id'] = self._ensure_str(key)        

        self.possible_selections = field_names
        eligible_args = [name for name in self.possible_selections if name not in ('report_solution', 'done')]
        self.possible_args = [self.problem_fact_field, *eligible_args]

        # Check that we haven't changed the field
        # state_ord_fieldnames = [x for x in state.keys() if x != self.problem_fact_field and 'label' not in x]
        # assert state_ord_fieldnames == field_names

        return ProblemState(state)

    def _filter_state(self, state):
        f_state = {}
        for k,obj in state.items():
            if(not self.include_obj_bounds):
                if("x" in obj): del obj["x"]
                if("y" in obj): del obj["y"]
                if("width" in obj): del obj["width"]
                if("height" in obj): del obj["height"]
            f_state[k] = obj

        return f_state

    def set_start_state(self, domain, initial_problem, scaffold="undef", **kwargs):
        from tutorgym.envs.apprentice.env_registry import ENVIRONMENTS

        env_entry = ENVIRONMENTS[domain]
        if len(env_entry) >= 3:
            domain_model, problem_generator, problem_fact_field = env_entry[:3]
        else:
            domain_model, problem_generator = env_entry
            problem_fact_field = None

        if(scaffold == "undef"):
            scaffold = self.default_scaffold

        self.domain = domain
        self.domain_model = deepcopy(domain_model)
        self.intermediate_hints = self.domain_model.pop("__intermediate_hints__", {}) or {}
        provided_field = self._ensure_str(problem_fact_field) if problem_fact_field else None
        self.problem_fact_field = provided_field or self._determine_problem_fact_field()
        self._resolve_scaffold_options()
        if(scaffold == "first"):
            scaffold = list(self.scaffold_options)[0]

        self.problem_generator = problem_generator
        self.scaffold = scaffold

        #print(args, kwargs)
        state = self._blank_state()
        state = self._filter_state(state)

        problem_label = self._resolve_problem_label(initial_problem)
        if not isinstance(problem_label, str):
            problem_label = str(problem_label)

        self.problem_name = f"{domain}/{problem_label}"
        self.problem = initial_problem
        self._initialize_problem_state_field(state, initial_problem)
        print("INITIAL PROBLEM:", state)
        self.start_state = ProblemState(state)
    
    def set_random_problem(self, domain=None, scaffold="undef"):
        from tutorgym.envs.apprentice.env_registry import ENVIRONMENTS

        if(domain is None and self.default_domain is not None):
            # If default set use that
            domain = self.default_domain
        else:
            # Otherwise randomly select one
            domains = list(ENVIRONMENTS.keys())
            domain = choice(domains)

        #print("domain", domain)
        env_entry = ENVIRONMENTS[domain]
        problem_generator = env_entry[1]        

        initial_problem = problem_generator()
        self.set_problem(domain, initial_problem, scaffold)

    def create_htn_model(self, state):
        curr_state = state.copy()
        task = [Task(head=('solve', self.problem_fact_field), primitive=False)]
        return HTNCognitiveModel(curr_state, task, self.domain_model, scaffold=self.scaffold, problem_fact_field=self.problem_fact_field)
    
    def get_possible_selections(self):
        return self.possible_selections

    def get_possible_args(self):
        return self.possible_args
    
    def _standardize_config(self, *args, **kwargs):
        sig = inspect.signature(self.set_start_state)
        
        problem_config = {}
        for (arg_name, arg) in zip(sig.parameters, args):
            problem_config[arg_name] = arg

        return {**problem_config, **kwargs}

    def set_problem(self, *args, **kwargs):
        self.set_start_state(*args, **kwargs)
        self.htn_model = self.create_htn_model(self.start_state)
        self.htn_model.scaffold = self.scaffold
        self.state = self.start_state

        self.problem_config = self._standardize_config(*args, **kwargs)
        # print("problem_config", self.problem_config)
    
    def get_problem(self):
        return getattr(self, 'problem_name', self.problem_config)

    def get_problem_config(self):
        return self.problem_config
    
    def reset(self):
        self.state = self.start_state.copy()

    def get_state(self):
        return self.state
    
    def set_state(self, objs):
        self.state = ProblemState(objs)

    def check(self, action, **kwargs):
        """ Returns 1 for correct next-step Actions, -1 for incorrect ones."""
        action = Action(action)
        correct_actions = self.htn_model.get_next_actions(self.state)
        # check_args = kwargs.get('check_args', self.check_args)
        # check_how = kwargs.get('check_how', self.check_how)
        for ca in correct_actions:


            if ca.is_equal(action, self.check_annotations):
                return 1
        return -1
    
    def action_makes_done(self, action):
        return action.selection == 'done'
    
    def apply(self, action, reward=1):
        """ Applies an Action. Modifying self.state. """
        if (self.action_makes_done(action)):
            self.state = ProblemState({}, is_done=True)
        else:
            self.state = make_next_state(self.state, action, reward)
        return self.state
    
    def _process_demo(self, action, **kwargs):
        action = Action(action.as_tuple(), 
                **{k:v for k,v in action.annotations.items() if k in self.demo_annotations
                })
        return action
    
    def get_demo(self, state=None, **kwargs):
        """ Returns a correct next-step Action """
        state = self.state if state is None else state
        correct_actions = self.htn_model.get_next_actions(self.state)
        return self._process_demo(correct_actions[0],**kwargs)
    
    def get_all_demos(self, state=None, **kwargs):
        """ Returns all correct next-step Actions """
        state = self.state if state is None else state 
        correct_actions = self.htn_model.get_next_actions(self.state)
        return [self._process_demo(a, **kwargs) for a in correct_actions]


    
