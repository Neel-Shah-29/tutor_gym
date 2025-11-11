import re
from random import choice

import sympy as sp
from sympy import latex, sstr

from shop2.domain import Task, Operator, Method
from shop2.fact import Fact
from shop2.conditions import Filter
from shop2.common import V

# from studymaterial import studymaterial


# ----------------------
# Problem generator
# ----------------------
def htn_geometry_solve_triangle_problem():
    """
    Return a single-string prompt describing a triangle scenario.
    We keep numbers friendly so we can validate cleanly.
    Patterns covered: RIGHT, ASA (Sines), SAS (Cosines), SIM (Similarity), AREA.
    """
    scenarios = [
        # Right triangle trig (SOH/CAH/TOA + Pythagorean)
        "Right triangle: a=3, b=4",
        # Law of Sines (ASA)
        "ASA: A=30, C=60, a=10",
        # Law of Cosines (SAS)
        "SAS: a=7, b=8, C=60.",
        # Similarity scaling
        # "SIM: scale=2, AB=5.",
        # Area relation 1/2 ab sin C
        # "AREA: a=8, b=10, C=30",
    ]
    return choice(scenarios)


# ----------------------
# Helpers
# ----------------------
deg = sp.pi/180


def _parse_vals(text):
    """Extract common symbols from the problem text into a dict of ints where present."""
    vals = {}
    for sym in ['a', 'b', 'c', 'A', 'B', 'C', 'scale', 'AB']:
        m = re.search(rf"\b{sym}\s*=\s*([0-9]+)", text)
        if m:
            vals[sym] = int(m.group(1))
    return vals


def _any_match(pattern, text):
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def _ok_any():
    # Accept anything non-empty; hint nudges what to put.
    return tuple([(re.compile(r".+"), "OK")])


# ----------------------
# Operator functions (return tuple of (regex, hint))
# ----------------------
def normalize_inputs(init_value):
    # Accept any acknowledgement; this is a staging step.
    return _ok_any()


def classify_triangle(init_value):
    # Accept user-friendly labels while constraining to the scenario in the prompt.
    # We return multiple acceptable patterns but one concise hint string.
    def pack(patterns, hint):
        return tuple([(re.compile(pat, re.I), hint) for pat in patterns])

    if _any_match(r"^\s*Right\s*triangle", init_value):
        return pack([
            r"right",
            r"right\s*triangle",
            r"righttriangletrig",
            r"right-?angled",
            r"rt|rtt",
            r"R*(i*(g*(h*t)))"
        ], "Right")
    if (_any_match(r"^\s*ASA\s*:\s*", init_value)
        or _any_match(r"^\s*AAS\s*:\s*", init_value)
        or _any_match(r"\bSSA\b", init_value)):
        return pack([
            r"sines",
            r"law\s*of\s*sines",
            r"los|sin",
            r"S*(i*(n*(e*s)))"
        ], "Sines")
    if _any_match(r"^\s*SAS\s*:\s*", init_value) or _any_match(r"^\s*SSS\s*:\s*", init_value):
        return pack([
            r"cosines",
            r"law\s*of\s*cosines",
            r"loc|cos",
            r"C*(o*(s*(i*(n*(e*s)))))"
        ], "Cosines")
    if _any_match(r"^\s*SIM\s*:\s*", init_value):
        return pack([
            r"similarity",
            r"similarity\s*scaling",
            r"sim"
        ], "Similarity")
    if _any_match(r"^\s*AREA\s*:\s*", init_value):
        return pack([
            r"area",
            r"area\s*relations",
            r"heron|\b1/2\s*ab\s*sin\s*c\b"
        ], "Area")
    # Fallback: default to Sines family but accept broad labels
    return pack([
        r"sines",
        r"law\s*of\s*sines",
        r"los|sin"
    ], "Sines")


def apply_pythagorean(init_value):
    vals = _parse_vals(init_value)
    a = vals.get('a')
    b = vals.get('b')
    if a is None or b is None:
        return _ok_any()
    c = sp.sqrt(a*a + b*b)
    # Prefer simplified int if perfect square
    hint = latex(c)
    ans = sstr(c, order="grlex")
    return tuple([(re.compile(re.escape(ans)), hint)])


