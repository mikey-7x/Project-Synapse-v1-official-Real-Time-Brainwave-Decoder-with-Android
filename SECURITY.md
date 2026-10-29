# Security policy

**POWERED BY [mikey:hexoid-sys]**

## Supported versions

| Version | Supported |
| --- | --- |
| 1.0.0 (current) | Yes |

## Scope

This is a local, single-user application. The realistic security and safety issues are:

- **Electrical safety** — any change that weakens the battery-only isolation rule, the
  rectifier stage or the 0–5 V ADC limit is treated as a critical issue. See
  [SAFETY.md](SAFETY.md).
- **Biological data** — recordings are stored unencrypted under
  `/storage/emulated/0/Documents/Project_Synapse`. Treat that folder as personal data; do not
  publish other people's recordings.
- **Network surface** — the GUI connects only to `127.0.0.1:5656`. Do not expose that port,
  bind the bridge to a public interface, or run a bridge you did not start.
- **Untrusted inputs** — the binary parser consumes whatever the bridge sends; a malformed
  stream should never crash the app or write outside the data folders. Reports of such
  behaviour are welcome.
- **Model files** — `.keras` and `.joblib` files can execute code when loaded. Only load models
  you trained or reviewed.

## Not in scope

- Vulnerabilities in TensorFlow, scikit-learn, XGBoost, Termux, PRoot or other third-party
  components — report those upstream.
- Physical injury from misuse contrary to the safety document.
- Experimental behaviour presented as certified: that is a documentation issue, not a
  vulnerability, and it will be treated as a bug.

## Reporting

Do not open a public issue for a safety or security problem. Contact the author privately
through https://github.com/mikey-7x with:

- affected file and version;
- steps to reproduce;
- impact (shock risk, data exposure, corrupted model, crash);
- any suggested fix.

You will get an acknowledgement as soon as reasonably possible.
