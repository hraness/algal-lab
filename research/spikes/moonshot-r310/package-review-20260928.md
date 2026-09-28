# Independent review of the fixed-remainder certificate package

On 2026-09-28 an independent computational agent reviewed the package
builder, focused controls, public explanation, and portable verifier.
This is computational review, not human peer review. The final source
verdict is approved for archive construction and end-to-end replay.

The finite-family claim includes centre coverage: each of the other
33 vertices must have a neighbour among the centre's six neighbours.
The explanation distinguishes this exclusion from the open Ramsey bound,
from all degree-six cases, and from a complete remainder census.

The builder preserves exact formula, proof, runtime, catalogue, and branch
bytes. Its public projections preserve unsuccessful statuses and original
record digests while omitting private paths and process identifiers. It
retains both the original case-four failure and the separately verified
replay of its unchanged certificate. Member names, file kinds, byte
bounds, the manifest, and local-path leakage receive explicit checks.

The portable verifier independently reconstructs each formula and binds
both formula and proof hashes to the package result. Each proof must pass
Python RUP replay and the supplied `lrat-trim` executable. The executable's
version is checked and its digest is recorded and checked on every replay.
Catalogue maps, saved branch trees, and the independent cover computation
are also replayed. Failure or interruption leaves an incomplete result.

Review identified that supervising a compiler driver as one direct child
would not establish custody of its subprocesses. The final code removes
compilation from the verifier. It requires an explicit `--lrat-trim`
executable; building the pinned source is documented as a separate
operation under the host's native-build controls. The actual verification
payloads remain direct Python or checker processes.

The implementation worker retained and the reviewer inspected the initial
admission and subsequent repair-control evidence in
`runs/moonshot-r310/fixed-remainder-package-admission-20260928/`:

```sh
python3 -B -m unittest discover -s research/spikes/moonshot-r310/fixed_remainder -p 'test_package.py' -v
python3 -B research/spikes/moonshot-r310/fixed_remainder/package.py build runs/moonshot-r310 runs/moonshot-r310/third-party/lrat-trim runs/moonshot-r310/packaged-fixed/r310-fixed-remainder-proof-20260928.tar.gz --check-only
```

The initial five focused tests passed in 0.010 seconds. Admission passed for 116
members totalling 126,351,234 uncompressed bytes, with manifest SHA-256
`31d97b48b675056250471139a4b7276e0cfa222e7deed38cf3bc28206ebf9a1a`.
The retained control log SHA-256 is
`b6cff1d9580e486284fe71969594a7d52ce12b0707238b093aa6adc0405c5e9a`;
the preflight result SHA-256 is
`498fd6d879103f364b3488a80b3f85dff9e3ac88e2c6e3cf2665d94e9d54a723`.
The unchanged controls were not duplicated by the reviewer.

The first supervised build then exposed an inherited-limit incompatibility:
the build command attempted to raise the supervisor's file-size hard cap.
The failed stage remains recorded, and it produced no archive. The repaired
`apply_build_limits()` takes the minimum of each inherited and requested
CPU and file-size soft/hard limit, treating infinity explicitly. It is
called only by the build command; proof workers were not affected by the
original issue. The new regression invokes that actual helper in a
collected direct child under CPU limits of `(3,3)` seconds and file-size
limits of `(1 MiB,1 MiB)`, with a five-second timeout. Both inherited
limits remain unchanged.

All six package controls passed after the repair in 0.075 seconds. Their
retained `focused-controls-r2.log` has SHA-256
`7a8323ba1856b6449e0fd3e53759ec447b47fbb31fd0e4af65576b48c5212154`.
Independent review also reversed the exact helper and regression additions
in memory and reproduced both previously reviewed source digests. No other
source changes were hidden in this repair.

Final reviewed identities, relative to `fixed_remainder/`:

```text
package.py 13922295dfa92f87852e6b4347b0e7cbdef765cf45b2e0d27e15462248fb39f2
README.md 97c303fff7bc6c24a7e54bfe00e65932e4454192b56ba777fe83c299b4541a52
test_package.py 40aa133f030b58bb7f23381ed08bb1733e98edaaede4e30d1b28f5698e94a85f
```

Every earlier runtime and dependency identity listed in
`fixed_remainder/REVIEW.md` was rechecked and remains unchanged. This note
is outside the frozen bundle inputs. The two linked proposal documents
were also read and their current mathematical scope, bounds and explicit
distinction between proposals and executed work checked. Their identities,
relative to this note's directory, are:

```text
degree_six/ANALYTIC-NEXT.md b43f31b32924fbd98434d63ec9f2c19043d8f6e941f0f8222f79f59423025d89
degree_six/NEXT-PROFILE.md 7c37e7b1e75da169716ce6e5f1b4271af7003892f7ea5bf4d225ed95dcf2124a
```

Archive construction, full portable replay, and release have their own
subsequent receipts. This source review does not replace those final gates.
