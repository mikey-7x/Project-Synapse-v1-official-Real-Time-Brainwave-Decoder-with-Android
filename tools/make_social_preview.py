#!/usr/bin/env python3
"""Project Synapse v1 - repository social preview generator (1280x640).

POWERED BY [mikey:hexoid-sys] - Created by mikey-7x
Copyright (c) 2026 mikey-7x. All rights reserved.
Licence: mikey-7x Strict Personal & Educational Use Licence (see LICENSE.md).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1280, 640
BG = (7, 8, 10)
PANEL = (12, 14, 17)
CYAN = (57, 224, 230)
SILVER = (199, 204, 211)
TEXT = (234, 236, 239)
MUTED = (155, 161, 168)
DIM = (107, 113, 120)
AMBER = (230, 179, 74)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
for y in range(H):
    v = int(24 - 16 * y / H)
    d.line([(0, y), (W, y)], fill=(v, v, v + 2))
for i in range(70):
    a = int(16 * (i / 70))
    d.rectangle([i, i, W - 1 - i, H - 1 - i], outline=(a + 8, a + 8, a + 10))
d.line([(44, 40), (W - 44, 40)], fill=(56, 59, 63), width=1)
d.line([(44, H - 40), (W - 44, H - 40)], fill=(56, 59, 63), width=1)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f_kick = ImageFont.truetype(MONO, 20)
f_title = ImageFont.truetype(BOLD, 66)
f_ver = ImageFont.truetype(BOLD, 34)
f_sub = ImageFont.truetype(REG, 23)
f_small = ImageFont.truetype(MONO, 18)
f_tiny = ImageFont.truetype(MONO, 16)
f_bold = ImageFont.truetype(BOLD, 20)

x = 60
d.text((x, 78), "SINGLE-CHANNEL BIOSIGNAL INSTRUMENT", font=f_kick, fill=MUTED)
d.text((x, 112), "PROJECT SYNAPSE", font=f_title, fill=TEXT)
d.text((x + 4, 190), "v1", font=f_ver, fill=SILVER)
d.line([(x, 248), (x + 520, 248)], fill=(74, 77, 82), width=2)
d.text((x, 264), "EEG / subvocal-EMG acquisition  ·  Trinx decoding", font=f_sub, fill=(206, 209, 214))
d.text((x, 300), "INA128  ·  ADS1115 16-bit  ·  140 Hz  ·  DTW  ·  CNN-LSTM/GRU", font=f_tiny, fill=DIM)
d.text((x, 340), "POWERED BY [mikey:hexoid-sys]", font=f_bold, fill=SILVER)
d.text((x, 372), "Created by mikey-7x", font=f_small, fill=MUTED)
d.text((x, 404), "Experimental prototype · not a medical device", font=f_tiny, fill=AMBER)
d.text((x, 470), "github.com/mikey-7x/Project-Synapse-v1-official-", font=f_tiny, fill=(122, 126, 132))
d.text((x, 492), "Real-Time-Brainwave-Decoder-with-Android", font=f_tiny, fill=(122, 126, 132))

# waveform motif on the right
rng = np.random.default_rng(11)
t = np.linspace(0, 6 * np.pi, 520)
sig = (np.sin(t) * 0.55 + 0.35 * np.sin(2.7 * t + 1) + 0.18 * np.sin(6.1 * t) * np.exp(-((t - 9) ** 2) / 8)
       + rng.normal(0, 0.06, t.size))
sig = (sig - sig.mean()) / (np.abs(sig).max() + 1e-9)
cx, cy, cw, ch = 700, 250, 500, 210
pts = [(cx + i * cw / sig.size, cy + ch / 2 - s * ch * 0.42) for i, s in enumerate(sig)]
d.line(pts, fill=DIM, width=1)
clean = np.convolve(sig, np.ones(9) / 9, mode="same")
pts2 = [(cx + i * cw / clean.size, cy + ch / 2 - s * ch * 0.42) for i, s in enumerate(clean)]
d.line(pts2, fill=CYAN, width=2)
d.text((cx, cy - 26), "conditioned trace", font=f_tiny, fill=DIM)
for i in range(4):
    xx = cx + 30 + i * 110
    d.rectangle([xx, cy + ch + 18, xx + 78, cy + ch + 18 + 8 + i * 6], outline=(60, 66, 72))
d.text((cx, cy + ch + 62), "band powers · Trinx slices · DTW cost", font=f_tiny, fill=DIM)

mark = Image.open(OUT / "mikey-hexoid-sys-mark.png").convert("RGBA")
mh = 118
mark = mark.resize((int(mark.width * mh / mark.height), mh), Image.LANCZOS)
img.paste(mark, (W - 60 - mark.width, 62), mark)

img.save(OUT / "github-social-preview.png", optimize=True)
print("social preview written:", (OUT / "github-social-preview.png").stat().st_size, "bytes")
