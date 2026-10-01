# Wiring Guide: Electronics Bench Bring-Up

This guide covers bringing up the electronics you have already bought (see
`COMPONENTS.md`), one stage at a time. Wire one stage, test it, and only then move to
the next.

This work does **not** conflict with the archive's "one rule". Nothing here commits a
frame dimension. The Phase 0 light-panel bench test is still the critical path; it
needs the LED strip, D4184 MOSFETs and opal acrylic. Run the two in parallel.

---

## 1. Ground rules

1. **One common ground.** Tie these together at one star point:
   - PSU −V
   - every ESP32 GND
   - every driver's logic GND
   - every MAX485 GND

   Signals without a shared ground do not work, and sometimes they destroy pins.
2. **ESP32 pins are 3.3 V only.** Nothing above 3.3 V may reach a GPIO. 24 V must never reach VIN, 3V3 or any GPIO.
3. **Never plug or unplug a stepper while its driver is powered.** Doing so kills the DRV8825 instantly.
4. **Power off before changing any wire.**
5. **Label the ESP32s with tape:** **A** (Hub), **B** (Motion), **C** (spare).
6. **You need a multimeter.** You cannot set Vref or the buck output without one.

---

## 2. Power architecture

```
                 230 V AC
                    │
        ┌───────────┴────────────┐
        ▼                        ▼
 [S-120-24  24V 5A]       [24V 10A — to buy]
   MOTION PSU               LIGHTING PSU
   +V ──┬──► DRV8825 ×4 VMOT       +V ──► LED strips (+)
        │    (100 µF cap on each)         strips (−) ──► D4184 ×5 ──► −V
        └──► LM2596 #1 ─5.0V─► ESP32-B VIN, MAX485-B VCC
                                   +V ──► LM2596 #2 ─5.0V─► ESP32-A VIN, MAX485-A VCC
   −V ──────────────┬─────────────────── −V
                    ▼
            COMMON GND STAR POINT  ◄── all ESP32 GND, driver logic GND, MAX485 GND
```

- **Bench stage:** only the 5 A motion PSU exists, so both bucks run from it for now.
- **LM2596 #3:** spare. It can power ESP32-C or the TCRT5000.
- **Wire gauge:**
  - The 24 AWG wire you have is fine for the one-motor bench test.
  - In the machine, run 24 V distribution in **18 AWG**. It is already on the archive's buy list.
- **Power budget on the 5 A PSU:** 4 drivers at about 1.1 A phase current draw roughly 2 A from the 24 V supply at speed, plus about 0.3 A for the logic. There is plenty of headroom.

---

## 3. Pin maps

### ESP32-B: Motion

| Function | GPIO | Board label | Connects to | Notes |
|---|---|---|---|---|
| Turntable STEP | 32 | D32 | DRV8825 #1 STEP | |
| Turntable DIR | 33 | D33 | DRV8825 #1 DIR | |
| J1 shoulder STEP | 13 | D13 | DRV8825 #2 STEP | |
| J1 shoulder DIR | 27 | D27 | DRV8825 #2 DIR | |
| J2 elbow STEP | 26 | D26 | DRV8825 #3 STEP | |
| J2 elbow DIR | 25 | D25 | DRV8825 #3 DIR | |
| J3 wrist STEP | 23 | D23 | DRV8825 #4 STEP | |
| J3 wrist DIR | 22 | D22 | DRV8825 #4 DIR | |
| **EN, all drivers** | 21 | D21 | EN of all 4 DRV8825s | **4.7 kΩ pull-up to 3V3**. Drivers stay OFF while the ESP32 boots. Active LOW. |
| Limit J1 | 34 | D34 | switch NC; COM → GND | 10 kΩ pull-up to 3V3 (input-only pin, no internal pull-up) |
| Limit J2 | 35 | D35 | switch NC; COM → GND | 10 kΩ pull-up to 3V3 |
| Limit J3 | 36 | VP | switch NC; COM → GND | 10 kΩ pull-up to 3V3 |
| Turntable index | 39 | VN | TCRT5000 module D0 | Power the TCRT5000 from **3V3** so its output is 3.3 V |
| RS485 TX | 17 | TX2 | MAX485 DI | |
| RS485 RX | 16 | RX2 | MAX485 RO **through divider** | 1 kΩ series + 2 kΩ to GND (5 V → 3.3 V) |
| RS485 direction | 4 | D4 | MAX485 DE + RE (tied together) | HIGH = transmit, LOW = receive |
| *Reserved: focus STEP* | 19 | D19 | 5th driver (NEMA11) | |
| *Reserved: focus DIR* | 5 | D5 | 5th driver | Toggles at boot. Harmless on DIR. |
| *Reserved: focus limit* | 18 | D18 | switch NC | Internal pull-up OK |

