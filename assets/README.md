# Brand and poster assets

POWERED BY [mikey:hexoid-sys]

These files belong to **Yogesh R. Chauhan (mikey-7x)** and may be reproduced only for the
attribution required by [`LICENSE.md`](../LICENSE.md).

| File | Size | Use |
| --- | --- | --- |
| `powered-by-mikey-hexoid-sys.png` | 2000 × 1428 | Hero image in the README and documentation covers |
| `powered-by-mikey-hexoid-sys.svg` | vector | Print and large-format use |
| `mikey-hexoid-sys-mark.png` | 1024 × 1024 | Square mark for icons, footers and labels |
| `mikey-hexoid-sys-mark.svg` | vector | Scalable square mark |
| `github-social-preview.png` | 1280 × 640 | Link-preview image for the repository |
| `scientific-poster.png` | 2481 × 3508 (A2, 150 dpi) | Research poster, screen and preview |
| `scientific-poster.pdf` | A2 vector | Print-ready poster |

## Rules

1. Do not crop out, erase or restyle the text `[mikey:hexoid-sys]`.
2. Proportional resizing is fine; stretching, skewing or recolouring to illegibility is not.
3. Always show the credit with the mark:
   `Created by mikey-7x — Yogesh R. Chauhan` and `POWERED BY [mikey:hexoid-sys]`.
4. Do not use these files for unrelated projects or to suggest endorsement or clinical
   validation.
5. The poster figures are illustrations of the processing chain, not measured results. Do not
   present them as experimental data, and do not remove the limits panel.

## Regenerating the poster

```bash
python3 tools/make_poster.py
```

The generator is deterministic: it synthesises its waveforms, feature vector and DTW cost
surface from a fixed seed, then writes `assets/scientific-poster.png` and
`assets/scientific-poster.pdf`.

## Integrity

`SHA256SUMS` records the exact bytes of every file in this folder.
