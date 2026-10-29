#!/usr/bin/env python3
"""Offline self-check for the Project Synapse v1 repository.

POWERED BY [mikey:hexoid-sys] - Created by mikey-7x - Yogesh R. Chauhan

Verifies the expected file set, required attribution, licence terms, the safety
document, Python syntax of both engines, the firmware constants that define the
acquisition format, the presence and integrity of the poster and brand assets,
and that no marketing overclaims crept back into the documentation.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND = "POWERED BY [mikey:hexoid-sys]"
REPO_URL = "https://github.com/mikey-7x/Project-Synapse-v1-official-Real-Time-Brainwave-Decoder-with-Android"
AUTHOR = "Yogesh R. Chauhan"

REQUIRED = [
    "README.md", "LICENSE.md", "NOTICE.md", "AUTHORS.md", "SAFETY.md",
    "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md", "SUPPORT.md", "CITATION.cff",
    ".gitattributes", ".gitignore",
    "synapse.py", "next_synapse.py", "sketch_mar20b.ino", "sketch_mar29a.cpp.hex",
    "assets/powered-by-mikey-hexoid-sys.png", "assets/powered-by-mikey-hexoid-sys.svg",
    "assets/mikey-hexoid-sys-mark.png", "assets/mikey-hexoid-sys-mark.svg",
    "assets/github-social-preview.png",
    "assets/scientific-poster.png", "assets/scientific-poster.pdf",
    "assets/README.md", "assets/SHA256SUMS",
    "docs/HARDWARE.md", "docs/PROTOCOL.md", "docs/ALGORITHM.md",
    "docs/ANDROID-SETUP.md", "docs/USAGE.md", "docs/LIMITATIONS.md",
    "docs/TROUBLESHOOTING.md", "docs/REPOSITORY-MAP.md",
    "tools/verify_repository.py", "tools/make_poster.py",
    ".github/workflows/verify.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/commercial_licence.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
]

passed, failed = [], []


def check(name, condition, detail=""):
    (passed if condition else failed).append(name + (f": {detail}" if detail and not condition else ""))


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8", errors="replace")


for rel in REQUIRED:
    check(f"file exists: {rel}", (ROOT / rel).is_file())

# ------------------------------------------------------------------ credit ---
for rel in ("README.md", "NOTICE.md", "AUTHORS.md", "LICENSE.md", "SAFETY.md",
            "synapse.py", "next_synapse.py", "assets/README.md", "docs/HARDWARE.md"):
    if (ROOT / rel).is_file():
        check(f"brand line in {rel}", BRAND in read(rel))

readme = read("README.md") if (ROOT / "README.md").is_file() else ""
check("README credits the author", "Created by mikey-7x" in readme and AUTHOR in readme)
check("README links the repository", REPO_URL in readme)
check("README shows the poster", "assets/scientific-poster.png" in readme)
check("README shows the hero logo", "assets/powered-by-mikey-hexoid-sys.png" in readme)
check("README states this is not a medical device",
      re.search(r"not a medical device", readme, re.I) is not None)
check("README has the safety warning callout", "battery power only" in readme.lower())

# ----------------------------------------------------------------- licence ---
licence = read("LICENSE.md") if (ROOT / "LICENSE.md").is_file() else ""
for phrase in ("STRICT PERSONAL & EDUCATIONAL USE LICENCE",
               "Attribution is a condition of permission",
               "ABSOLUTE COMMERCIAL, CLINICAL AND INDUSTRIAL PROHIBITION",
               "Copyright (c) 2026 Yogesh R. Chauhan",
               "not an open-source licence",
               BRAND, REPO_URL):
    check(f"licence contains: {phrase[:44]}", re.search(re.escape(phrase).replace(chr(92)+" ", r"\s+"), licence, re.I) is not None)
check("licence prohibits clinical use",
      "NOT permitted under any circumstance" in licence)
check("licence keeps prior CC BY-NC rights", "CC BY-NC" in licence or "Creative Commons" in licence)
check("licence has no published email address", "@gmail.com" not in licence)

safety = read("SAFETY.md") if (ROOT / "SAFETY.md").is_file() else ""
for phrase in ("Battery power only", "implanted electronic device", "informed consent",
               "Stop immediately"):
    check(f"safety covers: {phrase[:34]}", phrase.lower() in safety.lower())

# ----------------------------------------------------------------- scripts ---
for script in ("synapse.py", "next_synapse.py"):
    if (ROOT / script).is_file():
        proc = subprocess.run([sys.executable, "-m", "py_compile", str(ROOT / script)],
                              capture_output=True, text=True)
        check(f"{script} compiles", proc.returncode == 0, proc.stderr.strip()[:200])
        text = read(script)
        check(f"{script} keeps the Trinx engine", "class TrinxEngine" in text)
        check(f"{script} keeps the DTW matcher", "_fast_dtw" in text)
        check(f"{script} keeps the 90% acceptance rule", "conf >= 90.0" in text)
        check(f"{script} keeps the 140 Hz assumption", "self.sample_rate = 140" in text)
        check(f"{script} prints the attribution", BRAND in text)

# ---------------------------------------------------------------- firmware ---
ino = read("sketch_mar20b.ino") if (ROOT / "sketch_mar20b.ino").is_file() else ""
for label, pattern in (("140 Hz pacing", r"sampleInterval\s*=\s*7142"),
                       ("16-bit range setting", r"GAIN_TWOTHIRDS"),
                       ("ADC data rate", r"RATE_ADS1115_860SPS"),
                       ("sync byte 0xAA", r"0xAA"),
                       ("sync byte 0x55", r"0x55"),
                       ("serial rate", r"Serial\.begin\(9600\)")):
    check(f"firmware keeps {label}", re.search(pattern, ino) is not None)

# ------------------------------------------------------------------ assets ---
sums = ROOT / "assets" / "SHA256SUMS"
if sums.is_file():
    listed = 0
    for line in sums.read_text().splitlines():
        if not line.strip():
            continue
        digest, name = line.split(maxsplit=1)
        target = ROOT / "assets" / name.strip()
        actual = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else ""
        check(f"asset checksum: {name.strip()}", actual == digest)
        listed += 1
    check("asset checksum list is complete", listed == 7, f"listed {listed}")
else:
    check("asset checksum list exists", False)

poster = ROOT / "assets" / "scientific-poster.png"
check("poster has plausible dimensions/size",
      poster.is_file() and poster.stat().st_size > 300_000,
      "poster missing or suspiciously small")

# ------------------------------------------------------------- no overclaim --
banned = ["industrial-grade", "unparalleled precision", "reads thoughts",
          "massive architectural evolution", "decode raw human thoughts into text"]
for rel in ("README.md", "docs/HARDWARE.md", "docs/ALGORITHM.md", "docs/LIMITATIONS.md"):
    if (ROOT / rel).is_file():
        low = read(rel).lower()
        hits = [b for b in banned if b in low]
        check(f"no marketing overclaim in {rel}", not hits, ", ".join(hits))

for rel in ("README.md", "NOTICE.md", "SAFETY.md", "docs/USAGE.md"):
    if (ROOT / rel).is_file():
        low = read(rel).lower()
        check(f"no placeholders in {rel}",
              not any(w in low for w in ("todo", "tbd", "lorem ipsum", "fixme")))

citation = read("CITATION.cff") if (ROOT / "CITATION.cff").is_file() else ""
check("citation metadata present",
      "cff-version: 1.2.0" in citation and "Chauhan" in citation and "mikey-7x" in citation)

total = len(passed) + len(failed)
print(f"Repository verification: {len(passed)}/{total} passed")
if failed:
    print("\nFailed checks:")
    for item in failed:
        print(f"  - {item}")
    sys.exit(1)
print("All structural, branding, licence, safety, syntax, firmware and asset checks passed.")
print("This verifies files only; it does not test hardware, signals or model accuracy.")
