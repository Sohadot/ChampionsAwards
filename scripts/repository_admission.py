"""GAP-01 Repository Admission:  python scripts/repository_admission.py [--root PATH]

Asks one question of every tracked file, before anything reads it for meaning:
is this a kind of thing this repository accepts, at all?

The population is the Git index (`git ls-files --stage`), which in a clean CI
checkout is exactly the commit under test. Content is read from the object
database (`git cat-file`), never from the working tree, so the control sees what
is tracked rather than what happens to be on disk, never follows a symlink to
decide whether the symlink is admissible, and never touches a file. Ignored
output such as public/ and reports/ is not tracked and so is not in scope.

Standard library and the Git CLI only. This runs before dependencies are
installed, so that nothing an inadmissible tree could influence has run yet.

Decisions, strongest wins:  BLOCK > QUARANTINE > PASS.
Exit codes: 0 PASS, 1 QUARANTINE, 2 BLOCK, 3 the control could not run (which
is never a pass). Every finding is reported; nothing is repaired, renamed or
deleted, and a suspected secret is identified by rule, line and a one-way
fingerprint, never printed.
"""
from __future__ import annotations

import argparse
import hashlib
import posixpath
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Policy. Every constant the decision depends on is here, so the policy is one
# reviewable block rather than something inferred from the code below it.
# ---------------------------------------------------------------------------

# The file types this repository admits, derived from the tracked tree on
# 2026-09-30 (126 files: .yaml 57, .html 26, .md 19, .py 19, .txt 2, .css 1,
# .yml 1, and .gitignore). Exact, case-sensitive suffixes. Adding a type is a
# policy change made here, in a reviewed pull request - not a side effect of
# someone committing one.
ADMITTED_SUFFIXES: frozenset[str] = frozenset(
    {".py", ".yaml", ".yml", ".html", ".css", ".md", ".txt"})
# Repository metadata admitted by exact basename, because it has no suffix.
ADMITTED_BASENAMES: frozenset[str] = frozenset({".gitignore"})

# A fixed ceiling, not one derived from the largest current file: a threshold
# that moves with the tree would normalise an oversized file once it arrived.
# The largest tracked file at adoption was 85,195 bytes.
MAX_TRACKED_FILE_BYTES: int = 512 * 1024

# Git modes. Only a non-executable regular file is part of the vocabulary.
MODE_REGULAR = "100644"
MODE_EXECUTABLE = "100755"
MODE_SYMLINK = "120000"

# Suffixes that name an executable, compiled or archive payload. Matched
# case-insensitively, whatever the content: the name alone is a claim to be one.
BLOCKED_SUFFIXES: frozenset[str] = frozenset({
    # executables, libraries, bytecode, packages
    ".exe", ".dll", ".so", ".dylib", ".bin", ".com", ".scr", ".msi", ".elf",
    ".class", ".jar", ".war", ".apk", ".pyc", ".pyo", ".whl", ".egg",
    # archives and disk images
    ".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".rar", ".zst",
    ".lz", ".lzma", ".cab", ".iso", ".dmg", ".deb", ".rpm",
})

# Files whose name marks them as credential-bearing. Blocked by name, because
# their purpose is to hold a secret whether or not a signature below matches.
CREDENTIAL_BASENAMES: frozenset[str] = frozenset({
    ".env", ".netrc", ".pypirc", ".npmrc", ".htpasswd",
    "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
})
CREDENTIAL_SUFFIXES: frozenset[str] = frozenset(
    {".pem", ".key", ".p12", ".pfx", ".jks", ".keystore"})

