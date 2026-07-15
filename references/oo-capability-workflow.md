# OO Capability Workflow

Use this reference only when the finished Skill is OO-required or dual-runtime.

## Prepare the authoring environment

```bash
oo --version
oo auth status --json
```

If `oo` is missing, use the official installer for the current platform from
<https://cli.oomol.com/install-guide.md> only after explaining the dependency
and obtaining installation authority. If authentication is missing or invalid,
ask the user to authorize the login step, run `oo auth login`, and let them
complete secure login. Never ask the user to paste credentials into a prompt or
source file.

This prepares the authoring environment only. It does not satisfy the generated
Skill's end-user setup contract.

## Encode the end-user bootstrap

For an OO-required finished Skill, include a runtime reference that checks
`oo --version`. If OO is missing, it must explain the dependency, obtain
explicit installation authority, use the current-platform command from
<https://cli.oomol.com/install-guide.md>, and verify the installed command.
Handle a PATH refresh without discarding the active request.

After OO becomes available, attempt the intended substantive operation. When
that operation exposes an authentication blocker, check status and obtain
authority before running `oo auth login`. Let the user complete secure login;
never request credentials in chat. Preserve the original request, source files,
resolved options, and output destination through setup, then resume the same
task without making the user repeat it.

If the target host cannot install software, refresh PATH, open login, or expose
OO to the Skill runtime, name that exact blocker and stop. A compatibility field
or RED listing warning is not a substitute for this executable runtime flow.

## Discover before designing

Search with one short outcome sentence that preserves decisive provider,
language, file, format, account, cost, and data-routing constraints:

```bash
oo search "<outcome>" --json
```

Use connector results as candidates. For generic hosted transforms such as
image generation, OCR, ASR, translation, TTS, background removal, and document
conversion, prefer a matching `fusion-api` action unless a user constraint
requires another service.

Use `oo connector search` only to repair a known discovery gap in a shortlisted
connector path. Do not restart broad exploration at runtime.

## Prove the contract

Before writing commands into the finished Skill, inspect every required action:

```bash
oo connector schema "<service>.<action>"
```

Capture:

- exact service and action names;
- authentication and account requirements;
- required and optional payload fields;
- accepted file or URL forms;
- full CLI response paths for IDs, status, results, and artifact URLs;
- async terminal success, terminal failure, polling interval, and timeout;
- idempotency or resume behavior;
- auth, permission, billing, schema, timeout, and not-found failures.

Run a representative invocation only when it is cheap, non-sensitive,
non-destructive, and necessary to prove result shape. Mark schema-only result
paths as untested when a safe invocation is not appropriate.

## Design async waiting

Derive terminal states and timing from the selected action rather than assuming
every connector behaves alike. Poll in the background, stop immediately on a
terminal state, keep the task or session ID for recovery, and avoid narrating
every poll to the user.

For an OO image pipeline with the known long-running profile—typically about
150 seconds, up to 300 seconds for one attempt, and a transparent server retry
that can extend the full window toward 10 minutes—start near a 15-second poll
interval and relax toward 20–30 seconds. Give the user a brief expectation at
submission and a meaningful update about every 60–90 seconds. Do not expose
internal retry resets as a new user task or declare failure at the first
attempt boundary. At the overall deadline, stop bounded polling, preserve the
identifier, and provide a resume path instead of restarting blindly.

## Handle files and artifacts

Use `oo file upload "<path>" --json` only when a connector needs a remote URL
and the user supplied a local file. Pass its `downloadUrl` to the selected
action. Use connector-native upload/import actions when the intended result is
a user-visible write to another service.

Before uploading private or proprietary files, state the target service,
external data flow, likely cost, and known retention or deletion behavior. Ask
for authority when those facts were not already part of the user's request.
Do not log signed URLs, credentials, or file contents. Use a proven cleanup or
delete action when the connector exposes one and the workflow calls for
temporary remote storage.

Download a proven artifact URL with:

```bash
oo file download "<url>" "<out-dir>" --name "<name>" --ext "<ext>"
```

Preview, attach, or otherwise deliver every generated artifact. Reporting only
a local path is not a complete handoff. Verify the real file type rather than
trusting its extension. When the user requires PNG, check the PNG signature,
decode the image, verify dimensions and color mode, and check alpha when
transparency is required; convert and re-open the file when necessary.

## Author the finished runtime

Put the proven action identity and minimum executable command shape into the
finished Skill. Do not instruct its users to search for capabilities on every
run. Keep setup in an OO-specific reference when the domain workflow should
remain prominent.
