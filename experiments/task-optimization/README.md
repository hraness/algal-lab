# Task optimization comparison

This study compares a fixed task, labeled examples, a predefined prompt grid,
and feedback-based revision on the same decision: whether a disclosed Butler
assistant should respond to a message. It uses 28 public, handwritten cases
inspired by Textbutler's response policy. It imports no conversations and sends
no messages.

From the repository root, run the credential-free workflow check:

```sh
bun experiments/task-optimization/run.ts --out runs/task-scripted --seeds 11,23,37
bun experiments/task-optimization/inspect.ts runs/task-scripted 11
```

The scripted executor checks the workflow. It does not measure a model's quality.
Each run needs a new output directory. Keep that directory: it contains the
declared protocol, every arm's report and selected task, ALGAL execution records,
provider observations, and a completion summary. Failed runs keep partial results.

Live runs require one explicit seed per invocation so the complete four-arm campaign
fits within the call limit. For a live run, supply `AI_GATEWAY_API_KEY` or `VERCEL_OIDC_TOKEN` through the
environment and request live mode explicitly:

```sh
bun experiments/task-optimization/run.ts --out runs/task-live --seeds 11 \
  --live --max-calls 260 --max-usd 1
bun experiments/task-optimization/inspect.ts runs/task-live 11
```

The adapter uses Vercel AI Gateway's `openai/gpt-6-luna` through the OpenAI
provider only, with provider-default temperature (the parameter is omitted), reasoning disabled, and at most 1,024 output
tokens per request. It has no fallback or automatic retry. An uncertain transport
result stops further dispatch. Request bytes, response bytes, calls, and estimated
spend all have limits. Token prices come from the dated Gateway catalog record
in `live.ts`; the estimate does not reconcile the provider's invoice.

## Method

The corpus has eight training, eight validation, and 12 audit cases. Source groups
and message text cannot cross splits. The task model receives only a message;
the reviser receives training evidence and the declared task. Labels for validation
and audit cases never enter revision feedback or demonstrations.

Seeds reorder the training examples. They do not set the provider's sampling seed
or create additional audit cases. All arms share the same task schema, model,
per-call limits, and maximum campaign allowance. They can consume different
amounts of that allowance.

- **Fixed:** evaluate the original instructions.
- **Labeled:** also evaluate up to four training demonstrations.
- **Prompt grid:** evaluate three predefined task variants through ALGAL's
  existing foundry. This is a prompt grid, not generative search.
- **Feedback:** evaluate the fixed and labeled tasks, then allow one guarded
  revision informed by concrete training results.

Validation chooses the program before audit evaluation. The optimizer's final
foundry pass reruns that program's training and validation cases, so those calls
also count toward cost. Scores include invalid outputs in their denominator and
report invalid outputs and unwanted responses separately.

`inspect.ts` reruns the complete optimization workflow using the saved effects,
without contacting a model. It compares the selected program, candidate reports,
cost accounting, and scores exactly; elapsed time is excluded. This checks recorded
execution. It does not authenticate the provider or establish that the labels
represent production users.

See [the live findings](FINDINGS.md) and the separate retained-knowledge experiment
in [RETENTION.md](RETENTION.md).
