# Android setup (Termux → PRoot Arch → Miniforge)

**POWERED BY [mikey:hexoid-sys]** · Created by mikey-7x — Yogesh R. Chauhan

The application uses Tk and TensorFlow, neither of which is practical inside plain Termux.
The working arrangement is Termux as the host, an Arch Linux container under PRoot, and a
Python 3.11 environment created with Miniforge so that a stable TensorFlow build is available
on aarch64.

## Prerequisites

| Item | Note |
| --- | --- |
| Termux | Install from F-Droid, not from a third-party APK site |
| Termux:X11 | Display server for the Tk window |
| Storage | 4–6 GB free; TensorFlow and the Arch container are not small |
| Network | Wi-Fi for the first install |

## 1 · Prepare Termux

```bash
pkg update -y && pkg upgrade -y
pkg install proot-distro termux-x11-nightly -y
termux-setup-storage
```

## 2 · Install Arch Linux

```bash
proot-distro install archlinux
proot-distro login archlinux --shared-tmp
```

`--shared-tmp` matters: the X11 socket lives in `/tmp`, and without it the container cannot
reach the display.

## 3 · System packages inside Arch

```bash
pacman -Syu --noconfirm
pacman -S --noconfirm base-devel git wget tk xorg-server-xvfb openblas hdf5
```

## 4 · Python 3.11 environment

Arch ships a very new Python, which TensorFlow for aarch64 does not track. Miniforge solves
that without touching the system interpreter:

```bash
cd ~
wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh"
bash Miniforge3-Linux-aarch64.sh -b
source ~/miniforge3/bin/activate
conda create -n synapse_tf python=3.11 -y
conda activate synapse_tf
pip install --upgrade pip
pip install numpy pandas scipy matplotlib scikit-learn joblib xgboost tensorflow
```

## 5 · Get the code

```bash
git clone https://github.com/mikey-7x/Project-Synapse-v1-official-Real-Time-Brainwave-Decoder-with-Android.git
cd Project-Synapse-v1-official-Real-Time-Brainwave-Decoder-with-Android
```

## 6 · Run it

In Termux, start the display and leave the Termux:X11 app running in the background:

```bash
termux-x11 :0 &
```

Then, inside the Arch session:

```bash
proot-distro login archlinux --shared-tmp
cd ~/Project-Synapse-v1-official-Real-Time-Brainwave-Decoder-with-Android
source ~/miniforge3/bin/activate
conda activate synapse_tf
export DISPLAY=:0
python synapse.py
```

If the window opens but is black, the display variable is wrong; if it never opens, the
socket is unreachable — check that both sessions used `--shared-tmp`.

## Desktop alternative

On a normal Linux machine the same steps collapse to a virtual environment:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install numpy pandas scipy matplotlib scikit-learn joblib xgboost tensorflow
python synapse.py
```

A desktop with a real GPU is the sane place to train models; the phone is fine for recording,
display and small experiments.

## Data locations

| Path | Contents |
| --- | --- |
| `/storage/emulated/0/Documents/Project_Synapse/EEG_Data/<label>/` | one CSV per extracted Trinx |
| `/storage/emulated/0/Documents/Project_Synapse/Models/` | `labels.json`, `brain_model_lstm.keras`, `brain_model_gru.keras`, classical model files |

On a desktop these paths resolve to a local `Synapse_Memory` folder instead.

## Uninstall

```bash
proot-distro remove archlinux
rm -rf ~/miniforge3 ~/Project-Synapse-v1-official-Real-Time-Brainwave-Decoder-with-Android
```

Keep the `EEG_Data` folder if you want to retain recordings.
