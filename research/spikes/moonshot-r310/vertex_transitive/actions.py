"""Explicit reproducible actions, not a census of transitive groups of degree 40."""

import itertools


def compose(a, b):
    return tuple(a[b[i]] for i in range(len(a)))


def cycle(n, *vertices):
    result = list(range(n))
    for v, w in zip(vertices, vertices[1:] + vertices[:1]):
        result[v] = w
    return tuple(result)


def closure(identity, generators, multiply, cap=2000):
    seen, todo = {identity}, [identity]
    while todo:
        item = todo.pop()
        for g in generators:
            new = multiply(g, item)
            if new not in seen:
                seen.add(new)
                todo.append(new)
                if len(seen) > cap:
                    raise ValueError("finite group construction exceeds cap")
    return sorted(seen)


def coset_action(name, identity, generators, subgroup_generators, multiply, expected_group_order):
    group = closure(identity, generators, multiply)
    subgroup = closure(identity, subgroup_generators, multiply)
    if len(group) != expected_group_order or not set(subgroup) <= set(group):
        raise ValueError("incorrect group construction")
    membership, representatives = {}, []
    for g in group:
        if g in membership:
            continue
        index = len(representatives)
        representatives.append(g)
        coset = {multiply(g, h) for h in subgroup}
        if coset & membership.keys():
            raise ValueError("overlapping cosets")
        membership.update({x: index for x in coset})
    return {"name": name, "n": len(representatives), "generators": [
        [membership[multiply(g, representative)] for representative in representatives]
        for g in generators
    ]}


def product_action(action, name, other_generators):
    m = len(other_generators[0])
    n = action["n"]
    return {"name": name, "n": n * m, "generators": [
        [g[v] * m + w for v in range(n) for w in range(m)] for g in action["generators"]
    ] + [[v * m + g[w] for v in range(n) for w in range(m)] for g in other_generators]}


def cyclic_action(n):
    return {"name": f"C{n}", "n": n, "generators": [[(v + 1) % n for v in range(n)]]}


def eight_groups():
    for mods in [(8,), (4, 2), (2, 2, 2)]:
        elements = list(itertools.product(*(range(m) for m in mods)))
        index = {value: i for i, value in enumerate(elements)}
        table = [[index[tuple((x + y) % m for x, y, m in zip(a, b, mods))]
                  for b in elements] for a in elements]
        yield "x".join(f"C{m}" for m in mods), table
    elements = list(itertools.product(range(4), range(2)))
    index = {value: i for i, value in enumerate(elements)}
    for name, square in [("D8", 0), ("Q8", 2)]:
        table = [[index[((i + (-1 if j else 1) * k + square * j * l) % 4, (j + l) % 2)]
                  for k, l in elements] for i, j in elements]
        yield name, table


def all_homomorphisms(table):
    """Check every possible image, constrained only by element orders.

    Images are exponents in the additive group Z/4Z. This construction keeps
    all homomorphisms; it never identifies groups by a coarse invariant.
    """
    domains = []
    for a in range(8):
        power, order = a, 1
        while power:
            power = table[power][a]
            order += 1
            if order > 8:
                raise ValueError("invalid group of order eight")
        domains.append([image for image in range(4) if image * order % 4 == 0])
    for images in itertools.product(*domains):
        if all(images[table[a][b]] == (images[a] + images[b]) % 4 for a in range(8) for b in range(8)):
            yield images


def cayley_actions():
    actions = []
    for name, table in eight_groups():
        for images in all_homomorphisms(table):
            # Left regular action on (c, p), c in Z/5Z. Every right Cayley
            # graph is invariant under these permutations. Using all elements
            # as generators avoids a second group-generation assumption.
            generators = []
            for c, p in itertools.product(range(5), range(8)):
                generators.append([
                    8 * ((c + pow(2, images[p], 5) * d) % 5) + table[p][q]
                    for d, q in itertools.product(range(5), range(8))
                ])
            actions.append({"name": f"C5_semidirect_{name}_{''.join(map(str, images))}",
                            "n": 40, "generators": generators})
    return actions


def nonregular_actions():
    """Selected actions whose groups are not regular on the 40 vertices.

    An invariant graph can still be Cayley under another automorphism group.
    These examples do not constitute all non-Cayley or all transitive actions.
    """
    identity5 = tuple(range(5))
    a5 = [cycle(5, 0, 1, 2, 3, 4), cycle(5, 0, 1, 2)]
    c3 = cycle(5, 0, 1, 2)
    flip = compose(cycle(5, 0, 1), cycle(5, 3, 4))
    a5_20 = coset_action("A5_on_cosets_C3", identity5, a5, [c3], compose, 60)
    a5_10 = coset_action("A5_on_cosets_S3", identity5, a5, [c3, flip], compose, 60)
    actions = [
        product_action(a5_20, "A5_C3_times_C2", [[1, 0]]),
        product_action(a5_10, "A5_S3_times_C4", [[1, 2, 3, 0]]),
        product_action(a5_10, "A5_S3_times_V4", [[1, 0, 3, 2], [2, 3, 0, 1]]),
        coset_action("S5_on_cosets_C3", identity5,
                     [cycle(5, 0, 1, 2, 3, 4), cycle(5, 0, 1)], [c3], compose, 120),
    ]
    # A diagonal S3 subgroup gives a twisted action, not the Cartesian product
    # action above. Its sign maps to the unique involution of C4.
    def prod_multiply(a, b):
        return compose(a[0], b[0]), (a[1] + b[1]) % 4
    actions.append(coset_action(
        "A5_times_C4_on_diagonal_S3", (identity5, 0),
        [(g, 0) for g in a5] + [(identity5, 1)], [(c3, 0), (flip, 2)], prod_multiply, 240,
    ))
    identity6 = tuple(range(6))
    actions.append(coset_action(
        "A6_on_cosets_C3_times_C3", identity6,
        [cycle(6, 0, 1, 2, 3, 4), cycle(6, 3, 4, 5)],
        [cycle(6, 0, 1, 2), cycle(6, 3, 4, 5)], compose, 360,
    ))
    def matrix_multiply(a, b):
        return ((a[0] * b[0] + a[1] * b[2]) % 5,
                (a[0] * b[1] + a[1] * b[3]) % 5,
                (a[2] * b[0] + a[3] * b[2]) % 5,
                (a[2] * b[1] + a[3] * b[3]) % 5)
    actions.append(coset_action(
        "SL2_5_on_cosets_C3", (1, 0, 0, 1),
        [(1, 1, 0, 1), (0, 4, 1, 0)], [(0, 4, 1, 4)], matrix_multiply, 120,
    ))
    # Symplectic transvections on the 40 projective points of F_3^4.
    def normalize(vector):
        lead = next(value for value in vector if value)
        return tuple(value * lead % 3 for value in vector)
    points = sorted({normalize(v) for v in itertools.product(range(3), repeat=4) if any(v)})
    index = {point: i for i, point in enumerate(points)}
    generators = []
    for v in points:
        generator = []
        for x in points:
            form = (x[0] * v[2] + x[1] * v[3] - x[2] * v[0] - x[3] * v[1]) % 3
            generator.append(index[normalize(tuple((a + form * b) % 3 for a, b in zip(x, v)))])
        generators.append(generator)
    actions.append({"name": "PSp4_3_on_projective_points", "n": 40, "generators": generators})
    return actions
