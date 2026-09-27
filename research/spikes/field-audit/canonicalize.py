"""Build canonical claim sets from the two extraction passes.

Rule: a base claim enters the canonical set when both passes have it and
their order sets agree. Records come from pass A (quote granularity is
comparable; pass B's quote is stored for traceability). Bases with order
or direction disagreement, and one-sided bases, go to the per-paper
adjudication queue — they are NOT tested until adjudicated.

Output: canonical/<name>.json + adjudication/<name>.json (only when needed)
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from reconcile import parse_claim, norm_order, norm_dir, fn
SAMPLE = json.load(open(f'{ROOT}/sample100.json'))['sample']
TH = {'theorem','proposition','corollary','lemma'}
os.makedirs(f'{ROOT}/canonical', exist_ok=True)
os.makedirs(f'{ROOT}/adjudication', exist_ok=True)

summary = []
for s in SAMPLE:
    name = fn(s['key'])
    pa, pb = f'{ROOT}/extraction/pass-a/{name}', f'{ROOT}/extraction/pass-b/{name}'
    if not (os.path.exists(pa) and os.path.exists(pb)):
        continue
    a = json.load(open(pa)); b = json.load(open(pb))
    def bmap(arr):
        m = {}
        for r in arr:
            base,_,kind = parse_claim(r.get('claim',''))
            m.setdefault(base, []).append(r)
        return m
    am, bm = bmap(a), bmap(b)
    canon, queue = [], []
    for base in sorted(set(am) | set(bm)):
        ra, rb = am.get(base), bm.get(base)
        if ra is None or rb is None:
            queue.append({'claim': base, 'side': 'A' if rb is None else 'B',
                          'records': ra or rb}); continue
        ao = {norm_order(r.get('conclusion',{}).get('order')) for r in ra}
        bo = {norm_order(r.get('conclusion',{}).get('order')) for r in rb}
        ad = {norm_dir(r.get('conclusion',{}).get('direction')) for r in ra}
        bd = {norm_dir(r.get('conclusion',{}).get('direction')) for r in rb}
        if ao == bo and ad == bd:
            for r in ra:
                r2 = dict(r); r2['adjudication'] = 'agreed'; canon.append(r2)
        else:
            queue.append({'claim': base, 'a_orders': sorted(ao), 'b_orders': sorted(bo),
                          'a_dirs': sorted(ad), 'b_dirs': sorted(bd),
                          'a_records': ra, 'b_records': rb})
    # non-theorem records (examples/counterexamples): union of both passes,
    # deduped by normalized claim label, tagged with the source pass
    seen = {}
    for tag, arr in (('a', a), ('b', b)):
        for r in arr:
            if r.get('kind') in TH: continue
            k = re.sub(r'\W+','', r.get('claim','').lower())
            if k in seen:
                seen[k]['adjudication'] = seen[k]['adjudication'] + '+b' if tag=='b' else seen[k]['adjudication']
                continue
            r2 = dict(r); r2['adjudication'] = f'example record (pass {tag})'; seen[k] = r2
    canon.extend(seen.values())
    json.dump(canon, open(f'{ROOT}/canonical/{name}','w'), indent=1)
    if queue:
        json.dump(queue, open(f'{ROOT}/adjudication/{name}','w'), indent=1)
    summary.append((s['key'], len(canon), len(queue)))

papers = len(summary)
clean = sum(1 for _,c,q in summary if q == 0)
print(f"{papers} papers canonicalized; {clean} fully agreed, {papers-clean} have adjudication queues")
print("top queues:")
for k,c,q in sorted(summary, key=lambda t:-t[2])[:15]:
    print(f"  {q:3d}  {k}")
