"""A bounded necessary-condition CNF over distinct attachment columns."""

from pathlib import Path

from encode import independent_sets
from shared import Budget, Formula, SearchLimit, cardinality, checker, digest, graph_digest, write_json

PROFILE = "fixed-h-column-selector-v1"
MAX_SELECTORS = 1500
MAX_VARIABLES = 60_000
MAX_CLAUSES = 1_500_000
MAX_CNF_BYTES = 32 * 1024**2
MAX_I8 = 10_000


def catalogue_columns(adj, *, budget=None):
    """Independently enumerate every maximal independent set, then filter.

    This does not import the column-cover search or trust its census. The
    exact fixed-size enumerator and graph checker are reviewed dependencies.
    """
    budget = budget or Budget()
    checker.validate_adjacency(adj)
    if len(adj) != 33 or checker.triangle(adj) is not None:
        raise ValueError("selector profile requires a triangle-free 33-vertex H")
    degrees = [row.bit_count() for row in adj]
    if not set(degrees) <= {6, 7, 8}:
        raise ValueError("selector profile requires H degrees 6, 7, and 8 only")
    if checker.independent_set(adj, 9, node_limit=1_000_000,
                               deadline=budget.wall_start + budget.seconds) is not None:
        raise ValueError("H has an independent nine-set")
    full, degree8 = (1 << 33) - 1, sum(1 << v for v, degree in enumerate(degrees) if degree == 8)
    maximal_counts, all_set_counts, eligible, i8, maximal_masks = {}, {}, [], [], []
    for size in range(9):
        total, maximal = 0, 0
        for mask in independent_sets(adj, size, budget=budget):
            total += 1
            if size == 8:
                if len(i8) >= MAX_I8:
                    raise SearchLimit("independent-eight-set inventory limit")
                i8.append(mask)
            dominated, remaining = mask, mask
            while remaining:
                bit = remaining & -remaining
                remaining ^= bit
                dominated |= adj[bit.bit_length() - 1]
            if dominated != full:
                continue
            maximal += 1
            maximal_masks.append(mask)
            if size not in (7, 8):
                raise ValueError("complete H census contains a maximal set outside sizes 7 and 8")
            if (mask & degree8).bit_count() <= 4:
                if len(eligible) >= MAX_SELECTORS:
                    raise SearchLimit("eligible-column inventory limit")
                eligible.append(mask)
        all_set_counts[str(size)], maximal_counts[str(size)] = total, maximal
    eligible.sort()
    i8.sort()
    missed = missed_bitsets(eligible, i8, budget=budget)
    budget.check()
    return {"profile": PROFILE, "scope": "necessary cover for centre-covered fixed-H extensions after attachment saturation",
            "base_adjacency": list(adj), "base_adjacency_sha256": graph_digest(adj),
            "base_order": 33, "columns": eligible, "independent_eight_sets": i8,
            "missed_eight_set_bitsets": missed, "row_caps": [9 - degree for degree in degrees],
            "exact_rows": degree8, "choose": 6,
            "independent_set_counts": all_set_counts, "maximal_set_counts": maximal_counts,
            "maximal_set_inventory_sha256": graph_digest(sorted(maximal_masks)),
            "eligible_column_inventory_sha256": graph_digest(eligible),
            "independent_eight_set_inventory_sha256": graph_digest(i8),
            "eligible_set_counts": {str(size): sum(mask.bit_count() == size for mask in eligible)
                                    for size in (7, 8)},
            "all_maximal_sets_enumerated": True, "h_has_no_independent_nine_set": True,
            "attachment_saturation_reduction": "add only triangle-free A-H edges; H and the centre stay fixed",
            "distinct_columns_required": True, "duplicate_exclusion_premise":
            "coverage gives at least 18 private vertices; duplicate columns permit at most 16",
            "other_row_coverage_required": False, "sat_is_only_a_cover": True}


def missed_bitsets(columns, i8, *, budget=None):
    budget = budget or Budget()
    if len(i8) > MAX_I8 or len(columns) > MAX_SELECTORS:
        raise ValueError("column or independent-set inventory limit")
    result = []
    for index, column in enumerate(columns):
        if index % 16 == 0:
            budget.check()
        result.append(sum(1 << position for position, mask in enumerate(i8) if not column & mask))
    return result


