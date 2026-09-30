"""Machine checks for GAP-01 Repository Admission. Run:  python scripts/test_repository_admission.py

Every check builds a throwaway Git repository in a temporary directory and asks
the control about it; the real repository is never scanned or touched here.
Git runs with global and system configuration disabled, so no result depends on
the machine the suite runs on.

Secret-shaped fixtures are assembled at runtime from fragments and a fixed hash,
so this file holds no credential, and nothing in it matches the patterns it tests.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import repository_admission as ra

# No developer or runner configuration may influence a fixture repository.
os.environ["GIT_CONFIG_GLOBAL"] = os.devnull
os.environ["GIT_CONFIG_SYSTEM"] = os.devnull
os.environ["GIT_CONFIG_NOSYSTEM"] = "1"

failures: list[str] = []
# Every fixture lives under one directory, removed when the suite ends.
_BASE = Path(tempfile.mkdtemp(prefix="gap01-tests-"))
# ...and Git may not discover some enclosing repository above it.
os.environ["GIT_CEILING_DIRECTORIES"] = str(_BASE)


def check(name: str, condition: bool, detail: str = "") -> None:
    print(("PASS" if condition else "FAIL") + f"  {name}" + (f" -- {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(name)


def git(root: Path, *args: str, stdin: bytes | None = None) -> str:
    return subprocess.run(["git", "-C", str(root), *args], input=stdin, capture_output=True,
                          check=True).stdout.decode().strip()


def new_repo() -> Path:
    root = Path(tempfile.mkdtemp(prefix="repo-", dir=_BASE))
    git(root, "init", "-q")
    git(root, "config", "core.fileMode", "true")
    return root


def track(root: Path, path: str, data: bytes, mode: str = ra.MODE_REGULAR) -> None:
    """Record an entry in the index with an exact mode, straight from bytes.

    The working tree is not involved, so executable bits and symlinks are
    expressed identically on every filesystem.
    """
    oid = git(root, "hash-object", "-w", "--stdin", stdin=data)
    git(root, "update-index", "--add", "--cacheinfo", f"{mode},{oid},{path}")


def scan(root: Path) -> tuple[str, list[ra.Finding]]:
    _, findings = ra.scan(root)
    return ra.overall(findings), findings


def rules(findings: list[ra.Finding]) -> set[tuple[str, str, str]]:
    return {(f.path, f.rule, f.decision) for f in findings}


def run_main(root: Path) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = ra.main(["--root", str(root)])
    return code, buf.getvalue()


def synthetic(prefix: str, length: int, alphabet: str) -> str:
    """A deterministic, non-live token: a fixed hash mapped into an alphabet."""
    stream = b""
    while len(stream) < length:
        stream += hashlib.sha256(f"gap01-synthetic-{prefix}-{len(stream)}".encode()).digest()
    return prefix + "".join(alphabet[b % len(alphabet)] for b in stream[:length])


_UPPER_NUM = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
_ALNUM = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
PEM_HEAD = "-----" + "BEGIN " + "RSA " + "PRIVATE" + " KEY-----"
PEM_TAIL = "-----" + "END " + "RSA " + "PRIVATE" + " KEY-----"
AWS_ID = synthetic("AK" + "IA", 16, _UPPER_NUM)
GH_TOKEN = synthetic("gh" + "p_", 36, _ALNUM)
SECRET_VALUES = (PEM_HEAD, AWS_ID, GH_TOKEN)

# ---------------------------------------------------------------------------
# PASS: every admitted class, with ordinary content.
# ---------------------------------------------------------------------------
ok = new_repo()
ORDINARY = {
    "scripts/tool.py": b"from pathlib import Path\n\nprint(Path('.'))\n",
    "src/data/case.yaml": b"slug: example\ntitle: An example\ndomains: [physics]\n",
    ".github/workflows/ci.yml": b"name: ci\non: [push]\n",
    "src/templates/page.html": b"<!doctype html>\n<html><body><p>Hello</p></body></html>\n",
    "src/static/site.css": b"body { margin: 0; }\n",
    "docs/readme.md": b"# Title\n\nSome prose, a URL https://example.org/a/b and a hash "
                      b"3f786850e387550fdab836ed7e6dc881de23001b.\n",
    "requirements.txt": b"PyYAML==6.0.2\n",
    ".gitignore": b"/public/\n/reports/\n",
    "docs/at-ceiling.md": b"x" * ra.MAX_TRACKED_FILE_BYTES,
}
for path, data in ORDINARY.items():
    track(ok, path, data)
decision, findings = scan(ok)
check("every admitted file class passes with ordinary content", decision == ra.PASS and not findings,
      str([f.render() for f in findings]))
check("a file exactly at the ceiling is admitted", "docs/at-ceiling.md" not in {f.path for f in findings})
check("PASS exits 0", run_main(ok)[0] == 0)
check("the admitted vocabulary is exactly the audited one",
      ra.ADMITTED_SUFFIXES == {".py", ".yaml", ".yml", ".html", ".css", ".md", ".txt"}
      and ra.ADMITTED_BASENAMES == {".gitignore"})
check("the size ceiling is the fixed 512 KiB constant", ra.MAX_TRACKED_FILE_BYTES == 524288)

# ---------------------------------------------------------------------------
# QUARANTINE: inert but not admitted.
# ---------------------------------------------------------------------------
cases_q = {
    "unknown inert extension": ("random.xyz", b"inert\n", ra.MODE_REGULAR, "unadmitted-type"),
    "no suffix at all": ("LICENSE", b"text\n", ra.MODE_REGULAR, "unadmitted-type"),
    "suffix case is not normalised": ("Tool.PY", b"print(1)\n", ra.MODE_REGULAR, "unadmitted-type"),
    "file above the size ceiling": ("docs/big.md", b"y" * (ra.MAX_TRACKED_FILE_BYTES + 1),
                                    ra.MODE_REGULAR, "size-ceiling"),
    "internal symlink": ("docs/link.md", b"readme.md", ra.MODE_SYMLINK, "symlink-internal"),
    "internal symlink to a sibling directory": ("a/b/link", b"../c/file.md", ra.MODE_SYMLINK,
                                                "symlink-internal"),
    "admitted suffix that is not UTF-8 text": ("docs/latin1.md", b"caf\xe9\n", ra.MODE_REGULAR,
                                               "not-utf8"),
    "submodule / gitlink": ("vendor/lib", b"", "160000", "unadmitted-mode"),
}
for name, (path, data, mode, rule) in cases_q.items():
    root = new_repo()
    if mode == "160000":
        git(root, "update-index", "--add", "--cacheinfo", f"160000,{'1' * 40},{path}")
    else:
        track(root, path, data, mode)
    decision, findings = scan(root)
    check(f"QUARANTINE: {name}", decision == ra.QUARANTINE and (path, rule, ra.QUARANTINE)
          in rules(findings), str([f.render() for f in findings]))
    if name == "unknown inert extension":
        check("QUARANTINE exits non-zero (1)", run_main(root)[0] == 1)

# ---------------------------------------------------------------------------
# BLOCK: hazards.
# ---------------------------------------------------------------------------
ELF = b"\x7fELF\x02\x01\x01" + b"\x00" * 57
PE = bytearray(b"MZ" + b"\x90" * 62 + b"\x00" * 64)
PE[0x3c:0x40] = (0x40).to_bytes(4, "little")
PE[0x40:0x44] = b"PE\x00\x00"
ZIP = b"PK\x03\x04\x14\x00\x00\x00" + b"payload"
TAR = b"notes.txt".ljust(257, b"\x00") + b"ustar\x0000" + b"\x00" * 200
ENCODED = synthetic("", 2048, _ALNUM + "+/").encode()
cases_b = {
    "executable git mode, even on Python source": ("scripts/run.py", b"print(1)\n",
                                                   ra.MODE_EXECUTABLE, "executable-mode"),
    "archive by extension": ("bundle.zip", ZIP, ra.MODE_REGULAR, "payload-extension"),
    "archive by extension, whatever the case": ("bundle.TAR", b"x\n", ra.MODE_REGULAR,
                                                "payload-extension"),
    "zip payload disguised as .txt": ("notes.txt", ZIP, ra.MODE_REGULAR, "payload-signature"),
    "ELF executable disguised as .md": ("docs/notes.md", ELF, ra.MODE_REGULAR, "payload-signature"),
    "PE executable disguised as .css": ("site.css", bytes(PE), ra.MODE_REGULAR, "payload-signature"),
    "tar archive disguised as .yaml": ("data.yaml", TAR, ra.MODE_REGULAR, "payload-signature"),
    "NUL byte in an admitted text file": ("docs/notes.md", b"# Notes\nclean\x00hidden\n",
                                          ra.MODE_REGULAR, "nul-byte"),
    "encoded payload in admitted text": ("src/data/x.yaml", b"blob: " + ENCODED + b"\n",
                                         ra.MODE_REGULAR, "encoded-payload"),
    "symlink escaping the repository": ("docs/link.md", b"../../etc/passwd", ra.MODE_SYMLINK,
                                        "symlink-escape"),
    "symlink escaping via a deep relative path": ("a/link", b"b/../../..", ra.MODE_SYMLINK,
                                                  "symlink-escape"),
    "absolute symlink": ("docs/link.md", b"/etc/passwd", ra.MODE_SYMLINK, "symlink-absolute"),
    "absolute Windows-style symlink": ("link.md", b"C:\\Windows\\x", ra.MODE_SYMLINK,
                                       "symlink-absolute"),
    "private key block": ("docs/notes.md", f"text\n{PEM_HEAD}\nAAAA\n{PEM_TAIL}\n".encode(),
                          ra.MODE_REGULAR, "secret:private-key-block"),
    "AWS access key id": ("src/data/x.yaml", f"key: {AWS_ID}\n".encode(), ra.MODE_REGULAR,
                          "secret:aws-access-key-id"),
    "GitHub token": ("scripts/x.py", f"TOKEN = '{GH_TOKEN}'\n".encode(), ra.MODE_REGULAR,
                     "secret:github-token"),
    "credential-bearing file by name": (".env", b"NAME=value\n", ra.MODE_REGULAR, "credential-file"),
    "key file by suffix": ("deploy/site.pem", b"text\n", ra.MODE_REGULAR, "credential-file"),
}
for name, (path, data, mode, rule) in cases_b.items():
    root = new_repo()
    track(root, path, data, mode)
    decision, findings = scan(root)
    check(f"BLOCK: {name}", decision == ra.BLOCK and (path, rule, ra.BLOCK) in rules(findings),
          str([f.render() for f in findings]))
    if name == "archive by extension":
        check("BLOCK exits non-zero (2)", run_main(root)[0] == 2)

# ---------------------------------------------------------------------------
# Every secret signature the scanner claims, one fixture each. Values are
# assembled from fragments and a fixed hash at runtime; none is live.
# ---------------------------------------------------------------------------
_ALNUM_ = _ALNUM + "_"
_KEY_ARMOUR = "-----" + "BEGIN {}PRIVATE" + " KEY{}-----"
SIGNATURE_FIXTURES: dict[str, list[tuple[str, str]]] = {
    "private-key-block": [
        ("RSA armour", _KEY_ARMOUR.format("RSA ", "")),
        ("PKCS#8 armour", _KEY_ARMOUR.format("", "")),
        ("OpenSSH armour", _KEY_ARMOUR.format("OPEN" + "SSH ", "")),
        ("EC armour", _KEY_ARMOUR.format("EC ", "")),
        ("encrypted PKCS#8 armour", _KEY_ARMOUR.format("ENCRYPTED ", "")),
        ("PGP armour", _KEY_ARMOUR.format("PGP ", " BLOCK")),
    ],
    "aws-access-key-id": [
        ("long-term AKIA id", AWS_ID),
        ("temporary ASIA id", synthetic("AS" + "IA", 16, _UPPER_NUM)),
    ],
    "github-token": [
        ("classic personal token", GH_TOKEN),
        ("OAuth token", synthetic("gh" + "o_", 36, _ALNUM)),
        ("server token", synthetic("gh" + "s_", 36, _ALNUM)),
    ],
    "github-fine-grained-token": [
        ("fine-grained personal token", synthetic("github" + "_pat_", 82, _ALNUM_)),
    ],
    "slack-token": [
        ("bot token", synthetic("xo" + "xb-", 40, _ALNUM + "-")),
        ("user token", synthetic("xo" + "xp-", 40, _ALNUM + "-")),
    ],
    "google-api-key": [
        ("API key", synthetic("AI" + "za", 35, _ALNUM + "_-")),
    ],
    "stripe-live-secret-key": [
        ("live secret key", synthetic("sk" + "_live_", 24, _ALNUM)),
        ("live restricted key", synthetic("rk" + "_live_", 24, _ALNUM)),
    ],
    "anthropic-api-key": [
        ("API key", synthetic("sk" + "-ant-", 40, _ALNUM + "_-")),
    ],
}
check("every claimed secret signature has at least one fixture",
      set(SIGNATURE_FIXTURES) == {rule for rule, _ in ra.SECRET_SIGNATURES},
      f"untested: {sorted({r for r, _ in ra.SECRET_SIGNATURES} - set(SIGNATURE_FIXTURES))}")
_all_values: list[str] = []
for rule, variants in SIGNATURE_FIXTURES.items():
    for label, value in variants:
        _all_values.append(value)
        root = new_repo()
        track(root, "src/data/x.yaml", f"note: fixture\nvalue: {value}\n".encode())
        decision, findings = scan(root)
        check(f"BLOCK: secret signature {rule} ({label})",
              decision == ra.BLOCK and ("src/data/x.yaml", f"secret:{rule}", ra.BLOCK) in rules(findings),
              str([f.render() for f in findings]))
root = new_repo()
for i, value in enumerate(_all_values):
    track(root, f"docs/s{i:02d}.md", f"# s\n{value}\n".encode())
code, output = run_main(root)
check("every signature is reported at its line, and no value is echoed",
      code == 2 and output.count("line 2, fingerprint sha256:") == len(_all_values)
      and not any(v in output for v in _all_values))

# Guard against the obvious false positives the signatures were narrowed for.
root = new_repo()
track(root, "docs/a.md", b"MZ is how this paragraph starts, and it is prose.\n")
track(root, "docs/b.md", b"BZh is not an archive either.\n")
track(root, "docs/c.md", ("=" * 2000 + "\n" + "a" * 2000 + "\n").encode())
track(root, "docs/d.md", b"A key id looks like AKIA followed by sixteen characters.\n")
check("prose that merely resembles a signature is not blocked", scan(root) == (ra.PASS, []),
      str([f.render() for f in scan(root)[1]]))

# ---------------------------------------------------------------------------
# Several findings: all reported, strongest wins.
# ---------------------------------------------------------------------------
multi = new_repo()
track(multi, "random.xyz", b"inert\n")
track(multi, "docs/big.md", b"z" * (ra.MAX_TRACKED_FILE_BYTES + 1))
track(multi, "scripts/run.py", b"print(1)\n", ra.MODE_EXECUTABLE)
track(multi, "docs/notes.md", f"{PEM_HEAD}\n".encode())
track(multi, "fine.md", b"# fine\n")
decision, findings = scan(multi)
check("every finding is reported, not just the first",
      {("random.xyz", "unadmitted-type"), ("docs/big.md", "size-ceiling"),
       ("scripts/run.py", "executable-mode"), ("docs/notes.md", "secret:private-key-block")}
      <= {(f.path, f.rule) for f in findings})
check("BLOCK dominates QUARANTINE", decision == ra.BLOCK)
check("QUARANTINE dominates PASS",
      ra.overall([ra.Finding("a", "r", ra.QUARANTINE, ""), ra.Finding("b", "r", ra.PASS, "")])
      == ra.QUARANTINE)
check("an admitted file alongside offenders produces no finding",
      "fine.md" not in {f.path for f in findings})

# ---------------------------------------------------------------------------
# Diagnostics never carry the secret.
# ---------------------------------------------------------------------------
leak = new_repo()
track(leak, "docs/notes.md", f"{PEM_HEAD}\nMIIB\n{PEM_TAIL}\n".encode())
track(leak, "src/data/x.yaml", f"key: {AWS_ID}\n".encode())
track(leak, "scripts/x.py", f"T = '{GH_TOKEN}'\n".encode())
code, output = run_main(leak)
check("secrets are reported with rule, line and fingerprint",
      code == 2 and output.count("fingerprint sha256:") == 3 and "line 1" in output)
check("diagnostics never echo a detected secret value",
      not any(v in output for v in SECRET_VALUES) and "MIIB" not in output
      and not any(v[4:20] in output for v in (AWS_ID, GH_TOKEN)))

# ---------------------------------------------------------------------------
# Deterministic, read-only, and bounded to the tracked tree.
# ---------------------------------------------------------------------------
runs = [scan(multi) for _ in range(5)] + [scan(leak) for _ in range(5)]
check("repeated scans are identical", runs[:5] == [runs[0]] * 5 and runs[5:] == [runs[5]] * 5)
check("findings are ordered deterministically", runs[0][1] == sorted(runs[0][1]))
outputs = {run_main(multi)[1] for _ in range(3)}
check("the printed report is byte-identical across runs", len(outputs) == 1)

disk = new_repo()
(disk / "scripts").mkdir()
(disk / "scripts" / "tool.py").write_text("print(1)\n")
(disk / "scripts" / "run.py").write_text("print(2)\n")
(disk / "scripts" / "run.py").chmod(0o755)
(disk / ".gitignore").write_text("/public/\n/reports/\n")
for generated in ("public", "reports"):
    (disk / generated).mkdir()
    (disk / generated / "index.html").write_bytes(ZIP)
    (disk / generated / "leak.txt").write_text(PEM_HEAD + "\n")
(disk / "untracked.xyz").write_text("not added\n")
git(disk, "add", "scripts", ".gitignore")
outside = Path(tempfile.mkdtemp(prefix="outside-", dir=_BASE))
(outside / "secret.md").write_text(PEM_HEAD + "\n")
symlinks = True
try:
    (disk / "outlink.md").symlink_to(outside / "secret.md")
    git(disk, "add", "outlink.md")
except OSError:
    symlinks = False


def snapshot(root: Path) -> dict[str, tuple[bytes, int, int]]:
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_symlink():
            out[str(p)] = (os.readlink(p).encode(), 0, p.lstat().st_mtime_ns)
        elif p.is_file():
            st = p.stat()
            out[str(p)] = (p.read_bytes(), st.st_mode, st.st_mtime_ns)
    return out


before = snapshot(disk)
count, findings = ra.scan(disk)
check("the scanner does not mutate the tree or the index", snapshot(disk) == before)
check("ignored generated output is not in the admission population",
      not any(f.path.startswith(("public/", "reports/")) for f in findings)
      and count == (4 if symlinks else 3))
check("untracked files are not in the admission population",
      "untracked.xyz" not in {f.path for f in findings})
check("an executable bit set on disk is seen through git add",
      ("scripts/run.py", "executable-mode", ra.BLOCK) in rules(findings))
if symlinks:
    link = [f for f in findings if f.path == "outlink.md"]
    check("a symlink is judged as a link and never followed",
          [(f.rule, f.decision) for f in link] == [("symlink-absolute", ra.BLOCK)],
          str([f.render() for f in link]))

not_a_repo = Path(tempfile.mkdtemp(prefix="norepo-", dir=_BASE))
code, output = run_main(not_a_repo)
check("a control that cannot establish its population fails closed", code == ra.EXIT_CONTROL_ERROR
      and "CONTROL ERROR" in output)

# ---------------------------------------------------------------------------
# Where it runs: inside the required job, before anything else can.
# ---------------------------------------------------------------------------
_wf = (Path(__file__).resolve().parent.parent / ".github" / "workflows" / "governance.yml"
       ).read_text(encoding="utf-8")
check("the required job keeps its exact name", "    name: Governed admission checks\n" in _wf)
check("GAP-01 runs before dependencies are installed and before the build",
      _wf.index("scripts/repository_admission.py") < _wf.index("pip install")
      < _wf.index("scripts/build.py"))
check("the control imports nothing outside the standard library",
      all(line.split()[1].split(".")[0] in {"__future__", "argparse", "hashlib", "posixpath", "re",
                                            "subprocess", "sys", "dataclasses", "pathlib"}
          for line in (Path(ra.__file__).read_text(encoding="utf-8").splitlines())
          if line.startswith(("import ", "from "))))

shutil.rmtree(_BASE)
print("\n" + ("ALL CHECKS PASSED" if not failures else f"{len(failures)} CHECK(S) FAILED: {failures}"))
raise SystemExit(1 if failures else 0)
