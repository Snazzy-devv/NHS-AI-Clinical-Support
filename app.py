import streamlit as st
import pandas as pd
import requests
import time
from data_manager import get_patients, process_upload

# --- Page Configuration ---
st.set_page_config(
    page_title="NHS AI Clinical Support", 
    page_icon="🏥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium Refined CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
        
        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif !important;
            background-color: #f4f7f9;
        }

        /* Sidebar: Restored Deep Navy Background */
        [data-testid="stSidebar"] {
            background-color: #002f5c !important;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }

        /* FILE UPLOADER: Blue Text on White Background */
        [data-testid="stFileUploader"] section {
            background-color: #ffffff !important; 
            border: 2px solid #005eb8 !important; 
            border-radius: 12px;
        }
        [data-testid="stFileUploader"] label, 
        [data-testid="stFileUploader"] small,
        [data-testid="stFileUploader"] span {
            color: #005eb8 !important; 
            font-weight: 800 !important;
        }

        /* MAIN HEADER: NHS Blue with Logo Integration */
        .main-header-container {
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #005eb8;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 20px rgba(0, 94, 184, 0.2);
            margin-bottom: 5px;
        }
        .main-header-text {
            color: white;
            font-weight: 800;
            font-size: 2rem;
            margin-left: 20px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* NEWS TICKER */
        .news-ticker {
            background: #e6f2ff;
            padding: 12px;
            border-radius: 8px;
            border-left: 6px solid #005eb8;
            margin-bottom: 25px;
            overflow: hidden;
            white-space: nowrap;
        }
        .ticker-text {
            display: inline-block;
            padding-left: 100%;
            animation: ticker 30s linear infinite;
            font-weight: 700;
            color: #002f5c;
        }
        @keyframes ticker {
            0% { transform: translate(0, 0); }
            100% { transform: translate(-100%, 0); }
        }

        /* PULSING KPI CARDS */
        div[data-testid="stMetricValue"] {
            background-color: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            border-bottom: 5px solid #005eb8;
            animation: pulse-kpi 4s infinite ease-in-out;
        }
        @keyframes pulse-kpi {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar (Clinical Gateway) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/NHS-Logo.svg/1280px-NHS-Logo.svg.png", width=130)
    st.markdown("## Clinical Gateway")
    st.divider()
    
    st.subheader("Data Ingestion")
    file = st.file_uploader("UPLOAD PATIENT CASELOAD", type=['csv', 'xlsx', 'json'])
    
    if file:
        df_new, msg = process_upload(file)
        if df_new is not None: st.success("Database Synchronized")
        else: st.error(msg)
    
    st.divider()
    st.info("System Version: 2.2.5-Enterprise")

# --- Main Dashboard Header with Logo ---
st.markdown(f"""
    <div class="main-header-container">
        <img src="https://upload.wikimedia.org/wikipedia/commons/f/fa/NHS-Logo.svg" width="100">
        <div class="main-header-text">Clinical Decision Support: Population Health</div>
    </div>
""", unsafe_allow_html=True)

# News Feed Ticker
st.markdown("""
    <div class="news-ticker">
        <div class="ticker-text">
            LIVE UPDATE: AI Triage Model v2.2 active • 🔴 CRITICAL: 3 Alerts Pending • 🟢 STABLE: System Nominal • NHS Governance Protocol 2026 Verified ...
        </div>
    </div>
""", unsafe_allow_html=True)

df = get_patients()

if not df.empty:
    latest_df = df.sort_values('date').groupby('patient_id').tail(1)
    
    # KPI Row
    risk_threshold = 3
    high_risk_df = latest_df[latest_df['missed_appointments'] >= risk_threshold]
    stable_df = latest_df[latest_df['missed_appointments'] < risk_threshold]
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Caseload", len(latest_df))
        if st.button("🔎 View Master List", use_container_width=True): st.session_state['filter'] = 'all'
    with m2:
        st.metric("🔴 Critical Risks", len(high_risk_df), delta="Immediate Review")
        if st.button("🔴 Filter Critical", use_container_width=True): st.session_state['filter'] = 'high'
    with m3:
        st.metric("🟢 Normal Status", len(stable_df), delta="Operational")
        if st.button("🟢 Filter Stable", use_container_width=True): st.session_state['filter'] = 'stable'

    st.write("---")

    # Filter Logic
    current_filter = st.session_state.get('filter', 'all')
    if current_filter == 'high':
        display_df, title, box_bg = high_risk_df, "🔴 Priority Critical Queue", "#ffebe9"
    elif current_filter == 'stable':
        display_df, title, box_bg = stable_df, "🟢 Clinical Update: Stable Patients", "#e7f6ec"
    else:
        display_df, title, box_bg = latest_df, "📋 Master Patient Caseload", "#e6f2ff"

    left_col, right_col = st.columns([1, 1.8], gap="large")
    
    with left_col:
        st.markdown(f'<div style="background:{box_bg}; padding:15px; border-radius:10px; border-left:8px solid #005eb8;"><h3 style="margin:0; color:#002f5c; font-weight:800;">{title}</h3></div>', unsafe_allow_html=True)
        st.dataframe(display_df[['patient_id', 'missed_appointments', 'engagement_drop_percent']], use_container_width=True, hide_index=True)
        st.divider()
        target_id = st.selectbox("SEARCH PATIENT IDENTIFIER", display_df['patient_id'])
        current_data = display_df[display_df['patient_id'] == target_id].iloc[0]

    with right_col:
        if st.button(f"⚡ RUN AI DIAGNOSTICS FOR {target_id}"):
            with st.status("Engaging AI Triage Engine...", expanded=False):
                payload = {
                    "patient_id": str(current_data['patient_id']),
                    "missed_appointments": int(current_data['missed_appointments']),
                    "engagement_drop_percent": int(current_data['engagement_drop_percent']),
                    "prev_crisis": bool(current_data['prev_crisis']),
                    "referral_text": str(current_data['referral_text'])
                }
                resp = requests.post("https://nhs-ai-clinical-support-gl6v.onrender.com/analyze", json=payload).json()
            
            risk_color = "#d4351c" if resp['risk_level'] == "HIGH" else "#ffdd00" if resp['risk_level'] == "MODERATE" else "#00703c"
            
            st.markdown(f"""
                <div style="background: white; padding: 25px; border-radius: 15px; border-left: 12px solid {risk_color}; box-shadow: 0 10px 25px rgba(0,0,0,0.1);">
                    <h2 style="margin:0; color: {risk_color}; font-weight:800;">{resp['risk_level']} PRIORITY</h2>
                    <p style="color: #002f5c; font-weight: 700; font-size: 1.1rem; margin-top:5px;">CATEGORY: {resp['context'].upper()}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("#### 📈 Historical Analysis (Engagement vs Contacts)")
            hist = df[df['patient_id'] == target_id].sort_values('date')
            chart_data = hist.set_index('date')[['engagement_drop_percent', 'missed_appointments']]
            st.line_chart(chart_data, color=["#005eb8", "#d4351c"])
            
            st.info(f"**AI Reasoning:** {', '.join(resp['alerts']) if resp['alerts'] else 'No critical flags.'}")

else:
    st.info("System Ready. Please upload records via the Clinical Gateway.")