**Keep EN LOW whenever the arm is raised.** EN is shared, so disabling it releases all
three joints and the arm falls.

### ESP32-A: Hub

| Function | GPIO | Board label | Connects to | Notes |
|---|---|---|---|---|
| Light ch1: ceiling | 25 | D25 | D4184 #1 PWM/SIG | 25 kHz PWM. Needs a 10 kΩ gate pull-down; most D4184 modules have one on board, so check. |
| Light ch2: left | 26 | D26 | D4184 #2 | |
| Light ch3: right | 27 | D27 | D4184 #3 | |
| Light ch4: rear | 32 | D32 | D4184 #4 | |
| Light ch5: door | 33 | D33 | D4184 #5 | |
| AHT20 SDA | 21 | D21 | yellow wire | 4.7 kΩ pull-up to 3V3 |
| AHT20 SCL | 22 | D22 | white wire | 4.7 kΩ pull-up to 3V3 |
| Door interlock | 34 | D34 | switch NC; COM → GND | 10 kΩ pull-up. HIGH = door open or wire broken, so inhibit. |
| Roof insert ID | 36 | VP | ID resistor divider | Must be an ADC1 pin: **ADC2 stops working when WiFi is on** |
| RS485 TX | 17 | TX2 | MAX485 DI | |
| RS485 RX | 16 | RX2 | MAX485 RO through divider | same divider as B |
| RS485 direction | 4 | D4 | MAX485 DE + RE | |
| Spare | 13, 18, 19, 23, 35, 39 | | | |

### Why these pins

- **Avoided:**
  - GPIO 0, 2, 12 and 15 are boot-strapping pins. Pulling GPIO 12 high at boot bricks the boot.
  - GPIO 1 and 3 carry USB serial.
  - GPIO 6–11 connect to the flash chip and are not on the 30-pin board.
  - GPIO 5, 14 and 15 toggle during boot. That toggling on a STEP pin would move a motor.
- **GPIO 34, 35, 36 (VP) and 39 (VN)** are input-only and have **no internal pull-ups**. That is why they get external 10 kΩ resistors, and why they are used for switches.
- **Limit switches are wired normally-closed (NC) to GND.** A pressed switch *and* a broken wire both read HIGH, so a snapped cable stops the machine instead of letting it drive into a wall.

---

## 4. Board pinouts

### ESP32 DevKit 30-pin (antenna at top, USB at bottom)
```
        EN │●          ●│ D23
   GPIO36 VP│●          ●│ D22
   GPIO39 VN│●          ●│ TX0  (USB serial: don't use)
       D34 │●          ●│ RX0  (USB serial: don't use)
       D35 │●          ●│ D21
       D32 │●          ●│ D19
       D33 │●          ●│ D18
       D25 │●          ●│ D5
       D26 │●          ●│ TX2  (GPIO17)
       D27 │●          ●│ RX2  (GPIO16)
       D14 │●          ●│ D4
       D12 │●          ●│ D2   (blue LED)
       D13 │●          ●│ D15
       GND │●          ●│ GND
       VIN │●  [USB]   ●│ 3V3
```
- **VIN:** 5 V in only, from the LM2596 set to 5.0 V.
- **3V3:** a 3.3 V output for sensors and pull-ups.

