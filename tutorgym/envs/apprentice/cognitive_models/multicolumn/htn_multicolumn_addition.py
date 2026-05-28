import re
from random import choice

from shop2.common import V
from shop2.domain import Method, Operator, Task
from shop2.fact import Fact


MULTICOLUMN_TRAIN_PROBLEMS = [
    "574+798",
    "248+315",
    "252+533",
    "394+452",
    "872+371",
    "334+943",
    "189+542",
    "222+333",
    "777+777",
    "999+001",
    "999+111",
]

MULTICOLUMN_HOLDOUT_PROBLEMS = [
    "463+258",
    "625+174",
    "386+517",
    "741+159",
    "808+192",
]


def htn_multicolumn_addition_problem_pool(split="train"):
    split = str(split or "train").strip().lower()
    if split == "train":
        return list(MULTICOLUMN_TRAIN_PROBLEMS)
    if split == "holdout":
        return list(MULTICOLUMN_HOLDOUT_PROBLEMS)
    if split == "all":
        return [*MULTICOLUMN_TRAIN_PROBLEMS, *MULTICOLUMN_HOLDOUT_PROBLEMS]
    raise ValueError(f"Unsupported multicolumn addition problem split: {split}")


def htn_multicolumn_addition_problem(split="train"):
    return choice(htn_multicolumn_addition_problem_pool(split=split))


def _parse_problem(init_value, n_digits=3):
    text = str(init_value)
    match = re.search(r"(\d+)\s*\+\s*(\d+)", text)
    if not match:
        raise ValueError(f"Expected multicolumn addition problem like '574+798', got {init_value!r}.")

    upper, lower = match.groups()
    if max(len(upper), len(lower)) > n_digits:
        raise ValueError(
            f"Multicolumn HTN model supports at most {n_digits} digits per addend; got {upper}+{lower}."
        )
    return upper.zfill(n_digits), lower.zfill(n_digits)


def _column_total(init_value, column):
    upper, lower = _parse_problem(init_value)
    carry_in = 0
    for idx in range(1, column):
        carry_in = _column_total(init_value, idx) // 10

    upper_digit = int(upper[-column])
    lower_digit = int(lower[-column])
    return upper_digit + lower_digit + carry_in


def _answer(value):
    text = str(value)
    return tuple([(re.compile(rf"^{re.escape(text)}$"), text)])


def ones_digit(init_value, column):
    return _answer(_column_total(init_value, column) % 10)


def tens_digit(init_value, column):
    return _answer(_column_total(init_value, column) // 10)


def leading_digit(init_value):
    return _answer(_column_total(init_value, 3) // 10)


Domain = {
    "__intermediate_hints__": None,
    "__problem_fact_field__": "problem",

    "done": Operator(
        head=("done", V("kc")),
        precondition=[Fact(start=True)],
        effects=[Fact(field="done", value=((re.compile("x"),),), kc=V("kc"), answer=True)],
    ),

    "out1": Operator(
        head=("out1", V("problem"), V("kc")),
        precondition=Fact(field=V("problem"), value=V("val"), answer=False),
        effects=[
            Fact(
                field="out1",
                value=(ones_digit, V("val"), 1),
                kc=V("kc"),
                answer=True,
                how="OnesDigit(Add(a,b))",
            )
        ],
    ),
    "carry1": Operator(
        head=("carry1", V("problem"), V("kc")),
        precondition=Fact(field=V("problem"), value=V("val"), answer=False),
        effects=[
            Fact(
                field="carry1",
                value=(tens_digit, V("val"), 1),
                kc=V("kc"),
                answer=True,
                how="TensDigit(Add(a,b))",
            )
        ],
    ),
    "out2": Operator(
        head=("out2", V("problem"), V("kc")),
        precondition=Fact(field=V("problem"), value=V("val"), answer=False),
        effects=[
            Fact(
                field="out2",
                value=(ones_digit, V("val"), 2),
                kc=V("kc"),
                answer=True,
                how="OnesDigit(Add(a,b,c))",
            )
        ],
    ),
    "carry2": Operator(
        head=("carry2", V("problem"), V("kc")),
        precondition=Fact(field=V("problem"), value=V("val"), answer=False),
        effects=[
            Fact(
                field="carry2",
                value=(tens_digit, V("val"), 2),
                kc=V("kc"),
                answer=True,
                how="TensDigit(Add(a,b,c))",
            )
        ],
    ),
    "out3": Operator(
        head=("out3", V("problem"), V("kc")),
        precondition=Fact(field=V("problem"), value=V("val"), answer=False),
        effects=[
            Fact(
                field="out3",
                value=(ones_digit, V("val"), 3),
                kc=V("kc"),
                answer=True,
                how="OnesDigit(Add(a,b,c))",
            )
        ],
    ),
    "carry3": Operator(
        head=("carry3", V("problem"), V("kc")),
        precondition=Fact(field=V("problem"), value=V("val"), answer=False),
        effects=[
            Fact(
                field="carry3",
                value=(tens_digit, V("val"), 3),
                kc=V("kc"),
                answer=True,
                how="TensDigit(Add(a,b,c))",
            )
        ],
    ),
    "out4": Operator(
        head=("out4", V("problem"), V("kc")),
        precondition=Fact(field=V("problem"), value=V("val"), answer=False),
        effects=[
            Fact(
                field="out4",
                value=(leading_digit, V("val")),
                kc=V("kc"),
                answer=True,
                how="Copy(a)",
            )
        ],
    ),

    "solve": Method(
        head=("solve", V("problem")),
        preconditions=[
            Fact(scaffold="level_0"),
        ],
        subtasks=[
            [
                Task(head=("out1", V("problem"), ("out1",)), primitive=True),
                Task(head=("carry1", V("problem"), ("carry1",)), primitive=True),
                Task(head=("out2", V("problem"), ("out2",)), primitive=True),
                Task(head=("carry2", V("problem"), ("carry2",)), primitive=True),
                Task(head=("out3", V("problem"), ("out3",)), primitive=True),
                Task(head=("carry3", V("problem"), ("carry3",)), primitive=True),
                Task(head=("out4", V("problem"), ("out4",)), primitive=True),
                Task(head=("done", ("done",)), primitive=True),
            ],
        ],
    ),
}


def htn_multicolumn_addition_kc_mapping():
    return {
        "out1": "Write ones-column digit",
        "carry1": "Carry from ones column",
        "out2": "Write tens-column digit",
        "carry2": "Carry from tens column",
        "out3": "Write hundreds-column digit",
        "carry3": "Carry from hundreds column",
        "out4": "Write leading carry digit",
        "done": "Complete multicolumn addition",
    }


def htn_multicolumn_addition_intermediate_hints(): ## ambiguous because it doesnt mention which carry is considered. - 
    return {
        "out1": ["Add the ones digits and write the ones digit of that sum."],
        "carry1": ["Carry the tens digit from the ones-column sum. Enter 0 if there is no carry."],
        "out2": ["Add the tens digits plus the carry from the ones column, then write the ones digit."],
        "carry2": ["Carry the tens digit from the tens-column sum. Enter 0 if there is no carry."],
        "out3": ["Add the hundreds digits plus the carry from the tens column, then write the ones digit."],
        "carry3": ["Carry the tens digit from the hundreds-column sum. Enter 0 if there is no carry."],
        "out4": ["Copy the final carry into the leading answer place. Enter 0 if there is no final carry."],
        "done": ["Click done when the addition is complete."],
    }


Domain["__intermediate_hints__"] = htn_multicolumn_addition_intermediate_hints()
