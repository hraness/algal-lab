"""Aggregate eval_*.result.json into the running audit tally.

Distinguishes: claims tested (status holds/refuted), unsupported orders,
out-of-scope claims, ambiguous hypotheses. Pilot papers counted separately.
"""
import json, glob, os, collections
ROOT = os.path.dirname(os.path.abspath(__file__))
PILOT = {'arxiv_2103.00763','arxiv_2601.07249','arxiv_2407.18801','doi_10.4064_am39-2-1',
         'doi_10.2991_jsta.2018.17.3.8','doi_10.21136_am.2018.0105-17','doi_10.7153_mia-2020-23-03',
         'doi_10.1017_s0269964826100199','arxiv_1612.00571','arxiv_1704.06329'}
DUP_PAIRS = {frozenset(('arxiv_1612.00571','doi_10.1080_02331888.2020.1722670')),
             frozenset(('doi_10.2991_jsta.2018.17.3.8','arxiv_1704.03656'))}

rows = []
tot = collections.Counter()
for f in sorted(glob.glob(os.path.join(ROOT,'harness','eval_*.result.json'))):
    paper = os.path.basename(f)[5:-12]
    arr = json.load(open(f))
    c = collections.Counter(r.get('status','?') for r in arr)
    ref = [r for r in arr if r.get('status')=='refuted']
    rows.append((paper, len(arr), dict(c), bool(ref)))
    tot.update(c)
    tot['papers'] += 1
    tot['papers_with_refutation'] += bool(ref)

print(f"papers evaluated: {tot['papers']}  ({tot['papers_with_refutation']} with >=1 refutation)")
for s,c in tot.most_common():
    if s not in ('papers','papers_with_refutation'): print(f"  {s}: {c}")
print()
for p,n,c,ref in rows:
    if ref: print(f"  {p}: {c}")
