#!/usr/bin/env python3
"""Project Synapse v1 - A2 scientific poster generator (deterministic).

POWERED BY [mikey:hexoid-sys] - Created by mikey-7x
Copyright (c) 2026 mikey-7x. All rights reserved.
Licence: mikey-7x Strict Personal & Educational Use Licence (see LICENSE.md).

Every waveform, the feature vector and the DTW cost surface are synthesised
from a fixed seed: the poster illustrates the pipeline, it does not contain
measured experimental results. Requires matplotlib, numpy and Pillow.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
from matplotlib.gridspec import GridSpec
from matplotlib import font_manager as fm
import matplotlib.patheffects as pe
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
OUT.mkdir(parents=True, exist_ok=True)

BG      = "#07080A"
PANEL   = "#0C0E11"
PANEL2  = "#101318"
BORDER  = "#2B3037"
TEXT    = "#EAECEF"
MUTED   = "#9BA1A8"
DIM     = "#6B7178"
CYAN    = "#39E0E6"
SILVER  = "#C7CCD3"
AMBER   = "#E6B34A"
RED     = "#E2605C"

rng = np.random.default_rng(7)

# ---------------------------------------------------------------- data ------
FS = 140.0
T = 12.0
t = np.arange(0, T, 1 / FS)
# synthetic "EEG": alpha + beta + slow drift + mains + noise, with two word bursts
burst = np.exp(-((t - 3.2) ** 2) / 0.09) + np.exp(-((t - 7.9) ** 2) / 0.06)
raw = (14 * np.sin(2 * np.pi * 10 * t) * (0.6 + 0.9 * burst)
       + 7 * np.sin(2 * np.pi * 19.5 * t + 0.7) * (0.4 + burst)
       + 22 * np.sin(2 * np.pi * 0.35 * t)
       + 5 * np.sin(2 * np.pi * 50 * t)
       + rng.normal(0, 4.5, t.size))

def bandpass(sig, lo, hi):
    f = np.fft.rfftfreq(sig.size, 1 / FS)
    S = np.fft.rfft(sig)
    S[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(S, n=sig.size)

clean = bandpass(raw, 1.0, 40.0)
clean = clean - clean.mean()

# PSD (Welch-like, deterministic)
def psd(sig):
    n = 512
    win = np.hanning(n)
    segs = [sig[i:i + n] * win for i in range(0, sig.size - n, n // 2)]
    S = np.mean([np.abs(np.fft.rfft(s)) ** 2 for s in segs], axis=0)
    f = np.fft.rfftfreq(n, 1 / FS)
    return f, 10 * np.log10(S + 1e-9)

fp, Pp = psd(clean[140:])
mask = fp <= 45

# autocorrelation of the envelope -> period detection
env = np.convolve(np.abs(clean), np.ones(70) / 70, mode="same")
ac = np.correlate(env, env, mode="full")[env.size - 1:]
ac = ac / ac[0]
lag = np.arange(ac.size) / FS
peaks = [i for i in range(1, min(len(ac) - 1, 500))
         if ac[i] > ac[i - 1] and ac[i] > ac[i + 1] and ac[i] > 0.12]
period_idx = peaks[0] if peaks else 196
period_s = lag[period_idx]

# two "trinx" shapes, same gesture, different duration
def trinx(n, phase=0.0, squeeze=1.0):
    x = np.linspace(0, 1, n)
    y = (np.sin(2 * np.pi * 1.5 * x * squeeze + phase) * np.exp(-1.6 * (x - 0.35) ** 2)
         + 0.55 * np.sin(2 * np.pi * 3.1 * x * squeeze + 1.1 + phase) * np.exp(-2.2 * (x - 0.72) ** 2)
         + 0.25 * np.sin(2 * np.pi * 5.3 * x + 0.4))
    return (y - y.mean()) / (y.std() + 1e-9)

a = trinx(210, 0.0, 1.0)
b = trinx(150, 0.25, 1.25)

# DTW cost matrix + path
def dtw_path(x, y):
    n, m = len(x), len(y)
    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i, j] = abs(x[i - 1] - y[j - 1]) + min(D[i - 1, j], D[i, j - 1], D[i - 1, j - 1])
    i, j = n, m
    path = [(i, j)]
    while i > 1 or j > 1:
        step = np.argmin([D[i - 1, j - 1], D[i - 1, j], D[i, j - 1]])
        if step == 0:
            i, j = i - 1, j - 1
        elif step == 1:
            i -= 1
        else:
            j -= 1
        path.append((i, j))
    return D[1:, 1:], np.array(path[::-1])

D, path = dtw_path(a, b)

# feature vector (19 values, illustrated normalised magnitudes)
feat_labels = ["δ\n0.5–4", "θ\n4–8", "α\n8–13", "β\n13–30", "γ\n30–45",
               "MAV", "RMS", "ZCR", "LL", "SSC", "μ", "σ", "var", "p2p",
               "skew", "kurt", "mob", "cplx", "H"]
feat_vals = np.array([0.42, 0.55, 0.88, 0.61, 0.33,
                      0.52, 0.58, 0.47, 0.66, 0.44, 0.12, 0.58, 0.62, 0.71,
                      0.19, 0.36, 0.74, 0.48, 0.69])

# ---------------------------------------------------------------- canvas ----
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": TEXT,
    "axes.edgecolor": BORDER,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "font.size": 9,
})
W, H = 16.54, 23.39          # A2 portrait, inches
fig = plt.figure(figsize=(W, H), dpi=150)
fig.patch.set_facecolor(BG)

def fig_text(x, y, s, size=10, color=TEXT, weight="normal", ha="left", va="top",
             family="DejaVu Sans", style="normal", alpha=1.0, spacing=None, **kw):
    t = fig.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha,
                 va=va, family=family, style=style, alpha=alpha, **kw)
    return t

def panel(x, y, w, h, num, title, accent=CYAN):
    ax = fig.add_axes([x, y, w, h])
    ax.set_axis_off()
    ax.add_patch(FancyBboxPatch((0.006, 0.02), 0.988, 0.94,
                                boxstyle="round,pad=0.004,rounding_size=0.02",
                                transform=ax.transAxes, facecolor=PANEL,
                                edgecolor=BORDER, linewidth=1.1, zorder=0))
    ax.plot([0.03, 0.03], [0.06, 0.80], transform=ax.transAxes, color=accent,
            lw=2.2, solid_capstyle="round", zorder=2)
    ax.text(0.055, 0.905, num, transform=ax.transAxes, fontsize=11.5,
            color=accent, fontweight="bold", va="center", family="DejaVu Sans Mono")
    ax.text(0.135, 0.905, title, transform=ax.transAxes, fontsize=12.2,
            color=TEXT, fontweight="bold", va="center")
    return ax

def inner(ax, rect, **kw):
    """child axes inside a panel, rect in panel fraction coords (x,y,w,h)."""
    px, py, pw, ph = ax.get_position().bounds
    return fig.add_axes([px + rect[0] * pw, py + rect[1] * ph,
                         rect[2] * pw, rect[3] * ph], **kw)

def clean_axes(ax, grid=False, spine=False):
    ax.set_facecolor(PANEL2)
    for s in ax.spines.values():
        s.set_color(BORDER)
        s.set_visible(spine)
    if grid:
        ax.grid(True, color="#1B2026", lw=0.6, ls="-", zorder=0)
    ax.tick_params(labelsize=7.2, length=2.5, width=0.6)

def arrow(ax, p1, p2, color=SILVER, lw=1.5, style="-|>", rad=0.0, **kw):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=13,
                                 color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", **kw))

# =========================================================== HEADER =========
hdr = fig.add_axes([0.03, 0.935, 0.94, 0.055]); hdr.set_axis_off()
fig_text(0.030, 0.986, "PROJECT SYNAPSE  v1", size=44, weight="bold", color=TEXT)
fig_text(0.032, 0.9605,
         "A single-channel EEG and subvocal-EMG acquisition instrument with "
         "variable-length (“Trinx”) gesture decoding",
         size=15.2, color=SILVER)
fig_text(0.032, 0.9445,
         "Analog front-end  →  16-bit acquisition  →  Bluetooth transport  →  real-time desktop-class decoder",
         size=10.6, color=MUTED, family="DejaVu Sans Mono")

try:
    mark = plt.imread(str(OUT / "powered-by-mikey-hexoid-sys.png"))
    logo_ax = fig.add_axes([0.775, 0.944, 0.195, 0.048]); logo_ax.set_axis_off()
    logo_ax.imshow(mark)
except Exception as exc:              # poster still renders without the file
    print("logo not placed:", exc)

fig_text(0.968, 0.9375, "POWERED BY [mikey:hexoid-sys]", size=10.4, color=SILVER,
         weight="bold", ha="right", family="DejaVu Sans Mono", va="bottom")

fig.lines.append(plt.Line2D([0.03, 0.97], [0.9285, 0.9285], color=BORDER, lw=1.2))
fig_text(0.030, 0.9205, "mikey-7x", size=13.4, color=TEXT, weight="bold")
fig_text(0.325, 0.9212, "github.com/mikey-7x/Project-Synapse-v1-official-Real-Time-Brainwave-Decoder-with-Android",
         size=8.9, color=MUTED, family="DejaVu Sans Mono")
fig_text(0.970, 0.9205, "Experimental research prototype  ·  not a medical device",
         size=8.9, color=AMBER, ha="right")

# =========================================================== 01 CONCEPT =====
p1 = panel(0.030, 0.700, 0.452, 0.215, "01", "The problem: thoughts have no fixed clock")
fig_text(0.030 + 0.452 * 0.055, 0.700 + 0.215 * 0.845,
         "Fixed 2-second windows and zero-padding destroy the shape of a\n"
         "biological gesture: the same subvocalised word may last 0.8 s once\n"
         "and 1.3 s the next. Synapse instead treats a gesture as a\n"
         "time-elastic structure — a Trinx — and matches its topology\n"
         "after amplitude normalisation.",
         size=9.6, color=MUTED, va="top", linespacing=1.55)

axA = inner(p1, [0.09, 0.13, 0.82, 0.44]); axA.set_axis_off()
axA.set_xlim(0, 10); axA.set_ylim(-1.75, 1.35)
x1 = np.linspace(0.4, 4.1, 200); x2 = np.linspace(5.6, 9.5, 200)
axA.plot(x1, trinx(200, 0, 1.0) * 0.62, color=CYAN, lw=1.7)
axA.plot(x2, trinx(200, 0.25, 1.25) * 0.62, color=SILVER, lw=1.7)
axA.annotate("", xy=(4.1, -1.02), xytext=(0.4, -1.02),
             arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=0.8, mutation_scale=8))
axA.annotate("", xy=(9.5, -1.02), xytext=(5.6, -1.02),
             arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=0.8, mutation_scale=8))
axA.text(2.25, -1.12, "attempt 1 · 1.50 s", color=DIM, fontsize=7.4, ha="center", va="top")
axA.text(7.55, -1.12, "attempt 2 · 1.07 s", color=DIM, fontsize=7.4, ha="center", va="top")
axA.text(4.85, 1.12, "same Trinx", color=CYAN, fontsize=8.4, ha="center", weight="bold")

# =========================================================== 02 ARCH ========
p2 = panel(0.510, 0.700, 0.460, 0.215, "02", "System architecture", accent=SILVER)
axB = inner(p2, [0.045, 0.10, 0.915, 0.72]); axB.set_axis_off()
axB.set_xlim(0, 100); axB.set_ylim(0, 100)

def block(ax, x, y, w, h, title, sub="", fc=PANEL2, ec=BORDER, tc=TEXT, sc=MUTED, fs=8.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=2.0",
                                facecolor=fc, edgecolor=ec, lw=1.0))
    ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center",
            fontsize=fs, color=tc, fontweight="bold")
    if sub:
        ax.text(x + w / 2, y + h * 0.24, sub, ha="center", va="center",
                fontsize=fs - 2.1, color=sc, family="DejaVu Sans Mono")

block(axB, 1, 62, 21, 26, "Ag/AgCl", "Fp1 · Fp2 · mastoid", ec="#3A4A55")
block(axB, 26, 62, 21, 26, "INA128", "G = 501")
block(axB, 51, 62, 21, 26, "OPA2134", "HPF 0.48 Hz")
block(axB, 76, 62, 22, 26, "Rectifier", "0–5 V split")
block(axB, 76, 20, 22, 26, "ADS1115", "16-bit · 860 SPS")
block(axB, 51, 20, 21, 26, "Nano", "140 Hz loop")
block(axB, 26, 20, 21, 26, "HC-05", "9600 baud")
block(axB, 1, 20, 21, 26, "TCP 5656", "0xAA 0x55", ec="#3A4A55")
for x1_, x2_, y_ in ((22.4, 25.6, 75), (47.4, 50.6, 75), (72.4, 75.6, 75)):
    arrow(axB, (x1_, y_), (x2_, y_), color=SILVER, lw=1.2)
arrow(axB, (87, 61.5), (87, 46.5), color=SILVER, lw=1.2)
for x1_, x2_, y_ in ((75.6, 72.4, 33), (50.6, 47.4, 33), (25.6, 22.4, 33)):
    arrow(axB, (x1_, y_), (x2_, y_), color=SILVER, lw=1.2)
axB.text(50, 6, "user-space Python · Tk GUI · NumPy / SciPy / scikit-learn / XGBoost / TensorFlow-Keras",
         ha="center", fontsize=7.6, color=DIM, family="DejaVu Sans Mono")
axB.add_patch(FancyBboxPatch((0.5, 1.0), 99, 11.0, boxstyle="round,pad=0.4,rounding_size=2",
                             facecolor="#0E1418", edgecolor="#20303A", lw=0.9))
axB.text(50, 9.6, "HOST  ·  Trinx segmentation · 19-feature extraction · DTW bank · CNN-LSTM / CNN-GRU · XGB / RF / SVM / KNN / LR",
         ha="center", va="center", fontsize=6.5, color=CYAN, family="DejaVu Sans Mono")
axB.text(50, 4.4, "storage  ·  /storage/emulated/0/Documents/Project_Synapse  ·  EEG_Data/  ·  Models/",
         ha="center", va="center", fontsize=6.2, color=DIM, family="DejaVu Sans Mono")

# =========================================================== 03 FRONT-END ===
p3 = panel(0.030, 0.487, 0.452, 0.196, "03", "Analog front-end, stage by stage")
axC = inner(p3, [0.055, 0.34, 0.90, 0.42]); axC.set_axis_off()
axC.set_xlim(0, 100); axC.set_ylim(0, 30)
stages = [("electrodes", "µV"), ("INA128\n×501", "2 µV – 5 mV"),
          ("HPF\n0.48 Hz", "−DC"), ("LPF\n106 Hz", "−EMG/RFI"),
          ("split\nA0 / A1", "0–5 V")]
xs = np.linspace(1, 62, len(stages))
for (lab, sub), x in zip(stages, xs):
    axC.add_patch(FancyBboxPatch((x, 8), 16.5, 13, boxstyle="round,pad=0.4,rounding_size=1.6",
                                 facecolor=PANEL2, edgecolor=BORDER, lw=1.0))
    axC.text(x + 8.25, 16.4, lab, ha="center", va="center", fontsize=8.0,
             color=TEXT, fontweight="bold", linespacing=1.25)
    axC.text(x + 8.25, 11.3, sub, ha="center", va="center", fontsize=6.4,
             color=MUTED, family="DejaVu Sans Mono")
    if x < xs[-1]:
        arrow(axC, (x + 16.9, 14.5), (x + 20.4, 14.5), color=SILVER, lw=1.0)
axC.add_patch(FancyBboxPatch((82.5, 8), 14.0, 13, boxstyle="round,pad=0.4,rounding_size=1.6",
                             facecolor="#0E1418", edgecolor=CYAN, lw=1.0))
axC.text(89.5, 16.4, "ADS1115", ha="center", va="center", fontsize=8.0, color=CYAN,
         fontweight="bold")
axC.text(89.5, 11.3, "16-bit", ha="center", va="center", fontsize=6.4, color=MUTED,
         family="DejaVu Sans Mono")
arrow(axC, (78.4, 14.5), (81.8, 14.5), color=CYAN, lw=1.0)
fig_text(0.030 + 0.452 * 0.055, 0.487 + 0.196 * 0.30,
         "Dual supply: 3.7 V Li-Po → MT3608 (+5 V) and LM2776 (−5 V).  "
         "Protection: 1N5819 clamps and RC RFI filter ahead of the INA128.",
         size=8.2, color=MUTED, va="top", linespacing=1.5)
fig_text(0.030 + 0.452 * 0.055, 0.487 + 0.196 * 0.175,
         "Two rectified streams let a unipolar 0–5 V ADC observe both halves of a bipolar EEG signal.",
         size=8.2, color=MUTED, va="top", linespacing=1.5)

# =========================================================== 04 PROTOCOL ====
p4 = panel(0.510, 0.487, 0.460, 0.196, "04", "Binary link and timing budget", accent=SILVER)
axD = inner(p4, [0.05, 0.47, 0.90, 0.27]); axD.set_axis_off()
axD.set_xlim(0, 100); axD.set_ylim(0, 24)
cells = [("0xAA", "sync", CYAN), ("0x55", "sync", CYAN),
         ("A0 hi", "int16", SILVER), ("A0 lo", "int16", SILVER),
         ("A1 hi", "int16", SILVER), ("A1 lo", "int16", SILVER)]
cw = 13.2
for i, (val, sub, col) in enumerate(cells):
    x = 6 + i * (cw + 1.4)
    axD.add_patch(Rectangle((x, 7), cw, 13, facecolor="#12171C", edgecolor=col, lw=1.0))
    axD.text(x + cw / 2, 16.6, val, ha="center", va="center", fontsize=8.0,
             color=col, family="DejaVu Sans Mono", fontweight="bold")
    axD.text(x + cw / 2, 10.4, sub, ha="center", va="center", fontsize=6.4,
             color=MUTED, family="DejaVu Sans Mono")
    if i < len(cells) - 1:
        axD.plot([x + cw + 0.2, x + cw + 1.2], [13.5, 13.5], color=DIM, lw=0.8)
axD.text(6, 3.2, "6-byte frame · big-endian · differential channel = A0 − A1 (common-mode rejection in software)",
         fontsize=7.2, color=MUTED, family="DejaVu Sans Mono")

axD2 = inner(p4, [0.05, 0.12, 0.90, 0.28]); axD2.set_axis_off()
axD2.set_xlim(0, 100); axD2.set_ylim(0, 20)
rows = [("sample rate", "140.0 Hz", "micros()-paced 7 142 µs"),
        ("ADC rate", "860 SPS", "ADS1115 internal, oversampled"),
        ("payload", "840 B/s", "140 frames × 6 bytes"),
        ("link", "9 600 baud", "HC-05 SPP → TCP bridge"),
        ("UI buffer", "560 samples", "4.0 s rolling window")]
for i, (k, v, note) in enumerate(rows):
    y = 17 - i * 3.6
    axD2.text(0, y, k, fontsize=7.4, color=MUTED, va="center")
    axD2.text(26, y, v, fontsize=7.8, color=CYAN, va="center", family="DejaVu Sans Mono",
              fontweight="bold")
    axD2.text(52, y, note, fontsize=7.0, color=DIM, va="center", family="DejaVu Sans Mono")

# =========================================================== 05 SIGNAL ======
p5 = panel(0.030, 0.262, 0.452, 0.208, "05", "Signal conditioning and spectral view")
axE1 = inner(p5, [0.075, 0.585, 0.885, 0.245])
clean_axes(axE1, grid=True)
axE1.plot(t, raw, color=DIM, lw=0.7, label="raw (A0 − A1)")
axE1.plot(t, clean, color=CYAN, lw=0.8, label="1–40 Hz + 50 Hz notch")
axE1.set_xlim(0, T); axE1.set_yticks([])
axE1.legend(loc="upper right", fontsize=6.6, frameon=False, ncol=2,
            labelcolor=MUTED, handlelength=1.6)
axE1.text(0.006, 0.94, "raw vs conditioned input · 12 s", transform=axE1.transAxes,
          fontsize=6.6, color=MUTED, va="top")

axE2 = inner(p5, [0.075, 0.16, 0.46, 0.345])
clean_axes(axE2, grid=True)
axE2.plot(fp[mask], Pp[mask], color=SILVER, lw=1.2)
bands = [(0.5, 4, "δ", "#2C3A46"), (4, 8, "θ", "#31424B"),
         (8, 13, "α", "#3A4E58"), (13, 30, "β", "#2F4450"), (30, 45, "γ", "#28343D")]
axE2.set_xlim(0.5, 45)
axE2.set_ylim(Pp[mask].min() - 4, Pp[mask].max() + 9)
for lo, hi, name, col in bands:
    axE2.axvspan(lo, hi, color=col, alpha=0.55, lw=0)
    axE2.text((lo + hi) / 2, axE2.get_ylim()[1] - 4.5, name, ha="center", va="top",
              fontsize=6.8, color=MUTED)
axE2.set_xlabel("frequency (Hz)", fontsize=6.8, labelpad=2)
axE2.set_ylabel("PSD (dB)", fontsize=6.8, labelpad=2)
axE2.set_title("Welch PSD · five band powers", fontsize=7.0, color=MUTED, loc="left", pad=2)

axE3 = inner(p5, [0.60, 0.16, 0.36, 0.345])
clean_axes(axE3, grid=True)
axE3.plot(lag[:520], ac[:520], color=CYAN, lw=1.1)
axE3.axvline(period_s, color=AMBER, lw=1.0, ls="--")
axE3.annotate(f"T = {period_s:.2f} s", xy=(period_s, ac[period_idx]),
              xytext=(period_s + 0.7, ac[period_idx] - 0.05), fontsize=7.2,
              color=AMBER,
              arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.7))
axE3.set_xlim(0, 3.7); axE3.set_xlabel("lag (s)", fontsize=7, labelpad=2)
axE3.set_title("envelope autocorrelation → period T", fontsize=7.0,
               color=MUTED, loc="left", pad=2)

# =========================================================== 06 TRINX =======
p6 = panel(0.510, 0.262, 0.460, 0.208, "06", "Trinx extraction and elastic matching", accent=SILVER)
axF1 = inner(p6, [0.055, 0.62, 0.90, 0.26]); axF1.set_axis_off()
axF1.set_xlim(0, 100); axF1.set_ylim(0, 20)
seg = clean[int(1.0 * FS):int(9.0 * FS)]
seg = (seg - seg.mean()) / (np.abs(seg).max() + 1e-9)
dec = max(1, seg.size // 700)
seg = seg[::dec][:700]
axF1.plot(np.linspace(0, 100, seg.size), 10 + seg * 6.4, color=SILVER, lw=0.8)
slice_w = period_s / 8.0 * 100.0
for k in range(int(8 / period_s) + 1):
    x0 = k * slice_w
    if x0 + slice_w > 100:
        break
    axF1.add_patch(Rectangle((x0, 3.0), slice_w, 14.0, facecolor=CYAN, alpha=0.06,
                             edgecolor=CYAN, lw=0.5, ls=(0, (2, 2))))
axF1.text(1, 1.0, "recording sliced at the detected period · energy gate rejects silent slices",
          fontsize=6.8, color=MUTED, family="DejaVu Sans Mono", va="bottom")

axF2 = inner(p6, [0.055, 0.175, 0.40, 0.395])
clean_axes(axF2, grid=False)
axF2.plot(np.linspace(0, 1, a.size), a, color=CYAN, lw=1.3)
axF2.plot(np.linspace(0, 1, b.size), b - 3.6, color=SILVER, lw=1.3)
axF2.set_yticks([]); axF2.set_xticks([0, 0.5, 1])
axF2.set_title("two samples of one label, z-normalised", fontsize=7.0, color=MUTED, loc="left", pad=2)
axF2.set_xlabel("normalised time", fontsize=7, labelpad=2)
axF2.set_ylim(-6.2, 3.0)

axF3 = inner(p6, [0.545, 0.175, 0.40, 0.395])
clean_axes(axF3, grid=False)
Z = np.log1p(np.nan_to_num(D, nan=0.0, posinf=0.0))
vmax = float(np.percentile(Z, 96))
im = axF3.imshow(Z, origin="lower", cmap="magma", aspect="auto", vmax=vmax,
                 extent=[0, Z.shape[1], 0, Z.shape[0]], interpolation="nearest")
axF3.plot(path[:, 1], path[:, 0], color=CYAN, lw=1.2, alpha=0.95)
axF3.set_title("DTW cost surface + warp path", fontsize=7.0, color=MUTED,
               loc="left", pad=2)
axF3.set_xlabel("query frame", fontsize=7, labelpad=2)
axF3.set_ylabel("reference frame", fontsize=7, labelpad=2)
axF3.tick_params(labelsize=6.4)

# =========================================================== 07 DECODERS ====
p7 = panel(0.030, 0.052, 0.452, 0.196, "07", "Decoder stack")
axG = inner(p7, [0.06, 0.30, 0.88, 0.44]); axG.set_axis_off()
axG.set_xlim(0, 100); axG.set_ylim(0, 100)
rows = [("Trinx-DTW", "z-normalised DTW memory bank, nearest neighbour", CYAN),
        ("CNN-LSTM", "Conv1D(32) → BiLSTM(64) → LSTM(32) → softmax", SILVER),
        ("CNN-GRU", "Conv1D(32) → BiGRU(64) → GRU(32) → softmax", SILVER),
        ("Classical", "XGBoost · RandomForest · SVM-RBF · KNN · LogReg", MUTED)]
for i, (name, desc, col) in enumerate(rows):
    y = 84 - i * 23
    axG.add_patch(FancyBboxPatch((1, y - 9), 97, 17, boxstyle="round,pad=0.4,rounding_size=2",
                                 facecolor=PANEL2, edgecolor=BORDER, lw=0.9))
    axG.text(4, y - 0.5, name, fontsize=8.6, color=col, fontweight="bold", va="center")
    axG.text(27, y - 0.5, desc, fontsize=7.0, color=MUTED, va="center",
             family="DejaVu Sans Mono")
fig_text(0.030 + 0.452 * 0.06, 0.052 + 0.196 * 0.245,
         "Acceptance: a label is printed only at ≥ 90 % confidence; otherwise it is rejected.\n"
         "Confidence is a distance heuristic, not a calibrated probability.",
         size=8.0, color=AMBER, va="top", linespacing=1.5)

# =========================================================== 08 FEATURES ====
p8 = panel(0.510, 0.052, 0.460, 0.196, "08", "19-value feature vector", accent=SILVER)
axH = inner(p8, [0.055, 0.30, 0.90, 0.46])
clean_axes(axH, grid=True)
cols = [CYAN] * 5 + [SILVER] * 14
axH.bar(range(len(feat_vals)), feat_vals, color=cols, width=0.72,
        edgecolor="none", alpha=0.9)
axH.set_xticks(range(len(feat_labels)))
axH.set_xticklabels(feat_labels, fontsize=6.0, linespacing=0.85)
axH.set_ylim(0, 1.05); axH.set_yticks([0, 1])
axH.set_ylabel("normalised magnitude", fontsize=6.8, labelpad=2)
axH.set_title("5 band powers (cyan) + 14 descriptors (silver)",
              fontsize=7.0, color=MUTED, loc="left", pad=2)

# =========================================================== 09 LIMITS ======
p9 = fig.add_axes([0.030, 0.027, 0.940, 0.0235]); p9.set_axis_off()
p9.add_patch(FancyBboxPatch((0.004, 0.04), 0.992, 0.92,
                            boxstyle="round,pad=0.003,rounding_size=0.02",
                            transform=p9.transAxes, facecolor="#0E0A0A",
                            edgecolor="#4A2A2A", lw=1.1))
p9.text(0.012, 0.70, "LIMITS & SAFETY", transform=p9.transAxes, fontsize=9.6,
        color=RED, fontweight="bold", va="center")
p9.text(0.105, 0.70,
        "Not a medical device: no clinical validation, no regulatory certification, no diagnostic claim. "
        "Single subject-scale, single-channel data; no published accuracy is claimed here.",
        transform=p9.transAxes, fontsize=8.0, color="#D8B4B2", va="center")
p9.text(0.012, 0.26,
        "BATTERY POWER ONLY while electrodes touch a person — never mains-referenced equipment. "
        "Figures on this poster are synthetic illustrations of the pipeline, not measured results.",
        transform=p9.transAxes, fontsize=8.0, color="#B99B99", va="center")

# =========================================================== FOOTER =========
fig.lines.append(plt.Line2D([0.03, 0.97], [0.0215, 0.0215], color=BORDER, lw=1.0))
fig_text(0.030, 0.0165, "Project Synapse v1", size=10.2, weight="bold", color=TEXT)
fig_text(0.145, 0.0175, "Created by mikey-7x  ·  strict personal & educational licence",
         size=8.4, color=MUTED)
fig_text(0.970, 0.0165, "POWERED BY [mikey:hexoid-sys]", size=10.0, weight="bold",
         color=SILVER, ha="right", family="DejaVu Sans Mono")
fig_text(0.030, 0.0060, "github.com/mikey-7x  ·  github.com/mikey-7x?tab=repositories  ·  youtube.com/@mikey-7x",
         size=7.8, color=DIM, family="DejaVu Sans Mono")
fig_text(0.970, 0.0060, "Copyright © 2026 mikey-7x. All rights reserved.",
         size=7.8, color=DIM, ha="right")

fig.savefig(OUT / "scientific-poster.png", facecolor=BG, dpi=150)
fig.savefig(OUT / "scientific-poster.pdf", facecolor=BG)
print("poster written:", (OUT / "scientific-poster.png").stat().st_size)
