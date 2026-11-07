import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="AI Smart Lighting - ESP32 Simulator", page_icon="💡", layout="wide")

st.title("💡 AI-Based Smart Lighting Optimization using IoT")
st.caption("ESP32 + PIR + LDR + PWM LED | Hardware simulation dashboard")

# State initialization
if "history" not in st.session_state:
    st.session_state.history = []

st.sidebar.header("ESP32 Sensor Simulator")
st.sidebar.info("Change the sensor values to simulate the ESP32 hardware inputs.")
lux = st.sidebar.slider("LDR ambient light (lux)", 0, 1000, 320, 10)
pir = st.sidebar.selectbox("PIR human presence", ["Detected", "Not detected"])
manual_mode = st.sidebar.toggle("Manual brightness override", value=False)
manual_brightness = st.sidebar.slider("Manual LED brightness (%)", 0, 100, 50, 5, disabled=not manual_mode)

presence = 1 if pir == "Detected" else 0

# Simple explainable control policy, matching the ESP32 firmware
if not presence:
    brightness = 0
    decision = "No person detected — LED switched OFF."
elif lux >= 700:
    brightness = 10
    decision = "Daylight is strong — minimum supporting light (10%)."
elif lux >= 400:
    brightness = 35
    decision = "Ambient light is moderate — LED set to 35%."
elif lux >= 200:
    brightness = 60
    decision = "Ambient light is low — LED set to 60%."
else:
    brightness = 100
    decision = "Dark environment — LED set to 100%."

if manual_mode and presence:
    brightness = manual_brightness
    decision = f"Manual override active — LED set to {brightness}%."
elif manual_mode and not presence:
    decision = "No person detected — safety rule keeps LED OFF despite manual override."

# Approximate LED power model for demo only
led_power_w = 12.0
power_w = led_power_w * brightness / 100.0
energy_kwh = power_w / 1000.0  # one-hour equivalent shown for this sample

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ambient light", f"{lux} lux")
c2.metric("Human presence", pir, delta="PIR sensor")
c3.metric("LED brightness", f"{brightness}%")
c4.metric("Estimated LED power", f"{power_w:.2f} W")

st.divider()
left, right = st.columns([1.1, 1])
with left:
    st.subheader("Live lighting status")
    st.markdown(
        f"""
        <div style="background:#111827;border:1px solid #334155;border-radius:16px;padding:24px;color:white;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:20px;font-weight:700;">ESP32 LED OUTPUT</span>
            <span style="background:{'#14532d' if brightness else '#7f1d1d'};padding:6px 12px;border-radius:20px;">
              {'ON' if brightness else 'OFF'}
            </span>
          </div>
          <div style="height:18px;background:#374151;border-radius:20px;margin-top:25px;overflow:hidden;">
            <div style="height:18px;width:{brightness}%;background:linear-gradient(90deg,#0ea5e9,#facc15);"></div>
          </div>
          <div style="font-size:38px;font-weight:800;margin-top:12px;">{brightness}%</div>
          <div style="color:#cbd5e1;">PWM duty cycle sent to LED</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.success("AI / control decision: " + decision)
with right:
    st.subheader("Sensor readings")
    sensor_df = pd.DataFrame({
        "Sensor": ["LDR", "PIR"],
        "Reading": [f"{lux} lux", pir],
        "Status": ["Bright" if lux >= 700 else "Dim / moderate", "Occupied" if presence else "Empty"]
    })
    st.dataframe(sensor_df, use_container_width=True, hide_index=True)
    st.caption("The dashboard uses simulated sensor readings. Connect real ESP32 telemetry to replace these controls.")

# Add a snapshot to session history
now = datetime.now().strftime("%H:%M:%S")
snapshot = {"Time": now, "Ambient lux": lux, "Presence": pir, "Brightness %": brightness, "Power W": round(power_w, 2)}
if not st.session_state.history or st.session_state.history[-1] != snapshot:
    st.session_state.history.append(snapshot)
st.session_state.history = st.session_state.history[-30:]
hist = pd.DataFrame(st.session_state.history)

st.subheader("Recent sensor / output history")
if len(hist) >= 1:
    st.dataframe(hist.iloc[::-1], use_container_width=True, hide_index=True)
    fig = px.line(hist, x="Time", y="Brightness %", markers=True, title="LED brightness over simulator updates")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Move the sidebar controls to create readings.")

st.subheader("ESP32 serial monitor preview")
st.code(
    f"""[IoT] LDR: {lux} lux
[IoT] PIR: {presence_label.upper()}
[AI] Decision: {decision}
[OUTPUT] LED brightness: {brightness}%
[OUTPUT] PWM duty: {round(brightness * 255 / 100)}/255
[ENERGY] Estimated power: {power_w:.2f} W""",
    language="text"
)

st.caption("Academic prototype: power and energy values are estimates. Use a suitable LED driver/MOSFET for real hardware; never connect a high-power lamp directly to an ESP32 GPIO.")
