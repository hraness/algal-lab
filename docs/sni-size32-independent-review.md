# Independent review: SNI size-aware train-only intake (2026-10-13)

**Selection arithmetic confirmed; NO-GO for task-blob fetch or delivery.** This review closes the missing independent reconstruction of the *metadata-only selection*, not the later execution/rights gate. Reviewed `AGENTS.md`, `docs/roadmap.md`, `docs/sni-size32-freeze.md`, the older SNI freeze/receipt/review, the local size manifest/plan/selection, the old per-attempt ledger, and SNI source/tests. No task JSON, test body, score, model call, paid runner request, commit, PR or delivery operation was made here. Private `runs/` records stay ignored.

## Separate findings

- **Correctness:** Fresh HTTPS requests fetched only the pinned Git tree metadata and three split-name lists (no `tasks/*.json`). The tree API bytes match SHA-256 `3fe32279…`; root tree `cc84a807…`, `truncated: false`; 1,613 unique task paths with valid sizes (1,609 mode `100644`, four `100755`). The split lists independently rebuild the existing 1,613-row index byte-for-byte (`2e54d1a3…`), the size manifest (`951646cf…`), and test-*name* digest (`5f65a29a…`). The previous first-64 selection (`97cb7f38…`) has 64 distinct attempt records with exactly 12 closed sidecars and 52 terminal failure files (46 oversized, six invalid JSON); neither failure nor name is eligible again. Exactly 351 unattempted train rows meet the **metadata** size cap. The bytewise first 32 reproduce both TSV bytes and SHA-256 `6ea37fc2bff821ed5cbd5f10352c98b451442f29ee5dbf6bc2029c340c069388`; their metadata sizes sum to 4,016,222 bytes. The new private directory contains only the three pre-access files; zero new attempts/charges are **locally reported**, not independently verified against upstream access logs or a billing ledger. Git API `size` is not authenticated by the tree OID; a body must have a separate size and Git-blob-OID check before parsing. Old failure files omit observed byte counts, so they cannot prove exact old transport bytes. An offline ledger cannot prove pre-access chronology or historical absence of other access.
- **Novelty / claim-to-source:** Re-fetched and SHA-256-verified pinned upstream `README.md` (`bd5c0768…`) and `splits/README.md` (`db3737ce…`) without task bodies. The former exempts task *instances* from the task-definition Apache-2.0 grant; the latter already describes train/test/excluded roles and shared-source exclusions. This size-based selection is an intake filter on an existing split, **not** a new selective-memory result, independent-source proof or priority claim. Primary comparisons for any later memory algorithm remain absent.
- **Practical value:** The reproducible pre-access filter avoids reattempting the prior 64 and bounds possible development ingestion. A name/size list cannot show 16 independent, instance-use-permitted groups; multiple country/food and other similarly named tasks cannot be counted as distinct families without original terms and alias analysis. Public test names are used only to quarantine risks; no fresh holdout, accuracy result, model-pretraining isolation, six-arm numerical protocol or consumer advantage follows. CLINC150's development-only TF-IDF result is not comparable to these metadata counts.

**Gate decision / bounded repair:** This review file supplies the formerly missing independent selection audit, but **does not authorize a selected blob fetch**. There is no size32-specific fetcher or tests in the reviewed tree. The older `scripts/sni-train64.ts` hardcodes the already-consumed first 64 and does not enforce this run's aggregate response-byte cap, per-attempt observed-byte records, or stop-on-uncertain-terminal-write rule; reusing it would violate the freeze. Before any access, implement and independently review a new fail-closed executor bound to the frozen TSV and plan with 32 exclusive attempt slots, redirect/timeout/per-body/aggregate-byte limits, Git OID verification before parse, closed sidecars, and terminal records; deliberately fault-test interruption and writes. No retry/adaptive fill. Only after **separate** original instance-rights/source-family/alias review could >=16 development groups be considered. If fewer survive, stop with a negative intake. A source-disjoint untouched evaluation pool, cost/quality protocol and primary-method source comparison remain separate dependencies.

## Validation on the current dirty worktree

`bun test src/foundation/sni-intake.test.ts src/foundation/sni-train64.test.ts`: **42 pass, 0 fail** (seven root tests plus copies under ignored `runs/`; there is no size32 executor test). `bun x tsc --noEmit`: pass. `bun run discovery doctor`: ready. `bun run discovery agenda cost-aware-research-memory`: proposed. `bun run foundation doctor`: core ready. Metadata-only Python reconstruction below: pass. `git diff --check` and an explicit whitespace/LF check on the untracked freeze: pass (Git does not include untracked docs in its diff). `bun run check`: typecheck passed, test `src/required-runner.test.ts` timed out at its 30-second limit; the host stopped the aggregate at **600,000 ms** without a final suite result. It is **unresolved/red**, not a pass or an authorized waiver. A subsequent `git status --short` still showed the same unrelated tracked host-comparison modifications plus untracked overlays; no source files were changed by this review. No PR-head `Required` check exists for this work.

### Exact metadata-only reconstruction command

Run from the repository root; only the pinned tree metadata and split-name text are requested. The command makes no filesystem writes:

