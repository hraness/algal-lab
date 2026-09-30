"""Exact integer checks for the five-point coefficient certificates.

No optimizer or producer imports. Every fiber and coefficient is rebuilt from
the fixed support. A checked Farkas witness rules out only this coefficient
criterion; it is not a counterexample to the reflected H4 inequality.
"""

import hashlib
import itertools
import json
import math


SUPPORT = (0, 2, 7, 8, 11)
D = 10**9
EXPONENTS = tuple(e for e in itertools.product(range(5), repeat=5)
                  if sum(e) == 4)
M4 = (4, 0, 0, 0, 0)
DUAL_BASIS = tuple(e for e in EXPONENTS if e != M4)
ORDERS = tuple(itertools.permutations(range(5)))
TARGETS = {
    'U': {'numerators': [1109, 900, 675, 450, 225], 'denominator': 450},
    'V': {'numerators': [35488, 28461, 21434, 14407, 7380], 'denominator': 14400},
}
FIBERS = {}
for j, e in enumerate(EXPONENTS):
    z = sum(a * b for a, b in zip(SUPPORT, e))
    FIBERS.setdefault(z, []).append(j)
FIBER_SUMS = tuple(sorted(FIBERS))
STATUSES = ('PRIMAL_EXACT', 'DUAL_EXACT', 'UNRESOLVED')
ROW_KEYS = {'index', 'order', 'target', 'status', 'primal_numerators',
            'dual_numerators', 'primal_residual_numerators',
            'dual_fiber_maxima', 'dual_gap_numerator'}


class Invalid(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Invalid(reason)


def unique_object(pairs):
    answer = {}
    for key, value in pairs:
        require(key not in answer, 'duplicate JSON key')
        answer[key] = value
    return answer


def invalid_constant(value):
    raise Invalid('nonfinite JSON value')


def canonical_integer(value):
    require(len(value) <= 40, 'integer token length')
    number = int(value)
    require(str(number) == value and abs(number) < 2**128,
            'noncanonical or out-of-range integer token')
    return number


def finite_float(value):
    number = float(value)
    require(math.isfinite(number), 'nonfinite JSON number')
    return number


def parse(raw, cap):
    require(type(raw) is bytes and len(raw) <= cap, 'input byte limit')
    try:
        return json.loads(raw, object_pairs_hook=unique_object,
                          parse_constant=invalid_constant, parse_float=finite_float,
                          parse_int=canonical_integer)
    except (UnicodeError, ValueError) as error:
        raise Invalid('invalid bounded JSON') from error


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      allow_nan=False)


def lines(raw, maximum):
    require(type(raw) is bytes and len(raw) <= 8 * 1024**2, 'NDJSON byte limit')
    items = raw.splitlines()
    require(len(items) <= maximum and all(items), 'NDJSON line count/empty line')
    return [parse(item, 32768) for item in items]


def expected_basis():
    return {
        'schema': 'algal-five-point-order-cone-lp-basis-v1',
        'support': list(SUPPORT), 'denominator': D,
        'witnesses': [list(e) for e in EXPONENTS],
        'coefficient_basis': [list(e) for e in EXPONENTS],
        'fiber_sums': list(FIBER_SUMS), 'targets': TARGETS,
    }


def multiply_linear(polynomial, coefficients):
    result = {}
    for exponent, value in polynomial.items():
        for variable, coefficient in enumerate(coefficients):
            if coefficient:
                shifted = list(exponent)
                shifted[variable] += 1
                shifted = tuple(shifted)
                result[shifted] = result.get(shifted, 0) + value * coefficient
    return result


def coefficients_for_order(order):
    # order lists support indices from least to greatest weight. The weight at
    # rank r is x_0+...+x_r. Enumerate the four slots and their variable choices
    # directly, independently of the producer's polynomial multiplication.
    ranks = {support_index: rank for rank, support_index in enumerate(order)}
    result = []
    for witness in EXPONENTS:
        slots = [i for i, multiplicity in enumerate(witness)
                 for _ in range(multiplicity)]
        polynomial = {}
        for choices in itertools.product(*(range(ranks[i] + 1) for i in slots)):
            exponent = [0] * 5
            for variable in choices:
                exponent[variable] += 1
            exponent = tuple(exponent)
            polynomial[exponent] = polynomial.get(exponent, 0) + 1
        result.append(polynomial)
    return result