# High-confidence content signatures of an executable or archive, checked on
# every regular file regardless of its name, so that a payload renamed to
# `.txt` is still a payload. (offset, bytes) pairs; all must match.
MAGIC_SIGNATURES: tuple[tuple[str, tuple[tuple[int, bytes], ...]], ...] = (
    ("elf-executable", ((0, b"\x7fELF"),)),
    ("mach-o-executable", ((0, b"\xfe\xed\xfa\xce"),)),
    ("mach-o-executable", ((0, b"\xfe\xed\xfa\xcf"),)),
    ("mach-o-executable", ((0, b"\xce\xfa\xed\xfe"),)),
    ("mach-o-executable", ((0, b"\xcf\xfa\xed\xfe"),)),
    ("mach-o-or-java-class", ((0, b"\xca\xfe\xba\xbe"),)),
    ("zip-archive", ((0, b"PK\x03\x04"),)),
    ("zip-archive", ((0, b"PK\x05\x06"),)),
    ("zip-archive", ((0, b"PK\x07\x08"),)),
    ("gzip-archive", ((0, b"\x1f\x8b\x08"),)),
    ("xz-archive", ((0, b"\xfd7zXZ\x00"),)),
    ("7z-archive", ((0, b"7z\xbc\xaf\x27\x1c"),)),
    ("rar-archive", ((0, b"Rar!\x1a\x07"),)),
    ("zstd-archive", ((0, b"\x28\xb5\x2f\xfd"),)),
    ("tar-archive", ((257, b"ustar\x00"),)),
    ("tar-archive", ((257, b"ustar  \x00"),)),
    ("wasm-module", ((0, b"\x00asm"),)),
)
# bzip2 and PE need a little more than a prefix to be high-confidence: "BZh" and
# "MZ" are plausible opening letters of text, so the full structure is required.
_BZIP2 = re.compile(rb"\ABZh[1-9]\x31\x41\x59\x26\x53\x59")

# An encoded payload hidden in admitted text: an unbroken run of base64/hex
# alphabet at least this long, using at least this many distinct symbols. The
# longest such run in the tree at adoption was 89 characters; hand-written
# source does not produce a kilobyte of it, and a run of one repeated symbol is
# not an encoding. Escape-sequence encodings (\x41\x42...) are not covered.
ENCODED_RUN_MIN_CHARS: int = 1024
ENCODED_RUN_MIN_DISTINCT: int = 16
_ENCODED_RUN = re.compile(rb"[A-Za-z0-9+/_-]{%d,}" % ENCODED_RUN_MIN_CHARS)

# Secret signatures. Deliberately high-confidence only: each is a fixed prefix
# or armour line that an issuer puts there so that it can be recognised. There
# is no entropy heuristic, so a password typed into a YAML value, or a token
# format not listed here, is NOT detected. The list is the claim, and no more.
SECRET_SIGNATURES: tuple[tuple[str, re.Pattern[bytes]], ...] = (
    ("private-key-block",
     re.compile(rb"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----")),
    ("aws-access-key-id", re.compile(rb"(?<![A-Z0-9])(?:AKIA|ASIA)[A-Z0-9]{16}(?![A-Z0-9])")),
    ("github-token", re.compile(rb"(?<![A-Za-z0-9_])gh[pousr]_[A-Za-z0-9]{36,}")),
    ("github-fine-grained-token", re.compile(rb"github_pat_[A-Za-z0-9_]{60,}")),
    ("slack-token", re.compile(rb"(?<![A-Za-z0-9])xox[abprs]-[A-Za-z0-9-]{10,}")),
    ("google-api-key", re.compile(rb"(?<![A-Za-z0-9_-])AIza[0-9A-Za-z_-]{35}")),
    ("stripe-live-secret-key", re.compile(rb"(?<![A-Za-z0-9])[sr]k_live_[0-9A-Za-z]{24,}")),
    ("anthropic-api-key", re.compile(rb"(?<![A-Za-z0-9])sk-ant-[A-Za-z0-9_-]{32,}")),
)

PASS, QUARANTINE, BLOCK = "PASS", "QUARANTINE", "BLOCK"
_RANK = {PASS: 0, QUARANTINE: 1, BLOCK: 2}
EXIT_CODE = {PASS: 0, QUARANTINE: 1, BLOCK: 2}
EXIT_CONTROL_ERROR = 3


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    rule: str
    decision: str
    detail: str

    def render(self) -> str:
        return f"{self.decision:<10} {self.path}  [{self.rule}] {self.detail}"


@dataclass(frozen=True)
class Entry:
    mode: str
    oid: str
    path: str


# ---------------------------------------------------------------------------
# Git access - read-only, from the index and the object database.
# ---------------------------------------------------------------------------