def validate_selection(columns, row_caps, exact_rows, missed, choose):
    if (not 0 <= len(columns) <= MAX_SELECTORS or not 1 <= len(row_caps) <= 33
            or len(set(columns)) != len(columns) or len(missed) != len(columns)
            or type(choose) is not int or not 1 <= choose <= 6
            or type(exact_rows) is not int or not 0 <= exact_rows < 1 << len(row_caps)
            or any(type(mask) is not int or not 0 <= mask < 1 << len(row_caps) for mask in columns)
            or any(type(cap) is not int or not 0 <= cap <= 3 for cap in row_caps)
            or any(type(mask) is not int or mask < 0 or mask.bit_length() > MAX_I8 for mask in missed)
            or any(exact_rows >> v & 1 and cap != 1 for v, cap in enumerate(row_caps))):
        raise ValueError("unsupported selector parameters")


def encode_selection(columns, row_caps, exact_rows, missed, choose, emit, *, budget=None):
    """General small-control interface; production inventories come from H."""
    budget = budget or Budget()
    validate_selection(columns, row_caps, exact_rows, missed, choose)
    count, total, counts = len(columns), 0, {}
    formula = Formula(max(1, count))
    if choose > count:
        formula.add()
    else:
        cardinality(formula, list(range(1, count + 1)), choose, choose)
    counts["choose_distinct_columns"] = len(formula.clauses)
    before = len(formula.clauses)
    for vertex, cap in enumerate(row_caps):
        budget.check()
        members = [index + 1 for index, column in enumerate(columns) if column >> vertex & 1]
        lower, upper = int(exact_rows >> vertex & 1), min(cap, len(members))
        if lower > upper:
            formula.add()
        else:
            cardinality(formula, members, lower, upper)
    counts["row_constraints"] = len(formula.clauses) - before
    if formula.variables > MAX_VARIABLES:
        raise SearchLimit("selector variable limit")

    def append(clause):
        nonlocal total
        if total >= MAX_CLAUSES:
            raise SearchLimit("selector clause limit")
        if total % 256 == 0:
            budget.check()
        emit(tuple(clause))
        total += 1

    for clause in formula.clauses:
        append(clause)
    before = total
    for left in range(count):
        if left % 16 == 0:
            budget.check()
        for right in range(left + 1, count):
            if missed[left] & missed[right]:
                append((-left - 1, -right - 1))
    counts["incompatible_column_pairs"] = total - before
    budget.check()
    return {"profile": PROFILE, "variables": formula.variables, "clauses": total,
            "selector_variables": count, "clause_counts": counts,
            "choose": choose, "sat_is_only_a_cover": True,
            "full_ramsey_constraints_encoded": False}


def selection_parameters(inventory):
    return (inventory["columns"], inventory["row_caps"], inventory["exact_rows"],
            inventory["missed_eight_set_bitsets"], inventory["choose"])


def write_instance(output, inventory, *, budget=None):
    budget = budget or Budget()
    output = Path(output)
    body, partial, destination = (output / "selector-clauses.partial",
                                  output / "instance.cnf.partial", output / "instance.cnf")
    if any(path.exists() for path in (body, partial, destination, output / "instance.json")):
        raise ValueError("selector instance output must be new")
    byte_count = 0
    with body.open("xb") as target:
        def emit(clause):
            nonlocal byte_count
            raw = (" ".join(map(str, clause)) + " 0\n").encode("ascii")
            byte_count += len(raw)
            if byte_count + 64 > MAX_CNF_BYTES:
                raise SearchLimit("selector CNF byte limit")
            target.write(raw)
        metadata = encode_selection(*selection_parameters(inventory), emit, budget=budget)
    with partial.open("xb") as target, body.open("rb") as source:
        target.write(f"p cnf {metadata['variables']} {metadata['clauses']}\n".encode("ascii"))
        for block in iter(lambda: source.read(262144), b""):
            budget.check()
            target.write(block)
    budget.check()
    partial.replace(destination)
    body.unlink()
    metadata.update({"cnf_sha256": digest(destination), "cnf_bytes": destination.stat().st_size,
                     "scope": inventory["scope"]})
    write_json(output / "instance.json", metadata)
    return metadata


def check_cover(inventory, selected):
    """Direct necessary-condition check, independent of counter auxiliaries."""
    columns, row_caps, exact_rows, missed, choose = selection_parameters(inventory)
    validate_selection(columns, row_caps, exact_rows, missed, choose)
    if (len(selected) != choose or len(set(selected)) != choose
            or any(type(index) is not int or not 0 <= index < len(columns) for index in selected)):
        raise ValueError("wrong number or identity of selected columns")
    for vertex, cap in enumerate(row_caps):
        count = sum(columns[index] >> vertex & 1 for index in selected)
        if count > cap or exact_rows >> vertex & 1 and count != 1:
            raise ValueError("selected columns violate a row constraint")
    for position, left in enumerate(selected):
        if any(missed[left] & missed[right] for right in selected[position + 1:]):
            raise ValueError("selected columns miss an independent eight-set")
    return True
