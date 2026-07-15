# Runtime Patterns

Choose the smallest pattern that honestly supports the finished Skill.

## Standard

Use when every supported runtime path relies on instructions, local code,
local files, or tools already supplied by the host.

- Do not declare OO compatibility.
- Do not include OO installation or login instructions.
- Keep external writes and destructive actions behind normal user intent.
- Package only the deterministic scripts and references needed at runtime.

Standard means “no OO runtime,” not necessarily “offline.” When the user asks
for local-only or offline behavior, additionally require:

- no CDN scripts, remote fonts, analytics, tracking pixels, `fetch`, XHR,
  WebSocket, EventSource, or remote imports;
- no runtime dependency on a remote API or hosted asset;
- an offline smoke test of the important workflow;
- safe insertion of user text through `textContent` or equivalent escaping;
- no `eval`, `new Function`, or unvalidated persisted state.

## OO-required

Use only when removing OO makes the Skill unable to deliver its core advertised
outcome safely and completely. OO is normally required when it is the essential
execution, authentication, or managed-task layer—not merely a convenient tool.

Apply the core-promise test:

1. Remove `oo` from the proposed runtime.
2. Compare what remains with the Skill name, listing copy, and promised output.
3. Mark OO-required only when the core result disappears, becomes materially
   incomplete, or would require rebuilding managed authentication, connectors,
   or hosted execution.
4. Mark Dual-runtime when a manual export/upload, host-native tool, or local
   implementation still fulfills the same main promise.

Common OO-required cases include:

- reading or writing a user's connected Gmail, analytics, CRM, cloud, private
  repository, calendar, or task account through an OO connector;
- executing an existing OO workflow whose behavior is the product being
  exposed as a RED Skill;
- producing the promised image, video, OCR, transcription, translation, or
  document artifact through an OO-hosted pipeline with submit, polling, retry,
  and result download;
- relying on OO-managed OAuth, credential isolation, or permission boundaries
  for a sensitive external write;
- relying on an OO async task protocol as the only supported execution backend.

Do not mark OO-required merely because the task uses AI, accesses a public API,
needs Python or JavaScript dependencies, or used OO during authoring.

Examples:

| Skill promise | Classification | Reason |
| --- | --- | --- |
| Read connected Google Analytics and publish a weekly report | OO-required | Without the connector, the Skill cannot access the promised private account data. |
| Analyze a user-uploaded GA CSV, with optional automatic account sync | Dual-runtime | CSV upload still fulfills the reporting promise. |
| Generate a finished image through a named OO-hosted image workflow | OO-required | The promised artifact has no other supported backend. |
| Produce a complete image prompt, with optional OO rendering | Dual-runtime | The prompt remains a complete core deliverable. |
| Update a live Cloudflare Worker through OO-managed authorization | OO-required | The external write depends on the managed credential and permission boundary. |
| Generate Worker source code for the user to deploy | Standard | No external account operation occurs at runtime. |
| Rewrite product copy or validate local RED Skill files | Standard | Host reasoning and local code fully satisfy the outcome. |

- Check `oo --version`, authentication, and the selected capability.
- Put a permission-gated end-user bootstrap in the finished Skill: check
  `oo --version`, guide installation from
  <https://cli.oomol.com/install-guide.md> only when missing, verify the command,
  handle PATH refresh, and preserve the active request across setup.
- On a real authentication blocker, obtain authority before `oo auth login`,
  never collect credentials in chat, and resume the original task after login.
- Treat `compatibility: Requires the oo CLI.` as disclosure, not as a substitute
  for runtime setup instructions.
- Name the concrete connector service/action or stable OO command.
- Include required inputs, payload construction, result paths, polling,
  recovery, file transfer, and failure handling.
- Never hardcode or print credentials.
- Do not silently switch providers after auth, billing, permission, or schema
  failures.
- Obtain explicit authority before installing OO, opening login, starting a
  paid invocation, or uploading private user data.

## Dual-runtime

Use when a native host tool and an OO path both satisfy the same user outcome.

Keep domain logic in `SKILL.md`, then split mechanics:

```text
<skill>/
├── SKILL.md
└── references/
    ├── native-runtime.md
    └── oomol-runtime.md
```

Route explicitly:

1. Follow the user's named provider or runtime when specified.
2. Treat OO as ready only when the CLI exists, required authentication is
   valid, and the concrete connector, command, or companion Skill is runnable.
3. Otherwise use OO when the Skill defines it as the preferred ready path.
4. When OO is absent or incomplete, use a capable native tool without forcing
   installation, login, or companion setup.
5. When neither path exists, explain the missing capability and offer guided
   OO setup.

Do not duplicate domain quality rules in both runtime references. Do not use OO
session, polling, or file commands in the native path. Preserve the original
request across setup and never ask the user to repeat it.
