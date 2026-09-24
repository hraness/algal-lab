"""Bounded Decimal grid checks for the supplied two-agent softmax spike.

These finite checks are corroboration only; they do not prove the continuum theorem.
Stdlib only. No optimization package, network, writes, or external inference requests.
"""
from decimal import Decimal, localcontext
from fractions import Fraction
from itertools import product
import json


TEMPERATURES = (("0.5", "0.5"), ("4", "0.01"), ("4", "4"), ("4", "8"))
GRID_DENOMINATOR = 4
TOL = Decimal("1e-70")


def dec(value):
    return Decimal(str(value))


def softmax_mean(values, temperature):
    weights = [(temperature * value).exp() for value in values]
    return sum((value * weight for value, weight in zip(values, weights)), Decimal(0)) / sum(weights)


def nested_reward(rows, inner_t, outer_tau, tasks):
    scores = [softmax_mean([row[j] for row in rows], inner_t) for j in range(tasks)]
    return softmax_mean(scores, outer_tau)


def closed_h_d(tasks, inner_t, outer_tau):
    one = Decimal(1)
    e_tau = outer_tau.exp()
    h = e_tau / (e_tau + tasks - 1)
    e_inner = inner_t.exp()
    b = e_inner / (e_inner + one)
    e_tau_b = (outer_tau * b).exp()
    d = (2 * b * e_tau_b) / (2 * e_tau_b + tasks - 2)
    return h, d


def quarter_compositions(tasks):
    """All vectors in the full simplex with coordinates multiples of 1/4."""
    def visit(prefix, left, slots):
        if slots == 1:
            yield tuple(prefix + [left])
            return
        for amount in range(left + 1):
            yield from visit(prefix + [amount], left - amount, slots - 1)

    for units in visit([], GRID_DENOMINATOR, tasks):
        yield tuple(Decimal(value) / GRID_DENOMINATOR for value in units)


def is_pure(row):
    return sum(value != 0 for value in row) == 1 and max(row) == 1


def _two_agent_checks():
    with localcontext() as ctx:
        ctx.prec = 100
        # Exact integer/rational certificate from the supplied M=3 witness.
        assert 19**3 == 6859 < 6912 == 4 * 12**3
        r_lower = Fraction(19, 12)
        gap_lower = Fraction(2 * r_lower - 3, 6 * (2 * r_lower + 1))
        assert gap_lower == Fraction(1, 150)

        pure_cases = 0
        for tasks in range(2, 7):
            for t_text, tau_text in TEMPERATURES:
                t, tau = dec(t_text), dec(tau_text)
                h, d = closed_h_d(tasks, t, tau)
                concentrated = tuple((Decimal(1) if j == 0 else Decimal(0)) for j in range(tasks))
                separated0 = tuple((Decimal(1) if j == 0 else Decimal(0)) for j in range(tasks))
                separated1 = tuple((Decimal(1) if j == 1 else Decimal(0)) for j in range(tasks))
                actual_h = nested_reward((concentrated, concentrated), t, tau, tasks)
                actual_d = nested_reward((separated0, separated1), t, tau, tasks)
                assert abs(actual_h - h) <= TOL, ("pure-H", tasks, t_text, tau_text, actual_h, h)
                assert abs(actual_d - d) <= TOL, ("pure-D", tasks, t_text, tau_text, actual_d, d)
                pure_cases += 2

        row_grids = {tasks: tuple(quarter_compositions(tasks)) for tasks in range(2, 5)}
        grid_points = 0
        temperature_runs = 0
        pure_grid_maximizers = 0
        maximum_excess = Decimal(0)
        # Keep the four specified temperature pairs paired (rather than cross-producting them).
        for tasks in range(2, 5):
            for t_text, tau_text in TEMPERATURES:
                t, tau = dec(t_text), dec(tau_text)
                h, d = closed_h_d(tasks, t, tau)
                bound = max(h, d)
                values = []
                for row0, row1 in product(row_grids[tasks], repeat=2):
                    reward = nested_reward((row0, row1), t, tau, tasks)
                    excess = reward - bound
                    if excess > maximum_excess:
                        maximum_excess = excess
                    assert excess <= TOL, ("grid-upper-bound", tasks, t_text, tau_text, row0, row1, reward, bound)
                    values.append((reward, row0, row1))
                    grid_points += 1
                finite_best = max(value[0] for value in values)
                assert abs(finite_best - bound) <= TOL, ("grid-attains-bound", tasks, t_text, tau_text, finite_best, bound)
                for reward, row0, row1 in values:
                    if finite_best - reward <= TOL:
                        assert is_pure(row0) and is_pure(row1), ("nonpure-grid-maximizer", tasks, t_text, tau_text, reward, finite_best, row0, row1)
                        pure_grid_maximizers += 1
                temperature_runs += 1

        return {
            "status": "PASS",
            "exactRadicalCertificate": {
                "checked": "19^3 < 4*12^3",
                "rationalLowerBound": str(gap_lower),
                "strictGainClaimLowerBound": ">1/150",
            },
            "pureAllocationChecks": pure_cases,
            "quarterGrid": {
                "tasks": [2, 3, 4],
                "temperaturePairs": [list(pair) for pair in TEMPERATURES],
                "fullBudgetRowGridSizes": {str(tasks): len(rows) for tasks, rows in row_grids.items()},
                "nestedAllocationPointsChecked": grid_points,
                "temperatureTaskRuns": temperature_runs,
                "finiteGridMaximizersCheckedPure": pure_grid_maximizers,
                "maximumRewardMinusClosedBound": str(maximum_excess),
            },
            "scope": "Finite Decimal corroboration only; not a proof of continuum purity or the analytic crossover.",
        }


