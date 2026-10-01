# Components Inventory

Everything bought so far: **Skytronic, Kohuwala, 08/09/2026**, two receipts:
- TRO 1475: Rs 4,640
- TRO 1476: Rs 13,930
- **Total: Rs 18,570** (matches `PROJECT-ARCHIVE.md` §9)

Photos are in `components/`, receipts in `Bills/`. Each photo was identified from
the board silkscreen, then matched to the receipt line and its Skytronic SKU.

---

## What you have

| # | Product (identified) | Receipt line / SKU | Qty | Photo(s) | Job in the machine |
|---|---|---|---|---|---|
| 1 | **ESP32 DevKit, 30-pin** (ESP-WROOM-32, **CP2102** USB chip, AMS1117 3.3 V reg) | NodeMCU ESP32 Dev Board MicroUSB 30-pin, MD0245 | 3 (2 + 1) | `ESP32-DevKit-30pin-CP2102_front_1/2` | A = Hub, B = Motion, C = spare |
| 2 | **DRV8825 stepper driver** (purple clone, sense resistors R100 = 0.1 Ω) + stick-on heatsink | DRV8825 Stepper Motor Driver, MD0580 | 4 | `DRV8825-..._front-chip-side`, `..._back-pin-labels` | Turntable, J1, J2, J3 |
| 3 | **NEMA17 stepper, Usongshine 17HS4401**: 1.7 A/phase, 1.5 Ω, 2.8 mH, 0.4 N·m, 1.8°, 4-wire | Nema17 Stepper Motor 0.4Nm 4-wire, MT0382 | 3 | `NEMA17-Stepper-Motor-Usongshine-17HS4401_with-cable` | Turntable + arm joints |
| 4 | **MAX485 TTL↔RS485 module** (5 V part, on-board 120 Ω termination) | MAX485 TTL to RS485 MAX485CSA Converter, MD0053 | 2 | `MAX485-..._front`, `..._back` | Hub ↔ Motion bus |
| 5 | **LM2596 buck converter, HW-411** (in 3–40 V, out 1.5–35 V adjustable, multi-turn pot) | LM2596S DC-DC 4A, MD0042 | 3 | `LM2596-..._front`, `..._back` | 24 V → 5 V for the ESP32s |
| 6 | **24 V 5 A SMPS, S-120-24** (120 W, **110/220 V selector switch**) | 24V 5A SMPS Power Supply Metal Casing, PS0046 | 1 | `SMPS-24V-5A-S-120-24_box-label`, `..._unit-top` | Motion PSU |
| 7 | **AHT20 temperature & humidity sensor, AM2301B** wired-probe version (box still unopened) | AM2301 AHT20 Digital Temperature & Humidity, MD0993 | 1 | `AHT20-AM2301B-Temp-Humidity-Sensor_box` | Chamber humidity (Hub) |
| 8 | **Micro limit switch, 17 mm roller lever** (COM / NO / NC) | Micro Limit Switch with 17mm Roller Lever, BU0147 | 2 | `Micro-Limit-Switch-...-x2_and_Screw-Terminal-...` | Arm homing |
| 9 | **Screw terminal, 5.08 mm pitch, 2-way** | 5.08mm Pitch 2-Pin Screw Terminal, TB0009 | 2 | same photo as #8 | Power tap-offs |
| 10 | **IRF520 MOSFET module** (Keyes) | IRF520 MOSFET Module, MD0041 | 2 | `IRF520-MOSFET-Module-Keyes_front` | **None: superseded, see flag 2** |
| 11 | **400-point solderless breadboard** | 400TP Project Board Breadboard, TA0164 | 1 | `Breadboard-400-Tiepoint_packaged` | Bench testing |
| 12 | Jumper wires M-F, 40 pcs | TA0027 | 1 pack | not photographed | Bench wiring |
| 13 | Jumper wires M-M, 40 pcs | TA0026 | 1 pack | not photographed | Bench wiring |
| 14 | 24 AWG circuit wire, red + black | TA1177 / TA1176 | 2 m each | not photographed | Bench power wiring |
| 15 | DC barrel jack, female pigtail, 5.5 × 2.1 mm | TA0178 | 1 | not photographed | Not assigned yet |

I photographed one sample of each part where you bought several; the other units are
the same part.

---

## Flags: read before wiring

1. **AHT20 box is unopened. Count the wires when you open it.**
   - **4 wires** (red, black, yellow, white): this is the AM2301B, which has an AHT20 inside and uses I²C, as the design assumes. Wiring: red = VCC (3.3 V), black = GND, yellow = SDA, white = SCL.
   - **3 wires**: it is the older AM2301 / DHT21, a single-wire sensor. Wiring and code are different.