class ControlError(RuntimeError):
    """The control could not establish the population. Never a pass."""


def _git(root: Path, *args: str, stdin: bytes | None = None) -> bytes:
    try:
        proc = subprocess.run(["git", "-C", str(root), *args], input=stdin,
                              capture_output=True, check=False)
    except OSError as exc:
        raise ControlError(f"git could not be run: {exc}") from exc
    if proc.returncode != 0:
        raise ControlError(f"git {' '.join(args)} failed: "
                           + proc.stderr.decode("utf-8", "replace").strip())
    return proc.stdout


def tracked_entries(root: Path) -> list[Entry]:
    out = _git(root, "ls-files", "--stage", "-z")
    entries = []
    for record in out.split(b"\0"):
        if not record:
            continue
        meta, _, path = record.partition(b"\t")
        mode, oid, _stage = meta.decode("ascii").split(" ")
        entries.append(Entry(mode, oid, path.decode("utf-8", "surrogateescape")))
    return sorted(entries, key=lambda e: (e.path, e.oid))


def read_blobs(root: Path, oids: list[str]) -> dict[str, bytes]:
    """All blobs in one `cat-file --batch` call, parsed from its framed output."""
    unique = sorted(set(oids))
    if not unique:
        return {}
    out = _git(root, "cat-file", "--batch", stdin=("\n".join(unique) + "\n").encode("ascii"))
    blobs: dict[str, bytes] = {}
    pos = 0
    for _ in unique:
        nl = out.index(b"\n", pos)
        header = out[pos:nl].decode("ascii").split(" ")
        if len(header) != 3 or header[1] != "blob":
            raise ControlError(f"object {header[0]} is not a readable blob")
        size = int(header[2])
        blobs[header[0]] = out[nl + 1: nl + 1 + size]
        pos = nl + 1 + size + 1
    return blobs


# ---------------------------------------------------------------------------
# Rules. Each returns findings; none mutates anything.
# ---------------------------------------------------------------------------

def _suffix(basename: str) -> str:
    return posixpath.splitext(basename)[1]


def _line_of(data: bytes, offset: int) -> int:
    return data.count(b"\n", 0, offset) + 1


def _fingerprint(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()[:12]


def classify_symlink(entry: Entry, target_bytes: bytes) -> list[Finding]:
    target = target_bytes.decode("utf-8", "surrogateescape")
    if (target.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:[\\/]", target)):
        return [Finding(entry.path, "symlink-absolute", BLOCK,
                        "symlink target is absolute, outside any repository boundary")]
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(entry.path),
                                                 target.replace("\\", "/")))
    if resolved == ".." or resolved.startswith("../"):
        return [Finding(entry.path, "symlink-escape", BLOCK,
                        "symlink target resolves outside the repository root")]
    return [Finding(entry.path, "symlink-internal", QUARANTINE,
                    "symlinks are not part of the admitted vocabulary, even internal ones")]


def classify_name(entry: Entry) -> list[Finding]:
    basename = posixpath.basename(entry.path)
    suffix = _suffix(basename)
    lower = suffix.lower()
    findings = []
    if (basename in CREDENTIAL_BASENAMES or basename.startswith(".env.")
            or lower in CREDENTIAL_SUFFIXES):
        findings.append(Finding(entry.path, "credential-file", BLOCK,
                                "file name marks it as credential or key material"))
    if lower in BLOCKED_SUFFIXES:
        findings.append(Finding(entry.path, "payload-extension", BLOCK,
                                f"'{lower}' names an executable, compiled or archive payload"))
    if not findings and not (suffix in ADMITTED_SUFFIXES or basename in ADMITTED_BASENAMES):
        shown = suffix or "(no suffix)"
        findings.append(Finding(entry.path, "unadmitted-type", QUARANTINE,
                                f"file type {shown!r} is not in the admitted vocabulary"))
    return findings