def _three_task_checks():
    """An independent full quarter-grid calculation, with cached column scores."""
    with localcontext() as ctx:
        ctx.prec = 100
        rows = tuple(quarter_compositions(3))
        points = near_maxima = runs = 0
        maximum_excess = Decimal(0)
        for t_text, tau_text in TEMPERATURES:
            t, tau = dec(t_text), dec(tau_text)
            columns = {}
            for column in product(tuple(Decimal(k) / 4 for k in range(5)), repeat=3):
                score = softmax_mean(column, t)
                weight = (tau * score).exp()
                columns[column] = (score * weight, weight)

            def reward(allocation):
                terms = [columns[tuple(row[j] for row in allocation)] for j in range(3)]
                return sum((term[0] for term in terms), Decimal(0)) / sum(
                    (term[1] for term in terms), Decimal(0))

            units = tuple(tuple(Decimal(int(i == j)) for j in range(3)) for i in range(3))
            # Independent explicit pure representatives, not the occupancy solver.
            bound = max(reward((units[0], units[0], units[0])),
                        reward((units[0], units[0], units[1])),
                        reward((units[0], units[1], units[2])))
            best = Decimal(0)
            for allocation in product(rows, repeat=3):
                value = reward(allocation)
                maximum_excess = max(maximum_excess, value - bound)
                assert value - bound <= TOL
                best = max(best, value)
                if abs(value - bound) <= TOL:
                    assert all(is_pure(row) for row in allocation)
                    near_maxima += 1
                points += 1
            assert abs(best - bound) <= TOL
            runs += 1
        assert points == 13500 and runs == 4 and near_maxima == 45
        return {"tasks": 3, "agents": 3, "quarterGridMatrices": points,
                "temperatureRuns": runs, "nearMaximizersAllPure": near_maxima,
                "maximumRewardMinusPureBound": str(maximum_excess),
                "scope": "Finite Decimal grid only; all-population three-task purity requires the analytic proof."}


def verify():
    return {"softmaxSmallDimensions": {
        "twoAgents": _two_agent_checks(), "threeTasks": _three_task_checks()}}


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
