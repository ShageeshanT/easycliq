// EasyCliq arm motion firmware for ESP32-B (Motion board).
//
// Drives the three arm joints (J1 shoulder, J2 elbow, J3 wrist) as one arm:
// every move is coordinated, so all joints start and finish together, with a
// smooth speed-up and slow-down. Moves are in degrees at the joint; settings
// live in config.h.
//
// Serial Monitor at 115200 baud, then type a command and press Enter:
//   help                 list commands
//   move <j1> <j2> <j3>  go to these joint angles (degrees), all together
//   jog <joint> <deg>    move one joint by this many degrees (joint = 1, 2 or 3)
//   home                 go back to 0 0 0
//   zero                 call the current position 0 0 0
//   test                 each joint turns half a turn and back, one at a time
//   demo                 arm-style sequence; the wrist keeps the camera aimed
//   speed <deg/s>        top speed of the joint that moves furthest
//   accel <deg/s2>       acceleration
//   stop                 slow down and stop, clear queued moves
//   on / off             drivers on (holding) / off (joints go limp)
//   pos                  print joint angles
//   status               print state and settings
//
// How it works: a hardware timer ticks 20,000 times a second. On each tick the
// interrupt advances a speed profile for the joint with the most steps, and a
// Bresenham line algorithm decides which of the other joints step on the same
// tick, so all three arrive at the same moment.

#include "config.h"
#include "soc/gpio_reg.h"
#include "soc/soc.h"
#include "esp_rom_sys.h"

const int NJ = 3;
const uint32_t TICK_HZ = 20000;          // step generator rate (50 us per tick)
const uint64_t ONE_Q32 = 1ULL << 32;     // fixed point: 1 step = 2^32

// ---------------------------------------------------------------- motion core
// One coordinated move. Written by loop() only while no move is running.
struct Segment {
  uint32_t total;       // steps of the joint that moves furthest
  uint64_t vmaxQ;       // cruise speed, steps per tick (Q32)
  uint64_t vminQ;       // start / end speed, steps per tick (Q32)
  uint64_t accQ;        // speed change per tick (Q32)
  uint32_t accelEnd;    // step count where cruising starts
  uint32_t decelStart;  // step count where slowing down starts
};

Segment seg;
uint32_t absSteps[NJ], err[NJ], stepMask[NJ];
int32_t dirSign[NJ];
uint32_t limitMaskIn1 = 0;               // limit pins in GPIO_IN1 (pins 32-39)

volatile bool segBusy = false;
volatile bool stopReq = false;
volatile bool limitHit = false;
volatile int32_t posSteps[NJ] = {0, 0, 0};

// ISR-only state
uint64_t vQ = 0, phaseQ = 0;
uint32_t stepsDone = 0;

hw_timer_t* timer = nullptr;

void IRAM_ATTR onTick() {
  if (!segBusy) return;

  if (limitMaskIn1 && (REG_READ(GPIO_IN1_REG) & limitMaskIn1)) {
    limitHit = true;
    segBusy = false;
    return;
  }

  // speed profile (integer only: no floating point inside an interrupt)
  if (stopReq) {
    if (vQ > seg.vminQ + seg.accQ) vQ -= seg.accQ;
    else { segBusy = false; return; }
  } else if (stepsDone < seg.accelEnd) {
    vQ += seg.accQ;
    if (vQ > seg.vmaxQ) vQ = seg.vmaxQ;
  } else if (stepsDone >= seg.decelStart) {
    vQ = (vQ > seg.vminQ + seg.accQ) ? vQ - seg.accQ : seg.vminQ;
  }

  phaseQ += vQ;
  if (phaseQ < ONE_Q32) return;
  phaseQ -= ONE_Q32;

  // one step of the leading joint; Bresenham picks which others step too
  uint32_t mask = 0;
  for (int j = 0; j < NJ; j++) {
    err[j] += absSteps[j];
    if (err[j] >= seg.total) {
      err[j] -= seg.total;
      mask |= stepMask[j];
      posSteps[j] = posSteps[j] + dirSign[j];
    }
  }
  REG_WRITE(GPIO_OUT_W1TS_REG, mask);
  esp_rom_delay_us(2);                   // DRV8825 needs >= 1.9 us high
  REG_WRITE(GPIO_OUT_W1TC_REG, mask);

  if (++stepsDone >= seg.total) segBusy = false;
}

// ------------------------------------------------------------- planning layer
float stepsPerDeg[NJ];
float speedDegS = DEFAULT_SPEED_DEG_S;
float accelDegS2 = DEFAULT_ACCEL_DEG_S2;
bool driversOn = false;

struct Pose {
  float deg[NJ];
  uint16_t dwellMs;  // pause after arriving
};

