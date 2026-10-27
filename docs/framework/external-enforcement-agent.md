# External Enforcement Integration - Design Note

No external filesystem watcher or operating-system enforcement agent is shipped
with this framework. This note describes integration considerations, not an
implemented security boundary or a stable cross-version watcher specification.
The previous regex-based watcher contract is retired.

## Reuse Current Policy and Commands

A future integration should call the framework CLI from the host project root
rather than maintain its own Markdown approval regex or accept any approved
change in the repository:

```bash
python sdlc/scripts/sdlc.py check --json
python sdlc/scripts/sdlc.py gate implementation
python sdlc/scripts/sdlc.py check --ready-to-finalize --json
```

Use `python scripts/sdlc.py ...` in root-template mode. The gate command returns
zero when allowed and nonzero when blocked. Select the actual project profile
and change class through project configuration/state; do not pass weaker CLI
overrides to bypass the selected policy.

Current policy includes canonical approval fields, Active Change selection,
blocking ADRs, artifact validation, and profile/class requirements. Detailed
instructions also require acceptance/testing evidence and checks for pending or
blocked work. CLI success does not replace every assistant instruction or a
human review. See [policy profiles](policy-profiles.md) and
[assistant enforcement scope](assistant-adapters.md#enforcement-scope).

## Integration Constraints

- Resolve the host project and artifact roots consistently with the framework's
  path helpers and supported environment overrides. Missing or unreadable
  gate-critical evidence must not silently enable protected work.
- Validate before an operation when the integration can intercept it. A watcher
  observes writes after they happen and cannot establish that an unauthorized
  write was prevented.
- Preserve owner changes and untracked files. A watcher must not automatically
  reset files to HEAD or delete newly observed files; log and notify for an
  owner-controlled recovery process.
- Account for concurrent edits, editor temporary files, Git operations, generated
  outputs, and lifecycle artifacts. File notifications alone do not establish
  which actor wrote a file or whether the owner authorized the operation.
- Define version support and test compatibility against the selected framework
  version. No universal compatibility guarantee is provided by this note.

Claude's direct Write/Edit hooks provide the documented interception points;
Bash detection remains best effort. Arbitrary scripts, other tools, and operating
system writes require a separate, appropriately isolated runtime if stronger
security guarantees are needed. See [Claude hooks](../../adapters/claude/README.md).
