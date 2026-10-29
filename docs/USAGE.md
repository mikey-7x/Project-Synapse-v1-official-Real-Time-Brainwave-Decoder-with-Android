# Using the application

**POWERED BY [mikey:hexoid-sys]** · Created by mikey-7x — Yogesh R. Chauhan

> Read [SAFETY.md](../SAFETY.md) first. Everything below assumes battery power and a
> consenting adult.

## 1 · Bring up the link

1. Power the analog board from its battery.
2. Pair the HC-05 with the phone (default PIN 1234 or 0000 on most modules).
3. Start your Bluetooth-to-TCP bridge so that a local socket listens on `127.0.0.1:5656`.
4. Launch the engine and press **CONNECT**. The status light turns `LIVE` once frames are
   parsed; until then you will see `OFFLINE`.

The application never opens the Bluetooth device itself — it only reads the TCP stream.

## 2 · Watch the signal

The dashboard shows the rolling 4 s trace, the band powers and the current model. Use it to
judge contact quality before recording:

- a flat line means the electrodes are not making contact;
- a thick, clipped or wildly wandering trace means poor contact, dried gel, movement or
  50 Hz pickup;
- a clean trace still contains heartbeat, blink and jaw artefacts. Those are not the signal
  you are trying to classify — they are the competition.

## 3 · Record and label

1. Enter a label name (keep it short and consistent, e.g. `yes`, `no`, `left`, `rest`).
2. Start recording; the interface asks for a small number of strips. Keep still, repeat the
   gesture the same way each time.
3. The engine concatenates the strips, conditions them, estimates the period, slices the
   recording into Trinxs, applies the energy gate (`max |x| > 500`) and saves one CSV per
   Trinx under `EEG_Data/<label>/`.
4. Repeat for every label, in several sessions spread over days if you can. A single-session
   corpus will teach the model which session it was, not which gesture it was.

## 4 · Train

Training builds the selected decoder from the Trinx bank:

- **Trinx-DTW** stores templates and needs no training phase.
- **CNN-LSTM / CNN-GRU** pad the Trinx tensors and train for 40 epochs.
- **XGBoost / RF / SVM / KNN / Logistic regression** train on the 19-feature vectors.

Training fails loudly if fewer than five Trinxs were extracted — that is a signal-quality
message, not a bug.

## 5 · Predict

Enable prediction. Accepted labels appear as `>> LABEL (confidence) <<`; frames below the
90 % acceptance threshold appear as `[ REJECTED: LABEL (confidence) ]`.

Treat the accepted label as a hypothesis, not a measurement. If you want a number you can
defend, hold out whole sessions, never train and test on the same strips, and report the
confusion matrix.

## 6 · Housekeeping

| Task | Action |
| --- | --- |
| Move data off the phone | copy `Documents/Project_Synapse/EEG_Data` |
| Start clean | delete `EEG_Data` and `Models`, then rebuild |
| Change the model | select it in the model drop-down; each model keeps its own status |
| Reset the app | use the reset control, then retrain from scratch |

## What good practice looks like

- Record on at least three different days before trusting any classifier.
- Keep an `rest` label so the model has something to reject.
- Change one thing at a time: electrode placement, then gesture timing, then model.
- Log every session with its conditions. Without that, a good result is not reproducible.
