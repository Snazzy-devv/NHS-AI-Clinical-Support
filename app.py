import streamlit as st
import pandas as pd
import requests
import time
from data_manager import get_patients, process_upload

# --- Page Configuration ---
st.set_page_config(
    page_title="NHS Decision Support", 
    page_icon="🏥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium Sleek CSS Overhaul ---
st.markdown("""
    <style>
        /* Global Font Consistency */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
        
        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif !important;
            background-color: #f4f7f9;
        }

        /* Sidebar & Clinical Gateway */
        [data-testid="stSidebar"] {
            background-color: #002f5c;
        }

        /* FILE UPLOADER: All Blue Text on White Background */
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
            font-size: 0.95rem !important;
        }

        /* MAIN HEADER */
        .main-header {
            color: white;
            background: #005eb8;
            font-weight: 800;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 94, 184, 0.2);
            margin-bottom: 5px;
        }

        /* NEWS TICKER FEED */
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
            font-size: 1rem;
        }
        @keyframes ticker {
            0% { transform: translate(0, 0); }
            100% { transform: translate(-100%, 0); }
        }

        /* DYNAMIC PULSING KPI CARDS */
        div[data-testid="stMetricValue"] {
            background-color: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 6px 12px rgba(0,0,0,0.08);
            border-bottom: 5px solid #005eb8;
            animation: kpi-pulse 4s infinite ease-in-out;
        }
        @keyframes kpi-pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.03); }
            100% { transform: scale(1); }
        }

        /* BOLD DATA ELEMENTS */
        .stDataFrame, .stSelectbox, .stButton button {
            font-weight: 700 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar (Clinical Gateway) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/NHS-Logo.svg/1280px-NHS-Logo.svg.png", width=130)
    st.markdown("<h2 style='color:white; margin-top:10px;'>Clinical Gateway</h2>", unsafe_allow_html=True)
    st.divider()
    
    st.subheader("Data Ingestion")
    file = st.file_uploader("UPLOAD PATIENT CASELOAD", type=['csv', 'xlsx', 'json'])
    
    if file:
        df_new, msg = process_upload(file)
        if df_new is not None: st.success("Database Synchronized")
        else: st.error(msg)
    
    st.divider()
    st.caption("Secure Workforce Environment | Enterprise v2.2.5")

# --- Main Dashboard ---
st.markdown('<div class="main-header">Clinical Decision Support: Population Health</div>', unsafe_allow_html=True)

# 

# Interactive Triage News Feed
st.markdown("""
    <div class="news-ticker">
        <div class="ticker-text">
            SYSTEM STATUS: AI Diagnostics Active • 🔴 HIGH RISK: 3 New Alerts Detected • 🟢 STABLE: 85% Engagement Rate • GOVERNANCE: Human-in-the-loop Protocol verified for 2026 ...
        </div>
    </div>
""", unsafe_allow_html=True)

df = get_patients()

if not df.empty:
    latest_df = df.sort_values('date').groupby('patient_id').tail(1)
    
    # KPI Triage Summary
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
        display_df, title, header_color = high_risk_df, "🔴 Priority Critical Queue", "#ffebe9"
    elif current_filter == 'stable':
        display_df, title, header_color = stable_df, "🟢 Clinical Update: Stable Patients", "#e7f6ec"
    else:
        display_df, title, header_color = latest_df, "📋 Master Patient Caseload", "#e6f2ff"

    col_list, col_detail = st.columns([1, 1.8], gap="large")
    
    with col_list:
        st.markdown(f'<div style="background:{header_color}; padding:15px; border-radius:10px; border-left:8px solid #005eb8;"><h3 style="margin:0; color:#002f5c; font-weight:800;">{title}</h3></div>', unsafe_allow_html=True)
        st.dataframe(display_df[['patient_id', 'missed_appointments', 'engagement_drop_percent']], use_container_width=True, hide_index=True)
        
        st.divider()
        target_id = st.selectbox("SEARCH PATIENT IDENTIFIER", display_df['patient_id'])
        current_data = display_df[display_df['patient_id'] == target_id].iloc[0]

    with col_detail:
        if st.button(f"⚡ RUN AI DIAGNOSTICS FOR {target_id}"):
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
                    <h2 style="margin:0; color: {risk_color}; font-weight:800;">{resp['risk_level']} PRIORITY</h2>
                    <p style="color: #002f5c; font-weight: 700; font-size: 1.1rem;">CATEGORY: {resp['context'].upper()}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # CHART: Combined BOLD Line Analysis
            st.write("#### 📈 Historical Behavioral Velocity (Engagement vs Contacts)")
            hist = df[df['patient_id'] == target_id].sort_values('date')
            chart_data = hist.set_index('date')[['engagement_drop_percent', 'missed_appointments']]
            
            # Optimized line chart with high-contrast colors
            st.line_chart(chart_data, color=["#005eb8", "#d4351c"])
            
            st.info(f"**AI Reasoning Alerts:** {', '.join(resp['alerts']) if resp['alerts'] else 'No critical flags.'}")

else:
    st.info("System Ready. Use the Clinical Gateway to ingest records.")
