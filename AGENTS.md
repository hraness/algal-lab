# Algal Lab

Algal Lab hosts bounded, reproducible research applications on ALGAL. Keep the
runtime dependency pinned; laboratory semantics belong here rather than in a
fork of ALGAL.

- Parse external values from `unknown`, reject unknown fields, and bound inputs,
  outputs, iterations, and model calls. Model output is data, never host authority.
- Preserve requested designs, realized designs, predictions, failed attempts,
  observations, parent references, and exact instrument/protocol identities.
- Keep holdout outcomes out of researcher context and selection. Freeze portfolios
  before evaluation. Never claim a scripted baseline demonstrates LLM intelligence.
- Separate receipt verification, fresh numerical reproduction, and scientific
  validity. Signed or hashed evidence alone does not establish empirical truth.
- Run `bun run check` before delivery. Focused tests belong to their implementer;
  the integrator owns the final aggregate check and CI wait.
- Use a feature branch and a pull request after the initial repository bootstrap.
  Merge only after required checks and independent review pass. Do not force-push.
- Keep generated runs, credentials, local paths, and model-provider secrets out of
  Git. Public examples must run without credentials or paid inference.

## Layout

- `src/`: contracts, deterministic instruments, ALGAL integration, research loop,
  artifact verification, and colocated tests.
- `examples/`: bounded public study protocols and executor examples.
- `docs/`: research method, architecture, provenance, and scoped follow-up work.

The initial delivery is a headless network-resilience laboratory. Valhalla
integration, arbitrary generated-code admission, and physics claims are deferred.