def use_trig_ratios(init_value):
    # Prompt: Enter sin A for the right-triangle case
    vals = _parse_vals(init_value)
    a = vals.get('a')
    b = vals.get('b')
    if a is None or b is None:
        return _ok_any()
    c = sp.Integer(a*a + b*b) ** sp.Rational(1, 2)
    sinA = sp.Rational(a, c)
    hint = latex(sp.simplify(sinA))
    ans = sstr(sp.simplify(sinA), order="grlex")
    return tuple([(re.compile(re.escape(ans)), hint)])


def resolve_ssa_ambiguity(init_value):
    # If SSA present -> ambiguous; else unique
    ambiguous = _any_match(r"\bSSA\b", init_value)
    expected = "ambiguous" if ambiguous else "unique"

    # Always accept the plain word first.
    patterns = [(re.compile(expected, re.I), expected)]

    # Also accept MathLive-style character-multiplication strings like
    # u*(n*(i*(q*(e*u)))) for "unique", and analogous for "ambiguous".
    if expected == "unique":
        # Allow both ...u.*e... and ...e.*u... at the end, since we observed both.
        patterns.append((re.compile(r"u.*n.*i.*q.*u.*e", re.I), expected))
        patterns.append((re.compile(r"u.*n.*i.*q.*e.*u", re.I), expected))
    else:  # expected == "ambiguous"
        patterns.append((re.compile(r"a.*m.*b.*i.*g.*u.*o.*u.*s", re.I), expected))

    return tuple(patterns)


def compute_missing_angles(init_value):
    # For ASA/AAS: compute B = 180 - (A + C)
    vals = _parse_vals(init_value)
    A = vals.get('A')
    C = vals.get('C')
    if A is None or C is None:
        return _ok_any()
    B = 180 - (A + C)
    return tuple([(re.compile(str(B)), str(B))])


def compute_missing_sides(init_value):
    # For ASA example in generator: a known, find b via Law of Sines
    vals = _parse_vals(init_value)
    A = vals.get('A')
    C = vals.get('C')
    a = vals.get('a')
    if A is None or C is None or a is None:
        return _ok_any()
    B = 180 - (A + C)
    b = sp.nsimplify(a * sp.sin(B*deg) / sp.sin(A*deg))
    hint = latex(b)
    ans = sstr(b, order="grlex")
    return tuple([(re.compile(re.escape(ans)), hint)])


def compute_unknown_by_cosine(init_value):
    # For SAS example in generator: compute c from a, b, C
    vals = _parse_vals(init_value)
    a = vals.get('a')
    b = vals.get('b')
    C = vals.get('C')
    if a is None or b is None or C is None:
        return _ok_any()
    c2 = a*a + b*b - 2*a*b*sp.cos(C*deg)
    c = sp.sqrt(sp.simplify(c2))
    hint = latex(c)
    # ans = sstr(c, order="grlex")
    ans = re.compile(re.sub(r'([-+^()*])', r'\\\1', sstr(c, order="grlex")))
    return tuple([(ans, hint)])


def backfill_with_sines_if_needed(init_value):
    # Light-weight step: accept any non-empty.
    return _ok_any()


def map_correspondence(init_value):
    # Accept any short token like A->A' or AB->A'B'
    return tuple([(re.compile(r".+"), "Map corresponding vertices (e.g., A→A')")])


def scale_sides_angles(init_value):
    # For SIM example: scale=2, AB=5 -> A'B' = 10
    vals = _parse_vals(init_value)
    k = vals.get('scale')
    AB = vals.get('AB')
    if k is None or AB is None:
        return _ok_any()
    scaled = sp.Integer(k*AB)
    hint = latex(scaled)
    ans = sstr(scaled, order="grlex")
    return tuple([(re.compile(re.escape(ans)), hint)])


def select_area_formula(init_value):
    # Accept specific dropdown-friendly labels
    return tuple([
        (re.compile(r"1/2·a·b·sin\(C\)", re.I), "1/2·a·b·sin(C)"),
        (re.compile(r"Heron", re.I), "Heron")
    ])


def compute_area(init_value):
    # Support 1/2·a·b·sin(C) or Heron's formula if all sides known
    vals = _parse_vals(init_value)
    a = vals.get('a')
    b = vals.get('b')
    C = vals.get('C')
    c = vals.get('c')

    area = None
    if a is not None and b is not None and C is not None:
        area = sp.nsimplify(sp.Rational(1, 2) * a * b * sp.sin(C*deg))
    elif a is not None and b is not None and c is not None:
        s = sp.Rational(a + b + c, 2)
        area = sp.nsimplify(sp.sqrt(s * (s - a) * (s - b) * (s - c)))
    if area is None:
        return _ok_any()

    hint = latex(area)
    ans = sstr(area, order="grlex")
    return tuple([(re.compile(re.escape(ans)), hint)])


