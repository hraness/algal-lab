# Security

Algal Lab accepts bounded experiment data and evaluates it with a fixed graph
simulator. Model output, messages, parent references, and imported artifacts are
untrusted data. A valid hash or receipt does not grant execution permission or
prove a scientific claim.

## Boundaries

- Lab parsers validate values from `unknown`, reject unknown fields, and enforce
  graph, text, reference, iteration, and evaluation bounds. Do not rely on a
  model's compliance or a schema description alone.
- Researcher output is limited to depth 16 and 8,192 canonical JSON bytes before
  it enters an ALGAL receipt. Structural rejection records a bounded error;
  output admitted at that boundary remains inspectable if later proposal
  validation fails.
- The simulator is an admitted local tool. Proposals cannot install tools,
  supply executable code, change the evaluator, or choose host commands.
- Offline verification reconstructs ALGAL runs from recorded agent effects,
  executes the admitted simulator afresh, and compares the complete receipts,
  context, artifacts, and report. It does not invoke the original executor or
  require provider credentials. Hashes provide integrity, not authenticated
  authorship, trusted timestamps, or protection against wholesale replacement of
  a self-consistent archive.
- Holdout isolation separates discovery from evaluation within the workflow.
  It is not encryption or a defense against an operator who controls the host.

`--executor-command` is an explicit host-code boundary. ALGAL runs the supplied
operator command through a shell. Timeouts and output limits do not make that
command an operating-system sandbox. Use a reviewed wrapper with appropriate
filesystem, network, and provider permissions. Never construct its command from
a proposal, message, or artifact. The first version performs no arbitrary
generated-code admission.

The wrapper must be stateless across calls. Each invocation receives one bounded
request and must derive its proposal from that request alone. A wrapper that
keeps memory between calls (a cache, a running conversation, a scratch file, or
provider-side session state) leaks information across information-sharing
conditions and across researchers within a round's fixed snapshot. The lab
receives only the wrapper's output and cannot detect that leak; the recorded
receipts would still verify.

The wrapper owns credentials. Keep secrets out of command arguments, protocol
files, prompts, responses, and error text that may become retained evidence.
Model requests and outputs are research records; inspect a run before sharing
it. Generated runs are ignored by Git, but that is not encryption or a guarantee
against accidental publication.

The application creates a fresh output directory and has no resume or archive
repair command. Preserve a failed or questionable run for inspection. Do not
silently reset it, overwrite evidence, or infer a completed study from a partial
report.

## Reporting

The optional XCB adapter accepts only a separately qualified application route
with no tools or hooks and ephemeral requests. It binds the installed executable
and repeats admission before each call. It never uses an unqualified account,
refreshes credentials, or substitutes a coding-agent command. Its provider
transport sidecar is supplementary evidence outside offline study verification.
See [live executor qualification](docs/live-executor.md).

Report suspected boundary crossings, unbounded work, command injection, or
verification bypass privately. Use the repository's Security tab if GitHub
private vulnerability reporting is enabled. Otherwise contact a repository
maintainer privately before sending reproduction details; the
[Hraness organization](https://github.com/hraness) identifies the project owner.
Do not disclose an unpatched exploit in a public issue.

Include the smallest reproducing protocol or artifact, the Algal Lab revision,
Bun version, command, and observed versus expected behavior. Remove credentials
and personal data before sending evidence. Reports about scientific model
limitations without a security impact belong in an ordinary issue, with the
model and measurement assumptions stated explicitly.
