# Limitations

**POWERED BY [mikey:hexoid-sys]** · Created by mikey-7x — Yogesh R. Chauhan

Stated plainly, because an instrument is only credible when its boundaries are visible.

## Measurement limits

| Limit | Consequence |
| --- | --- |
| Single differential channel | No spatial information; cannot separate cortical, ocular and muscular sources |
| 140 Hz host sample rate | 70 Hz Nyquist; the analog low-pass is designed near 106 Hz, so 70–106 Hz content can alias |
| Serial link at 9 600 baud | 840 B/s payload is ~87 % of link capacity; gaps and latency are expected |
| No CRC in the frame | A corrupted payload that still starts with `0xAA 0x55` is accepted silently |
| Hobby-grade electrodes and wiring | Contact noise, motion and mains pickup dominate many recordings |
| No shielding, no driven reference | Common-mode rejection depends on the INA128 and the software subtraction alone |

## Method limits

- The Trinx period is estimated from one autocorrelation peak; a strong rhythmic artefact
  (heartbeat, equipment hum) can be mistaken for the gesture period.
- The energy gate is a fixed threshold (`max |x| > 500`) on raw ADC counts, not a
  subject-adaptive criterion.
- DTW confidence is a distance heuristic, not a calibrated probability.
- Classical and deep models are trained and evaluated on the same small self-recorded
  corpus; no held-out subject, cross-validation protocol or accuracy figure is published.
- The deep models pad Trinxs to the longest template, which reintroduces a little of the
  fixed-length assumption the Trinx idea was meant to avoid.

## Claims this project does not make

- It does not decode thoughts, imagined speech or intent with any demonstrated reliability.
- It is not a lie detector, a mood meter, a sleep monitor or a cognitive-load gauge.
- It is not a medical device and has no diagnostic value.
- It has not been reviewed by an ethics committee or a regulatory body.

## What would make it stronger

1. Two or three channels with a driven reference and proper shielding.
2. A lower analog cutoff (or 500 Hz sampling) so the digital band is genuinely protected.
3. 115 200 baud with a length-prefixed, CRC-checked frame.
4. Session-wise held-out evaluation, several subjects, and a published confusion matrix.
5. Impedance monitoring so bad contacts are rejected instead of classified.

None of these are implemented here. They are the honest next steps, not hidden features.