const int QUEUE_LEN = 24;
Pose queue[QUEUE_LEN];
int qHead = 0, qCount = 0;
float plannedDeg[NJ] = {0, 0, 0};        // where the arm ends up after the queue
uint16_t currentDwell = 0;
uint32_t dwellUntil = 0;
bool wasBusy = false;

float jointDeg(int j) { return posSteps[j] / stepsPerDeg[j]; }

void setDrivers(bool on) {
  digitalWrite(EN_PIN, on ? LOW : HIGH);
  if (on && !driversOn) delay(2);
  driversOn = on;
}

void printPos(const char* label) {
  Serial.printf("%s J1=%.1f J2=%.1f J3=%.1f\n", label, jointDeg(0), jointDeg(1), jointDeg(2));
}

bool withinLimits(const float* deg, bool report) {
  for (int j = 0; j < NJ; j++) {
    if (deg[j] < JOINT_MIN_DEG[j] || deg[j] > JOINT_MAX_DEG[j]) {
      if (report) Serial.printf("Refused: J%d %.1f is outside %.0f..%.0f\n", j + 1, deg[j],
                                JOINT_MIN_DEG[j], JOINT_MAX_DEG[j]);
      return false;
    }
  }
  return true;
}

bool pushPose(const float* deg, uint16_t dwellMs) {
  if (qCount >= QUEUE_LEN) {
    Serial.println("Refused: move queue is full");
    return false;
  }
  Pose& p = queue[(qHead + qCount) % QUEUE_LEN];
  for (int j = 0; j < NJ; j++) p.deg[j] = deg[j];
  p.dwellMs = dwellMs;
  qCount++;
  for (int j = 0; j < NJ; j++) plannedDeg[j] = deg[j];
  return true;
}

// Queue a move to `target`, adding the same-direction approach if enabled.
bool enqueue(const float* target, uint16_t dwellMs) {
  if (!withinLimits(target, true)) return false;
  if (APPROACH_OVERSHOOT_DEG > 0) {
    float via[NJ];
    bool needVia = false;
    for (int j = 0; j < NJ; j++) {
      via[j] = target[j];
      if (target[j] < plannedDeg[j] && target[j] - APPROACH_OVERSHOOT_DEG >= JOINT_MIN_DEG[j]) {
        via[j] = target[j] - APPROACH_OVERSHOOT_DEG;
        needVia = true;
      }
    }
    if (needVia && !pushPose(via, 0)) return false;
  }
  return pushPose(target, dwellMs);
}

void clearQueue() {
  qCount = 0;
  currentDwell = 0;
  for (int j = 0; j < NJ; j++) plannedDeg[j] = jointDeg(j);
}

// Start one coordinated move (call only while no move is running).
void startMove(const float* target) {
  int32_t delta[NJ];
  uint32_t total = 0;
  for (int j = 0; j < NJ; j++) {
    int32_t targetSteps = lroundf(target[j] * stepsPerDeg[j]);
    delta[j] = targetSteps - posSteps[j];
    uint32_t a = (uint32_t)abs(delta[j]);
    if (a > total) total = a;
  }
  if (total == 0) return;

  // The joint that needs the most time at the set speed decides the timing.
  float limitingDeg = 0, moveTime = 0;
  for (int j = 0; j < NJ; j++) {
    float deg = abs(delta[j]) / stepsPerDeg[j];
    float t = deg / speedDegS;
    if (t > moveTime) { moveTime = t; limitingDeg = deg; }
  }
  float vmax = total / moveTime;                     // leading-joint steps/s
  float acc = total / limitingDeg * accelDegS2;      // leading-joint steps/s^2
  float vmin = min(vmax, max(20.0f, sqrtf(acc)));
  float sAcc = (vmax * vmax - vmin * vmin) / (2 * acc);
  if (2 * sAcc > total) sAcc = total / 2.0f;

  seg.total = total;
  seg.vmaxQ = (uint64_t)((double)vmax / TICK_HZ * ONE_Q32);
  seg.vminQ = (uint64_t)((double)vmin / TICK_HZ * ONE_Q32);
  seg.accQ = (uint64_t)((double)acc / ((double)TICK_HZ * TICK_HZ) * ONE_Q32);
  if (seg.accQ == 0) seg.accQ = 1;
  seg.accelEnd = (uint32_t)sAcc;
  seg.decelStart = total - (uint32_t)sAcc;

  for (int j = 0; j < NJ; j++) {
    absSteps[j] = (uint32_t)abs(delta[j]);
    err[j] = total / 2;
    stepMask[j] = 1UL << STEP_PIN[j];
    dirSign[j] = delta[j] >= 0 ? 1 : -1;
    bool forward = (delta[j] >= 0) != INVERT_DIR[j];
    digitalWrite(DIR_PIN[j], forward ? HIGH : LOW);
  }
  delayMicroseconds(5);                              // DIR setup before STEP

  setDrivers(true);
  vQ = seg.vminQ;
  phaseQ = 0;
  stepsDone = 0;
  stopReq = false;
  __sync_synchronize();
  segBusy = true;
}

