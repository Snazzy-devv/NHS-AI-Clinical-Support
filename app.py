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

# --- Premium Custom CSS ---
st.markdown("""
    <style>
        /* Main App Background */
        .stApp {
            background-color: #f0f4f7;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #002f5c;
            color: white;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }

        /* UPLOADER VISIBILITY FIX */
        [data-testid="stFileUploader"] section {
            background-color: #e1e8ed !important; 
            border: 2px dashed #005eb8 !important; 
            border-radius: 10px;
            padding: 10px;
        }
        /* Fix for "200MB per file" and uploader labels */
        [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] label {
            color: #002f5c !important; 
            font-weight: bold !important;
        }
        [data-testid="stFileUploader"] button {
            background-color: #005eb8 !important;
            color: white !important;
        }

        /* Blue Header Styling */
        .main-header {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: white;
            background-color: #005eb8;
            font-weight: 800;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }

        /* NEW: Light Blue Background for Master List Header */
        .list-header-box {
            background-color: #d1e9ff;
            padding: 15px;
            border-radius: 10px;
            border-left: 6px solid #005eb8;
            margin-bottom: 15px;
        }
        .list-header-text {
            color: #002f5c !important;
            font-weight: 800;
            margin: 0;
        }

        /* Metric Cards */
        div[data-testid="stMetricValue"] {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border-left: 5px solid #005eb8;
        }

        /* Buttons */
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            background-color: #005eb8;
            color: white;
            transition: all 0.3s ease;
            border: none;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #003087;
            transform: translateY(-2px);
        }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar Management ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/NHS-Logo.svg/1280px-NHS-Logo.svg.png", width=120)
    st.markdown("## **🏥 Clinical Gateway**")
    st.caption("Secure Workforce Entry")
    st.divider()
    
    st.subheader("📁 Data Ingestion")
    file = st.file_uploader("Drop patient caseload here", type=['csv', 'xlsx', 'json'])
    
    if file:
        with st.spinner("Syncing Database..."):
            df_new, msg = process_upload(file)
            if df_new is not None:
                st.success("Records Synchronized")
            else:
                st.error(msg)
    
    st.divider()
    st.info("System Version: 2.1.0-Enterprise")

# --- Main Dashboard ---
st.markdown('<div class="main-header">🏥 Clinical Decision Support: Population Health</div>', unsafe_allow_html=True)

df = get_patients()

if not df.empty:
    latest_df = df.sort_values('date').groupby('patient_id').tail(1)
    
    st.markdown("### 📊 Interactive Triage Summary")
    
    risk_threshold = 3
    high_risk_df = latest_df[latest_df['missed_appointments'] >= risk_threshold]
    stable_df = latest_df[latest_df['missed_appointments'] < risk_threshold]
    
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.metric("Total Caseload", f"{len(latest_df)} Patients")
        if st.button("View Full Queue"):
            st.session_state['filter'] = 'all'
            
    with m2:
        st.metric("Critical Flags", f"{len(high_risk_df)} Patients", delta="Requires Review", delta_color="inverse")
        if st.button("🔴 Filter High Risk"):
            st.session_state['filter'] = 'high'
            
    with m3:
        st.metric("Stable Engagement", f"{len(stable_df)} Patients", delta="Operational")
        if st.button("🟢 Filter Stable"):
            st.session_state['filter'] = 'stable'

    st.write("---")

    # Filter Application
    current_filter = st.session_state.get('filter', 'all')
    if current_filter == 'high':
        display_df, table_title = high_risk_df, "🚩 Critical Queue: High Risk"
    elif current_filter == 'stable':
        display_df, table_title = stable_df, "✅ Clinical Update: Stable Patients"
    else:
        display_df, table_title = latest_df, "📋 Patient Caseload Master List"

    col_list, col_detail = st.columns([1.2, 1.8], gap="large")
    
    with col_list:
        st.markdown(f"""
            <div class="list-header-box">
                <h3 class="list-header-text">{table_title}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(
            display_df[['patient_id', 'missed_appointments', 'engagement_drop_percent']], 
            use_container_width=True,
            hide_index=True
        )
        
        st.divider()
        st.markdown("#### **Detailed Analysis Selection**")
        target_id = st.selectbox("Search Patient ID", display_df['patient_id'])
        current_data = display_df[display_df['patient_id'] == target_id].iloc[0]

    with col_detail:
        if st.button(f"⚡ Generate AI Intelligence for {target_id}"):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.005)
                progress_bar.progress(i + 1)
            
            payload = {
                "patient_id": str(current_data['patient_id']),
                "missed_appointments": int(current_data['missed_appointments']),
                "engagement_drop_percent": int(current_data['engagement_drop_percent']),
                "prev_crisis": bool(current_data['prev_crisis']),
                "referral_text": str(current_data['referral_text'])
            }
            
            try:
                resp = requests.post("https://nhs-ai-clinical-support-gl6v.onrender.com/analyze", json=payload).json()
                
                risk_color = "#d4351c" if resp['risk_level'] == "HIGH" else "#ffdd00" if resp['risk_level'] == "MODERATE" else "#00703c"
                
                st.markdown(f"""
                    <div style="background-color: white; padding: 25px; border-radius: 15px; border-left: 10px solid {risk_color};">
                        <h2 style="margin:0; color: {risk_color};">{resp['risk_level']} RISK</h2>
                        <p style="color: #505a5f;">Clinical Triage Context: <b>{resp['context'].upper()}</b></p>
                    </div>
                """, unsafe_allow_html=True)
                
                # --- NEW: Enhanced Visualization (Line for Engagement, Bar for Contacts) ---
                st.write("### 📈 Engagement & Contact Velocity")
                hist = df[df['patient_id'] == target_id].sort_values('date')
                
                st.line_chart(hist.set_index('date')['engagement_drop_percent'], color="#005eb8")
                st.bar_chart(hist.set_index('date')['missed_appointments'], color="#d4351c")
                
                st.markdown("### 🤖 Neural Alert Reasoning")
                for alert in resp['alerts']:
                    st.warning(f"**Alert:** {alert}")
                
                st.caption(f"🛡️ **Governance:** {resp['governance']}")
                
            except Exception as e:
                st.error("Engine Connection Timeout. Verify Render backend is operational.")

else:
    st.info("System Ready. Please use the 'Clinical Gateway' in the sidebar to ingest patient data.")
