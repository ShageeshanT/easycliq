# Shopping List

Prices were checked on **tronic.lk** (Skytronic's online store; the codes match your
receipts) on 24/09/2026. Rows marked *est.* are estimates, not store prices.
"Out of stock" means out of stock online; ask at the Kohuwala counter.

---

## List 1: Core, get all three motors spinning

| Item | Code | Qty | Price (Rs) |
|---|---|---|---|
| MB-102 830-point breadboard | TA0036 | 1 | 250 |
| 100 µF 50 V electrolytic capacitor | CA0122 | 5 | 25 |
| 4.7 kΩ resistor pack (~40 pcs) | RP0043 | 1 | 50 |
| 10 kΩ resistor pack (~40 pcs) | RP0047 | 1 | 50 |
| **Subtotal** | | | **375** |

Only if you don't already have them:

| Item | Code | Price (Rs) |
|---|---|---|
| DT830D multimeter | TA0077 | 830 |
| Computer power cord 13A (for the 24 V 5 A supply) | TA1235 | 720 |

---

## List 2: Core + next phase

The next phase is **finishing the electronics and doing the light test**. The archive's
rule is that the light test (LED-to-diffuser gap) sets the wall depth, and the wall
depth sets every frame dimension. So it has to happen before any exterior work.

### A. Core (List 1)

| Item | Code | Qty | Price (Rs) |
|---|---|---|---|
| Everything in List 1 | | | 375 |

### B. Finish the electronics

| Item | Code | Qty | Price (Rs) | For |
|---|---|---|---|---|
| Adjustable soldering iron 60 W | TA0127 | 1 | 1,350 (out of stock online) | LM2596 pads; anything permanent |
| Solder wire 60/40 0.8 mm, 50 g | TA0062 | 1 | 700 (out of stock online) | |
| 1 kΩ resistor pack | RP0035 | 1 | 50 | RS485 dividers |
| 2 kΩ resistor pack | RP0039 | 1 | 50 *est.* | RS485 dividers |
| Micro limit switch, roller lever | BU0147 | 2 | 80 | J3 homing + spare |
| TCRT5000 IR module, 3-pin with preset | MD0100 | 1 | 190 | turntable index |
| NEMA17 17HS4401 | MT0382 | 1 | 2,300 | turntable (4th motor; the 4th driver is already bought) |
| **Subtotal** | | | **4,720** | |

### C. Light test (Phase 0, the gate)

| Item | Code | Qty | Price (Rs) | For |
|---|---|---|---|---|
| D4184 dual MOSFET module | MD0364 | 5 | 850 | one per light wall (replaces the IRF520s) |
| 24 V 10 A power supply | PS0059 | 1 | 3,200 | separate lighting supply |
| Computer power cord 13A | TA1235 | 1 | 720 | for the new supply |
| Red-black twin power wire | TA0154 | 5 m | 250 | strip power runs |
| **High-CRI 24 V LED strip, 4000 K, 5 m, R9 > 90 published** | import | 1 reel | ~30,000–40,000 *est.* | the actual light source |
| Opal acrylic 3 mm, ~400 × 400 offcut | plastics shop | 1 | ~1,500–3,000 *est.* | diffuser for the gap test |
| Chrome / steel ball, 40–50 mm | hardware | 1 | ~500–1,500 *est.* | reflection test target |
| **Subtotal** | | | **~37,000–49,500** | |

- **Strip price.** The reference is Yuji CRI-MAX 4000 K 24 V at USD 92.65 for 5 m (20 W/m, R9 > 90 published). The rupee figure adds shipping at about Rs 300/USD. Cheaper CRI 95 strips exist, but **only buy one whose listing publishes R9 ≥ 90**. Start the order early: this is the one item with import lead time.
- **D4184 PWM limit.** The module is rated to 20 kHz PWM, so the lights will run at 20 kHz. Banding only shows up below ~5 kHz.
- **Optional: Godox FL60.** Only needed if you want the side-by-side comparison from the archive. CameraLK doesn't list it online, so ask them for a quote. It's not included in the total.

### Total

| | Rs |
|---|---|
| A. Core | 375 |
| B. Finish the electronics | 4,720 |
| C. Light test | ~37,000–49,500 |
| **Grand total** | **~42,000–54,500** |
| + multimeter and first power cord, if needed | + 1,550 |

About Rs 10,100 of this is at Skytronic prices. The rest is the imported strip and the three estimated items.

---

## Not in these lists (exterior and mechanical, later)

Alumex frame sections, base plate, PVC foam board skins, coves, sweep, turntable
bearing/belt/pulleys, arm links and reducers, camera, lens. See `PROJECT-ARCHIVE.md`
§9 and §10.