bool anyLimitTriggered(bool report) {
  for (int j = 0; j < NJ; j++) {
    if (LIMIT_WIRED[j] && digitalRead(LIMIT_PIN[j]) == HIGH) {
      if (report) Serial.printf("J%d limit switch is TRIGGERED (pressed or wire broken)\n", j + 1);
      return true;
    }
  }
  return false;
}

// ------------------------------------------------------------------ commands
void queueDemo() {
  // Shoulder and elbow sweep; the wrist follows J3 = -(J1 + J2), so the
  // camera keeps pointing the same way whatever the other two joints do.
  const float pts[][2] = {{30, -60}, {60, -90}, {45, -30}, {-30, 60}, {-60, 90}, {0, 0}};
  for (auto& p : pts) {
    float target[NJ] = {p[0], p[1], -(p[0] + p[1])};
    if (!enqueue(target, 400)) return;
  }
  Serial.println("Demo queued");
}

void queueTest() {
  for (int j = 0; j < NJ; j++) {
    float out[NJ] = {0, 0, 0}, back[NJ] = {0, 0, 0};
    out[j] = 180;
    if (!enqueue(out, 300) || !enqueue(back, 300)) return;
  }
  Serial.println("Test queued: J1, then J2, then J3, half a turn and back");
}

void printHelp() {
  Serial.println(
      "Commands:\n"
      "  move <j1> <j2> <j3>   go to joint angles in degrees\n"
      "  jog <joint> <deg>     move one joint (1-3) by degrees\n"
      "  home | zero           go to 0 0 0 | call this spot 0 0 0\n"
      "  test | demo           one joint at a time | arm-style sequence\n"
      "  speed <deg/s>         top speed of the furthest-moving joint\n"
      "  accel <deg/s2>        acceleration\n"
      "  stop                  slow down, stop, clear the queue\n"
      "  on | off              drivers on (holding) | off (limp)\n"
      "  pos | status");
  Serial.printf("  speed now %.0f deg/s, accel %.0f deg/s2\n", speedDegS, accelDegS2);
}

void printStatus() {
  printPos("Position:");
  Serial.printf("Moving: %s  queued: %d  drivers: %s\n", segBusy ? "yes" : "no", qCount,
                driversOn ? "ON" : "off");
  Serial.printf("Speed %.0f deg/s  accel %.0f deg/s2  microsteps %d  steps/deg %.3f %.3f %.3f\n",
                speedDegS, accelDegS2, MICROSTEPS, stepsPerDeg[0], stepsPerDeg[1], stepsPerDeg[2]);
  for (int j = 0; j < NJ; j++) {
    if (!LIMIT_WIRED[j]) Serial.printf("J%d limit: not wired\n", j + 1);
    else Serial.printf("J%d limit: %s\n", j + 1, digitalRead(LIMIT_PIN[j]) == HIGH ? "TRIGGERED" : "ok");
  }
}

