/*
  AI-Based Smart Lighting Optimization using IoT
  ESP32 + LDR voltage divider + PIR motion sensor + PWM LED

  Wiring:
  LDR voltage-divider midpoint -> GPIO34 (ADC)
  PIR OUT                    -> GPIO27
  LED (through suitable resistor / MOSFET driver) -> GPIO18
  Sensor VCC/GND              -> appropriate supply and common GND

  NOTE:
  - This demo uses an explainable rule-based controller as the local
    "AI decision" prototype. It can later be replaced by a trained model.
  - Do not connect mains AC lighting directly to an ESP32.
*/

const int LDR_PIN = 34;       // ADC1 input
const int PIR_PIN = 27;
const int LED_PIN = 18;

const int PWM_CHANNEL = 0;
const int PWM_FREQ = 5000;
const int PWM_RESOLUTION = 8; // 0..255

int luxEstimateFromAdc(int adcValue) {
  // Approximate mapping for demonstration only.
  // Calibrate against a lux meter for real measurements.
  return map(adcValue, 0, 4095, 0, 1000);
}

int decideBrightness(int lux, bool occupied) {
  if (!occupied) return 0;
  if (lux >= 700) return 10;
  if (lux >= 400) return 35;
  if (lux >= 200) return 60;
  return 100;
}

void setup() {
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);
  ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(LED_PIN, PWM_CHANNEL);

  Serial.println();
  Serial.println("======================================");
  Serial.println(" AI SMART LIGHTING - ESP32 STARTED");
  Serial.println("======================================");
}

void loop() {
  int adcValue = analogRead(LDR_PIN);
  int lux = luxEstimateFromAdc(adcValue);
  bool occupied = digitalRead(PIR_PIN) == HIGH;

  int brightness = decideBrightness(lux, occupied);
  int pwmValue = map(brightness, 0, 100, 0, 255);

  ledcWrite(PWM_CHANNEL, pwmValue);

  Serial.println("--------------------------------------");
  Serial.print("LDR ADC       : "); Serial.println(adcValue);
  Serial.print("Ambient light : "); Serial.print(lux); Serial.println(" lux (estimated)");
  Serial.print("PIR presence  : "); Serial.println(occupied ? "DETECTED" : "NOT DETECTED");
  Serial.print("LED brightness: "); Serial.print(brightness); Serial.println("%");
  Serial.print("PWM output    : "); Serial.print(pwmValue); Serial.println("/255");
  Serial.print("LED status    : "); Serial.println(brightness > 0 ? "ON" : "OFF");

  if (!occupied) {
    Serial.println("AI decision   : No person detected; lights OFF.");
  } else if (lux >= 700) {
    Serial.println("AI decision   : Strong daylight; minimum supporting light.");
  } else if (lux >= 400) {
    Serial.println("AI decision   : Moderate daylight; brightness 35%.");
  } else if (lux >= 200) {
    Serial.println("AI decision   : Low ambient light; brightness 60%.");
  } else {
    Serial.println("AI decision   : Dark environment; brightness 100%.");
  }

  delay(2000);
}