### DRV8825 (read the labels on the back of your board)
```
   EN   ●──────────────● VMOT   ← 24 V +
   M0   ●              ● GND    ← 24 V −
   M1   ●   [pot]      ● 2B  ┐ coil B
   M2   ●              ● 1B  ┘
   RST  ●   DRV8825    ● 1A  ┐ coil A
   SLP  ●              ● 2A  ┘
   STEP ●              ● FLT    ← leave unconnected
   DIR  ●──────────────● GND    ← logic GND → ESP32 GND
```
- **Orientation:** EN sits opposite VMOT; DIR sits opposite the logic GND. **Do not go by where the pot is.** Flip the board and read the silkscreen (photo `DRV8825-Stepper-Driver_back-pin-labels_with-heatsink.jpeg`).
- **No logic supply:** the DRV8825 takes no logic power. Do **not** put 3.3 V or 5 V on FLT.
- **Microstepping:** M0, M1 and M2 have internal pull-downs, so leaving them unconnected gives full step.

| M2 | M1 | M0 | Microstep |
|---|---|---|---|
| 0 | 0 | 0 | full (200 steps/rev) |
| 0 | 0 | 1 | 1/2 |
| 0 | 1 | 0 | 1/4 |
| 0 | 1 | 1 | 1/8 |
| 1 | 0 | 0 | **1/16 (3200 steps/rev)** |
| 1 | 0 | 1 | 1/32 |

- **Current limit:** your boards have **R100** sense resistors, so **current limit = 2 × Vref**.

### MAX485 module
```
  DI ●  ← ESP32 TX2                VCC ●  ← 5 V
  DE ●┐ ← ESP32 GPIO4               B  ●  ── bus B ┐ twisted pair
  RE ●┘   (bridge DE and RE)        A  ●  ── bus A ┘ A↔A, B↔B
  RO ●  → divider → ESP32 RX2      GND ●  ── GND (run a GND wire between boards too)
```
Both modules have a 120 Ω termination resistor on board. That is correct here, because
the two modules sit at the two ends of the bus.

### LM2596 HW-411
- **Terminals:** IN+, IN−, OUT+, OUT−. The arrow on the back points IN → OUT.
- **Pot:** the blue multi-turn pot sets the output. It may take 10–20 turns before the voltage moves.

### S-120-24 SMPS
- **Terminal strip, left to right:** normally L, N, ⏚ (earth), −V, −V, +V, +V. **Read the labels printed next to the screws on your unit** rather than trusting the order.
- **V.ADJ:** the small pot next to the terminals trims the output about ±10 %.
- **Selector switch:** the 110/220 V switch is on the side.

### NEMA17 17HS4401 cable
- **The wire colours are not reliable across cables.** Find the coil pairs with the multimeter on Ω:
  - about **1.5–3 Ω** between two wires: same coil
  - **OL** (open): different coils
- **Your cables pair red + black and blue + green.** This was confirmed on 01/10/2026, when J1 turned with the wiring below. It is **not** the generic 17HS4401 code (black + green / red + blue).
  - At the motor's white 6-slot plug, the wires run **red, black, blue, green**, with an empty slot between the two pairs. Each half of that plug is one coil.
  - At the other end, the black plug runs **black, green, blue, red**, which splits the pairs. Never push that plug straight into four neighbouring holes. Use four separate male-male jumpers instead.
- **No multimeter?** Twist two bare wire ends together and turn the shaft by hand. If it suddenly gets stiff and notchy, those two wires are the same coil.

| Wire | Coil | DRV8825 pin | Pin position (counting from VMOT) |
|---|---|---|---|
| Red | 1 | **2B** | 3rd |
| Black | 1 | **1B** | 4th |
| Blue | 2 | **1A** | 5th |
| Green | 2 | **2A** | 6th |

Easy to remember: the same order as at the motor's white plug.

- **The rule that matters:** one coil goes on the 3rd + 4th pins and the other coil on the 5th + 6th pins. Getting that right makes the motor turn. Which way round each pair goes only sets the direction.
- **To reverse the direction:** swap red ↔ black only, or change DIR in software. Never swap wires *between* the two coils.

### Micro limit switch
- **Pins:** three pins, marked on the body: **C** (common), **NO**, **NC**.
- **Wiring:** C → GND, NC → GPIO (with the pull-up).

---

## 5. Bring-up sequence

### Step 1: 24 V PSU (mains side)

> ⚠ **230 V can kill.** If you are not confident wiring mains, have an electrician do
> these three screws. Everything after this step is low voltage.

