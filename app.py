
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="AI Smart Lighting - ESP32 Simulator",
    page_icon="💡",
    layout="wide"
)

st.title("💡 AI-Based Smart Lighting Optimization using IoT")
st.caption("ESP32 + PIR + LDR + PWM LED | Hardware Simulation Dashboard")

if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar sensor controls
st.sidebar.header("ESP32 Sensor Simulator")
st.sidebar.info("Adjust sensor values to simulate hardware.")

lux = st.sidebar.slider(
    "LDR ambient light (lux)", 0, 1000, 320, 10
)

pir_status = st.sidebar.selectbox(
    "PIR human presence",
    ["Detected", "Not detected"]
)

manual_mode = st.sidebar.toggle(
    "Manual brightness override", value=False
)

manual_brightness = st.sidebar.slider(
    "Manual LED brightness (%)",
    0, 100, 50, 5,
    disabled=not manual_mode
)

# Sensor processing
presence = 1 if pir_status == "Detected" else 0

# Smart lighting decision
if presence == 0:
    brightness = 0
    decision = "No person detected - LED switched OFF."

elif lux >= 700:
    brightness = 10
    decision = "Strong daylight - LED set to 10%."

elif lux >= 400:
    brightness = 35
    decision = "Moderate ambient light - LED set to 35%."

elif lux >= 200:
    brightness = 60
    decision = "Low ambient light - LED set to 60%."

else:
    brightness = 100
    decision = "Dark environment - LED set to 100%."

# Manual override
if manual_mode and presence == 1:
    brightness = manual_brightness
    decision = f"Manual override active - LED set to {brightness}%."

elif manual_mode and presence == 0:
    decision = "No person detected - LED remains OFF."

# Energy calculations
rated_led_power_w = 12.0
power_w = rated_led_power_w * brightness / 100
energy_kwh = power_w / 1000

# Dashboard metrics
c1, c2, c3, c4 = st.columns(4)

c1.metric("Ambient Light", f"{lux} lux")
c2.metric("Human Presence", pir_status)
c3.metric("LED Brightness", f"{brightness}%")
c4.metric("Estimated Power", f"{power_w:.2f} W")

st.divider()

left, right = st.columns([1.1, 1])

with left:
    st.subheader("Live Lighting Status")

    led_state = "ON" if brightness > 0 else "OFF"
    led_color = "#14532d" if brightness > 0 else "#7f1d1d"

    st.markdown(
        f"""
        <div style="
            background:#111827;
            border:1px solid #334155;
            border-radius:16px;
            padding:24px;
            color:white;
        ">
            <h3>ESP32 LED OUTPUT</h3>
            <span style="
                background:{led_color};
                padding:8px 15px;
                border-radius:20px;
            ">{led_state}</span>

            <div style="
                height:18px;
                background:#374151;
                border-radius:20px;
                margin-top:25px;
                overflow:hidden;
            ">
                <div style="
                    height:18px;
                    width:{brightness}%;
                    background:linear-gradient(90deg,#0ea5e9,#facc15);
                "></div>
            </div>

            <h1>{brightness}%</h1>
            <p>PWM duty cycle sent to LED</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.success("Smart lighting decision: " + decision)

with right:
    st.subheader("Sensor Readings")

    sensor_df = pd.DataFrame({
        "Sensor": ["LDR", "PIR"],
        "Reading": [f"{lux} lux", pir_status],
        "Status": [
            "Bright" if lux >= 700 else "Dim / Moderate",
            "Occupied" if presence else "Empty"
        ]
    })

    st.dataframe(
        sensor_df,
        use_container_width=True,
        hide_index=True
    )

    st.caption("Simulation readings. Connect ESP32 telemetry for live hardware data.")

# History tracking
current_time = datetime.now().strftime("%H:%M:%S")

snapshot = {
    "Time": current_time,
    "Ambient lux": lux,
    "Presence": pir_status,
    "Brightness %": brightness,
    "Power W": round(power_w, 2)
}

if (
    not st.session_state.history
    or st.session_state.history[-1] != snapshot
):
    st.session_state.history.append(snapshot)

st.session_state.history = st.session_state.history[-30:]

history_df = pd.DataFrame(st.session_state.history)

st.subheader("Recent Sensor / Output History")

if not history_df.empty:

    st.dataframe(
        history_df.iloc[::-1],
        use_container_width=True,
        hide_index=True
    )

    fig = px.line(
        history_df,
        x="Time",
        y="Brightness %",
        markers=True,
        title="LED Brightness History"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Change sensor controls to generate readings.")

# ESP32 serial monitor preview
st.subheader("ESP32 Serial Monitor Preview")

pwm_value = round(brightness * 255 / 100)

serial_output = f"""
[IoT] LDR: {lux} lux
[IoT] PIR: {pir_status.upper()}
[AI] Decision: {decision}
[OUTPUT] LED Status: {led_state}
[OUTPUT] LED Brightness: {brightness}%
[OUTPUT] PWM Duty: {pwm_value}/255
[ENERGY] Estimated Power: {power_w:.2f} W
[ENERGY] One-hour Energy: {energy_kwh:.4f} kWh
"""

st.code(serial_output, language="text")

st.caption(
    "Academic prototype: sensor readings are simulated. "
    "Power and energy are estimates based on a 12 W LED. "
    "Use a suitable LED driver for actual hardware."
)
