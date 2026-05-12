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

# --- High-Impact Enterprise Styling ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
        
        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif !important;
            background-color: #f0f4f7;
        }

        /* SIDEBAR: Solid NHS Navy Background */
        [data-testid="stSidebar"] {
            background-color: #002f5c !important;
            color: white !important;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }

        /* FILE UPLOADER: Solid Blue Background with Bold White Text */
        [data-testid="stFileUploader"] section {
            background-color: #005eb8 !important; 
            border: 3px solid #ffffff !important; 
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        /* Forcing all text in the uploader to be white and extra bold */
        [data-testid="stFileUploader"] label, 
        [data-testid="stFileUploader"] small,
        [data-testid="stFileUploader"] span,
        [data-testid="stFileUploader"] div {
            color: #ffffff !important; 
            font-weight: 900 !important;
            font-size: 1rem !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }

        /* MAIN HEADER: NHS Blue */
        .main-header-container {
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #005eb8;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(0, 94, 184, 0.3);
            margin-bottom: 5px;
        }
        .main-header-text {
            color: white;
            font-weight: 700; 
            font-size: 2rem;
            margin-left: 20px;
        }

        /* NEWS TICKER FEED */
        .news-ticker {
            background: #e6f2ff;
            padding: 12px;
            border-radius: 8px;
            border-left: 8px solid #005eb8;
            margin-bottom: 25px;
            overflow: hidden;
            white-space: nowrap;
        }
        .ticker-text {
            display: inline-block;
            padding-left: 100%;
            animation: ticker 30s linear infinite;
            font-weight: 800;
            color: #002f5c;
        }
        @keyframes ticker {
            0% { transform: translate(0, 0); }
            100% { transform: translate(-100%, 0); }
        }

        /* TRIAGE FILTER BUTTONS: High-Contrast Design */
        .stButton>button {
            background-color: #005eb8 !important;
            color: white !important;
            border: 2px solid #ffffff !important;
            font-weight: 900 !important;
            font-size: 1.1rem !important;
            height: 3.8rem !important;
            border-radius: 10px !important;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #003087 !important;
            transform: translateY(-3px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        }

        /* KPI Cards with Pulse */
        div[data-testid="stMetricValue"] {
            background-color: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-bottom: 6px solid #005eb8;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar (Clinical Gateway) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/NHS-Logo.svg/1280px-NHS-Logo.svg.png", width=130)
    st.markdown("<h2 style='text-align: center; color: white; font-weight: 900;'>Clinical Gateway</h2>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("<h4 style='color: white; font-weight: 700;'>📁 DATA INGESTION</h4>", unsafe_allow_html=True)
    # The background here is now solid blue via CSS
    file = st.file_uploader("DROP PATIENT CASELOAD HERE", type=['csv', 'xlsx', 'json'])
    
    if file:
        df_new, msg = process_upload(file)
        if df_new is not None: st.success("Database Synchronized")
        else: st.error(msg)
    
    st.divider()
    st.info("System: NHS Decision Support v2.2.8")

# --- Main Dashboard Header ---
st.markdown(f"""
    <div class="main-header-container">
        <img src="https://upload.wikimedia.org/wikipedia/commons/f/fa/NHS-Logo.svg" width="100">
        <div class="main-header-text">🏥 Clinical Decision Support: Population Health</div>
    </div>
""", unsafe_allow_html=True)

# Live News Ticker
st.markdown("""
    <div class="news-ticker">
        <div class="ticker-text">
            URGENT FEED: AI Diagnostic Engine Verified • 🔴 HIGH RISK: 3 Priority Reviews Pending • 🟢 STABLE: 91% Engagement Stability ... 
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
        st.metric("Total Active Caseload", len(latest_df))
        if st.button("VIEW MASTER LIST", use_container_width=True): st.session_state['filter'] = 'all'
    with m2:
        st.metric("🔴 Critical Flags", len(high_risk_df), delta="Immediate Action")
        if st.button("🔴 FILTER HIGH RISK", use_container_width=True): st.session_state['filter'] = 'high'
    with m3:
        st.metric("🟢 Stable Engagement", len(stable_df), delta="Nominal")
        if st.button("🟢 FILTER STABLE", use_container_width=True): st.session_state['filter'] = 'stable'

    st.write("---")

    # Filter Application
    current_filter = st.session_state.get('filter', 'all')
    if current_filter == 'high':
        display_df, title, box_bg = high_risk_df, "🔴 Priority Critical Queue", "#ffebe9"
    elif current_filter == 'stable':
        display_df, title, box_bg = stable_df, "🟢 Clinical Update: Stable Patients", "#e7f6ec"
    else:
        display_df, title, box_bg = latest_df, "📋 Master Patient Caseload List", "#e6f2ff"

    col_list, col_detail = st.columns([1, 1.8], gap="large")
    
    with col_list:
        st.markdown(f'<div style="background:{box_bg}; padding:15px; border-radius:10px; border-left:10px solid #005eb8;"><h3 style="margin:0; color:#002f5c; font-weight:900;">{title}</h3></div>', unsafe_allow_html=True)
        st.dataframe(display_df[['patient_id', 'missed_appointments', 'engagement_drop_percent']], use_container_width=True, hide_index=True)
        st.divider()
        target_id = st.selectbox("SEARCH PATIENT IDENTIFIER", display_df['patient_id'])
        current_data = display_df[display_df['patient_id'] == target_id].iloc[0]

    with col_detail:
        if st.button(f"⚡ RUN AI DIAGNOSTICS FOR {target_id}", type="primary"):
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
                <div style="background: white; padding: 25px; border-radius: 20px; border-left: 15px solid {risk_color}; box-shadow: 0 10px 30px rgba(0,0,0,0.15);">
                    <h2 style="margin:0; color: {risk_color}; font-weight:900;">{resp['risk_level']} PRIORITY</h2>
                    <p style="color: #002f5c; font-weight: 800; font-size: 1.2rem; margin-top:10px;">CONTEXT: {resp['context'].upper()}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("#### 📈 Historical Behavioral Analysis")
            hist = df[df['patient_id'] == target_id].sort_values('date')
            st.line_chart(hist.set_index('date')[['engagement_drop_percent', 'missed_appointments']], color=["#005eb8", "#d4351c"])
            
            if resp['alerts']:
                for alert in resp['alerts']:
                    st.markdown(f"<p style='font-style:italic; color:#d4351c; font-weight:900;'>• {alert}</p>", unsafe_allow_html=True)

else:
    st.info("System Ready. Please use the Clinical Gateway to upload records.")
