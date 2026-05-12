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

# --- Premium Sleek CSS Overhaul ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif !important;
            background-color: #f4f7f9;
        }

        /* Sidebar: Solid NHS Navy */
        [data-testid="stSidebar"] {
            background-color: #002f5c !important;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }

        /* FILE UPLOADER VISIBILITY */
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

        /* UPDATED HEADER: NHS Blue with Logo & Refined Text */
        .main-header-container {
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #005eb8;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 94, 184, 0.2);
            margin-bottom: 5px;
        }
        .main-header-text {
            color: white;
            font-weight: 600; /* Less bold as requested */
            font-size: 1.8rem;
            margin-left: 20px;
            letter-spacing: 0.5px;
        }

        /* NEWS TICKER FEED */
        .news-ticker {
            background: #e6f2ff;
            padding: 10px;
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

        /* DYNAMIC PULSING KPI CARDS */
        div[data-testid="stMetricValue"] {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            border-bottom: 5px solid #005eb8;
            animation: kpi-pulse 4s infinite ease-in-out;
        }
        @keyframes kpi-pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }

        /* ITALIC ALERTS */
        .ai-alert-text {
            font-style: italic;
            color: #d4351c;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar (Clinical Gateway) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/NHS-Logo.svg/1280px-NHS-Logo.svg.png", width=120)
    st.markdown("## Clinical Gateway")
    st.divider()
    
    st.subheader("Data Ingestion")
    file = st.file_uploader("UPLOAD PATIENT CASELOAD", type=['csv', 'xlsx', 'json'])
    
    if file:
        df_new, msg = process_upload(file)
        if df_new is not None: st.success("Database Synchronized")
        else: st.error(msg)
    
    st.divider()
    st.info("System Version: 2.1.0-Enterprise")

# --- Main Dashboard Header ---
st.markdown(f"""
    <div class="main-header-container">
        <img src="https://upload.wikimedia.org/wikipedia/commons/f/fa/NHS-Logo.svg" width="90">
        <div class="main-header-text">🏥 Clinical Decision Support: Population Health</div>
    </div>
""", unsafe_allow_html=True)

# Live News Ticker
st.markdown("""
    <div class="news-ticker">
        <div class="ticker-text">
            SYSTEM UPDATE: AI Analysis Node Active • 🔴 HIGH RISK: 3 Pending Reviews • 🟢 STABLE: 91 Patients Operational • Clinical Governance Protocol 2026 Verified ...
        </div>
    </div>
""", unsafe_allow_html=True)

df = get_patients()

if not df.empty:
    latest_df = df.sort_values('date').groupby('patient_id').tail(1)
    
    # --- Interactive Triage Summary ---
    st.markdown("### 📊 Interactive Triage Summary")
    risk_threshold = 3
    high_risk_df = latest_df[latest_df['missed_appointments'] >= risk_threshold]
    stable_df = latest_df[latest_df['missed_appointments'] < risk_threshold]
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Caseload", len(latest_df))
        if st.button("View Full Queue", use_container_width=True): st.session_state['filter'] = 'all'
    with m2:
        st.metric("🔴 Critical Flags", len(high_risk_df), delta="Requires Review")
        if st.button("Filter High Risk", use_container_width=True): st.session_state['filter'] = 'high'
    with m3:
        st.metric("🟢 Stable Engagement", len(stable_df), delta="Operational")
        if st.button("Filter Stable", use_container_width=True): st.session_state['filter'] = 'stable'

    st.write("---")

    # Filter Application
    current_filter = st.session_state.get('filter', 'all')
    if current_filter == 'high':
        display_df, title, box_bg = high_risk_df, "🔴 Priority Critical Queue", "#ffebe9"
    elif current_filter == 'stable':
        display_df, title, box_bg = stable_df, "🟢 Clinical Update: Stable Patients", "#e7f6ec"
    else:
        display_df, title, box_bg = latest_df, "📋 Patient Caseload Master List", "#e6f2ff"

    col_list, col_detail = st.columns([1, 1.8], gap="large")
    
    with col_list:
        st.markdown(f'<div style="background:{box_bg}; padding:15px; border-radius:10px; border-left:8px solid #005eb8;"><h3 style="margin:0; color:#002f5c; font-weight:800;">{title}</h3></div>', unsafe_allow_html=True)
        st.dataframe(display_df[['patient_id', 'missed_appointments', 'engagement_drop_percent']], use_container_width=True, hide_index=True)
        st.divider()
        target_id = st.selectbox("Search Patient ID", display_df['patient_id'])
        current_data = display_df[display_df['patient_id'] == target_id].iloc[0]

    with col_detail:
        if st.button(f"⚡ Generate AI Intelligence for {target_id}", type="primary"):
            with st.status("Analyzing...", expanded=False):
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
                <div style="background: white; padding: 25px; border-radius: 15px; border-left: 12px solid {risk_color}; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
                    <h2 style="margin:0; color: {risk_color}; font-weight:800;">{resp['risk_level']} RISK</h2>
                    <p style="color: #002f5c; font-weight: 700; margin-top:5px;">CONTEXT: {resp['context'].upper()}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("#### 📈 Historical Analysis")
            hist = df[df['patient_id'] == target_id].sort_values('date')
            st.line_chart(hist.set_index('date')[['engagement_drop_percent', 'missed_appointments']], color=["#005eb8", "#d4351c"])
            
            st.markdown("### 🤖 Neural Reasoning")
            # UPDATED: Alerts in Italic
            if resp['alerts']:
                for alert in resp['alerts']:
                    st.markdown(f"<p class='ai-alert-text'>• {alert}</p>", unsafe_allow_html=True)
            else:
                st.markdown("<p class='ai-alert-text'>No critical behavioral anomalies detected.</p>", unsafe_allow_html=True)
                
            st.caption(f"🛡️ Governance: {resp['governance']}")

else:
    st.info("System Ready. Please use the Clinical Gateway to upload records.")
