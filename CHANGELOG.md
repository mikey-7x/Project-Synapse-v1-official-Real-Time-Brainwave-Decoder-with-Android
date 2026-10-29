# Changelog

**POWERED BY [mikey:hexoid-sys]**

## [1.0.0-redesign] — repository and documentation revision

### Added

- Research poster: A2 print-ready PNG and PDF in `assets/`, with the deterministic generator
  `tools/make_poster.py`.
- Repository identity: the approved silver `POWERED BY [mikey:hexoid-sys]` logo set, square mark, social preview and
  `assets/README.md` usage guide.
- Documentation set: `HARDWARE.md`, `PROTOCOL.md`, `ALGORITHM.md`, `ANDROID-SETUP.md`,
  `USAGE.md`, `LIMITATIONS.md`, `TROUBLESHOOTING.md`, `REPOSITORY-MAP.md`.
- `SAFETY.md` as a standalone document covering isolation, consent, electrodes and stop rules.
- `NOTICE.md`, `AUTHORS.md`, `CITATION.cff`, `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`.
- `tools/verify_repository.py` and a GitHub Actions workflow that check structure, credits,
  licence terms, Python syntax of both engines, firmware constants and asset checksums.
- Issue forms for bug reports and commercial/clinical licence requests, plus a PR template.
- `.gitattributes` and `.gitignore`.

### Changed

- `LICENSE.md` replaced with the **mikey-7x Strict Personal & Educational Use Licence**,
  written for a biomedical-adjacent hardware/software project: mandatory attribution and logo
  use, absolute prohibition of commercial, clinical and industrial use, human-subject and
  data conditions, and an explicit no-medical-claim clause. Recipients of earlier revisions
  obtained under CC BY-NC 4.0 keep those rights; the new licence governs this revision.
- `README.md` rewritten for accuracy: measured stage parameters, an honest protocol and
  bandwidth budget, an explicit “what this project does not claim” section, and the
  anti-alias and link-margin caveats stated plainly.
- `synapse.py` and `next_synapse.py`: author, licence and powered-by header block, an
  in-application `POWERED BY [mikey:hexoid-sys]` window title, and a one-line startup banner.
  **No acquisition, filtering, extraction, training or prediction logic was changed.**
- Unsupported marketing framing removed: the README no longer claims industrial or
  carrier-grade reliability, no longer claims superlative precision, and no longer implies
  that the system decodes thoughts or speech content.

### Removed from the README

- The published personal email address. Commercial and clinical enquiries now go through the
  GitHub profile and the repository's licence-request issue form.

### Unchanged

- `sketch_mar20b.ino`, `sketch_mar29a.cpp.hex`, all figures, `PROJECT SYNAPSE.BMP` and
  `project synapse original.jpg` are byte-identical to the previous revision.

## [1.0.0] — published prototype

- Analog front-end, firmware, HC-05 transport, Tk application, Trinx segmentation,
  classical and deep-learning decoders.
