#!/usr/bin/env python3
"""make_tables.py -- render the result files under out/ as Markdown tables for memo.md."""
import glob, os, re, ast, math
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'out')
def kv(line):
    return {k: v for k, v in re.findall(r'(\w+)=([-\d.]+)', line)}
print("#### Full-grid census (`count5 grid n`): degenerate 5-subsets of `[n]^3` by type\n")
print("| n | 5-subsets | in an axis plane | other coplanar | cospherical (not coplanar) | ...of which contain a concyclic quadruple | total degenerate |")
print("|---|---|---|---|---|---|---|")
rows = []
for f in ('grid-census-3-4.txt', 'grid-census-5-7.txt'):
    for line in open(os.path.join(OUT, f)):
        if line.startswith('points='):
            d = kv(line); N = int(d['points']); n = round(N ** (1/3))
            rows.append((n, N, d))
for n, N, d in sorted(rows):
    tot = math.comb(N, 5)
    print(f"| {n} | {tot} | {d['axis']} | {d['plane']} | {d['sphere']} | {d.get('sphere_with_concyclic4', 'n/a')} | {d['degenerate']} |")
print("\n#### Random plane-4-regular sets (`rand4reg.py`, `count5 file`): degenerate 5-subsets\n")
print("| n | seed | coplanar (non-axis) | cospherical | ...with concyclic quadruple | total | cospherical / n |")
print("|---|---|---|---|---|---|---|")
rows = []
for f in ('r4-census-8-32.txt', 'r4-census-48-128.txt'):
    for line in open(os.path.join(OUT, f)):
        if 'points=' in line and 'degenerate=' in line:
            d = kv(line); rows.append((int(d['n']), int(d['s']), d))
for n, s, d in sorted(rows):
    print(f"| {n} | {s} | {d['plane']} | {d['sphere']} | {d.get('sphere_with_concyclic4', 'n/a')} | {d['degenerate']} | {int(d['sphere'])/n:.0f} |")
print("\n#### Monte Carlo `E(n)` (`mc_extra n samples 7`): further grid points on the circumsphere of four random grid points (exact arithmetic per sample)\n")
print("| n | samples | E(n) | n·E(n) | n²·E(n) | P(≥1 further point) | 8.53·n²·E(n) (predicted cospherical 5-subsets of a random 4n-set) |")
print("|---|---|---|---|---|---|---|")
for line in open(os.path.join(OUT, 'mc_extra.txt')):
    if line.startswith('n='):
        d = kv(line); n = int(d['n']); e = float(d['mean_extra'])
        p = re.search(r'P\(extra>=1\)=([\d.]+)', line).group(1)
        print(f"| {n} | {d['samples']} | {e:.4f} | {n*e:.1f} | {n*n*e:.0f} | {p} | {8.533*n*n*e:.0f} |")
print("\n#### Window maxima `W(k,n)` (`window_max.py n k 900`)\n")
print("| k | n | W(k,n) | proved optimal | rounds | 5-clauses | 4-clauses | seconds |")
print("|---|---|---|---|---|---|---|---|")
for line in open(os.path.join(OUT, 'windows.txt')):
    if line.startswith('{'):
        d = ast.literal_eval(line.strip())
        print(f"| {d['k']} | {d['n']} | {d['W']} | {'yes' if d['proved_optimal'] else 'NO (time limit)'} | {d['rounds']} | {d['clauses5']} | {d['clauses4']} | {d['secs']} |")
print("\n#### Spheres with at least five grid points (`spheres n 5`) and certified LP values (`lp_bound.py`)\n")
print("| n | spheres with ≥5 points | max points on one sphere | n² | LP constraints | GLOP primal | certified dual bound | ⌊bound⌋ | 4n |")
print("|---|---|---|---|---|---|---|---|---|")
for n in (3, 4, 5, 6):
    sf = os.path.join(OUT, f'spheres-n{n}.txt'); lf = os.path.join(OUT, f'lp-n{n}.txt')
    if not os.path.exists(sf) or os.path.getsize(sf) == 0: continue
    cnt = 0; mx = 0
    for line in open(sf):
        m = int(line.split()[0]); cnt += 1; mx = max(mx, m)
    lp = open(lf).read() if os.path.exists(lf) else ''
    m1 = re.search(r'constraints=(\d+)', lp); m2 = re.search(r'primal value = ([\d.]+); certified dual bound = (\S+) ~ ([\d.]+); so C\(\d+\) <= (\d+)', lp)
    if m2:
        print(f"| {n} | {cnt} | {mx} | {n*n} | {m1.group(1)} | {m2.group(1)} | {m2.group(2)} | {m2.group(4)} | {4*n} |")
    else:
        print(f"| {n} | {cnt} | {mx} | {n*n} | not solved (see out/lp-n{n}.txt) | | | | {4*n} |")
