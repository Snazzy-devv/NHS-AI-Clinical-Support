import streamlit as st
import pandas as pd
import requests
import time
from data_manager import get_patients, process_upload

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="NHS Clinical Decision Support",
    page_icon="🏥",
    layout="wide"
)

# --- NHS DESIGN SYSTEM ---
NHS_BLUE = "#005EB8"
NHS_DARK = "#003087"
BG_COLOR = "#F4F6F8"
TEXT_COLOR = "#212B36"
SUCCESS = "#00703c"
WARNING = "#ffdd00"
DANGER = "#d4351c"

# --- GLOBAL CSS ---
st.markdown(f"""
<style>
    .stApp {{
        background-color: {BG_COLOR};
        font-family: 'Inter', sans-serif;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {NHS_DARK};
    }}

    /* Header */
    .header {{
        background: {NHS_BLUE};
        color: white;
        padding: 18px;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
        font-size: 22px;
        margin-bottom: 25px;
    }}

    /* Cards */
    .card {{
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        border-left: 6px solid {NHS_BLUE};
    }}

    .card h3 {{
        margin: 0;
        font-size: 14px;
        color: #6B7280;
    }}

    .card h1 {{
        margin: 5px 0;
        font-size: 28px;
        color: {TEXT_COLOR};
    }}

    /* Buttons */
    .stButton>button {{
        background-color: {NHS_BLUE};
        color: white;
        border-radius: 8px;
        font-weight: 500;
    }}

</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/NHS-Logo.svg/1280px-NHS-Logo.svg.png", width=110)
    st.markdown("### Clinical Gateway")
    st.caption("Secure Workforce Entry")

    st.divider()

    st.markdown("#### Data Ingestion")
    file = st.file_uploader("Upload Patient Dataset", type=['csv', 'xlsx', 'json'])

    if file:
        with st.spinner("Processing data..."):
            df_new, msg = process_upload(file)
            if df_new is not None:
                st.success("Upload successful")
            else:
                st.error(msg)

    st.divider()
    st.caption("System Version 2.1.0")

# --- HEADER ---
st.markdown('<div class="header">Clinical Decision Support — Population Health</div>', unsafe_allow_html=True)

# --- LOAD DATA ---
df = get_patients()

if df.empty:
    st.info("No data available. Upload patient dataset.")
    st.stop()

# --- DATA PROCESSING ---
latest_df = df.sort_values('date').groupby('patient_id').tail(1)

risk_threshold = 3
high_risk_df = latest_df[latest_df['missed_appointments'] >= risk_threshold]
stable_df = latest_df[latest_df['missed_appointments'] < risk_threshold]

# --- KPI CARDS ---
col1, col2, col3 = st.columns(3)

def card(title, value):
    return f"""
    <div class="card">
        <h3>{title}</h3>
        <h1>{value}</h1>
    </div>
    """

with col1:
    st.markdown(card("Total Caseload", len(latest_df)), unsafe_allow_html=True)
    if st.button("View All Patients"):
        st.session_state['filter'] = 'all'

with col2:
    st.markdown(card("High Risk Cohort", len(high_risk_df)), unsafe_allow_html=True)
    if st.button("Filter High Risk"):
        st.session_state['filter'] = 'high'

with col3:
    st.markdown(card("Stable Cohort", len(stable_df)), unsafe_allow_html=True)
    if st.button("Filter Stable"):
        st.session_state['filter'] = 'stable'

st.divider()

# --- FILTER LOGIC ---
current_filter = st.session_state.get('filter', 'all')

if current_filter == 'high':
    display_df = high_risk_df
    title = "High Risk Patients"
elif current_filter == 'stable':
    display_df = stable_df
    title = "Stable Patients"
else:
    display_df = latest_df
    title = "All Patients"

# --- MAIN LAYOUT ---
left, right = st.columns([1.2, 1.8])

with left:
    st.subheader(title)

    st.dataframe(
        display_df[['patient_id', 'missed_appointments', 'engagement_drop_percent']],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("#### Select Patient")
    patient_id = st.selectbox("Patient ID", display_df['patient_id'])

    patient_data = display_df[display_df['patient_id'] == patient_id].iloc[0]

# --- AI PANEL ---
with right:
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

                # Risk color mapping
                risk_map = {
                    "HIGH": DANGER,
                    "MODERATE": WARNING,
                    "LOW": SUCCESS
                }

                color = risk_map.get(resp['risk_level'], NHS_BLUE)

                st.markdown(f"""
                <div style="background:white;padding:20px;border-radius:12px;border-left:8px solid {color}">
                    <h2 style="color:{color};margin:0">{resp['risk_level']} RISK</h2>
                    <p>{resp['context']}</p>
                </div>
                """, unsafe_allow_html=True)

                # Chart
                history = df[df['patient_id'] == patient_id].sort_values('date')
                st.line_chart(history.set_index('date')['engagement_drop_percent'])

                # Alerts
                st.markdown("### Clinical Alerts")
                for alert in resp['alerts']:
                    st.warning(alert)

                st.caption(f"Governance: {resp['governance']}")

            except Exception:
                st.error("Backend connection failed. Check API service.")
