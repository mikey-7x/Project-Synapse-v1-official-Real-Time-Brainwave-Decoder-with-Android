# Repository map

**POWERED BY [mikey:hexoid-sys]** · Created by mikey-7x — Yogesh R. Chauhan

Every file in this repository, and why it exists.

| Path | Role | Status in the redesign |
| --- | --- | --- |
| `README.md` | Front page: what it is, what it is not, how to run it | Rewritten |
| `LICENSE.md` | Strict personal & educational licence | Replaced |
| `NOTICE.md` | Required credit text and logo rules | New |
| `AUTHORS.md` | Author identity and official links | New |
| `SAFETY.md` | Isolation, electrodes, consent, stop rules | New |
| `CHANGELOG.md` | What changed and why | New |
| `CONTRIBUTING.md` | Contribution rules, including claim standards | New |
| `SECURITY.md` | Safety and data-handling reporting | New |
| `SUPPORT.md` | Where to look and where to ask | New |
| `CITATION.cff` | Citation metadata | New |
| `.gitattributes`, `.gitignore` | Line endings and ignored run-time artefacts | New |
| `synapse.py` | Engine build v18 | Header, window title, banner only |
| `next_synapse.py` | Engine build v19 | Header, window title, banner only |
| `sketch_mar20b.ino` | Firmware for the Nano + ADS1115 | Unchanged |
| `sketch_mar29a.cpp.hex` | Prebuilt AVR binary (legacy filename) | Unchanged |
| `ps.jpg` | Schematic | Unchanged |
| `psl.jpg`, `psl2.jpg`, `psl4.jpg`, `psl5.jpg` | PCB layout and assembled board | Unchanged |
| `pss.jpg`, `pss2.pdf` | Flow chart | Unchanged |
| `PROJECT SYNAPSE.BMP`, `project synapse original.jpg` | Original artwork | Unchanged |
| `assets/powered-by-mikey-hexoid-sys.png` / `.svg` | Brand hero | New |
| `assets/mikey-hexoid-sys-mark.png` / `.svg` | Square mark | New |
| `assets/github-social-preview.png` | Link-preview image | New |
| `assets/scientific-poster.png` / `.pdf` | A2 research poster | New |
| `assets/README.md`, `assets/SHA256SUMS` | Asset guide and checksums | New |
| `docs/HARDWARE.md` | BOM, stage-by-stage design, bring-up | New |
| `docs/PROTOCOL.md` | Frame format, timing and bandwidth budget | New |
| `docs/ALGORITHM.md` | Conditioning, Trinx, DTW, models, 19 features | New |
| `docs/ANDROID-SETUP.md` | Termux, PRoot Arch, Miniforge, X11 | Rewritten from the README |
| `docs/USAGE.md` | Connect, record, train, predict | New |
| `docs/LIMITATIONS.md` | Measurement and method limits | New |
| `docs/TROUBLESHOOTING.md` | Failure modes and fixes | New |
| `docs/REPOSITORY-MAP.md` | This file | New |
| `tools/verify_repository.py` | Offline self-check | New |
| `tools/make_poster.py` | Deterministic poster generator | New |
| `.github/workflows/verify.yml` | CI: structure, credits, syntax | New |
| `.github/ISSUE_TEMPLATE/*` | Bug and licence-request forms | New |
| `.github/PULL_REQUEST_TEMPLATE.md` | Review checklist | New |

## Naming note

`sketch_mar20b.ino` and `sketch_mar29a.cpp.hex` keep their original names so that the
published binary stays traceable to the sketch revision that produced it. Arduino expects a
sketch folder to share the `.ino` name; if you copy the firmware into a project of your own,
put it in a folder with the same name.
