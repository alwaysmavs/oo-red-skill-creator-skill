#!/usr/bin/env python3
"""Validate and build a Xiaohongshu RED Skill ZIP with deterministic entries."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlparse


ALLOWED_EXTENSIONS = {".md", ".txt", ".html", ".css", ".js", ".py", ".json", ".xml"}
BLOCKED_SOURCE_EXTENSIONS = {
    ".bash", ".cjs", ".go", ".java", ".jsx", ".kt", ".mjs", ".php",
    ".rb", ".rs", ".sh", ".swift", ".ts", ".tsx", ".yaml", ".yml", ".zsh",
}
SKIP_DIRECTORIES = {".git", "__pycache__", "agents", "examples", "node_modules", "outputs", "tests"}
SKIP_FILES = {".DS_Store", ".oo-metadata.json"}
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 30 * 1024 * 1024
REFERENCE_PATTERNS = {
    ".md": [re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")],
    ".html": [re.compile(r"(?:src|href)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)],
    ".css": [re.compile(r"url\(\s*[\"']?([^\"')]+)", re.IGNORECASE)],
    ".js": [
        re.compile(r"(?:from\s+|require\(\s*|import\(\s*)[\"']([^\"']+)[\"']"),
    ],
}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SECRET_PATTERNS = [
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("OpenAI-style API key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "literal credential assignment",
        re.compile(
            r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password)\b\s*[:=]\s*[\"'][^\"'\r\n]{16,}[\"']"
        ),
    ),
]
OFFLINE_PATTERNS = [
    ("remote URL", re.compile(r"https?://", re.IGNORECASE)),
    ("fetch API", re.compile(r"\bfetch\s*\(")),
    ("XMLHttpRequest", re.compile(r"\bXMLHttpRequest\b")),
    ("WebSocket", re.compile(r"\bWebSocket\s*\(")),
    ("EventSource", re.compile(r"\bEventSource\s*\(")),
]
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
OO_BOOTSTRAP_REQUIREMENTS = [
    ("OO availability check", re.compile(r"\boo\s+--version\b", re.IGNORECASE)),
    (
        "official OO installation guide",
        re.compile(r"https://cli\.oomol\.com/install-guide\.md", re.IGNORECASE),
    ),
    (
        "explicit installation or login authority",
        re.compile(
            r"\b(?:authority|approval|permission|consent)\b|授权|许可|同意",
            re.IGNORECASE,
        ),
    ),
    ("OO login command", re.compile(r"\boo\s+auth\s+login\b", re.IGNORECASE)),
    (
        "original-task preservation across setup",
        re.compile(
            r"(?:preserve|resume|continue)[^\n]{0,160}(?:request|task)|"
            r"(?:request|task)[^\n]{0,160}(?:preserve|resume|continue)|"
            r"保留[^\n]{0,80}(?:请求|任务)|"
            r"继续[^\n]{0,80}(?:原始|原有|当前)(?:请求|任务)",
            re.IGNORECASE,
        ),
    ),
]


class ContractError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and package a RED Skill source directory.",
    )
    parser.add_argument("skill_directory", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--archive-name")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Reject obvious remote URLs and browser network APIs in runtime files.",
    )
    return parser.parse_args()


def is_hidden(relative: Path) -> bool:
    return any(part.startswith(".") for part in relative.parts)


def should_skip_file(relative: Path) -> str | None:
    if is_hidden(relative) or relative.name in SKIP_FILES:
        return "hidden or management metadata"
    if relative.name.lower().startswith("readme"):
        return "repository documentation"
    if relative.suffix.lower() in BLOCKED_SOURCE_EXTENSIONS:
        raise ContractError(
            f"unsupported source or configuration file requires conversion: {relative.as_posix()}"
        )
    if relative.suffix.lower() not in ALLOWED_EXTENSIONS:
        return "unsupported extension"
    return None


def collect_files(root: Path) -> tuple[list[Path], list[dict[str, str]]]:
    included: list[Path] = []
    skipped: list[dict[str, str]] = []

    for current, directories, files in os.walk(root):
        current_path = Path(current)
        relative_current = current_path.relative_to(root)
        kept_directories = []
        for name in sorted(directories):
            relative = relative_current / name
            if name in SKIP_DIRECTORIES or name.startswith("."):
                skipped.append({"path": relative.as_posix(), "reason": "non-runtime directory"})
                continue
            path = current_path / name
            if path.is_symlink():
                raise ContractError(f"symlink directories are not allowed: {relative.as_posix()}")
            kept_directories.append(name)
        directories[:] = kept_directories

        for name in sorted(files):
            path = current_path / name
            relative = path.relative_to(root)
            if path.is_symlink():
                raise ContractError(f"symlink files are not allowed: {relative.as_posix()}")
            reason = should_skip_file(relative)
            if reason:
                skipped.append({"path": relative.as_posix(), "reason": reason})
                continue
            included.append(relative)

    included.sort(key=lambda value: value.as_posix())
    return included, skipped


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    try:
        text = skill_md.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ContractError("SKILL.md must be UTF-8 text") from error
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ContractError("SKILL.md must begin with YAML frontmatter")
    try:
        closing = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as error:
        raise ContractError("SKILL.md frontmatter is missing its closing ---") from error

    metadata: dict[str, str] = {}
    for line in lines[1:closing]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line[:1].isspace():
            continue
        if ":" not in line:
            raise ContractError("SKILL.md frontmatter must use simple top-level key: value fields")
        key, raw_value = line.split(":", 1)
        value = raw_value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        metadata[key.strip()] = value
    return metadata


def verify_skill_contract(root: Path) -> dict[str, str]:
    metadata = parse_frontmatter(root / "SKILL.md")
    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if not name or len(name) > 64 or not NAME_PATTERN.fullmatch(name):
        raise ContractError("frontmatter name must be lowercase hyphen-case and at most 64 characters")
    if name != root.name:
        raise ContractError(f"frontmatter name must match the Skill directory: {root.name}")
    if not description or len(description) > 1024:
        raise ContractError("frontmatter description must be 1 to 1024 characters")
    return metadata


def read_runtime_texts(root: Path, included: list[Path]) -> dict[Path, str]:
    texts: dict[Path, str] = {}
    for relative in included:
        data = (root / relative).read_bytes()
        if b"\x00" in data:
            raise ContractError(f"runtime file contains NUL bytes: {relative.as_posix()}")
        try:
            texts[relative] = data.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ContractError(f"runtime file must be UTF-8 text: {relative.as_posix()}") from error
    return texts


def verify_sensitive_content(texts: dict[Path, str]) -> None:
    errors: list[str] = []
    for relative, text in texts.items():
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"{relative.as_posix()}: possible {label}")
    if errors:
        raise ContractError("possible embedded secret detected:\n" + "\n".join(errors))


def verify_offline_contract(texts: dict[Path, str]) -> None:
    errors: list[str] = []
    for relative, text in texts.items():
        for label, pattern in OFFLINE_PATTERNS:
            if pattern.search(text):
                errors.append(f"{relative.as_posix()}: offline mode found {label}")
    if errors:
        raise ContractError("offline static scan failed:\n" + "\n".join(errors))


def verify_oo_runtime_bootstrap(
    metadata: dict[str, str], texts: dict[Path, str]
) -> bool:
    compatibility = metadata.get("compatibility", "")
    if not re.search(r"\boo\b", compatibility, re.IGNORECASE):
        return False

    runtime_text = "\n".join(texts.values())
    missing = [
        label
        for label, pattern in OO_BOOTSTRAP_REQUIREMENTS
        if not pattern.search(runtime_text)
    ]
    if missing:
        raise ContractError(
            "frontmatter declares an OO runtime dependency but the packaged "
            "end-user bootstrap is incomplete; missing: " + ", ".join(missing)
        )
    return True


def normalize_link(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    return unquote(target)


def verify_local_references(root: Path, included: list[Path], texts: dict[Path, str]) -> None:
    included_set = set(included)
    errors: list[str] = []

    for relative in included:
        patterns = REFERENCE_PATTERNS.get(relative.suffix.lower(), [])
        if not patterns:
            continue
        text = texts[relative]
        for pattern in patterns:
            for match in pattern.finditer(text):
                target = normalize_link(match.group(1))
                if not target or target.startswith("#"):
                    continue
                if relative.suffix.lower() == ".js" and not target.startswith((".", "/")):
                    continue
                parsed = urlparse(target)
                if parsed.scheme or target.startswith("//"):
                    continue
                target_path = target.split("#", 1)[0].split("?", 1)[0]
                if not target_path:
                    continue
                candidate = relative.parent / target_path
                normalized = Path(os.path.normpath(candidate.as_posix()))
                if normalized.is_absolute() or normalized.as_posix().startswith("../"):
                    errors.append(f"{relative.as_posix()}: reference escapes Skill root: {target}")
                    continue
                resolved = root / normalized
                if resolved.is_dir():
                    continue
                if normalized not in included_set:
                    errors.append(f"{relative.as_posix()}: missing or excluded local reference: {target}")

    if errors:
        raise ContractError("\n".join(errors))


def verify_sizes(root: Path, included: list[Path]) -> tuple[int, list[dict[str, int | str]]]:
    total = 0
    details: list[dict[str, int | str]] = []
    for relative in included:
        size = (root / relative).stat().st_size
        if size > MAX_FILE_BYTES:
            raise ContractError(
                f"file exceeds 10 MiB: {relative.as_posix()} ({size} bytes)"
            )
        total += size
        details.append({"path": relative.as_posix(), "bytes": size})
    if total > MAX_TOTAL_BYTES:
        raise ContractError(f"included files exceed 30 MiB total ({total} bytes)")
    return total, details


def write_zip(root: Path, included: list[Path], destination: Path) -> None:
    prefix = root.name
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in included:
            source = root / relative
            entry = f"{prefix}/{relative.as_posix()}"
            info = zipfile.ZipInfo(entry, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xFFFF) << 16
            archive.writestr(info, source.read_bytes())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    root = args.skill_directory.expanduser().resolve()
    if not root.is_dir():
        raise ContractError(f"Skill directory does not exist: {root}")
    if not (root / "SKILL.md").is_file():
        raise ContractError(f"Skill root does not contain SKILL.md: {root}")

    metadata = verify_skill_contract(root)
    included, skipped = collect_files(root)
    if Path("SKILL.md") not in included:
        raise ContractError("SKILL.md was unexpectedly excluded")
    total_bytes, files = verify_sizes(root, included)
    texts = read_runtime_texts(root, included)
    verify_sensitive_content(texts)
    oo_runtime_bootstrap_scan = verify_oo_runtime_bootstrap(metadata, texts)
    if args.offline:
        verify_offline_contract(texts)
    verify_local_references(root, included, texts)

    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    archive_name = args.archive_name or f"{root.name}-red-skill.zip"
    if Path(archive_name).name != archive_name:
        raise ContractError("archive name must not contain a directory")
    if not archive_name.lower().endswith(".zip"):
        archive_name += ".zip"
    destination = out_dir / archive_name
    write_zip(root, included, destination)

    result = {
        "ok": True,
        "skill_directory": str(root),
        "archive": str(destination),
        "sha256": sha256(destination),
        "total_uncompressed_bytes": total_bytes,
        "offline_static_scan": args.offline,
        "oo_runtime_bootstrap_scan": oo_runtime_bootstrap_scan,
        "scan_scope": "Static high-confidence checks only; runtime behavior still requires review and smoke testing.",
        "files": files,
        "skipped": skipped,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractError as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(1)
