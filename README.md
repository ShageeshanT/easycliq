# EasyCliq

An automated product-photography machine. A sealed, fully lit box with a turntable
and a 3-joint camera arm takes consistent shots of jewellery and small products.

This repo holds the electronics bring-up: the motion firmware, wiring guides and
diagrams, and the parts list. It is being built on the bench in Colombo.

## Status

- Core electronics bought and identified ([COMPONENTS.md](COMPONENTS.md)).
- **J1 motor turned under firmware control on 01/10/2026.**
- J2 and J3 are being wired the same way.
- Next: limit switches, the RS485 link between the two ESP32s, the AHT20 sensor, and the Phase 0 light test. The light test decides the frame dimensions.

## Repo layout

| Path | What it is |
|---|---|
| [`firmware/arm_motion/`](firmware/arm_motion/) | Arm firmware for ESP32-B: coordinated 3-joint moves, demo, test |
| [`firmware/bench/stepper_test/`](firmware/bench/stepper_test/) | Simple one-motor-at-a-time bench test |
| [`EasyCliq-Wiring-Diagram.pdf`](EasyCliq-Wiring-Diagram.pdf) | Illustrated wiring (page 1) and tick-off wire list (page 2) |
| [`wiring-diagram.html`](wiring-diagram.html) | Same wiring as a web page, including the power supply and RS485 details |
| [`WIRING.md`](WIRING.md) | Step-by-step bring-up, pin maps, troubleshooting |
| [`COMPONENTS.md`](COMPONENTS.md) | What was bought, what each part does, known issues |
| [`SHOPPING-LIST.md`](SHOPPING-LIST.md) | What to buy next, with Skytronic product codes |
| [`components/`](components/) | Photos of the parts |
| [`tools/gen_wiring_pdf.py`](tools/gen_wiring_pdf.py) | Regenerates the wiring PDF |

## Pin map (ESP32-B)

| Joint | STEP | DIR | Limit switch |
|---|---|---|---|
| J1 shoulder | D13 | D27 | D34 |
| J2 elbow | D26 | D25 | D35 |
| J3 wrist | D23 | D22 | VP (GPIO36) |
| All drivers | EN = D21, LOW = on, 4.7 kΩ pull-up to 3.3 V | | |

Motor cable: red → 2B, black → 1B, blue → 1A, green → 2A.

## Upload the arm firmware

1. Arduino IDE 2.x with **esp32 by Espressif Systems** (tested on 3.0.7). The ESP32's USB chip is a CP2102, which needs the Silicon Labs CP210x driver on Windows.
2. Open `firmware/arm_motion/arm_motion.ino`.
3. Board **ESP32 Dev Module**, choose the COM port, then Upload.
4. Open the Serial Monitor at **115200** and type `help`.

```
move <j1> <j2> <j3>   go to joint angles (degrees), all joints together
jog <joint> <deg>     move one joint by some degrees
home | zero           go to 0 0 0 | call the current spot 0 0 0
test                  each joint half a turn and back, one at a time
demo                  arm-style sequence; the wrist keeps the camera aimed
speed / accel         set top speed (deg/s) and acceleration (deg/s²)
stop | on | off | pos | status
```

Gear ratios, microstepping, direction, joint limits and the backlash approach are set in
[`firmware/arm_motion/config.h`](firmware/arm_motion/config.h).

**Before any motor runs:** set Vref to 0.55 V on every driver, fit a 100 µF capacitor on
every VMOT, and only plug or unplug motors with the 24 V supply off.
