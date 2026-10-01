// EasyCliq arm motion: the settings you are most likely to change.
#pragma once

// ---------- Pins (ESP32-B, see wiring-diagram.html) ----------
const int STEP_PIN[3]  = {13, 26, 23};  // J1 shoulder, J2 elbow, J3 wrist
const int DIR_PIN[3]   = {27, 25, 22};
const int LIMIT_PIN[3] = {34, 35, 36};  // 36 = VP on the board
const int EN_PIN = 21;                  // shared by all drivers, LOW = on

// ---------- Mechanics ----------
// Microsteps set by M0/M1/M2 on the drivers: 1 while they are unconnected.
const int MICROSTEPS = 1;
const int MOTOR_STEPS_PER_REV = 200;    // 1.8 degree motors
// Motor turns per joint turn. 1 = bare motor on the bench.
const float GEAR_RATIO[3] = {1.0, 1.0, 1.0};
// Flip a joint's direction without rewiring it.
const bool INVERT_DIR[3] = {false, false, false};

// ---------- Joint limits and default motion ----------
const float JOINT_MIN_DEG[3] = {-180, -180, -180};
const float JOINT_MAX_DEG[3] = { 180,  180,  180};
const float DEFAULT_SPEED_DEG_S = 180;  // speed of the joint that moves furthest
const float DEFAULT_ACCEL_DEG_S2 = 360;

// Approach every pose from the same direction so gearbox backlash cancels out
// (PROJECT-ARCHIVE.md, section 3). 0 = off; set about 2 once reducers are fitted.
const float APPROACH_OVERSHOOT_DEG = 0;

// ---------- Limit switches ----------
// Set an entry true once that switch and its 10k pull-up are wired.
const bool LIMIT_WIRED[3] = {false, false, false};

// Keep the drivers on after a move so the joints hold their position.
const bool HOLD_WHEN_IDLE = true;