def consistency_checks(init_value):
    # Check common triangle consistency rules:
    # - Angle sum property
    # - Side length positivity
    # - Appropriate side/angle relationships
    vals = _parse_vals(init_value)
    A = vals.get('A')
    B = vals.get('B')
    C = vals.get('C')
    a = vals.get('a')
    b = vals.get('b')
    c = vals.get('c')

    hints = []
    if A is not None and B is not None and C is not None:
        # Angle sum property
        if A + B + C != 180:
            return _ok_any()  # Fail consistency
        hints.append("Angle sum property OK.")
    if a is not None and b is not None and c is not None:
        # Side length positivity
        if a <= 0 or b <= 0 or c <= 0:
            return _ok_any()  # Fail consistency
        hints.append("Side lengths positive.")
    if A is not None and a is not None and B is not None and b is not None:
        # Check relationships for given A, a, B, b
        if A > 90 and a <= b:
            return _ok_any()  # Fail consistency
        if B > 90 and b <= a:
            return _ok_any()  # Fail consistency
        hints.append("Angle-side relationships OK.")

    # If we have hints, return success with hints
    if hints:
        return tuple([(re.compile("consistent"), "Consistent: " + ", ".join(hints))])

    # Default to OK
    return _ok_any()


def report_solution(init_value):
    # Report the solution: list all sides, angles, and area if computable.
    vals = _parse_vals(init_value)
    A = vals.get('A')
    B = vals.get('B')
    C = vals.get('C')
    a = vals.get('a')
    b = vals.get('b')
    c = vals.get('c')

    # fill in missing angles
    if a is not None and b is not None and c is not None:
        if A is None:
            A = sp.N(sp.acos((b**2 + c**2 - a**2) / (2*b*c)) / deg)
        if B is None:
            B = sp.N(sp.acos((a**2 + c**2 - b**2) / (2*a*c)) / deg)
        if C is None:
            C = sp.N(sp.acos((a**2 + b**2 - c**2) / (2*a*b)) / deg)
    else:
        if A is not None and B is not None and C is None:
            C = 180 - (A + B)
        elif A is not None and C is not None and B is None:
            B = 180 - (A + C)
        elif B is not None and C is not None and A is None:
            A = 180 - (B + C)

    area = None
    if a is not None and b is not None and C is not None:
        area = sp.nsimplify(sp.Rational(1, 2) * a * b * sp.sin(C*deg))
    elif a is not None and b is not None and c is not None:
        s = sp.Rational(a + b + c, 2)
        area = sp.nsimplify(sp.sqrt(s * (s - a) * (s - b) * (s - c)))

    # Canonical plain-text summary (used also for the hint)
    solution = []
    if A is not None:
        solution.append(f"A = {sstr(sp.nsimplify(A))}")
    if B is not None:
        solution.append(f"B = {sstr(sp.nsimplify(B))}")
    if C is not None:
        solution.append(f"C = {sstr(sp.nsimplify(C))}")
    if a is not None:
        solution.append(f"a = {a}")
    if b is not None:
        solution.append(f"b = {b}")
    if c is not None:
        solution.append(f"c = {c}")
    if area is not None:
        solution.append(f"area = {sstr(area)}")

    final_str = "Solution: " + ", ".join(solution)
    patterns = [(re.compile(re.escape(final_str), re.I), final_str)]

    # Lenient matcher that allows extra spacing or words between parts, keeping order
    def part(label, value):
        return rf"{label}\s*=\s*{re.escape(value)}"

    parts = []
    var_values = []
    for lbl, val in [("A", A), ("B", B), ("C", C), ("a", a), ("b", b), ("c", c)]:
        if val is not None:
            v = sstr(sp.nsimplify(val)) if lbl.isupper() else str(val)
            parts.append(part(lbl, v))
            var_values.append((lbl, v))
    if area is not None:
        v = sstr(area)
        parts.append(part("area", v))
        var_values.append(("area", v))

    if parts:
        loose = r"Solution:\s*" + r".*".join(parts)
        patterns.append((re.compile(loose, re.I), final_str))

        # Accept MathLive/Sympy-style equation forms like Eq((S...)/X, value)
        # We don't depend on exact letter-by-letter tokenization; match any LHS over X.
        for var_name, var_val in var_values:
            eq_pat = r"^Eq\(.*/" + re.escape(var_name) + r",\s*" + re.escape(var_val) + r"\)$"
            patterns.append((re.compile(eq_pat, re.I), final_str))

    return tuple(patterns)


