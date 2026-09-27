"""Reconcile extraction pass A and pass B per paper.

Alignment unit: the base claim = (kind, number, part) where number like 3.7
or (1) and part like i/ii/a/b. Each pass may split a claim's conclusions
into several records (one per order) or keep them bundled; we compare the
SET of (normalized order, normalized direction) conclusions per base claim.

Outputs reconciliation/<name>.json per paper + a summary to stdout.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SAMPLE = json.load(open(os.path.join(ROOT, 'sample100.json')))['sample']
def fn(k): return k.replace(':','_').replace('/','_').replace('(','_').replace(')','_') + '.json'

FA = '۰۱۲۳۴۵۶۷۸۹'
def strip_fa(t):  # remove Persian/Arabic text inside parens and elsewhere
    t = re.sub(r'[؀-ۿ]+', '', t)
    return t

def canon(t):
    t = strip_fa(t.lower())
    t = re.sub(r'[()\[\]{}_\s,;:!؟\-]+', ' ', t)
    t = re.sub(r'(?<![0-9])\.|\.(?![0-9])', ' ', t)  # keep dots inside numbers
    return re.sub(r'\s+', ' ', t).strip()

NUM = r'(\d+(?:[.]\d+)?(?:[.]\d+)?|\(\d+\)|\d+:\d+)'
PART = r'(i{1,3}|iv|v|a|b|c|d)(?![a-z])'
ORDER_PAT = r'(st|hr|rh|lr|mrl|disp|star|cx|icx|icv|rs|lorenz|fsd|ageing|whr|rhr|usual stochastic|hazard rate|reversed|likelihood|mean residual|dispersive|convex)'

def parse_claim(label):
    """-> (base_key, order_hint or None)"""
    t = canon(label)
    m = re.search(r'(theorem|proposition|corollary|lemma|example|counterexample|remark|result|statement)\s*' + NUM, t)
    if m:
        kind, num = m.group(1), m.group(2).strip('()')
        rest = t[m.end():]
        pm = re.match(r'\s*' + PART, rest)
        part = pm.group(1) if pm else ''
        # section-level unnumbered fall into 'num' only if numbered
        base = f"{kind}{num}{part}"
    else:
        # unnumbered: use a compact signature of the leading words + section
        sm = re.search(r'section\s*(\d+(?:\.\d+)*)', t)
        sec = sm.group(1) if sm else ''
        head = ' '.join(t.split()[:6])
        base = f"unn{sec}:{head}"
        kind = 'unnumbered'
    om = re.search(ORDER_PAT, t)
    return base, (om.group(1) if om else None), kind

def norm_order(o):
    o = canon(o or '')
    m = {'usualstochastic':'st','stochastic':'st','st':'st','fsd':'st',
         'hazardrate':'hr','hr':'hr','fr':'hr','failurerate':'hr',
         'reversedhazard':'rh','reversedfailure':'rh','rh':'rh','rhr':'rh','rf':'rh',
         'likelihoodratio':'lr','lr':'lr',
         'meanresiduallife':'mrl','mrl':'mrl','dispersive':'disp','disp':'disp',
         'star':'star','convextransform':'star','convex':'cx','cx':'cx',
         'increasingconvex':'icx','icx':'icx','increasingconcave':'icv','icv':'icv',
         'lorenz':'lorenz','rightspread':'rs','rs':'rs','weakhazard':'whr','whr':'whr'}
    for k,v in m.items():
        if k in o: return v
    mm = re.match(r'other (\w+)', o)
    return mm.group(1) if mm else (o or '?')

def norm_dir(d):
    raw = (d or '').strip().lower()
    if not raw: return ''
    d = canon(raw)
    # canonical smaller side: first entity token on the left of the relation
    m = re.search(r'([a-z][a-z0-9*^_\s{}]{0,18}?)\s*(?:<=|<|≤|≼|preceq|\bst\b|\bhr\b|\blr\b|\brh\b|smaller)', raw)
    if not m:
        m2 = re.search(r'([a-z][a-z0-9*^_\s{}]{0,18}?)\s*(?:>=|>|≥|≽|succeq|larger)', raw)
        if m2:
            # the LARGER side is named; the other operand is smaller -> mark as 'other'
            return 'B_smaller'
        return d[:60]
    lhs = m.group(1).strip()
    return 'A_smaller' if not re.search(r'\*|prime|2\b|_2', lhs) else 'B_smaller'

if __name__ == '__main__':
    rows = []
    mismatched_bases = []
    for s in SAMPLE:
        name = fn(s['key'])
        pa = os.path.join(ROOT,'extraction','pass-a',name)
        pb = os.path.join(ROOT,'extraction','pass-b',name)
        if not (os.path.exists(pa) and os.path.exists(pb)):
            rows.append({'position': s['position'], 'key': s['key'],
                         'status': 'missing pass-a' if not os.path.exists(pa) else 'missing pass-b'})
            continue
        a = json.load(open(pa)); b = json.load(open(pb))
        def base_map(arr):
            out = {}
            for r in arr:
                base, ohint, kind = parse_claim(r.get('claim',''))
                out.setdefault(base, []).append(r)
            return out
        am, bm = base_map(a), base_map(b)
        shared = sorted(set(am) & set(bm))
        details = []
        agree = 0
        for k in shared:
            ao = {norm_order(r.get('conclusion',{}).get('order')) for r in am[k]}
            bo = {norm_order(r.get('conclusion',{}).get('order')) for r in bm[k]}
            ad = {norm_dir(r.get('conclusion',{}).get('direction')) for r in am[k]}
            bd = {norm_dir(r.get('conclusion',{}).get('direction')) for r in bm[k]}
            ok = ao == bo and ad == bd
            agree += ok
            if not ok:
                details.append({'claim': k, 'a_orders': sorted(ao), 'b_orders': sorted(bo),
                                'a_dirs': sorted(ad)[:3], 'b_dirs': sorted(bd)[:3]})
                mismatched_bases.append((s['position'], s['key'], k))
        rec = {'position': s['position'], 'key': s['key'],
               'a_records': len(a), 'b_records': len(b),
               'a_bases': len(am), 'b_bases': len(bm), 'matched_bases': len(shared),
               'agree_full': agree,
               'a_only': sorted(set(am)-set(bm)), 'b_only': sorted(set(bm)-set(am)),
               'disagreements': details}
        json.dump(rec, open(os.path.join(ROOT,'reconciliation',name),'w'), indent=1)
        rows.append(rec)

    done = [r for r in rows if 'status' not in r]
    U = sum(r['a_bases']+r['b_bases']-r['matched_bases'] for r in done)
    M = sum(r['matched_bases'] for r in done)
    A = sum(r['agree_full'] for r in done)
    print(f"papers reconciled: {len(done)}/100")
    print(f"base claims: matched {M} of union {U} -> structural agreement {M/U:.3f}")
    print(f"order+direction identical on matched: {A}/{M} = {A/M:.3f}")
    print(f"claims needing adjudication (order/direction diff): {len(mismatched_bases)}")
    for p,k,c in mismatched_bases[:25]: print('  ', p, k, '->', c)
