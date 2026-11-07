# AI-Based Smart Lighting Optimization using IoT
## ESP32 + PIR + LDR hardware simulation

### 1. What this project demonstrates
- PIR sensor detects whether a person is present.
- LDR sensor estimates surrounding light intensity.
- ESP32 applies a smart brightness-control policy.
- LED brightness is controlled using PWM.
- A Streamlit dashboard simulates sensor inputs and displays the resulting lighting output.

**Important:** The included dashboard is a software simulation. The Arduino sketch is intended for an ESP32 board or an ESP32 simulator such as Wokwi. No physical sensor readings are claimed by the dashboard.

### 2. Hardware / simulator components
- ESP32 DevKit V1
- PIR motion sensor (HC-SR501)
- LDR photoresistor
- 10 kΩ resistor for LDR voltage divider
- LED + suitable current-limiting resistor, or an LED driver/MOSFET for a larger lamp
- Breadboard and jumper wires

### 3. Wiring
| Component | ESP32 connection |
|---|---|
| LDR divider midpoint | GPIO34 (ADC) |
| PIR OUT | GPIO27 |
| LED control input | GPIO18 |
| Sensor GND | ESP32 GND |
| Sensor VCC | According to sensor module rating |

LDR divider: connect 3.3V -> LDR -> midpoint -> 10 kΩ resistor -> GND.
Connect the midpoint to GPIO34.

**Safety:** Never connect mains AC or a high-power lamp directly to an ESP32 GPIO. Use an appropriately rated isolated relay/driver and get qualified supervision for mains wiring.

### 4. Smart control logic
| Condition | LED output |
|---|---:|
| No person detected | 0% (OFF) |
| Person detected and light >= 700 lux | 10% |
| Person detected and light 400–699 lux | 35% |
| Person detected and light 200–399 lux | 60% |
| Person detected and light < 200 lux | 100% |

This is an explainable baseline controller. For a research-grade AI extension, collect labelled sensor/brightness data and train a regression model, then compare its performance with this baseline.

### 5. Run the Python + Streamlit simulator
Install Python 3.10 or newer, then run:

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# Ubuntu/macOS:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (normally http://localhost:8501).
Use the sidebar sliders to change ambient light and PIR presence. The dashboard updates the LED status, brightness, estimated power, decision explanation and serial-monitor-style output.

### 6. Upload ESP32 firmware
1. Open Arduino IDE.
2. Install the ESP32 board package.
3. Select your ESP32 DevKit board and its serial port.
4. Open `esp32_firmware/smart_lighting_esp32.ino`.
5. Upload the sketch.
6. Open Serial Monitor at 115200 baud.
7. Change the LDR illumination and trigger the PIR sensor to observe the output.

### 7. Sample serial output
```text
======================================
 AI SMART LIGHTING - ESP32 STARTED
======================================
LDR ADC       : 1310
Ambient light : 319 lux (estimated)
PIR presence  : DETECTED
LED brightness: 60%
PWM output    : 153/255
LED status    : ON
AI decision   : Low ambient light; brightness 60%.
```

### 8. Project limitations
- The ADC-to-lux conversion is approximate and must be calibrated for the actual LDR and resistor.
- The dashboard uses user-controlled simulated sensor inputs, not a live ESP32 connection.
- Power is an illustrative estimate for a 12 W LED at the selected duty cycle.
- The decision policy is a baseline intelligent controller, not a trained AI model. Add a trained model only after collecting real sensor data.

### 9. Files
- `app.py` — Streamlit dashboard simulator
- `esp32_firmware/smart_lighting_esp32.ino` — ESP32 firmware
- `requirements.txt` — Python dependencies