# ----------------------
# Domain
# ----------------------
Domain = {
    'done': Operator(head=('done', V('kc')),
                     precondition=[Fact(start=True)],
                     effects=[Fact(field='done', value=((re.compile('x'),),), kc=V('kc'), answer=True)],
    ),

    'normalize_inputs': Operator(head=('normalize_inputs', V('triangle'), V('kc')),
                                precondition=Fact(field=V('triangle'), value=V('val'), answer=False),
                                effects=[Fact(field='normalize_inputs', value=(normalize_inputs, V('val')), kc=V('kc'), answer=True)],
    ),

    'classify_triangle': Operator(head=('classify_triangle', V('triangle'), V('kc')),
                                precondition=Fact(field=V('triangle'), value=V('val'), answer=False),
                                effects=[Fact(field='classify_triangle', value=(classify_triangle, V('val')), kc=V('kc'), answer=True)],
    ),

    # Right-triangle path
    'apply_pythagorean': Operator(head=('apply_pythagorean', V('triangle'), V('kc')),
                                precondition=Fact(field=V('triangle'), value=V('val'), answer=False),
                                effects=[Fact(field='apply_pythagorean', value=(apply_pythagorean, V('val')), kc=V('kc'), answer=True)],
    ),
    'use_trig_ratios': Operator(head=('use_trig_ratios', V('triangle'), V('kc')),
                                precondition=Fact(field=V('triangle'), value=V('val'), answer=False),
                                effects=[Fact(field='use_trig_ratios', value=(use_trig_ratios, V('val')), kc=V('kc'), answer=True)],
    ),

    # Law of sines path
    'resolve_ssa_ambiguity': Operator(head=('resolve_ssa_ambiguity', V('triangle'), V('kc')),
                                precondition=Fact(field=V('triangle'), value=V('val'), answer=False),
                                effects=[Fact(field='resolve_ssa_ambiguity', value=(resolve_ssa_ambiguity, V('val')), kc=V('kc'), answer=True)],
    ),
    'compute_missing_angles': Operator(head=('compute_missing_angles', V('triangle'), V('kc')),
                                precondition=Fact(field=V('triangle'), value=V('val'), answer=False),
                                effects=[Fact(field='compute_missing_angles', value=(compute_missing_angles, V('val')), kc=V('kc'), answer=True)],
    ),
    'compute_missing_sides': Operator(head=('compute_missing_sides', V('triangle'), V('kc')),
                                precondition=Fact(field=V('triangle'), value=V('val'), answer=False),
                                effects=[Fact(field='compute_missing_sides', value=(compute_missing_sides, V('val')), kc=V('kc'), answer=True)],
    ),

    # Law of cosines path
    'compute_unknown_by_cosine': Operator(head=('compute_unknown_by_cosine', V('triangle'), V('kc')),
                                precondition=Fact(field=V('triangle'), value=V('val'), answer=False),
                                effects=[Fact(field='compute_unknown_by_cosine', value=(compute_unknown_by_cosine, V('val')), kc=V('kc'), answer=True)],
    ),
    'backfill_with_sines_if_needed': Operator(head=('backfill_with_sines_if_needed', V('triangle'), V('kc')),
                                precondition=Fact(field=V('triangle'), value=V('val'), answer=False),
                                effects=[Fact(field='backfill_with_sines_if_needed', value=(backfill_with_sines_if_needed, V('val')), kc=V('kc'), answer=True)],
    ),

    # Similarity path
    'map_correspondence': Operator(head=('map_correspondence', V('triangle'), V('kc')),
                                    precondition=Fact(field=V('triangle'), value=V('val'), answer=False),
                                    effects=[Fact(field='map_correspondence', value=(map_correspondence, V('val')), kc=V('kc'), answer=True)],
    ),
    'scale_sides_angles': Operator(head=('scale_sides_angles', V('triangle'), V('kc')),
                                    precondition=Fact(field=V('triangle'), value=V('val'), answer=False),
                                    effects=[Fact(field='scale_sides_angles', value=(scale_sides_angles, V('val')), kc=V('kc'), answer=True)],
    ),

    # Area relations path
    'select_area_formula': Operator(head=('select_area_formula', V('triangle'), V('kc')),
                                precondition=Fact(field=V('triangle'), value=V('val'), answer=False),
                                effects=[Fact(field='select_area_formula', value=(select_area_formula, V('val')), kc=V('kc'), answer=True)],
    ),
    'compute_area': Operator(head=('compute_area', V('triangle'), V('kc')),
                                precondition=Fact(field=V('triangle'), value=V('val'), answer=False),
                                effects=[Fact(field='compute_area', value=(compute_area, V('val')), kc=V('kc'), answer=True)],
    ),

    # Consistency checks path
    'consistency_checks': Operator(head=('consistency_checks', V('triangle'), V('kc')),
                                precondition=Fact(field=V('triangle'), value=V('val'), answer=False),
                                effects=[Fact(field='consistency_checks', value=(consistency_checks, V('val')), kc=V('kc'), answer=True)],
    ),

    # Report solution path
    'report_solution': Operator(head=('report_solution', V('triangle'), V('kc')),
                                precondition=Fact(field=V('triangle'), value=V('val'), answer=False),
                                effects=[Fact(field='report_solution', value=(report_solution, V('val')), kc=V('kc'), answer=True)],
    ),

    # Master method chosen only by triangle_type (frontend derived)
    'solve': Method(head=('solve', V('triangle')),
        preconditions=[
            Fact(field='triangle_type', value='Right'),
            Fact(field='triangle_type', value='Sines'),
            Fact(field='triangle_type', value='Cosines'),
            Fact(field='triangle_type', value='Similarity'),
            Fact(field='triangle_type', value='Area'),
            # Terminal branch when all subtasks answered
            Fact(scaffold='level_0'),
        ],
        subtasks=[
          
            [
                Task(head=('normalize_inputs', V('triangle'), ('normalize_inputs',)), primitive=True),
                Task(head=('classify_triangle', V('triangle'), ('classify_triangle',)), primitive=True),
                Task(head=('apply_pythagorean', V('triangle'), ('apply_pythagorean',)), primitive=True),
                Task(head=('use_trig_ratios', V('triangle'), ('use_trig_ratios',)), primitive=True),
                Task(head=('consistency_checks', V('triangle'), ('consistency_checks',)), primitive=True),
                Task(head=('report_solution', V('triangle'), ('report_solution',)), primitive=True),
                Task(head=('done', ('done',)), primitive=True)
            ],
            # Law of Sines via triangle_type
            [
                Task(head=('normalize_inputs', V('triangle'), ('normalize_inputs',)), primitive=True),
                Task(head=('classify_triangle', V('triangle'), ('classify_triangle',)), primitive=True),
                Task(head=('resolve_ssa_ambiguity', V('triangle'), ('resolve_ssa_ambiguity',)), primitive=True),
                Task(head=('compute_missing_angles', V('triangle'), ('compute_missing_angles',)), primitive=True),
                Task(head=('compute_missing_sides', V('triangle'), ('compute_missing_sides',)), primitive=True),
                Task(head=('consistency_checks', V('triangle'), ('consistency_checks',)), primitive=True),
                Task(head=('report_solution', V('triangle'), ('report_solution',)), primitive=True),
                Task(head=('done', ('done',)), primitive=True)
            ],
            # Law of Cosines via triangle_type
            [
                Task(head=('normalize_inputs', V('triangle'), ('normalize_inputs',)), primitive=True),
                Task(head=('classify_triangle', V('triangle'), ('classify_triangle',)), primitive=True),
                Task(head=('compute_unknown_by_cosine', V('triangle'), ('compute_unknown_by_cosine',)), primitive=True),
                Task(head=('backfill_with_sines_if_needed', V('triangle'), ('backfill_with_sines_if_needed',)), primitive=True),
                Task(head=('consistency_checks', V('triangle'), ('consistency_checks',)), primitive=True),
                Task(head=('report_solution', V('triangle'), ('report_solution',)), primitive=True),
                Task(head=('done', ('done',)), primitive=True)
            ],
            # Similarity via triangle_type
            [
                Task(head=('normalize_inputs', V('triangle'), ('normalize_inputs',)), primitive=True),
                Task(head=('classify_triangle', V('triangle'), ('classify_triangle',)), primitive=True),
                Task(head=('map_correspondence', V('triangle'), ('map_correspondence',)), primitive=True),
                Task(head=('scale_sides_angles', V('triangle'), ('scale_sides_angles',)), primitive=True),
                Task(head=('consistency_checks', V('triangle'), ('consistency_checks',)), primitive=True),
                Task(head=('report_solution', V('triangle'), ('report_solution',)), primitive=True),
                Task(head=('done', ('done',)), primitive=True)
            ],
            # Area via triangle_type
            [
                Task(head=('normalize_inputs', V('triangle'), ('normalize_inputs',)), primitive=True),
                Task(head=('classify_triangle', V('triangle'), ('classify_triangle',)), primitive=True),
                Task(head=('select_area_formula', V('triangle'), ('select_area_formula',)), primitive=True),
                Task(head=('compute_area', V('triangle'), ('compute_area',)), primitive=True),
                Task(head=('consistency_checks', V('triangle'), ('consistency_checks',)), primitive=True),
                Task(head=('report_solution', V('triangle'), ('report_solution',)), primitive=True),
                Task(head=('done', ('done',)), primitive=True)
            ],
            # Terminal branch once all work is complete
            [
                Task(head=('done', ('done',)), primitive=True)
            ],
        ]
    ),
}


