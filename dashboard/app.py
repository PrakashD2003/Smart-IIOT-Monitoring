import streamlit as st
from utils.api import get_all_machines

st.set_page_config(page_title="PdM Dashboard", layout="wide")

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
st.title("🛠 Predictive Maintenance Dashboard")
st.subheader("Machine Overview")

machines = get_all_machines()

cols = st.columns(2)

for i, m in enumerate(machines):
    with cols[i % 2]:
        st.markdown(f"### {m['name']} ({m['id']})")
        color = "green" if m["status"] == "OK" else "red"
        status_html = (
            f"**Status:** <span style='color:{color};"
            f"font-weight:bold'>{m['status']}</span>"
        )
        st.markdown(status_html, unsafe_allow_html=True)

        failure_pct = f"{m['failure_probability']*100:.2f}%"
        st.metric("Failure Probability", failure_pct)
        st.write(f"Last Updated: {m['last_updated']}")

        if st.button("🔍 View Machine", key=m["id"]):
            st.session_state["machine_id"] = m["id"]
            st.switch_page("pages/machine_view.py")
