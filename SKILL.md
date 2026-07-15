---
name: oo-red-skill-creator
description: 'Create, redesign, validate, and package upload-ready Xiaohongshu RED Skills, including Chinese listing metadata and optional OOMOL/ooCLI-powered runtime capabilities. Use when the user asks to create a 小红书 Skill or RED Skill, turn an existing workflow or script into a RED Skill, add OO connectors or Fusion API capabilities, validate RED Skill restrictions, or produce a folder/ZIP and Chinese publishing copy for upload.'
metadata:
  icon: ':lucide:package-plus:'
  title: OO RED Skill Creator
  packageName: '@alwaysmavs/oo-red-skill-creator'
  version: 0.0.3
compatibility: Requires the oo CLI.
---

# OO RED Skill Creator

Create a focused Agent Skill and deliver it as a Xiaohongshu RED Skill upload
package plus Chinese listing copy. Treat RED distribution, OO authoring, and OO
runtime dependency as separate decisions.

## Establish the contract

Derive the following from the user's request and existing files:

- repeated user outcome and realistic trigger phrases;
- required inputs and expected outputs;
- whether an existing workflow must be preserved;
- whether the finished Skill needs OO at runtime;
- whether target users may lack the OO CLI and whether the target host permits
  software installation, PATH refresh, and an interactive login flow;
- whether it must run fully offline without remote assets or network calls;
- artifact destination, account, cost, privacy, and data-routing constraints;
- preferred Skill ID when the user has one.

Ask only when a missing answer changes repeated behavior, cost, external data
flow, destructive actions, or the runtime type. Inspect files and commands for
facts that can be discovered safely.

Normalize the internal name to lowercase hyphen-case under 64 characters. Keep
the RED display name Chinese and no longer than 15 characters. Use English for
the generated Skill instructions by default; generate the RED listing fields in
Chinese.

## Classify the finished runtime

Choose exactly one pattern and read
[references/runtime-patterns.md](references/runtime-patterns.md):

1. **Standard:** the finished Skill uses instructions, local files, local code,
   or host-native tools and never calls `oo`.
2. **OO-required:** without an OO connector, Fusion API, OO-hosted LLM, OO file
   capability, or another `oo` command, the Skill cannot deliver its core
   user-visible promise safely and completely.
3. **Dual-runtime:** it can use a host-native capability without OO and a
   separate OO path when OO is installed or materially improves the result.

Authoring-time use of `oo skills init`, `adopt`, or `validate` does not make the
finished Skill OO-required. Do not add an OO dependency merely because this
creator is OO-aware. Judge necessity against the Skill name, listing copy, and
promised artifact—not against implementation convenience. Prefer Dual-runtime
when a credible manual, uploaded-file, or host-native path still fulfills the
same core outcome.

## Inspect or initialize

Treat existing scripts, configs, tests, references, and output conventions as
the source of truth. Inspect them for entrypoints, dependencies, credentials,
network calls, writes, outputs, and failure modes before preserving them.

For a new Standard Skill, create it in the user's chosen source directory with
the host's standard Skill initializer. Do not write to a global Skill directory
or invoke OO merely because OO is installed.

For an OO-required Skill, or when the user explicitly approves OO-managed
authoring, run the native permission probe and initializer:

```bash
oo skills preflight --agent universal
oo skills init <skill-id> --agent universal --description "<trigger contract>"
```

For an existing workflow, adopt it without overwriting user files:

```bash
oo skills adopt "<workflow-path>" --agent universal --description "<trigger contract>"
```

Before installing software, opening a login flow, or writing to a global Skill
directory, state the target and obtain the authority required by the host. If an
OO-required path is requested and `oo` is missing, follow
[references/oo-capability-workflow.md](references/oo-capability-workflow.md)
instead of inventing connector behavior.

## Prove OO capabilities when needed

Read [references/oo-capability-workflow.md](references/oo-capability-workflow.md)
for OO-required and dual-runtime Skills. Discover and verify capabilities during
authoring. Put concrete service/action identities, payload rules, result paths,
polling behavior, file transfer, and failures into the finished Skill. Do not
make its users repeat capability discovery on every run.

