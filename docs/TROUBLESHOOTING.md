# Troubleshooting

**POWERED BY [mikey:hexoid-sys]** · Created by mikey-7x — Yogesh R. Chauhan

## The window never appears

| Symptom | Cause | Fix |
| --- | --- | --- |
| `_tkinter.TclError: couldn't connect to display` | `DISPLAY` not set, or the PRoot session lacks the socket | `export DISPLAY=:0`, and log in with `--shared-tmp` |
| Blank black window | Termux:X11 not running | start `termux-x11 :0 &` and open the app |
| `ModuleNotFoundError: tkinter` | Arch is missing Tk | `pacman -S tk` |
| TensorFlow import crash | Python version mismatch on aarch64 | use the Miniforge Python 3.11 environment |

## No connection

1. Confirm the TCP bridge is listening: `ss -ltn | grep 5656` or `netstat -ltn`.
2. Check the HC-05 is paired and not connected to another app.
3. Look at the raw stream: a correct feed starts with the bytes `AA 55` repeating every six
   bytes. Anything else means the bridge is forwarding text or the firmware is not running.
4. Power-cycle the Nano; the sketch halts if the ADS1115 is not detected at boot.

## Trace is flat, clipped or 50 Hz dominated

| Observation | Usual cause |
| --- | --- |
| Flat line | electrodes not contacting, gel dried, lead broken, ADS1115 channel wrong |
| Clipped / square | input exceeds the ±6.144 V range or the rectifier stage is saturating |
| Thick 50 Hz band | mains pickup: move away from chargers and lamps, check the reference electrode |
| Slow wandering | skin-battery offset drifting; re-prep the skin, re-gel the electrodes |

## Training fails

- `Signal too weak to extract valid Trinxs` — fewer than five slices passed the energy gate.
  Record longer strips, press more firmly on the gesture, or check the trace first.
- Keras error on input shape — delete `Models/` and retrain; a stale `.keras` file from a
  different feature length cannot be reused.
- Memory error on the phone — train on a desktop, then copy the model files across.

## Predictions look random

Expected, until the corpus is good. Check, in order: are there at least three sessions per
label; is there an `rest` class; do the labels differ in the trace as well as in the name; is
the acceptance threshold rejecting most frames (a sign the templates do not match).

## Data does not appear on the phone

`/storage/emulated/0/Documents/Project_Synapse` requires storage permission for Termux
(`termux-setup-storage`) and a working Documents path. If the folder cannot be created the app
falls back to a local `Synapse_Memory` directory next to the script.

## Reinstalling from scratch

```bash
rm -rf ~/Project-Synapse-v1-official-Real-Time-Brainwave-Decoder-with-Android
git clone https://github.com/mikey-7x/Project-Synapse-v1-official-Real-Time-Brainwave-Decoder-with-Android.git
```

Bring your `EEG_Data` folder back afterwards; the models can be rebuilt from it.
