import streamlit as st
import pandas as pd
import requests
import time
from data_manager import get_patients, process_upload

# --- Page Configuration ---
st.set_page_config(
    page_title="NHS AI Decision Support", 
    page_icon="🏥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sleek Enterprise CSS Overhaul ---
st.markdown("""
    <style>
        /* Global Background */
        .stApp { background-color: #f4f7f9; }
        
        /* Sidebar Navigation */
        [data-testid="stSidebar"] { background-color: #002f5c; color: white; }

        /* Uploader Visibility & Metadata Fix */
        [data-testid="stFileUploader"] section {
            background-color: #ffffff !important; 
            border: 1px solid #d1d8e0 !important; 
            border-radius: 8px;
        }
        [data-testid="stFileUploader"] small {
            color: #002f5c !important; 
            font-weight: 900 !important;
            font-size: 0.9rem !important;
        }

        /* NHS Blue Header */
        .main-header {
            color: white;
            background: #005eb8;
            font-weight: 700;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 10px;
        }

        /* NEWS TICKER STYLE FEED */
        .news-ticker {
            background: #e6f2ff;
            padding: 10px;
            border-radius: 5px;
            border-left: 5px solid #005eb8;
            margin-bottom: 25px;
            overflow: hidden;
            white-space: nowrap;
        }
        .ticker-text {
            display: inline-block;
            padding-left: 100%;
            animation: ticker 25s linear infinite;
            font-weight: 600;
            color: #002f5c;
        }
        @keyframes ticker {
            0% { transform: translate(0, 0); }
            100% { transform: translate(-100%, 0); }
        }

        /* DYNAMIC KPI ANIMATION */
        div[data-testid="stMetricValue"] {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            animation: pulse 3s infinite ease-in-out;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }

        /* Chart Axis Boldness */
        .js-plotly-plot .plotly .xtick text, .js-plotly-plot .plotly .ytick text {
            font-weight: 800 !important;
            fill: #002f5c !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar (Clinical Gateway + Logo) ---
with st.sidebar:
    # RE-ADDED: NHS Logo at Gateway
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/NHS-Logo.svg/1280px-NHS-Logo.svg.png", width=120)
    st.markdown("## **🏥 Clinical Gateway**")
    st.divider()
    
    st.subheader("Data Ingestion")
    file = st.file_uploader("Upload caseload records", type=['csv', 'xlsx', 'json'])
    
    if file:
        df_new, msg = process_upload(file)
        if df_new is not None: st.success("Database Synchronized")
        else: st.error(msg)
    
    st.divider()
    st.caption("Secure Workforce Environment | v2.2.1")

# --- Main Dashboard ---
st.markdown('<div class="main-header">Clinical Decision Support: Population Health</div>', unsafe_allow_html=True)

# DYNAMIC NEWS FEED
st.markdown("""
    <div class="news-ticker">
        <div class="ticker-text">
            LATEST UPDATES: AI Model DistilBERT-MNLI is now processing live requests ... 
            System detected 3 new high-risk flags in the last hour ... 
            Clinical governance protocols active ... 
            Next database sync scheduled for 22:00 GMT ...
        </div>
    </div>
""", unsafe_allow_html=True)

df = get_patients()

if not df.empty:
    latest_df = df.sort_values('date').groupby('patient_id').tail(1)
    
    # Logic for categories
    risk_threshold = 3
    high_risk_df = latest_df[latest_df['missed_appointments'] >= risk_threshold]
    stable_df = latest_df[latest_df['missed_appointments'] < risk_threshold]
    
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.metric("Total Caseload", len(latest_df))
        if st.button("View Master List"): st.session_state['filter'] = 'all'
            
    with m2:
        # ADDED: Red Emoji for Critical
        st.metric("🔴 Critical Risks", len(high_risk_df), delta="Review Required", delta_color="inverse")
        if st.button("Filter High Risk"): st.session_state['filter'] = 'high'
            
    with m3:
        # ADDED: Green Emoji for Stable
        st.metric("🟢 Normal Status", len(stable_df))
        if st.button("Filter Stable"): st.session_state['filter'] = 'stable'

    st.write("---")

    current_filter = st.session_state.get('filter', 'all')
    if current_filter == 'high':
        display_df, title = high_risk_df, "🔴 Priority Risk Queue"
    elif current_filter == 'stable':
        display_df, title = stable_df, "🟢 Normal Caseload"
    else:
        display_df, title = latest_df, "📋 Master Patient Caseload"

    col_list, col_detail = st.columns([1, 2], gap="large")
    
    with col_list:
        st.markdown(f'<div style="background:#e6f2ff; padding:10px; border-radius:5px; border-left:5px solid #005eb8; margin-bottom:10px;"><b style="color:#002f5c;">{title}</b></div>', unsafe_allow_html=True)
        st.dataframe(display_df[['patient_id', 'missed_appointments', 'engagement_drop_percent']], use_container_width=True, hide_index=True)
        st.divider()
        target_id = st.selectbox("Search Patient Identifier", display_df['patient_id'])
        current_data = display_df[display_df['patient_id'] == target_id].iloc[0]

    with col_detail:
        if st.button(f"Analyze Trends: {target_id}"):
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
                <div style="background: white; padding: 20px; border-radius: 12px; border-left: 8px solid {risk_color}; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    <h2 style="margin:0; color: {risk_color};">{resp['risk_level']} PRIORITY</h2>
                    <p style="color: #002f5c; font-weight: 700;">Context: {resp['context'].upper()}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # CHART OPTIMIZATION
            st.write("#### Historical Behavioral Data (Bold Metrics)")
            hist = df[df['patient_id'] == target_id].sort_values('date')
            chart_data = hist.set_index('date')[['engagement_drop_percent', 'missed_appointments']]
            
            # Using Line Chart for dual view
            st.line_chart(chart_data, color=["#005eb8", "#d4351c"])
            
            st.info(f"**Alerts:** {', '.join(resp['alerts']) if resp['alerts'] else 'Stable'}")

else:
    st.info("System Ready. Please use the Clinical Gateway to upload patient data.")