def target_coefficients(target):
    polynomial = {(0, 0, 0, 0, 0): 1}
    for _ in range(4):
        polynomial = multiply_linear(polynomial, TARGETS[target]['numerators'])
    return polynomial


def integers(value, count):
    require(type(value) is list and len(value) == count, 'integer-vector length')
    require(all(type(n) is int and 0 <= n <= D for n in value),
            'integer-vector range/type')
    return value


def identify(row, index):
    require(type(row) is dict and set(row) == ROW_KEYS, 'certificate fields')
    require(type(row['index']) is int and row['index'] == index, 'case index')
    require(type(row['order']) is list and len(row['order']) == 5
            and all(type(i) is int for i in row['order'])
            and tuple(row['order']) == ORDERS[index // 2], 'case order')
    require(row['target'] == ('U', 'V')[index % 2], 'case target')
    require(type(row['status']) is str and row['status'] in STATUSES, 'case status')


def check_case(row, index, matrix):
    identify(row, index)
    target = target_coefficients(row['target'])
    q4 = TARGETS[row['target']]['denominator']**4
    primal_ok = dual_ok = False
    if row['primal_numerators'] is None:
        require(row['primal_residual_numerators'] is None, 'missing primal')
    else:
        primal = integers(row['primal_numerators'], 70)
        require(all(sum(primal[j] for j in FIBERS[z]) == D for z in FIBER_SUMS),
                'primal fiber masses must equal denominator')
        residuals = [q4 * sum(primal[j] * matrix[j].get(e, 0) for j in range(70))
                     - D * target[e] for e in EXPONENTS]
        require(row['primal_residual_numerators'] == [str(r) for r in residuals],
                'claimed primal residuals differ')
        primal_ok = all(r >= 0 for r in residuals)
    if row['dual_numerators'] is None:
        require(row['dual_fiber_maxima'] is None and row['dual_gap_numerator'] is None,
                'missing dual')
    else:
        dual = integers(row['dual_numerators'], 69)
        columns = [sum(y * polynomial.get(e, 0) for y, e in zip(dual, DUAL_BASIS))
                   for polynomial in matrix]
        maxima = [max(columns[j] for j in FIBERS[z]) for z in FIBER_SUMS]
        gap = sum(y * target[e] for y, e in zip(dual, DUAL_BASIS)) - q4 * sum(maxima)
        require(row['dual_fiber_maxima'] == [str(r) for r in maxima],
                'claimed dual fiber maxima differ')
        require(row['dual_gap_numerator'] == str(gap), 'claimed dual gap differs')
        dual_ok = gap > 0
    require(not (primal_ok and dual_ok), 'contradictory exact certificates')
    status = 'PRIMAL_EXACT' if primal_ok else 'DUAL_EXACT' if dual_ok else 'UNRESOLVED'
    require(row['status'] == status, 'status differs from exact checks')
    return status


def check_diagnostics(diagnostics):
    require(len(diagnostics) == 480, 'complete run needs 480 diagnostic events')
    for position, row in enumerate(diagnostics):
        index = position // 2
        require(type(row) is dict, 'diagnostic object required')
        require(type(row.get('index')) is int and row['index'] == index,
                'diagnostic index')
        require(row.get('event') == ('started', 'result')[position % 2],
                'diagnostic event order')
        require(canonical(row.get('order')) == canonical(list(ORDERS[index // 2]))
                and row.get('target') == ('U', 'V')[index % 2],
                'diagnostic case identity')


def rejects(action):
    try:
        action()
    except Invalid:
        return True
    raise Invalid('a required corruption control was accepted')


def verify(basis_raw, certificates_raw, diagnostics_raw, checkpoint):
    require(callable(checkpoint), 'controller checkpoint required')
    checkpoint()
    basis = parse(basis_raw, 65536)
    require(canonical(basis) == canonical(expected_basis()), 'basis mismatch')
    rows = lines(certificates_raw, 240)
    diagnostics = lines(diagnostics_raw, 480)
    require(len(rows) == 240, 'exactly 240 certificates required')
    for index, row in enumerate(rows):
        identify(row, index)
    check_diagnostics(diagnostics)
    counts = dict.fromkeys(STATUSES, 0)
    covered = 0
    one_bound_orders = 0
    for order_index, order in enumerate(ORDERS):
        checkpoint()
        matrix = coefficients_for_order(order)
        statuses = [check_case(rows[index], index, matrix)
                    for index in (2 * order_index, 2 * order_index + 1)]
        for status in statuses:
            counts[status] += 1
        one_bound_orders += 'PRIMAL_EXACT' in statuses
        covered += all(status == 'PRIMAL_EXACT' for status in statuses)
    checkpoint()

    # Controls exercise schema identity and the actual mathematical checker.
    # They use only retained candidates; they make no optimizer calls.
    controls = {}
    controls['negative_zero_integer_rejected'] = rejects(lambda: parse(b'{"x":-0}', 64))
    bad_index = dict(rows[0], index=1)
    controls['changed_case_index_rejected'] = rejects(lambda: identify(bad_index, 0))
    controls['duplicate_json_key_rejected'] = rejects(lambda: parse(b'{"x":0,"x":1}', 64))
    controls['nonfinite_json_rejected'] = rejects(lambda: parse(b'{"x":NaN}', 64))
    primal_index = next((i for i, row in enumerate(rows)
                         if row['primal_numerators'] is not None), None)
    if primal_index is not None:
        bad = dict(rows[primal_index])
        bad['primal_numerators'] = list(bad['primal_numerators'])
        bad['primal_numerators'][0] += -1 if bad['primal_numerators'][0] == D else 1
        matrix = coefficients_for_order(ORDERS[primal_index // 2])
        controls['changed_fiber_mass_rejected'] = rejects(
            lambda: check_case(bad, primal_index, matrix))
    else:
        controls['changed_fiber_mass_rejected'] = 'not applicable; no primal candidate'
    dual_index = next((i for i, row in enumerate(rows)
                      if row['dual_numerators'] is not None), None)
    if dual_index is not None:
        bad = dict(rows[dual_index])
        bad['dual_gap_numerator'] = str(int(bad['dual_gap_numerator']) + 1)
        matrix = coefficients_for_order(ORDERS[dual_index // 2])
        controls['changed_dual_gap_rejected'] = rejects(
            lambda: check_case(bad, dual_index, matrix))
    else:
        controls['changed_dual_gap_rejected'] = 'not applicable; no dual candidate'
    checkpoint()
    return {
        'schema': 'algal-five-point-order-cone-lp-verification-v1',
        'status': 'VERIFIED', 'cases': 240, 'counts': counts,
        'all_primal': counts['PRIMAL_EXACT'] == 240,
        'orders_with_at_least_one_primal': one_bound_orders,
        'orders_with_both_primal': covered,
        'all_orders_covered': covered == 120,
        'input_sha256': {
            'basis': hashlib.sha256(basis_raw).hexdigest(),
            'certificates': hashlib.sha256(certificates_raw).hexdigest(),
            'diagnostics': hashlib.sha256(diagnostics_raw).hexdigest(),
        },
        'corruption_controls': controls,
        'claim_limit': 'Exact coefficient certificates for the fixed support and two fixed bounds. '
                       'A primal certificate proves its order-cone polynomial inequality. '
                       'Both targets on all 120 cones, together with the separately reviewed '
                       'corner comparison C^4 <= T_F, suffice for the reviewed reflected H4 '
                       'reduction on this support only. One target per cone is insufficient. '
                       'A dual certificate refutes only '
                       'that fixed coefficient criterion. Neither a dual nor an unresolved '
                       'case is an H4 counterexample; no priority conclusion is established.',
    }
