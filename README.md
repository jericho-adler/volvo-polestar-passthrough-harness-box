# Volvo/Polestar Passthrough Harness Box

A small automotive ADAS harness pass-through box designed in KiCad. It sits inline on the camera/VCU harness and provides a fail-safe electrical bypass plus signal switching, protected against automotive power-rail transients and ESD.

![Assembled board render, showing the VCU and CAR Harness connectors](3D%20models/Passthrough_HarnessBox_Final.png)

- **Board:** 73.0 × 43.0 mm, 4-layer (F.Cu / In1.Cu=GND / In2.Cu / B.Cu), 25 components, 73 nets
- **Power inputs:** VBAT and VOBD, each TVS-protected (SMAJ16A) and OR'd through Schottky diodes (STPS2H100ZFY) into a combined VIN rail
- **Fail-safe passthrough:** a DPDT relay (Panasonic TQ2-12V) wired so the normally-closed contacts connect CAMERA↔VCU when the box is unpowered, and open when VIN is applied
- **Signal switching:** two DG419 SPDT analog switches route CAMERA/VCU signal pairs under control of an `SBU 1` logic input
- **Protection:** PESD1CAN ESD diodes on signal lines at the connectors
- **Connectors:** JAE MX34032NF4 (32-pin automotive, ×2) for the harness pass-through, plus a USB-C and Molex connector

## Repository structure

```
PCB Files/     KiCad project (schematic, PCB, rules), design review, and analysis/datasheet data
3D models/     STEP export of the assembled board, plus a rendered preview image
```

### PCB Files

- `Passthrough_HarnessBox_Final.kicad_pro` / `.kicad_sch` / `.kicad_pcb` — the KiCad project. Open `Passthrough_HarnessBox_Final.kicad_pro` in KiCad 10 to get started.
- `design_review_2026-08-06.md` — a design review from an earlier revision of the schematic/PCB, covering consistency, ESD/decoupling/stackup checks, and datasheet-verified pinouts for the relay, MOSFET, and analog switches. **Predates the current `_Final` revision** — treat findings as a starting point, not a check of the current files, until it's re-run.
- `analysis/` — machine-readable analysis output backing that earlier design review (same caveat — predates the `_Final` revision).
- `datasheets/` — datasheet sync manifest for the BOM parts.

### 3D models

- `Passthrough_HarnessBox.step` — STEP export of the assembled board.
- `Passthrough_HarnessBox_Final.png` — rendered preview of the assembled board (shown above).

## Status

This is the `_Final` revision of the design, which has diverged substantially from the schematic/PCB the linked design review was run against. The review's specific findings (MPNs, fiducials, decoupling, stackup, etc.) should be re-verified against the current files before fabricating rather than assumed to still apply.

## Disclaimer

This is a community hardware design shared as-is, with no warranty. Review the design review's blockers before fabricating or installing in a vehicle.
