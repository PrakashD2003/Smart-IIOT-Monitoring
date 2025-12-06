import time

import pandas as pd
import plotly.express as px
import streamlit as st
from utils.api import get_machine_live

st.set_page_config(page_title="Machine Live View", layout="wide")

# ==============================
# CSS FIX (Sidebar + Theme)
# ==============================
st.markdown(
    """
<style>

    /* Hide default Streamlit multipage sidebar */
    section[data-testid="stSidebarNav"] {
        display: none !important;
    }
    div[data-testid="stSidebarNav"] {
        display: none !important;
    }
    /* Older Streamlit versions */
    .css-1oe6wy4, .css-nqowgj, .css-1v0mbdj {
        display: none !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0E1117;
        padding: 20px;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

</style>
""",
    unsafe_allow_html=True,
)
# ==============================
# Custom Sidebar
# ==============================
with st.sidebar:
    st.markdown(
        "<h2 style='color:white;'>📊 Dashboard</h2>",
        unsafe_allow_html=True,
    )

    if st.button("📡 Monitoring"):
        st.switch_page("app.py")
    if st.button("🛠 Machine View"):
        st.switch_page("pages/machine_view.py")

# ==============================
# PAGE CONTENT
# ==============================
if "machine_id" not in st.session_state:
    st.error("No machine selected! Go back to Dashboard.")
    st.stop()

machine_id = st.session_state["machine_id"]

st.title(f"📡 Real-Time Monitoring — Machine {machine_id}")

# Initialize history
if "history" not in st.session_state:
    st.session_state["history"] = {
        "timestamp": [],
        "failure_prob": [],
        "temp": [],
        "speed": [],
        "pressure": [],
        "vibration": [],
        "torque": [],
        "tool_wear": [],
    }

if "start_time" not in st.session_state:
    st.session_state["start_time"] = time.time()

placeholder = st.empty()

# ==============================
# LOOP FOR REAL-TIME UPDATES
# ==============================
while True:
    data = get_machine_live(machine_id)
    sensors = data["sensor_data"]

    elapsed = round(time.time() - st.session_state["start_time"], 2)

    hist = st.session_state["history"]
    hist["timestamp"].append(elapsed)
    hist["failure_prob"].append(data["failure_probability"])

    for key in sensors:
        hist[key].append(sensors[key])

    df = pd.DataFrame(hist).tail(100)

    with placeholder.container():
        # =========================
        # KPI CARDS
        # =========================
        k1, k2, k3 = st.columns(3)

        k1.markdown(
            f"""
            <div style="padding:15px;border-radius:10px;background:#1E1E1E;
                        border:1px solid #333;color:white;text-align:center;">
                <h4>Temperature</h4>
                <h2 style="color:#FF6B6B;">{sensors['temp']} °C</h2>
            </div>
        """,
            unsafe_allow_html=True,
        )

        k2.markdown(
            f"""
            <div style="padding:15px;border-radius:10px;background:#1E1E1E;
                        border:1px solid #333;color:white;text-align:center;">
                <h4>Speed</h4>
                <h2 style="color:#4D96FF;">{sensors['speed']} rpm</h2>
            </div>
        """,
            unsafe_allow_html=True,
        )

        k3.markdown(
            f"""
            <div style="padding:15px;border-radius:10px;background:#1E1E1E;
                        border:1px solid #333;color:white;text-align:center;">
                <h4>Failure Probability</h4>
                <h2 style="color:#FFA600;">
                {round(data['failure_probability']*100,2)}%
                </h2>
            </div>
        """,
            unsafe_allow_html=True,
        )

        # =========================
        # FAILURE PROBABILITY PLOT
        # =========================
        st.subheader("📉 Failure Probability Over Time")

        fig = px.line(
            df,
            x="timestamp",
            y="failure_prob",
            labels={
                "timestamp": "Time (s)",
                "failure_prob": "Failure Probability",
            },
        )

        fig.update_layout(
            template="plotly_dark",
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
        )

        st.plotly_chart(fig, use_container_width=True)

        # =========================
        # SENSOR TRENDS PLOT
        # =========================
        st.subheader("📈 Sensor Trends")

        fig2 = px.line(
            df,
            x="timestamp",
            y=[
                "temp",
                "speed",
                "pressure",
                "vibration",
                "torque",
                "tool_wear",
            ],
            labels={"timestamp": "Time (s)"},
        )

        fig2.update_layout(
            template="plotly_dark",
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
        )

        st.plotly_chart(fig2, use_container_width=True)

    time.sleep(1)
