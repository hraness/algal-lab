"""Aggregate eval_*.result.json + c3_report_*.json into the audit tally.

Distinct-paper counting: the two same-paper pairs (amendment 5) merge into
single papers for headline rates. Evidence-kind records (example/counterexample)
are tracked separately from theorem-level claims.
"""
import json, glob, os, collections, re

ROOT = os.path.dirname(os.path.abspath(__file__))
PAIR_A = {'arxiv_1612.00571', 'doi_10.1080_02331888.2020.1722670'}   # PO paper
PAIR_B = {'doi_10.2991_jsta.2018.17.3.8', 'arxiv_1704.03656'}        # thinned-Weibull
PILOT = {'arxiv_2103.00763','arxiv_2601.07249','arxiv_2407.18801','doi_10.4064_am39-2-1',
         'doi_10.2991_jsta.2018.17.3.8','doi_10.21136_am.2018.0105-17','doi_10.7153_mia-2020-23-03',
         'doi_10.1017_s0269964826100199','arxiv_1612.00571','arxiv_1704.06329'}
EVIDENCE_KINDS = {'example','counterexample','remark','application'}

def canonical_paper(name):
    if name in PAIR_A: return 'PO-paper(1612.00571)'
    if name in PAIR_B: return 'thinned-Weibull(jsta/1704.03656)'
    return name

def load_results():
    out = {}   # canonical_paper -> list of records (with _paper field)
    for f in sorted(glob.glob(os.path.join(ROOT,'harness','eval_*.result.json'))):
        p = f.split('eval_')[1][:-12]
        for r in json.load(open(f)):
            r = dict(r); r['_paper'] = p
            out.setdefault(canonical_paper(p), []).append(r)
    return out

def load_c3():
    """c3_report_<name>.json -> {paper: {claim: classification}}"""
    cov = collections.defaultdict(dict)
    for f in glob.glob(os.path.join(ROOT,'harness','c3_report_*.json')):
        try:
            doc = json.load(open(f))
            items = doc.get('claims') if isinstance(doc, dict) else doc
            pname = os.path.basename(f)[10:-5]
            for item in items or []:
                cl = item.get('classification') or item.get('verdict') or ''
                cov[item.get('paper') or pname][item.get('claim','')] = cl
        except Exception:
            pass
    return cov

def main():
    results = load_results(); c3 = load_c3()
    tot = collections.Counter()
    per_paper = {}
    for p, recs in results.items():
        c = collections.Counter(r.get('status','?') for r in recs)
        th = [r for r in recs if (r.get('_kind') or '') not in EVIDENCE_KINDS]
        per_paper[p] = dict(c)
        tot.update(c)
    papers = len(results)
    print(f'distinct papers: {papers}')
    for s,c in tot.most_common(): print(f'  {s}: {c}')
    # refuted tally (records, then theorem-level-only)
    def th_level(r):
        cl = r.get('claim','').lower()
        return not any(k in cl for k in ('example','counterexample','figure','remark'))
    ref_recs = [(p,r) for p,rs in results.items() for r in rs if r.get('status')=='refuted']
    ref_th = [(p,r) for p,r in ref_recs if th_level(r)]
    p_ref = {p for p,_ in ref_recs}; p_ref_th = {p for p,_ in ref_th}
    print(f'\nrefuted records: {len(ref_recs)} ({len(ref_th)} theorem-level)')
    print(f'papers with any refutation: {len(p_ref)}; theorem-level: {len(p_ref_th)}')
    print(f'P1 incl. pilot: {len(p_ref_th)}/{papers}')
    nonpilot = {p for p in p_ref_th if p not in {canonical_paper(x) for x in PILOT}}
    np_papers = papers - len({canonical_paper(x) for x in PILOT})
    print(f'P1 excl. pilot: {len(nonpilot)}/{np_papers}')
    print(f'\nc3 reports on file: {len(c3)} papers')

if __name__ == '__main__':
    main()
