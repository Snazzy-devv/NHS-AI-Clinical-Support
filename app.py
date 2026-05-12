import streamlit as st
import pandas as pd
import requests
import time
from data_manager import get_patients, process_upload

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NHS Clinical Decision Support",
    layout="wide"
)

# ---------------- NHS DESIGN SYSTEM ----------------
NHS_BLUE = "#005EB8"
NHS_DARK = "#003087"
BG = "#F4F6F8"
TEXT = "#212B36"
SUCCESS = "#00703c"
WARNING = "#ffb81c"
DANGER = "#d4351c"

# ---------------- GLOBAL CSS ----------------
st.markdown(f"""
<style>

/* App */
.stApp {{
    background-color: {BG};
    font-family: 'Inter', sans-serif;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background-color: {NHS_DARK};
}}
[data-testid="stSidebar"] * {{
    color: white !important;
}}

/* Header */
.header {{
    background: {NHS_BLUE};
    color: white;
    padding: 16px 20px;
    border-radius: 10px;
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 25px;
}}

/* KPI Section */
.kpi-container {{
    display: flex;
    gap: 20px;
    margin-bottom: 25px;
}}

.kpi-card {{
    flex: 1;
    background: linear-gradient(135deg, #ffffff, #f9fbfd);
    padding: 22px;
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    border: 1px solid #e6ecf2;
    transition: 0.3s ease;
}}

.kpi-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 10px 22px rgba(0,0,0,0.08);
}}

.kpi-title {{
    font-size: 13px;
    color: #6b7280;
    text-transform: uppercase;
}}

.kpi-value {{
    font-size: 34px;
    font-weight: 700;
    color: {NHS_DARK};
    margin-top: 5px;
}}

.kpi-tag {{
    margin-top: 10px;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 12px;
    display: inline-block;
}}

.tag-danger {{ background: #fdecea; color: {DANGER}; }}
.tag-success {{ background: #e8f5e9; color: {SUCCESS}; }}
.tag-neutral {{ background: #e3f2fd; color: {NHS_BLUE}; }}

/* Cards */
.card {{
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}}

/* Buttons */
.stButton > button {{
    width: 100%;
    background-color: {NHS_BLUE};
    color: white;
    border-radius: 8px;
    font-weight: 500;
    border: none;
}}

</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/NHS-Logo.svg/1280px-NHS-Logo.svg.png", width=110)
    st.markdown("### Clinical Gateway")
    st.caption("Secure Workforce Access")

    st.divider()

    st.markdown("#### Data Ingestion")
    file = st.file_uploader("Upload Patient Dataset", type=['csv', 'xlsx', 'json'])

    if file:
        with st.spinner("Processing..."):
            df_new, msg = process_upload(file)
            if df_new is not None:
                st.success("Upload successful")
            else:
                st.error(msg)

    st.divider()
    st.caption("System Version 2.1.0")

# ---------------- HEADER ----------------
st.markdown('<div class="header">Clinical Decision Support — Population Health</div>', unsafe_allow_html=True)

# ---------------- DATA ----------------
df = get_patients()

if df.empty:
    st.info("Upload patient data to begin analysis.")
    st.stop()

latest_df = df.sort_values('date').groupby('patient_id').tail(1)

risk_threshold = 3
high_risk_df = latest_df[latest_df['missed_appointments'] >= risk_threshold]
stable_df = latest_df[latest_df['missed_appointments'] < risk_threshold]

# ---------------- KPI SECTION ----------------
st.markdown("### Clinical Triage Overview")

st.markdown(f"""
<div class="kpi-container">

    <div class="kpi-card">
        <div class="kpi-title">Total Caseload</div>
        <div class="kpi-value">{len(latest_df)}</div>
        <div class="kpi-tag tag-neutral">Active Patients</div>
    </div>

    <div class="kpi-card">
        <div class="kpi-title">Critical Cases</div>
        <div class="kpi-value">{len(high_risk_df)}</div>
        <div class="kpi-tag tag-danger">Requires Review</div>
    </div>

    <div class="kpi-card">
        <div class="kpi-title">Stable Patients</div>
        <div class="kpi-value">{len(stable_df)}</div>
        <div class="kpi-tag tag-success">Under Monitoring</div>
    </div>

</div>
""", unsafe_allow_html=True)

# ---------------- FILTER BUTTONS ----------------
f1, f2, f3 = st.columns(3)

with f1:
    if st.button("All Patients"):
        st.session_state['filter'] = 'all'

with f2:
    if st.button("High Risk"):
        st.session_state['filter'] = 'high'

with f3:
    if st.button("Stable"):
        st.session_state['filter'] = 'stable'

st.divider()

# ---------------- FILTER LOGIC ----------------
filter_state = st.session_state.get('filter', 'all')

if filter_state == 'high':
    display_df = high_risk_df
    title = "High Risk Patients"
elif filter_state == 'stable':
    display_df = stable_df
    title = "Stable Patients"
else:
    display_df = latest_df
    title = "All Patients"

# ---------------- MAIN LAYOUT ----------------
left, right = st.columns([1.2, 1.8], gap="large")

# LEFT PANEL
with left:
    st.markdown(f'<div class="card">', unsafe_allow_html=True)

    st.subheader(title)

    st.dataframe(
        display_df[['patient_id', 'missed_appointments', 'engagement_drop_percent']],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("#### Select Patient")
    patient_id = st.selectbox("Patient ID", display_df['patient_id'])

    patient_data = display_df[display_df['patient_id'] == patient_id].iloc[0]

    st.markdown('</div>', unsafe_allow_html=True)

# RIGHT PANEL (AI)
with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    if st.button("Generate Clinical Intelligence"):

        with st.spinner("Running AI analysis..."):
            payload = {
                "patient_id": str(patient_data['patient_id']),
                "missed_appointments": int(patient_data['missed_appointments']),
                "engagement_drop_percent": int(patient_data['engagement_drop_percent']),
                "prev_crisis": bool(patient_data['prev_crisis']),
                "referral_text": str(patient_data['referral_text'])
            }

            try:
                resp = requests.post(
                    "https://nhs-ai-clinical-support-gl6v.onrender.com/analyze",
                    json=payload,
                    timeout=15
                ).json()

                color_map = {
                    "HIGH": DANGER,
                    "MODERATE": WARNING,
                    "LOW": SUCCESS
                }

                color = color_map.get(resp['risk_level'], NHS_BLUE)

                st.markdown(f"""
                <div style="padding:20px;border-left:8px solid {color};background:white;border-radius:10px;">
                    <h2 style="color:{color};margin:0">{resp['risk_level']} RISK</h2>
                    <p>{resp['context']}</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("### Engagement Trend")
                history = df[df['patient_id'] == patient_id].sort_values('date')
                st.line_chart(history.set_index('date')['engagement_drop_percent'])

                st.markdown("### Clinical Alerts")
                for alert in resp['alerts']:
                    st.warning(alert)

                st.caption(f"Governance: {resp['governance']}")

            except:
                st.error("Unable to connect to analysis engine.")

    st.markdown('</div>', unsafe_allow_html=True)
