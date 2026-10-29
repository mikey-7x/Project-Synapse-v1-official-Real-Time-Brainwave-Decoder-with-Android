# Safety

**POWERED BY [mikey:hexoid-sys]** · Created by mikey-7x — Yogesh R. Chauhan

> [!CAUTION]
> This is an experimental electronics prototype, not a medical device. It has no electrical
> isolation, no regulatory approval and no clinical validation. You are responsible for every
> person who touches an electrode connected to it.

## 1. Electrical isolation — the non-negotiable rule

- **Battery power only** while electrodes are attached to a person.
- Never connect the device to mains-powered equipment, a mains charger, a desktop computer
  on mains supply, an oscilloscope, a soldering iron's earthed tip or any instrument that is
  referenced to earth while electrodes are on a body.
- Charging and measuring are separate activities. Unplug the charger, disconnect USB, then
  attach electrodes.
- Keep the analog board, the Nano and the phone electrically independent of each other
  except through the HC-05 radio link.

The original project documentation says the same thing in stronger terms; it remains true:
a fault in a mains-referenced path can put dangerous current through the electrode path.

## 2. People

- Do not use this device on yourself or anyone else if either of you has a pacemaker,
  implantable defibrillator, neurostimulator, cochlear implant, insulin pump or any other
  implanted electronic device.
- Do not use it on broken, inflamed, infected or recently shaved-irritated skin.
- Stop immediately if there is stinging, burning, itching, redness or headache. Remove the
  electrodes, wash the area, and do not continue that session.
- Do not use it during driving, operating machinery, bathing, or while exercising to
  exhaustion.
- Do not use it on children, on anyone unable to consent, or on an unconscious person.
- Obtain informed consent before recording anyone other than yourself, and explain that the
  output has no medical meaning.

## 3. Skin and electrodes

- Clean the site with an alcohol wipe and let it dry; apply medical conductive gel so the
  Ag/AgCl electrode makes a stable, low-impedance contact.
- Use intact electrodes. Discard electrodes with dried gel, corroded silver or damaged leads.
- Never bridge two electrode sites with gel or sweat; keep the reference electrode on the
  mastoid or collarbone, not across the chest.
- Remove electrodes gently after the session and clean the skin.
- Treat every recording as personal data belonging to the person who produced it.

## 4. Hardware practice

- Verify the ±5 V rails and the 0–5 V signal range at the ADC inputs with the electrodes
  **disconnected** before connecting anything to a person.
- Confirm the rectifier stage never lets a negative voltage reach the ADS1115.
- Use a current-limited bench supply for first power-up of a new board; use the battery
  afterwards.
- Do not hot-plug electrodes while the board is powered.
- Keep the analog front-end away from chargers, motors, switch-mode supplies and mains
  wiring; the INA128 will happily amplify the interference you did not intend to measure.

## 5. Disposal and hygiene

Electrodes, gel and wipes are single-subject consumables. Dispose of them as ordinary
non-hazardous waste unless local rules say otherwise. Do not share electrodes between people.

## 6. Radio and regulatory

- The HC-05 module is a licence-exempt 2.4 GHz device; using it does not exempt the rest of
  the system from electrical-safety or EMC obligations.
- The assembled device must not be represented as certified for clinical, workplace or
  industrial use, and must never be marketed as a medical product.
- Radio emission and immunity have not been tested. Do not operate near life-support,
  aviation, automotive or other safety-critical systems.

## 7. If something goes wrong

1. Disconnect the battery first, not the electrodes, if you suspect an electrical fault.
2. Remove electrodes and move away from the apparatus.
3. Treat any skin reaction as a reason to stop and seek advice if it persists.
4. Record what happened, then fix the cause before the next session.
