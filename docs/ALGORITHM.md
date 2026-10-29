# Algorithm

**POWERED BY [mikey:hexoid-sys]** · Created by mikey-7x — Yogesh R. Chauhan

Everything here is implemented in `synapse.py` (build v18) and `next_synapse.py` (build v19).
The two builds share the pipeline; v19 changes model hyper-parameters.

## 1 · Conditioning

| Step | Setting | Purpose |
| --- | --- | --- |
| Notch | `iirnotch(50.0, 30.0, fs=140)` | Remove mains hum at 50 Hz |
| Band-pass | `butter(2, [1.0, 40.0], btype='band')` applied with `filtfilt` | Keep the useful band, zero phase distortion |
| Buffer | 560 samples (4 s) | Rolling display and prediction window |

`filtfilt` runs the filter forwards and backwards, so the phase response is flat and the
filtered trace stays aligned with the displayed stimulus — important when a human is trying
to time a gesture.

## 2 · The Trinx idea

Fixed windows and zero padding assume every gesture lasts the same time. Biological gestures
do not. Synapse measures the recording's own rhythm and slices at that period:

```python
envelope  = |x| smoothed with a 70-sample (0.5 s) centred rolling mean
autocorr  = correlate(envelope, envelope)[positive lags]
period_T  = first autocorrelation peak at least 70 samples away
period_T  = clamp(period_T, 70, 420)          # 0.5 s … 3.0 s
slices    = recording[i*T : (i+1)*T] for i in range(len(recording) // T)
keep slice if max(|slice|) > 500               # energy gate
```

Each surviving slice is a **Trinx**: a candidate instance of one gesture, already the right
length for that person on that day. Because the period is measured, trimming and padding —
the two operations that corrupt shape — are unnecessary.

## 3 · Templates and matching

Two families of decoder are trained from the same Trinx bank.

**Trinx-DTW (instance-based, no training phase).** Each stored Trinx is z-normalised, and a
live query is compared with every template using dynamic time warping:

```text
D[i][j] = |a_i - b_j| + min(D[i-1][j], D[i][j-1], D[i-1][j-1])
distance = D[n][m] / (n + m)
confidence = clip(100 - 70 × distance, 0, 100)      (+10 if 2 of the top 3 agree)
```

DTW allows the two instances to stretch relative to one another, so a slow and a fast
rendering of the same gesture land close together in cost space. The cost surface and the
warp path are what the poster visualises.

**Sequence models (CNN-LSTM / CNN-GRU).** Trinx arrays are padded to the longest training
template, reshaped to `(samples, length, 1)` and fed to:

```text
Conv1D(32, 5, relu) → BatchNorm → MaxPool → BiLSTM/GRU(64) → LSTM/GRU(32) → Dense(softmax)
optimizer Adam(1e-3) · loss categorical_crossentropy · 40 epochs · batch 8
```

**Classical models.** The same Trinxs are reduced to 19 descriptive numbers and classified by
XGBoost (300 trees), Random Forest (300 trees), SVM (RBF), KNN and logistic regression.

## 4 · The 19-feature vector

| Group | Features |
| --- | --- |
| Band powers (Welch PSD) | δ 0.5–4 Hz, θ 4–8 Hz, α 8–13 Hz, β 13–30 Hz, γ 30–45 Hz |
| Amplitude | mean absolute value, RMS, peak-to-peak, variance |
| Timing / shape | zero-crossing count, line length, slope-sign changes |
| Statistics | mean, standard deviation, skewness, kurtosis |
| Complexity | Hjorth mobility, Hjorth complexity, spectral entropy |

Band powers are computed by averaging the Welch periodogram over each band, so they are
robust to a single bad epoch. Hjorth parameters describe how quickly the signal changes and
how quickly that change itself changes; spectral entropy describes how spread the spectrum
is.

## 5 · Decision rule

A prediction is accepted only when the highest score reaches **90 %**; otherwise the frame is
rejected and displayed as `REJECTED: <label> (<confidence>)`. For the tree and SVM models the
score is a class probability; for the DTW engine it is a distance-derived heuristic. The two
are not calibrated against each other and should not be compared as if they were.

## 6 · Honest notes

- The confidence numbers are **not** calibrated probabilities. DTW confidence is a monotone
  function of distance; nothing in the pipeline verifies that "95 %" means correct 95 % of
  the time.
- Templates and models are trained and tested on the same small, self-recorded corpus. No
  held-out subject, no cross-validation figure and no split protocol are published here, so
  no generalisation claim can be made.
- With one channel and 140 Hz, the same pipeline will happily learn to recognise jaw clench,
  blinks and cable movement. Separating those from the intended gesture needs better
  instrumentation, not a bigger model.
- The v19 build changes hyper-parameters and extraction details; treat the two builds as
  successive experiments, not as a benchmarked comparison.
