// EasyCliq bench test: three DRV8825 + NEMA17 channels (J1, J2, J3) on ESP32-B (Motion).
// Wiring: EasyCliq-Wiring-Diagram.pdf, wiring-diagram.html, and WIRING.md Steps 4-5.
//
// Serial Monitor at 115200 baud. Commands:
//   a = ALL three motors forward 1 rev together
//   f = selected motor forward 1 rev    r = selected motor reverse 1 rev
//   j = select next motor (J1 -> J2 -> J3)
//   e = enable drivers    d = disable drivers (motors go limp)
//   1..5 = speed          l = read limit switches

const int NUM_MOTORS = 3;
const char* NAMES[NUM_MOTORS]   = {"J1", "J2", "J3"};
const int STEP_PINS[NUM_MOTORS] = {13, 26, 23};
const int DIR_PINS[NUM_MOTORS]  = {27, 25, 22};
const int LIMIT_PINS[NUM_MOTORS] = {34, 35, 36};  // 36 = VP on the board
const int PIN_EN = 21;  // shared EN, active LOW; 4.7k pull-up keeps drivers off at boot

// Set an entry true once that switch and its 10k pull-up are wired (Step 5).
// These are input-only pins with no internal pull-up, so an unwired pin reads random values.
const bool LIMIT_WIRED[NUM_MOTORS] = {false, false, false};

// 1 with M0/M1/M2 unconnected; 16 once M2 is tied to 3V3 (Step 4c).
const int MICROSTEPS = 1;
const long STEPS_PER_REV = 200L * MICROSTEPS;

// Full-step interval (us) per speed level: 30, 60, 120, 200, 300 rpm.
const unsigned int SPEED_US[] = {0, 10000, 5000, 2500, 1500, 1000};
const unsigned int START_US = 5000;  // ramp starts here so the motors don't stall
const long RAMP_FULL_STEPS = 40;
int speedLevel = 2;
int selected = 0;

bool limitTriggered(int m) {
  return LIMIT_WIRED[m] && digitalRead(LIMIT_PINS[m]) == HIGH;
}

void setEnabled(bool on) {
  digitalWrite(PIN_EN, on ? LOW : HIGH);
  Serial.println(on ? "Drivers ENABLED" : "Drivers DISABLED");
}

// Moves every motor whose bit is set in `mask` by `steps`, all in lockstep.
void moveSteps(unsigned mask, long steps, bool forward) {
  for (int m = 0; m < NUM_MOTORS; m++) {
    if ((mask & (1u << m)) && limitTriggered(m)) {
      Serial.printf("Refused: %s limit switch is TRIGGERED\n", NAMES[m]);
      return;
    }
  }
  setEnabled(true);
  for (int m = 0; m < NUM_MOTORS; m++) {
    if (mask & (1u << m)) digitalWrite(DIR_PINS[m], forward ? HIGH : LOW);
  }
  delayMicroseconds(5);  // DIR setup time before the first STEP

  const float startUs  = (float)START_US / MICROSTEPS;
  const float targetUs = (float)SPEED_US[speedLevel] / MICROSTEPS;
  const long rampSteps = RAMP_FULL_STEPS * MICROSTEPS;

  for (long i = 0; i < steps; i++) {
    for (int m = 0; m < NUM_MOTORS; m++) {
      if ((mask & (1u << m)) && limitTriggered(m)) {
        Serial.printf("STOP: %s limit switch hit after %ld steps\n", NAMES[m], i);
        return;
      }
    }
    // Linear ramp up at the start and down at the end.
    float us = targetUs;
    long fromEdge = min(i, steps - 1 - i);
    if (startUs > targetUs && fromEdge < rampSteps) {
      us = startUs - (startUs - targetUs) * fromEdge / rampSteps;
    }
    for (int m = 0; m < NUM_MOTORS; m++) {
      if (mask & (1u << m)) digitalWrite(STEP_PINS[m], HIGH);
    }
    delayMicroseconds(4);  // DRV8825 needs >= 1.9 us high
    for (int m = 0; m < NUM_MOTORS; m++) {
      if (mask & (1u << m)) digitalWrite(STEP_PINS[m], LOW);
    }
    delayMicroseconds((unsigned int)us - 4);
    if ((i & 0xFF) == 0) yield();
  }
  Serial.printf("Done: %ld steps %s\n", steps, forward ? "forward" : "reverse");
}

void setup() {
  pinMode(PIN_EN, OUTPUT);
  digitalWrite(PIN_EN, HIGH);  // disabled until commanded
  for (int m = 0; m < NUM_MOTORS; m++) {
    pinMode(STEP_PINS[m], OUTPUT);
    pinMode(DIR_PINS[m], OUTPUT);
    digitalWrite(STEP_PINS[m], LOW);
    pinMode(LIMIT_PINS[m], INPUT);  // input-only pins, external pull-ups
  }

  Serial.begin(115200);
  delay(300);
  Serial.println();
  Serial.println("EasyCliq stepper bench test (ESP32-B, J1/J2/J3)");
  Serial.println("Check before running: Vref = 0.55 V, 100 uF cap on each VMOT, common GND.");
  Serial.printf("Microsteps: %d  Steps/rev: %ld\n", MICROSTEPS, STEPS_PER_REV);
  Serial.println("Commands: a f r j e d 1-5 l");
  Serial.printf("Selected: %s\n", NAMES[selected]);
}

void loop() {
  if (!Serial.available()) return;
  char c = Serial.read();
  switch (c) {
    case 'a': moveSteps(0b111, STEPS_PER_REV, true); break;
    case 'f': moveSteps(1u << selected, STEPS_PER_REV, true); break;
    case 'r': moveSteps(1u << selected, STEPS_PER_REV, false); break;
    case 'j':
      selected = (selected + 1) % NUM_MOTORS;
      Serial.printf("Selected: %s\n", NAMES[selected]);
      break;
    case 'e': setEnabled(true); break;
    case 'd': setEnabled(false); break;
    case 'l':
      for (int m = 0; m < NUM_MOTORS; m++) {
        if (!LIMIT_WIRED[m]) Serial.printf("%s limit: not wired (LIMIT_WIRED is false)\n", NAMES[m]);
        else Serial.printf("%s limit: %s\n", NAMES[m],
                           digitalRead(LIMIT_PINS[m]) == HIGH ? "TRIGGERED" : "OK");
      }
      break;
    case '1': case '2': case '3': case '4': case '5':
      speedLevel = c - '0';
      Serial.printf("Speed %d (%lu us per full step)\n", speedLevel,
                    (unsigned long)SPEED_US[speedLevel]);
      break;
    case '\r': case '\n': case ' ': break;
    default: Serial.printf("Unknown command '%c'\n", c);
  }
}