Prefer a host-native path when it fully satisfies the task and OO adds no
material value. Prefer a dual-runtime design when both paths are credible and
can share one domain workflow without pretending their execution mechanics are
identical.

## Make OO runtimes self-onboarding

For every finished Skill that requires OO, put the end-user setup flow inside
the finished runtime package. Authoring-time setup in this Creator does not
count, and `compatibility: Requires the oo CLI.` alone is not sufficient.

The finished Skill must:

1. check `oo --version` before its first OO operation;
2. when missing, explain the dependency and installation target, obtain the
   user's explicit installation authority, and use the current platform command
   from <https://cli.oomol.com/install-guide.md>;
3. verify `oo --version` after installation and handle a PATH refresh without
   losing the task;
4. respond to an actual authentication blocker by checking status, obtaining
   authority to open login, and running `oo auth login` without collecting
   credentials in chat;
5. preserve the user's original request, selected files, resolved parameters,
   and destination across installation and login, then resume without asking
   the user to repeat the task;
6. stop with the exact environment blocker when the host cannot install or
   expose OO, rather than claiming success or silently changing providers.

For Dual-runtime Skills, do not force OO installation when the native path
already fulfills the request. Apply this setup flow only when the user selects
the OO path or the native path is unavailable and the user accepts guided OO
setup. State the real behavior in the RED listing copy.

## Author with progressive disclosure

Keep the generated `SKILL.md` centered on the reusable domain workflow:

- put trigger conditions in frontmatter;
- keep selection and essential execution steps in the body;
- move platform, provider, or runtime variants to one-level-deep references;
- include scripts only for deterministic, repeatedly rewritten operations;
- include assets only when the Skill's output actually consumes them;
- do not add README, changelog, installation guide, or showcase files to the
  runtime package.

Read [references/artifact-safety.md](references/artifact-safety.md) whenever
the finished Skill writes local files, uploads user data, or returns generated
artifacts.

When generating a dual-runtime Skill, place domain quality rules in `SKILL.md`
and use separate references such as `native-runtime.md` and `oomol-runtime.md`.
Do not let setup instructions dominate the Skill's actual expertise.

## Apply the RED contract

Read [references/red-skill-contract.md](references/red-skill-contract.md) before
packaging. Keep only files required at runtime. Do not rename unsupported code
to a supported extension without converting and testing its module semantics.

Generate the Chinese form fields with
[references/listing-copy.md](references/listing-copy.md):

- Skill 名称;
- Skill ID;
- 简介;
- Skill 介绍;
- 版本;
- optional category and tag suggestions.

Keep the form copy outside the upload ZIP. The ZIP should contain only the
Skill's runnable source tree.

## Validate and package

Run the native Skill validator and every deterministic script added to the
finished Skill:

```bash
oo skills validate "<skill-directory>"
```

Exercise realistic positive triggers, negative neighboring cases, the main
runtime path, and safe failure behavior. Do not spend money or mutate a live
service solely to learn a response shape.

Build the RED package with the bundled validator:

```bash
python3 "<this-skill-dir>/scripts/build_red_skill.py" \
  "<skill-directory>" --out-dir "<distribution-directory>"
```

Add `--offline` when the user requires a self-contained local Skill. Treat the
packager's dependency scan as a static guard, then still run the generated
workflow in its intended environment because dynamic dependencies cannot be
proven by filename scanning alone.

When frontmatter compatibility declares an OO CLI dependency, the packager
rejects a runtime that omits the availability check, official installation
guide, permission language, login command, or original-task preservation. Fix
the finished runtime rather than removing an accurate compatibility declaration.

Fix missing local references, unsupported files, size violations, unsafe
symlinks, or validation failures before handoff.

## Deliver

Return all of the following:

1. the finished source directory;
2. the RED upload ZIP;
3. copy-ready Chinese form fields;
4. validation status, packaged file list, total size, and SHA-256;
5. a clear runtime dependency statement: standard, OO-required, or
   dual-runtime;
6. any untested paid, authenticated, or externally mutating path.

Do not upload to Xiaohongshu, publish to the OO registry, push GitHub changes,
or create public content unless the user separately authorizes that action.
