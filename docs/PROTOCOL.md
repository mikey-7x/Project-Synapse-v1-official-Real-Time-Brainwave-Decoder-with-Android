# Wire protocol and timing budget

**POWERED BY [mikey:hexoid-sys]** · Created by mikey-7x — Yogesh R. Chauhan

## Frame format

Every sample is a fixed six-byte frame written by the firmware:

| Offset | Bytes | Field | Meaning |
| --- | --- | --- | --- |
| 0 | 1 | `0xAA` | sync word, first byte |
| 1 | 1 | `0x55` | sync word, second byte |
| 2–3 | 2 | `A0` | ADS1115 single-ended channel 0, big-endian signed 16-bit |
| 4–5 | 2 | `A1` | ADS1115 single-ended channel 1, big-endian signed 16-bit |

The host computes the differential sample as `A0 − A1` (`struct.unpack('>hh', ...)`), so the
recorded channel is a software-reconstructed bipolar signal.

## Timing

| Quantity | Value | Where it comes from |
| --- | --- | --- |
| Host sample rate | **140.0 Hz** | `sampleInterval = 7142 µs` in the firmware loop |
| ADC internal rate | 860 SPS | `RATE_ADS1115_860SPS` |
| ADC range | ±6.144 V | `GAIN_TWOTHIRDS` |
| Frame size | 6 bytes | 2 sync + 2 + 2 |
| Payload | 840 B/s | 140 × 6 |
| Serial link | 9600 baud | `Serial.begin(9600)` for the HC-05 |
| UI buffer | 560 samples | 4.0 s rolling window in the host |

The loop is paced with `micros()` rather than `delay()`, so I²C reads and serial writes do not
accumulate drift, and the host assumes the nominal 140 Hz rate when it builds time and
frequency axes.

## Bandwidth budget

At 9 600 baud with 8-N-1 framing, one byte costs ten bit-times, so the link carries at most
960 B/s. A 140 Hz frame rate needs 840 B/s — about **87 % of the link**. That is a real
constraint, not a theoretical one:

- any retransmission, Bluetooth handshake or buffering hiccup creates gaps;
- the HC-05 buffer adds latency, which is why the receiving bridge must not block;
- a single malformed frame shifts the phase of everything after it unless the parser
  re-synchronises on `0xAA 0x55`.

If you raise the sample rate, raise the baud rate at the same time. 115 200 baud and 500 Hz
sampling would give a much healthier margin, and the parser already tolerates it.

## Parser behaviour

```python
sync = buffer.find(b'\xAA\x55')
if sync == -1:            # keep a trailing 0xAA, drop the rest
    ...
elif sync > 0:            # discard leading noise
    del buffer[:sync]
a0, a1 = struct.unpack('>hh', buffer[2:6])
sample = a0 - a1
```

The implementation reads in 8 192-byte chunks, drains as many complete frames as are
available, rolls them into the display buffer and — when recording — appends them to the
session list. Frames are never partially consumed, so a burst of delayed data (the classic
"tsunami" after a Bluetooth stall) is parsed in one pass instead of freezing the UI.

## Transport map

```text
HC-05 (RFCOMM/SPP) ──▶ Android Bluetooth socket ──▶ local TCP bridge on 127.0.0.1:5656 ──▶ synapse.py
```

The application only ever opens `127.0.0.1:5656`; it does not talk Bluetooth directly. Any
bridge that forwards the serial stream to that port works, which keeps the decoder portable
between Android and Linux.

## Versioning rule

If you change the frame (add a channel, change endianness, add a CRC), version the format and
update both the firmware and the parser in the same change. The current format has no CRCs:
the two-byte sync word is the only integrity check, which is acceptable at 9 600 baud over a
short, local link and not acceptable over anything less reliable.
