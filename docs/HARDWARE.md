# Hardware

**POWERED BY [mikey:hexoid-sys]** · Created by mikey-7x — Yogesh R. Chauhan

> Battery power only while electrodes touch a person. See [SAFETY.md](../SAFETY.md).

## Bill of materials

| Function | Part | Notes |
| --- | --- | --- |
| Instrumentation amplifier | INA128U/2K5 (SOIC-8) | First gain stage, G = 501 with R_g = 100 Ω |
| Precision op-amps | 2 × OPA2134UA/2K5 | Filter, second gain stage, rectifiers |
| ADC | ADS1115 module | 16-bit, I²C, ±6.144 V range selected |
| Microcontroller | Arduino Nano (ATmega328P, CH340) | 140 Hz acquisition loop |
| Radio | HC-05 (6-pin) | Classic Bluetooth SPP, 9600 baud |
| Battery | 3.7 V 500 mAh Li-Po | Isolated supply for the whole chain |
| Boost | MT3608 | 3.7 V → +5 V |
| Inverter | LM2776DBVR | +5 V → −5 V for a true split supply |
| Electrodes | Ag/AgCl cup electrodes ×3 | Reference plus differential pair |
| Passives | 10 nF polystyrene, 1 nF/100 V 0805, 1 µF X7R 1210, 10 µF/25 V 1210, 100 nF X7R 1206 | Filter and decoupling network |
| Resistors | 0.1 % SMD: 100 Ω, 1 k, 1.5 k, 4.7 k, 10 k, 330 k, 1 M | Gain, filtering, bias |
| Diodes | 10 × 1N5819 (DO-214AC), 1N4148 | Input clamps, precision rectifiers |

Schematic, layout and board photographs are in the repository root: `ps.jpg` (schematic),
`psl.jpg` / `psl2.jpg` (layout), `psl4.jpg` / `psl5.jpg` (assembled board), `pss.jpg`
(flow chart).

## Stage-by-stage design

### 1 · Input protection and RFI filter

A 4.7 kΩ series resistor with 10 nF / 1 nF capacitors forms a passive low-pass network ahead
of the INA128; 1N5819 Schottky clamps divert static discharge away from the amplifier inputs.
This is protection, not signal conditioning: it does not make an unsafe source safe.

### 2 · First gain stage — INA128

The INA128 gain is set by one resistor:

```text
G = 1 + 50 kΩ / R_g = 1 + 50 000 / 100 = 501  (≈ 54 dB)
```

A 20 µV EEG feature therefore arrives at the next stage at about 10 mV — large enough to be
filtered and digitised without being dominated by the op-amp's own noise contribution.

### 3 · DC blocking

1 µF into 330 kΩ gives:

```text
f_c = 1 / (2π · R · C) = 1 / (2π · 330e3 · 1e-6) ≈ 0.48 Hz
```

This removes the skin-battery half-cell offset (tens to hundreds of millivolts) that would
otherwise consume the entire amplifier headroom.

### 4 · Second stage and active low-pass

The OPA2134 provides additional gain and an active low-pass response designed for roughly
**106 Hz**, intended to reject muscle (EMG) activity and radio-frequency pickup above the
band of interest. See the anti-alias note below.

### 5 · Splitter and precision rectifiers

The ADS1115 module measures 0 V to +6.144 V, not negative voltages. The conditioned bipolar
signal is split and precision-rectified into two unipolar streams, presented on **A0** and
**A1**. The host reconstructs a differential channel as `A0 − A1`; subtracting in software
also cancels common-mode drift that survived the analog stages.

## Power

```text
3.7 V Li-Po ──▶ MT3608 ──▶ +5 V ──┬──▶ analog stages
                                  └──▶ LM2776 ──▶ −5 V ──▶ analog stages
```

The Nano and the HC-05 run from the same battery through their own regulators. There is no
galvanic connection to mains anywhere in the chain during a session.

## Bring-up checklist

1. Power the board from a current-limited bench supply with **no electrodes connected**.
2. Confirm +5 V and −5 V rails, then check for excessive current draw.
3. Inject a known 10 Hz, 0.5 mV test signal at the input and confirm gain and phase.
4. Sweep 0.2–200 Hz and record the measured −3 dB points; they will not match the design
   values exactly with 5 % capacitors.
5. Confirm both A0 and A1 stay inside 0–5 V for the largest expected input.
6. Only then attach electrodes — on battery — following [SAFETY.md](../SAFETY.md).

## Known hardware caveats

- **Anti-alias margin.** The host samples at 140 Hz, so the Nyquist frequency is 70 Hz, while
  the analog low-pass is designed near 106 Hz. Content between roughly 70 Hz and 106 Hz can
  therefore alias into the sampled band. A lower analog cutoff, an additional passive RC, or
  a higher sample rate would fix this; the firmware is unchanged in this revision, so the
  caveat is documented rather than hidden.
- **Single channel.** One differential pair means no spatial information, no common-mode
  rejection beyond what the INA128 and the software subtraction provide, and no ability to
  separate cortical from muscular or ocular sources.
- **Electrode quality dominates.** Contact impedance, gel drying and motion produce artefacts
  far larger than the signals of interest.