2. **IRF520 modules: do not use them on the ESP32.** The archive already records this. The IRF520 needs about 10 V on the gate, but the ESP32 gives 3.3 V, which is at or below its switching threshold. Buy **D4184 (or IRLZ44N) modules** for the 5 light channels. Keep the IRF520s as spares.

3. **Some parts are short or missing** for the full motion system:
   - **NEMA17:** you have 3, but you need 4 (turntable + J1 + J2 + J3).
   - **Limit switches:** you have 2, but you need 4 (J1, J2, J3, focus axis).
   - **TCRT5000 module** for the turntable index: none bought.
   - **Capacitors and resistors:** none bought. A **100 µF capacitor on every DRV8825 is mandatory** (see `WIRING.md` §5).

4. **J1 torque budget.** The archive gives 2.41 N·m worst case at J1. The motor is 0.4 N·m holding at full 1.7 A. We will run it at about 1.1 A to keep the DRV8825 cool, which gives roughly 0.26 N·m. Printed reducers lose efficiency, so **plan for about 20–30:1 reduction on J1**, not the bare 10:1. This feeds the open question "arm reduction method".

5. **MAX485 is a 5 V chip and the ESP32 is 3.3 V.**
   - For bench work: power the module from 5 V and put a divider on RO (see `WIRING.md`).
   - For the production board: swap to **MAX3485 / SP3485** modules. They have the same pinout, run natively at 3.3 V, and need no divider.

6. **Project files missing.** The archive lists `kit.py`, `arm_kinematics.py`, `printable-kit/*.stl`, `master-checklist.md` and others. None of them are in this folder. Copy them in if you have them.

---

## Rename log

| Original | Renamed to |
|---|---|
| `components/WhatsApp Image 2026-09-23 at 10.08.56 PM.jpeg` | `DRV8825-Stepper-Driver_back-pin-labels_with-heatsink.jpeg` |
| `components/WhatsApp Image 2026-09-23 at 10.10.49 PM.jpeg` | `DRV8825-Stepper-Driver_front-chip-side_with-heatsink.jpeg` |
| `components/WhatsApp Image 2026-09-23 at 10.08.57 PM.jpeg` | `IRF520-MOSFET-Module-Keyes_front.jpeg` |
| `components/WhatsApp Image 2026-09-23 at 10.09.19 PM.jpeg` | `AHT20-AM2301B-Temp-Humidity-Sensor_box.jpeg` |
| `components/WhatsApp Image 2026-09-23 at 10.10.26 PM.jpeg` | `LM2596-Buck-Converter-HW-411_front.jpeg` |
| `components/WhatsApp Image 2026-09-23 at 10.09.23 PM.jpeg` | `LM2596-Buck-Converter-HW-411_back.jpeg` |
| `components/WhatsApp Image 2026-09-23 at 10.10.27 PM (1).jpeg` | `Micro-Limit-Switch-Roller-Lever-x2_and_Screw-Terminal-5.08mm-2pin-x2.jpeg` |
| `components/WhatsApp Image 2026-09-23 at 10.10.27 PM.jpeg` | `Breadboard-400-Tiepoint_packaged.jpeg` |
| `components/WhatsApp Image 2026-09-23 at 10.10.42 PM.jpeg` | `NEMA17-Stepper-Motor-Usongshine-17HS4401_with-cable.jpeg` |
| `components/WhatsApp Image 2026-09-23 at 10.10.43 PM.jpeg` | `ESP32-DevKit-30pin-CP2102_front_1.jpeg` |
| `components/WhatsApp Image 2026-09-23 at 10.10.48 PM (1).jpeg` | `ESP32-DevKit-30pin-CP2102_front_2.jpeg` |
| `components/WhatsApp Image 2026-09-23 at 10.10.44 PM.jpeg` | `SMPS-24V-5A-S-120-24_box-label.jpeg` |
| `components/WhatsApp Image 2026-09-23 at 10.10.45 PM.jpeg` | `SMPS-24V-5A-S-120-24_unit-top.jpeg` |
| `components/WhatsApp Image 2026-09-23 at 10.10.47 PM.jpeg` | `MAX485-TTL-to-RS485-Module_front.jpeg` |
| `components/WhatsApp Image 2026-09-23 at 10.10.48 PM.jpeg` | `MAX485-TTL-to-RS485-Module_back.jpeg` |
| `Bills/WhatsApp Image 2026-09-23 at 10.48.15 PM.jpeg` | `Skytronic_2026-09-08_TRO1476_Rs13930.jpeg` |
| `Bills/WhatsApp Image 2026-09-23 at 10.48.16 PM.jpeg` | `Skytronic_2026-09-08_TRO1475_Rs4640.jpeg` |