1. **Check the 110/220 V selector switch on the side of the PSU and set it to 220 V.** Sri Lanka is 230 V. If you power it on while the switch is at 110 V, the PSU is destroyed, sometimes violently.
2. Connect a 3-core cable with a plug:
   - brown (live) → **L**
   - blue (neutral) → **N**
   - green/yellow → **⏚**

   The earth is mandatory, because the metal case must be earthed.
3. Connect nothing to the output yet. Plug in; the green LED should light.
4. Set the multimeter to DC V and measure +V to −V. You should see **24.0 V**. Trim with V.ADJ if needed.
5. Unplug and **wait 30 seconds** before touching any terminal.
6. Cover the mains terminals (insulating tape or heat-shrink boot) and mount the PSU so they can't be touched.

✅ **Pass:** a steady 24.0 V with no load.

### Step 2: set all three LM2596s to 5.0 V (before any ESP32 is connected)

1. Connect PSU +V → **IN+** and −V → **IN−**. Leave the output unconnected.
2. Power on and measure OUT+ to OUT−. These modules ship at random voltages, often close to the input voltage, which would kill an ESP32.
3. Turn the brass screw on the blue pot until the output reads **5.0–5.1 V**. Counter-clockwise usually lowers it. Keep turning, because the pot is multi-turn.
4. Power off and **write "5V" on the module with a marker.**
5. Repeat for modules #2 and #3.

✅ **Pass:** all three modules read 5.0–5.1 V and are labelled.

### Step 3: test each ESP32 alone over USB

1. **Arduino IDE 2.x** with **"esp32 by Espressif Systems" 3.0.7** is already installed on this PC. `stepper_test.ino` compiles against it.
2. Plug in the board with a **data** micro-USB cable. Charge-only cables are common and show nothing.
3. In Device Manager → Ports you should see **"Silicon Labs CP210x USB to UART Bridge (COMx)"**. If it doesn't appear, install the CP210x VCP driver from silabs.com.
4. Select board **"ESP32 Dev Module"** and the COM port, then upload **File → Examples → 01.Basics → Blink**. The blue LED on GPIO2 should blink.
   - If the upload hangs at `Connecting....`, hold the **BOOT** button until it starts writing.
5. Repeat for all three boards and label them **A, B, C**.

✅ **Pass:** all three boards blink.

### Step 4: first motor (ESP32-B + DRV8825 #1 + NEMA17 #1, the J1 channel)

> The visual version of Steps 4–6, covering all three motors on an 830-point
> breadboard, is in `EasyCliq-Wiring-Diagram.pdf` (illustrated, with a tick-off wire
> list) and `wiring-diagram.html`.
>
> J1 and J2 were re-pinned on 30/09/2026 so that the drivers sit J1, J2, J3 from left
> to right and no wires cross: J1 = D13/D27, J2 = D26/D25, J3 = D23/D22.

**You need a 100 µF electrolytic capacitor (≥ 35 V, 50 V preferred) before doing this.**
The DRV8825 is known to die from voltage spikes on VMOT without one. See §6.

**Layout.**
- Put the DRV8825 on the breadboard, straddling the centre gap.
- Leave the ESP32 off the breadboard and run **M-F jumpers** from its pins. The 30-pin board is too wide to leave usable holes on a 400-point breadboard.
- Keep the 24 V rows physically away from the 3.3 V rows, and mark them.

| From | To | Wire |
|---|---|---|
| PSU +V | DRV8825 **VMOT** | red 24 AWG |
| PSU −V | DRV8825 **GND** (next to VMOT) | black 24 AWG |
| **100 µF cap** | across VMOT and GND, *right at the driver* | **stripe (−) to GND** |
| DRV8825 **GND** (next to FLT) | ESP32-B **GND** | M-F jumper |
| DRV8825 **RST** + **SLP** | bridge them, then to ESP32-B **3V3** | jumpers |
| DRV8825 **STEP** | ESP32-B **D13** | M-F |
| DRV8825 **DIR** | ESP32-B **D27** | M-F |
| DRV8825 **EN** | ESP32-B **D21**, plus a **4.7 kΩ** resistor from D21 to 3V3 | M-F |
| M0, M1, M2, FLT | leave unconnected | |
| Motor coil A pair | **1A**, **2A** | |
| Motor coil B pair | **1B**, **2B** | |

