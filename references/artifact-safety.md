# Artifact and Data Safety

Apply these rules when a generated Skill reads, writes, uploads, downloads, or
returns files.

## Local writes

- Resolve output under a user-selected or task-appropriate directory.
- Sanitize generated names and reject `..`, absolute-path injection, or path
  separators supplied as a filename.
- Do not overwrite an existing file unless the user requested replacement.
- Write to a temporary sibling file, verify it, then atomically rename it when
  practical.
- Remove incomplete temporary files after failure.

## Uploads

- Explain an external upload when it was not already obvious from the request.
- Name the destination service, data class, likely cost, and known retention or
  deletion behavior.
- Do not put source contents, signed URLs, tokens, or credentials in logs,
  listing copy, session files, or the RED upload package.
- Delete temporary remote objects when a proven cleanup action exists and the
  workflow does not require retention.

## Downloads and generated artifacts

- Verify the response and real file type before trusting the extension.
- Re-open or decode the artifact before delivery.
- Check dimensions, expected media properties, and non-empty content.
- For PNG, check the PNG signature; verify alpha when transparency is required.
- For background removal, inspect the subject crop and transparent edge for
  obvious white or dark halos.
- Deliver the artifact visibly or as an attachment, not only as a local path.