void handleCommand(char* line) {
  for (char* c = line; *c; c++) *c = tolower(*c);
  char cmd[12] = "";
  float a = 0, b = 0, c3 = 0;
  int n = sscanf(line, "%11s %f %f %f", cmd, &a, &b, &c3);
  if (n < 1) return;

  bool isMove = !strcmp(cmd, "move") || !strcmp(cmd, "jog") || !strcmp(cmd, "home") ||
                !strcmp(cmd, "test") || !strcmp(cmd, "demo");
  if (isMove && anyLimitTriggered(true)) return;

  if (!strcmp(cmd, "help") || !strcmp(cmd, "?")) {
    printHelp();
  } else if (!strcmp(cmd, "move")) {
    if (n < 4) { Serial.println("Usage: move <j1> <j2> <j3>"); return; }
    float t[NJ] = {a, b, c3};
    if (enqueue(t, 0)) Serial.printf("Moving to J1=%.1f J2=%.1f J3=%.1f\n", a, b, c3);
  } else if (!strcmp(cmd, "jog")) {
    int j = (int)a - 1;
    if (n < 3 || j < 0 || j >= NJ) { Serial.println("Usage: jog <1|2|3> <degrees>"); return; }
    float t[NJ] = {plannedDeg[0], plannedDeg[1], plannedDeg[2]};
    t[j] += b;
    if (enqueue(t, 0)) Serial.printf("Jogging J%d by %.1f\n", j + 1, b);
  } else if (!strcmp(cmd, "home")) {
    float t[NJ] = {0, 0, 0};
    if (enqueue(t, 0)) Serial.println("Going home (0 0 0)");
  } else if (!strcmp(cmd, "zero")) {
    if (segBusy || qCount) { Serial.println("Refused: wait until the arm has stopped"); return; }
    for (int j = 0; j < NJ; j++) { posSteps[j] = 0; plannedDeg[j] = 0; }
    Serial.println("Current position is now 0 0 0");
  } else if (!strcmp(cmd, "test")) {
    queueTest();
  } else if (!strcmp(cmd, "demo")) {
    queueDemo();
  } else if (!strcmp(cmd, "speed")) {
    if (n >= 2 && a > 0) speedDegS = a;
    Serial.printf("Speed %.0f deg/s\n", speedDegS);
  } else if (!strcmp(cmd, "accel")) {
    if (n >= 2 && a > 0) accelDegS2 = a;
    Serial.printf("Accel %.0f deg/s2\n", accelDegS2);
  } else if (!strcmp(cmd, "stop")) {
    qCount = 0;
    currentDwell = 0;
    if (segBusy) stopReq = true;
    Serial.println("Stopping");
  } else if (!strcmp(cmd, "on")) {
    setDrivers(true);
    Serial.println("Drivers ON (joints hold)");
  } else if (!strcmp(cmd, "off")) {
    segBusy = false;
    clearQueue();
    setDrivers(false);
    Serial.println("Drivers OFF (joints limp)");
  } else if (!strcmp(cmd, "pos")) {
    printPos("Position:");
  } else if (!strcmp(cmd, "status")) {
    printStatus();
  } else {
    Serial.printf("Unknown command '%s' (type help)\n", cmd);
  }
}

// ------------------------------------------------------------- serial input
char lineBuf[64];
int lineLen = 0;
uint32_t lastCharMs = 0;

void readSerial() {
  while (Serial.available()) {
    char ch = Serial.read();
    lastCharMs = millis();
    if (ch == '\n' || ch == '\r') {
      if (lineLen) { lineBuf[lineLen] = 0; handleCommand(lineBuf); lineLen = 0; }
    } else if (lineLen < (int)sizeof(lineBuf) - 1) {
      lineBuf[lineLen++] = ch;
    }
  }
  // Serial Monitor set to "No line ending": run the command after a short pause
  if (lineLen && millis() - lastCharMs > 150) {
    lineBuf[lineLen] = 0;
    handleCommand(lineBuf);
    lineLen = 0;
  }
}

// ------------------------------------------------------------- setup / loop
void setup() {
  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, HIGH);            // drivers off until the first move
  for (int j = 0; j < NJ; j++) {
    pinMode(STEP_PIN[j], OUTPUT);
    digitalWrite(STEP_PIN[j], LOW);
    pinMode(DIR_PIN[j], OUTPUT);
    pinMode(LIMIT_PIN[j], INPUT);        // input-only pins, external pull-ups
    stepsPerDeg[j] = MOTOR_STEPS_PER_REV * MICROSTEPS * GEAR_RATIO[j] / 360.0f;
    if (LIMIT_WIRED[j] && LIMIT_PIN[j] >= 32) limitMaskIn1 |= 1UL << (LIMIT_PIN[j] - 32);
  }

  Serial.begin(115200);
  delay(300);

  timer = timerBegin(1000000);           // 1 MHz timer clock
  timerAttachInterrupt(timer, &onTick);
  timerAlarm(timer, 1000000 / TICK_HZ, true, 0);

  Serial.println();
  Serial.println("EasyCliq arm motion (ESP32-B). Type help for commands.");
  Serial.println("Before moving: Vref 0.55 V on every driver, 100 uF on every VMOT.");
  printPos("Position:");
}

void loop() {
  readSerial();

  if (limitHit) {
    limitHit = false;
    clearQueue();
    anyLimitTriggered(true);
    printPos("STOPPED by limit switch at");
  }

  bool busy = segBusy;
  if (wasBusy && !busy) {
    for (int j = 0; j < NJ; j++) if (!qCount) plannedDeg[j] = jointDeg(j);
    printPos(stopReq ? "Stopped at" : "Arrived:");
    dwellUntil = millis() + currentDwell;
    if (!qCount && !HOLD_WHEN_IDLE) setDrivers(false);
  }
  wasBusy = busy;

  if (!busy && qCount && (int32_t)(millis() - dwellUntil) >= 0) {
    Pose p = queue[qHead];
    qHead = (qHead + 1) % QUEUE_LEN;
    qCount--;
    currentDwell = p.dwellMs;
    startMove(p.deg);
    wasBusy = segBusy;
    if (!segBusy) dwellUntil = millis() + currentDwell;  // already there
  }
}
