# Preserve large research files in less space

Use this procedure when completed research evidence occupies substantial disk space and disposable output cleanup is insufficient. It preserves the exact file content through a lossless archive. It does not apply to active outputs, agent/session history, application databases, credentials, or backups. Keep original run records and scientific status unchanged.

## Establish that the file can be archived

Confirm the producing run is terminal from its retained records and current process state. Inspect the exact source path, file identity, size, mode, timestamps, links and relevant extended metadata. Reject unexpected symlinks, hardlinks, path changes or uncertain ownership. Recheck open readers and writers; one empty process snapshot is insufficient.

Find tools and manifests that consume the raw filename. An archive does not satisfy a reader that expects the uncompressed path. Preserve historical references and place a recovery record beside the evidence, explaining that those readers require restoration first. If an active or pending operation needs the raw file, leave it in place. Do not rerun an experiment to recover a file.

Record an exact-target plan privately: source and destination identities, compressor and format, maximum temporary growth, time and resource limits, required free reserve, recovery method, and the current allowance covering storage maintenance. Use installed, supported tools; an unavailable tool is not permission to install or spend. Use the host's actual scheduler where required.

## Create and verify one archive at a time

Create an exclusive staging file on the destination filesystem while retaining the original. Bound output size, runtime and concurrency, monitor free space, and stop owned child processes cleanly on cancellation or failure. Admission must allow for peak temporary growth and the reserve required by the concurrent work. Record intent before writing. Keep partial files identifiable; reconcile any interrupted attempt before retrying.

Fully decode the staged archive and compare every byte directly with the original through both end-of-file checks. Require successful decoder completion as well: a decoder can emit every expected byte before reporting a corrupt checksum or trailer. Record independent original and decoded hashes, compressed-file hash, and both byte lengths. Bound decoding time and output length. A compressed checksum, a successful compressor exit, a sampled comparison, or a matching filename is insufficient. Confirm the original and archive identities did not change during these reads. Streaming the comparison avoids allocating another full uncompressed copy.

Promote the verified archive without overwriting an existing destination. Flush its content and directory updates. Durably save a private sidecar containing the verification results, original metadata, archive identity, format/tool version, original run reference and restoration instructions. Preserve the original's recorded scientific hash and status; storage verification does not check a proof or turn a partial attempt into a completed result.

Before removing the uncompressed file, revalidate its identity and absence of consumers, verify the promoted archive matches the verified bytes, and confirm the sidecar and recovery instructions exist durably. Remove only that exact original. Log promotion and removal separately so a crash cannot be mistaken for completion. Leave every original intact when preservation is uncertain. Do not sweep neighboring files or discard a partial archive without reconciling its recorded ownership and state.

Take settled free-space readings after releasing the allocation. Report physical gain separately from logical size savings, since other tasks and filesystem snapshots can change the volume concurrently. Stop reclaiming when the pending operation has enough headroom; preserve recoverable evidence even when a batch fails.

## Restore before using a raw-file consumer

Check the archive's recorded hash and reserve enough space for the full decoded length plus the operation's headroom. Decode into a new exclusive temporary file, keeping the archive. Require successful decoder completion and verify the entire output length and hash before promoting it to the original path without overwriting an existing file. A decoder error or interruption leaves the archive and identifiable partial output for reconciliation. Restore the applicable recorded file metadata; record any platform-specific metadata that cannot be reproduced rather than silently claiming an identical filesystem object.

Keep the archive and recovery record until the raw-path consumer has completed. Confirm the intended consumer accepts the restored file, under its own remaining allowance, before claiming that workflow has been recovered. Byte preservation alone establishes no mathematical result. Move the archive, sidecar, recovery notes and original run records together on a machine handoff. Cleanup does not renew the campaign's research or provider budget.