def htn_geometry_solve_triangle_kc_mapping():
    return {
        "normalize_inputs": "Normalize triangle inputs",
        "classify_triangle": "Classify triangle type",
        "apply_pythagorean": "Apply Pythagorean theorem",
        "use_trig_ratios": "Use trig ratios (SOH/CAH/TOA)",
        "resolve_ssa_ambiguity": "Resolve SSA ambiguity",
        "compute_missing_angles": "Compute missing angles",
        "compute_missing_sides": "Compute missing sides",
        "compute_unknown_by_cosine": "Law of Cosines for unknown",
        "backfill_with_sines_if_needed": "Backfill with Law of Sines if needed",
        "map_correspondence": "Map triangle correspondence",
        "scale_sides_angles": "Scale sides/angles by similarity",
        "select_area_formula": "Select area formula",
        "compute_area": "Compute area",
        "consistency_checks": "Check triangle consistency",
        "report_solution": "Report solution",
        "done": "Complete triangle solution"
    }


def htn_geometry_solve_triangle_intermediate_hints():
    return {
        "normalize_inputs": ["Normalize all triangle inputs (angles, sides)."],
        "classify_triangle": [
            "Classify: Right, Sines (ASA/AAS/SSA), Cosines (SAS/SSS), Similarity, or Area.",
            "Use natural labels, e.g., 'Right' or 'Sines'."
        ],
        "apply_pythagorean": ["Use Pythagorean theorem for right triangles."],
        "use_trig_ratios": ["Use SOH/CAH/TOA for right triangles."],
        "resolve_ssa_ambiguity": ["Check for SSA ambiguity and resolve."],
        "compute_missing_angles": ["Compute missing angles using Law of Sines."],
        "compute_missing_sides": ["Compute missing sides using Law of Sines."],
        "compute_unknown_by_cosine": ["Use Law of Cosines for SSS/SAS cases."],
        "backfill_with_sines_if_needed": ["Use Law of Sines after Law of Cosines if needed."],
        "map_correspondence": ["Map corresponding sides/angles for similarity."],
        "scale_sides_angles": ["Scale sides/angles using similarity criteria."],
        "select_area_formula": ["Select appropriate area formula (Heron, ½ab sin C, etc.)."],
        "compute_area": ["Compute area using selected formula."],
        "consistency_checks": ["Check angle sum, triangle inequality, etc."],
        "report_solution": ["Report the solution for all unknowns."],
        "done": ["Click done when finished."]
    }


def htn_geometry_solve_triangle_studymaterial():
    return studymaterial.get("geometry_solve_triangle", [])


# htn_loaded_models.register(HTNCognitiveModel(
#     'htn_geometry',
#     'htn_geometry_solve_triangle',
#     Domain,
#     Task(head=('solve', 'triangle'), primitive=False),
#     htn_geometry_solve_triangle_problem,
#     htn_geometry_solve_triangle_kc_mapping(),
#     htn_geometry_solve_triangle_intermediate_hints(),
#     htn_geometry_solve_triangle_studymaterial()
# ))