def classify_content(entry: Entry, data: bytes) -> list[Finding]:
    findings = []
    for name, parts in MAGIC_SIGNATURES:
        if all(data[off:off + len(sig)] == sig for off, sig in parts):
            findings.append(Finding(entry.path, "payload-signature", BLOCK,
                                    f"content carries a {name} signature"))
            break
    else:
        if _BZIP2.match(data):
            findings.append(Finding(entry.path, "payload-signature", BLOCK,
                                    "content carries a bzip2-archive signature"))
        elif (data[:2] == b"MZ" and len(data) >= 0x40
              and data[int.from_bytes(data[0x3c:0x40], "little"):][:4] == b"PE\x00\x00"):
            findings.append(Finding(entry.path, "payload-signature", BLOCK,
                                    "content carries a pe-executable signature"))
    nul = data.find(b"\x00")
    if nul >= 0:
        findings.append(Finding(entry.path, "nul-byte", BLOCK,
                                f"NUL byte at line {_line_of(data, nul)}: "
                                "admitted types are text, so this is a binary payload"))
    else:
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as exc:
            findings.append(Finding(entry.path, "not-utf8", QUARANTINE,
                                    f"not valid UTF-8 (line {_line_of(data, exc.start)}); "
                                    "admitted types are UTF-8 text"))
    for match in _ENCODED_RUN.finditer(data):
        if len(set(match.group())) >= ENCODED_RUN_MIN_DISTINCT:
            findings.append(Finding(entry.path, "encoded-payload", BLOCK,
                                    f"line {_line_of(data, match.start())}: unbroken encoded run "
                                    f"of {len(match.group())} characters"))
            break
    for rule, pattern in SECRET_SIGNATURES:
        for match in pattern.finditer(data):
            # Rule, line and a one-way fingerprint. Never the value.
            findings.append(Finding(entry.path, f"secret:{rule}", BLOCK,
                                    f"line {_line_of(data, match.start())}, "
                                    f"fingerprint sha256:{_fingerprint(match.group())}"))
    return findings


def classify_entry(entry: Entry, data: bytes) -> list[Finding]:
    if entry.mode == MODE_SYMLINK:
        # Decided on the link itself; the target is never opened.
        return classify_symlink(entry, data)
    if entry.mode not in (MODE_REGULAR, MODE_EXECUTABLE):
        # Submodules (160000) and anything else Git may record: not a file this
        # repository can inspect, so not one it admits.
        return [Finding(entry.path, "unadmitted-mode", QUARANTINE,
                        f"git mode {entry.mode} is not a regular file")]
    findings = []
    if entry.mode == MODE_EXECUTABLE:
        findings.append(Finding(entry.path, "executable-mode", BLOCK,
                                "tracked with executable mode 100755; nothing here needs one"))
    findings += classify_name(entry)
    if len(data) > MAX_TRACKED_FILE_BYTES:
        findings.append(Finding(entry.path, "size-ceiling", QUARANTINE,
                                f"{len(data)} bytes exceeds the {MAX_TRACKED_FILE_BYTES}-byte ceiling"))
    findings += classify_content(entry, data)
    return findings


def overall(findings: list[Finding]) -> str:
    return max((f.decision for f in findings), key=_RANK.__getitem__, default=PASS)


def scan(root: Path) -> tuple[int, list[Finding]]:
    """(number of tracked entries, sorted findings) for the repository at root."""
    entries = tracked_entries(root)
    blobs = read_blobs(root, [e.oid for e in entries if e.mode != "160000"])
    findings: list[Finding] = []
    for entry in entries:
        findings += classify_entry(entry, blobs.get(entry.oid, b""))
    return len(entries), sorted(findings)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    print("GAP-01 Repository Admission")
    try:
        count, findings = scan(args.root)
    except ControlError as exc:
        print(f"CONTROL ERROR - the population could not be established: {exc}")
        return EXIT_CONTROL_ERROR
    for finding in findings:
        print("  " + finding.render())
    decision = overall(findings)
    counts = {d: sum(1 for f in findings if f.decision == d) for d in (BLOCK, QUARANTINE)}
    print(f"{count} tracked entries, {counts[BLOCK]} BLOCK finding(s), "
          f"{counts[QUARANTINE]} QUARANTINE finding(s)")
    print(f"DECISION: {decision}")
    return EXIT_CODE[decision]


if __name__ == "__main__":
    sys.exit(main())