- **Powering ESP32-B:** use USB for this test so you can use the Serial Monitor. The 24 V PSU and the laptop share ground through the GND jumper, which is correct.
- **Missing the 4.7 kΩ resistor?** For this one test you can omit it, because the firmware drives EN anyway. The motor will just be energised during boot.

**4a. Set Vref with the motor NOT connected.**
1. With 24 V on and ESP32-B on USB, set the multimeter to DC V. Put black on **GND** and red on the **metal top of the pot**.
2. Turn the pot gently to **Vref = 0.55 V**, which gives a 1.1 A limit.
   - The motor's maximum is 0.85 V (1.7 A), but a DRV8825 without a fan overheats above about 1.5 A.
   - Only raise it towards 0.70 V if the motor skips steps under real load.
3. Power off. Connect the motor. Stick the heatsink on the chip, making sure it doesn't touch any pin or the pot.

**4b. Run the test sketch.**
1. Upload `firmware/bench/stepper_test/stepper_test.ino`.
2. Open the Serial Monitor at 115200 baud.
3. Type `f` for one revolution forward on the selected motor (J1 at start-up), `r` for reverse, and `1`–`5` for speed. `j` selects the next motor. `a` turns all three together.

✅ **Pass:**
- The shaft turns exactly one revolution per `f`, smoothly, both directions.
- The driver is warm but touchable after a minute.

| Symptom | Cause |
|---|---|
| Motor buzzes or shakes but doesn't turn | Coil pairs are split, e.g. one wire from each coil on 1A/2A. Re-measure. |
| Turns the wrong way | Swap the two wires of **one** coil, or flip DIR in software. |
| Nothing at all, no holding torque | RST/SLP not at 3V3, EN not LOW, VMOT missing, or no common GND. |
| Stalls at speed 4–5 | Too fast without enough ramp. Use speed 1–3, or raise Vref slightly. |
| Driver too hot to touch | Vref too high, or the heatsink is missing. |

**4c. Try microstepping.**
1. Power off. Connect **M2 → 3V3** for 1/16.
2. In the sketch, set `MICROSTEPS = 16` and re-upload.
3. The motor should be much quieter and smoother. The final turntable microstep setting will be chosen in the motion firmware.

### Step 5: limit switch (J1 input)

1. Wire the switch: **C → GND** and **NC → ESP32-B D34**, plus a **10 kΩ** resistor from D34 to 3V3.
2. Optional: add a **100 nF** capacitor from D34 to GND. It filters stepper noise on long switch cables.
3. In the sketch, set the J1 entry of `LIMIT_WIRED` to `true` and re-upload.
4. Type `l` to read the switches:
   - `OK` normally
   - `TRIGGERED` when you press the lever
5. Start `f`, then press the switch while the motor turns.

✅ **Pass:** the motor stops as soon as the switch is pressed. Unplugging the NC wire also reads TRIGGERED.

### Steps 6–10 (guides to follow)

| Step | What | Waiting on |
|---|---|---|
| 6 | J2 and J3 drivers on ESP32-B per the pin map, shared EN; type `a` to spin all three | 830-point breadboard, 100 µF caps |
| 7 | RS485 link A ↔ B: ping/pong test | resistors for the RO dividers |
| 8 | AHT20 on ESP32-A (I²C) | open the box and check the wire count |
| 9 | Move ESP32 power from USB to the LM2596s | nothing |
| 10 | Lighting channels + PWM > 20 kHz flicker test (= Phase 0 bench test) | D4184 ×5, LED strip, opal acrylic |

---

## 6. Still to buy

The priced list, with Skytronic codes, is in **`SHOPPING-LIST.md`**:
- List 1 is what the three-motor test needs.
- List 2 adds the next phase: finishing the electronics and the Phase 0 light test.

Don't buy Skytronic's DRV8825/A4988 base board (MD0575). It takes 24 V through a
push-in header labelled "9V" and feeds its "5V" pin into the DRV8825's FLT pin, and
its RST/SLP wiring can't be confirmed from the listing.

For the production build, consider MAX3485 modules (3.3 V RS485, no divider needed).
