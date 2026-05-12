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
        /* Global Background & Typography */
        .stApp {
            background-color: #f4f7f9;
        }
        
        /* Sidebar: Professional Deep Navy */
        [data-testid="stSidebar"] {
            background-color: #002f5c;
            color: white;
        }

        /* UPLOADER VISIBILITY FIX */
        [data-testid="stFileUploader"] section {
            background-color: #ffffff !important; 
            border: 1px solid #d1d8e0 !important; 
            border-radius: 8px;
            padding: 15px;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
        }
        /* Metadata Visibility (200MB limit text) */
        [data-testid="stFileUploader"] small {
            color: #002f5c !important; 
            font-weight: 800 !important;
            font-size: 0.85rem !important;
            display: block;
            margin-top: 5px;
        }
        [data-testid="stFileUploader"] label {
            color: #002f5c !important;
            font-weight: 600 !important;
        }

        /* Unified Header: Sleek & Flat */
        .main-header {
            font-family: 'Inter', -apple-system, sans-serif;
            color: white;
            background: linear-gradient(90deg, #005eb8 0%, #003087 100%);
            font-weight: 700;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: left;
            box-shadow: 0 4px 15px rgba(0, 94, 184, 0.2);
        }

        /* Metric/KPI Card Styling */
        div[data-testid="stMetricValue"] {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border-bottom: 4px solid #005eb8;
        }

        /* Patient List Header: Sleek Light Blue */
        .list-header-box {
            background-color: #e6f2ff;
            padding: 12px 20px;
            border-radius: 8px 8px 0 0;
            border-bottom: 2px solid #005eb8;
            margin-bottom: 0px;
        }
        .list-header-text {
            color: #002f5c;
            font-size: 1rem;
            font-weight: 700;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Premium Buttons */
        .stButton>button {
            border-radius: 6px;
            background-color: #005eb8;
            color: white;
            transition: all 0.2s;
            border: none;
            font-weight: 600;
            height: 3rem;
        }
        .stButton>button:hover {
            background-color: #003087;
            box-shadow: 0 4px 12px rgba(0, 48, 135, 0.2);
        }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar (Clinical Control) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/NHS-Logo.svg/1280px-NHS-Logo.svg.png", width=100)
    st.markdown("### Clinical Gateway")
    st.divider()
    
    st.subheader("Data Ingestion")
    file = st.file_uploader("Upload caseload records", type=['csv', 'xlsx', 'json'])
    
    if file:
        with st.spinner("Processing..."):
            df_new, msg = process_upload(file)
            if df_new is not None:
                st.success("Database Synchronized")
            else:
                st.error(msg)
    
    st.divider()
    st.caption("Version 2.2.0 | Secure Environment")

# --- Main Dashboard ---
st.markdown('<div class="main-header">Clinical Decision Support: Population Health</div>', unsafe_allow_html=True)

df = get_patients()

if not df.empty:
    latest_df = df.sort_values('date').groupby('patient_id').tail(1)
    
    # --- Category Summary ---
    risk_threshold = 3
    high_risk_df = latest_df[latest_df['missed_appointments'] >= risk_threshold]
    stable_df = latest_df[latest_df['missed_appointments'] < risk_threshold]
    
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.metric("Total Caseload", len(latest_df))
        if st.button("View Master List"): st.session_state['filter'] = 'all'
            
    with m2:
        st.metric("Critical Risks", len(high_risk_df), delta="Requires Review", delta_color="inverse")
        if st.button("Filter High Risk"): st.session_state['filter'] = 'high'
            
    with m3:
        st.metric("Stable Engagement", len(stable_df))
        if st.button("Filter Stable"): st.session_state['filter'] = 'stable'

    st.write("---")

    # Filter Application
    current_filter = st.session_state.get('filter', 'all')
    if current_filter == 'high':
        display_df, table_title = high_risk_df, "Priority Risk Queue"
    elif current_filter == 'stable':
        display_df, table_title = stable_df, "Stable Caseload"
    else:
        display_df, table_title = latest_df, "Master Patient Caseload"

    col_list, col_detail = st.columns([1, 2], gap="large")
    
    with col_list:
        st.markdown(f'<div class="list-header-box"><p class="list-header-text">{table_title}</p></div>', unsafe_allow_html=True)
        st.dataframe(
            display_df[['patient_id', 'missed_appointments', 'engagement_drop_percent']], 
            use_container_width=True,
            hide_index=True
        )
        st.divider()
        target_id = st.selectbox("Search Patient Identifier", display_df['patient_id'])
        current_data = display_df[display_df['patient_id'] == target_id].iloc[0]

    with col_detail:
        if st.button(f"Analyze Clinical Trends: {target_id}"):
            with st.status("Running AI Diagnostics...", expanded=False):
                payload = {
                    "patient_id": str(current_data['patient_id']),
                    "missed_appointments": int(current_data['missed_appointments']),
                    "engagement_drop_percent": int(current_data['engagement_drop_percent']),
                    "prev_crisis": bool(current_data['prev_crisis']),
                    "referral_text": str(current_data['referral_text'])
                }
                # Render Backend Endpoint [cite: 54]
                resp = requests.post("https://nhs-ai-clinical-support-gl6v.onrender.com/analyze", json=payload).json()
            
            risk_color = "#d4351c" if resp['risk_level'] == "HIGH" else "#ffdd00" if resp['risk_level'] == "MODERATE" else "#00703c"
            
            # Risk Display Card
            st.markdown(f"""
                <div style="background-color: white; padding: 20px; border-radius: 12px; border-left: 8px solid {risk_color}; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    <h4 style="margin:0; color: #505a5f; font-size: 0.8rem; text-transform: uppercase;">AI Risk Classification</h4>
                    <h2 style="margin:0; color: {risk_color}; font-size: 2.2rem;">{resp['risk_level']}</h2>
                    <p style="margin:5px 0 0 0; color: #002f5c; font-weight: 600;">Clinical Context: {resp['context'].upper()}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # --- Unified Line Chart: Engagement vs Missed Contacts ---
            st.write("#### Historical Behavioral Trends")
            hist = df[df['patient_id'] == target_id].sort_values('date')
            chart_data = hist.set_index('date')[['engagement_drop_percent', 'missed_appointments']]
            # Single chart with two lines for direct correlation analysis 
            st.line_chart(chart_data, color=["#005eb8", "#d4351c"])
            
            st.info(f"**Diagnostic Reasoning:** {', '.join(resp['alerts']) if resp['alerts'] else 'No critical behavioral alerts detected.'}")
            st.caption(f"Governance Note: {resp['governance']}")

else:
    st.info("Clinical Gateway ready. Please ingest patient caseload records to initialize triage.")