```sh
python3 -c 'import collections,hashlib,json,pathlib,urllib.request
H=lambda b:hashlib.sha256(b).hexdigest()
root=pathlib.Path("runs"); old=root/"sni-train64-20261011-01"; fresh=root/"sni-size32-20261013-01"
p=json.loads((fresh/"plan.json").read_text()); q=json.loads((old/"report.json").read_text()); oldplan=json.loads((old/"plan.json").read_text())
base="https://raw.githubusercontent.com/allenai/natural-instructions/55a365637381ce7f3748fa2eac7aef1a113bbb82/splits/default/"
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs): raise RuntimeError("redirect forbidden")
opener=urllib.request.build_opener(NoRedirect)
def get(url,limit):
 with opener.open(urllib.request.Request(url,headers={"User-Agent":"algal-independent-metadata-audit","Accept":"application/vnd.github+json"}),timeout=30) as r:
  b=r.read(limit+1); assert len(b)<=limit and r.status==200
  return b
splits={name:get(base+name+"_tasks.txt",100000) for name in ("train","test","excluded")}
assert tuple(map(lambda s:len(splits[s].decode("utf8").splitlines()),("train","test","excluded")))==(756,119,738)
assert H(("\n".join(sorted(splits["test"].decode().splitlines()))+"\n").encode())==p["testNamesSha256"]
treebytes=get("https://api.github.com/repos/allenai/natural-instructions/git/trees/"+p["treeOid"]+"?recursive=1",2000000)
tree=json.loads(treebytes); assert tree["sha"]==p["treeOid"] and tree["truncated"] is False
blobs={}
for item in tree["tree"]:
 path=item["path"]
 if path.startswith("tasks/") and path.endswith(".json"):
  name=path[6:-5]
  assert name not in blobs and item["type"]=="blob" and item["mode"] in ("100644","100755") and isinstance(item["size"],int) and not isinstance(item["size"],bool) and item["size"]>=0
  blobs[name]=(item["sha"],item["size"])
assert len(blobs)==1613
rows=[]; seen=set()
for split in ("train","test","excluded"):
 for task in splits[split].decode("utf8").splitlines():
  assert task not in seen and task in blobs; seen.add(task)
  oid,size=blobs[task]; rows.append((split,task,oid,size))
assert seen==set(blobs)
idx="".join("\t".join(row[:3])+"\n" for row in rows).encode(); sizes="".join("\t".join(map(str,row))+"\n" for row in rows).encode()
assert idx==(root/"sni-index-20261008-01/task-blob-oids.tsv").read_bytes() and H(idx)==p["indexSha256"]
assert sizes==(fresh/"all-task-sizes.tsv").read_bytes() and H(sizes)==p["allTaskSizesTsvSha256"]
first=sorted((r for r in rows if r[0]=="train"),key=lambda r:r[1].encode())[:64]
oldsel="".join("\t".join(r[:3])+"\n" for r in first).encode()
assert oldsel==(old/"selection.tsv").read_bytes() and H(oldsel)==p["previousSelectionSha256"]
fail=collections.Counter(); side=0
for n,(split,task,oid,size) in enumerate(first,1):
 stem=f"{n:02d}"; a=json.loads((old/(stem+".attempt.json")).read_text()); assert a=={"task":task,"blobOid":oid,"status":"started"}
 f=old/(stem+".failure.json"); s=old/(stem+".sidecar.json"); assert f.exists()!=s.exists()
 x=json.loads((f if f.exists() else s).read_text()); assert x["task"]==task and x["blobOid"]==oid
 if f.exists(): assert set(x)=={"task","blobOid","code","disposition"}; fail[x["code"]]+=1
 else: assert set(x)=={"task","blobOid","Source","Categories","Instance License"}; side+=1
assert len(list(old.iterdir()))==131 and side==q["statuses"]["extracted"]==12 and fail=={"blob-too-large":46,"invalid-JSON":6} and sum(fail.values())==q["statuses"]["failed"]==52
assert oldplan["paidUsd"]==q["paidUsd"]==p["paidAllowanceUsd"]==p["chargedUsd"]==0
available=sorted((r for r in rows if r[0]=="train" and r[1] not in {x[1] for x in first} and r[3]<=1000000),key=lambda r:r[1].encode()); sample=available[:32]
sel="".join("\t".join(map(str,r))+"\n" for r in sample).encode()
assert len(available)==p["eligibleUnattemptedCount"]==351 and len(sample)==p["selectionCount"]==32 and sum(r[3] for r in sample)==p["selectedGitTreeSizeSumBytes"]==4016222
assert sel==(fresh/"selection.tsv").read_bytes() and H(sel)==p["selectionSha256"] and len(list(fresh.iterdir()))==3
assert p["attemptsStarted"]==p["resultsExtracted"]==p["failures"]==p["unresolved"]==p["maxModelCalls"]==0
print("PASS fresh tree+split metadata; tree response SHA256",H(treebytes),"expected",p["treeApiResponseSha256"],"modes",dict(collections.Counter(item["mode"] for item in tree["tree"] if item["path"].startswith("tasks/") and item["path"].endswith(".json"))))
print("PASS index",H(idx),"manifest",H(sizes),"previous 64: 12 sidecars,",dict(fail),"new eligible",len(available),"new selection",H(sel),"size sum",sum(r[3] for r in sample),"no new attempts (local files); $0 reported")'
```

Outputs: tree API SHA-256 `3fe32279…` with modes `{'100644': 1609, '100755': 4}`; index `2e54d1a3…`; manifest `951646cf…`; old 64 outcomes `12 / 46 / 6`; 351 eligible; new 32-row SHA-256 `6ea37fc2…`; metadata size sum 4,016,222; $0 **reported**.
