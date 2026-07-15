# RED Skill Contract

Apply these constraints from the Xiaohongshu upload UI supplied by the user.
If the live uploader shows a different rule, the live UI wins.

## Source package

- Upload a folder or ZIP whose Skill root contains `SKILL.md`.
- Keep one top-level Skill directory inside the ZIP.
- Supported source extensions shown by the uploader include `.md`, `.txt`,
  `.html`, `.css`, `.js`, `.py`, `.json`, and `.xml`.
- Do not include `.mjs`, YAML, images, videos, archives, binaries, credentials,
  caches, logs, generated outputs, or host-only metadata in the upload package.
- Do not merely rename `.mjs` to `.js`; convert ESM/CommonJS semantics and test
  the resulting script.
- A single file must not exceed 10 MiB.
- Total included file size must not exceed 30 MiB.

Repository source may retain showcase images, `agents/openai.yaml`, or
management metadata when another host needs them. Exclude those files only from
the RED distribution package.

## Listing fields

- Skill 名称: required Chinese display name, at most 15 characters.
- Skill ID: stable identifier, preferably lowercase hyphen-case.
- 简介: concise Chinese outcome summary, within the uploader's displayed
  1000-character limit.
- Skill 介绍: copy-ready Chinese Markdown explaining outcomes, use cases,
  inputs, runtime expectations, and important boundaries.
- 版本: use semantic versioning such as `1.0.0` unless an established package
  version must remain aligned.

## Packaging quality

- Every relative file linked from an included Markdown file must also be in the
  package.
- Keep listing copy and validation reports outside the upload ZIP.
- Use descriptive, stable file names and forward slashes in ZIP entries.
- Report the packaged file list, total uncompressed size, ZIP path, and SHA-256.
