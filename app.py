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

# --- Premium Custom CSS (Hospital/Enterprise Style) ---
st.markdown("""
    <style>
        /* Main App Background */
        .stApp {
            background-color: #f0f4f7;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #002f5c; /* Deep NHS Navy */
            color: white;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }

        /* Hospital Card Style for Metrics and Containers */
        div[data-testid="stMetricValue"] {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border-left: 5px solid #005eb8;
        }
        
        /* UPDATED: Blue Header Styling */
        .main-header {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: white; /* Changed to white for blue bg */
            background-color: #005eb8; /* NHS Blue */
            font-weight: 800;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }

        /* Dynamic Button Effect */
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
            box-shadow: 0 4px 12px rgba(0,94,184,0.3);
        }

        /* Table Styling */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar Management ---
with st.sidebar:
    # ADDED: Logo at gateway section
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/NHS-Logo.svg/1280px-NHS-Logo.svg.png", width=120)
    st.markdown("### **🏥 Clinical Gateway**")
    st.divider()
    st.subheader("📁 Data Ingestion")
    file = st.file_uploader("Upload Caseload", type=['csv', 'xlsx', 'json'])
    
    if file:
        with st.spinner("Processing Records..."):
            df_new, msg = process_upload(file)
            if df_new is not None:
                st.success("Sync Complete")
            else:
                st.error(msg)
    
    st.info("System Version: 2.1.0-Enterprise")

# --- Main Dashboard ---
# UPDATED: Blue background applied via CSS class
st.markdown('<div class="main-header">🏥 Clinical Decision Support: Population Health</div>', unsafe_allow_html=True)

df = get_patients()

if not df.empty:
    latest_df = df.sort_values('date').groupby('patient_id').tail(1)
    
    # --- UPDATED: Dynamic & Clickable KPI Category Filters ---
    st.markdown("### 📊 Interactive Triage Summary")
    st.caption("Click a button below to filter the caseload queue by category.")
    
    # Logic for categories
    risk_threshold = 3
    high_risk_df = latest_df[latest_df['missed_appointments'] >= risk_threshold]
    stable_df = latest_df[latest_df['missed_appointments'] < risk_threshold]
    
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.metric("Total Caseload", f"{len(latest_df)} Patients")
        if st.button("View All Patients"):
            st.session_state['filter'] = 'all'
            
    with m2:
        st.metric("High Risk", f"{len(high_risk_df)} Patients", delta="Requires Review", delta_color="inverse")
        if st.button("🔴 Filter High Risk"):
            st.session_state['filter'] = 'high'
            
    with m3:
        st.metric("Stable Engagement", f"{len(stable_df)} Patients", delta="Operational")
        if st.button("🟢 Filter Stable"):
            st.session_state['filter'] = 'stable'

    st.write("---")

    # Apply Filter Logic
    current_filter = st.session_state.get('filter', 'all')
    if current_filter == 'high':
        display_df = high_risk_df
        table_title = "🚩 High Risk Queue (3+ Missed Appointments)"
    elif current_filter == 'stable':
        display_df = stable_df
        table_title = "✅ Stable Engagement Queue"
    else:
        display_df = latest_df
        table_title = "📋 Full Caseload Queue"

    col_list, col_detail = st.columns([1.2, 1.8], gap="large")
    
    with col_list:
        st.subheader(table_title)
        # Displaying the filtered dataframe
        st.dataframe(
            display_df[['patient_id', 'missed_appointments', 'engagement_drop_percent']], 
            use_container_width=True,
            hide_index=True
        )
        
        st.divider()
        st.markdown("#### **Deep-Dive Action**")
        target_id = st.selectbox("Select Patient Profile", display_df['patient_id'])
        current_data = display_df[display_df['patient_id'] == target_id].iloc[0]

    with col_detail:
        if st.button(f"⚡ Generate AI Intelligence for {target_id}"):
            # Dynamic Loading Bar for "Premium" feel
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
                # Note: Ensure the URL matches your backend deployment
                resp = requests.post("https://nhs-ai-clinical-support-gl6v.onrender.com/analyze", json=payload).json()
                
                # Risk Visualization
                risk_color = "#d4351c" if resp['risk_level'] == "HIGH" else "#ffdd00" if resp['risk_level'] == "MODERATE" else "#00703c"
                
                st.markdown(f"""
                    <div style="background-color: white; padding: 25px; border-radius: 15px; border-left: 10px solid {risk_color};">
                        <h2 style="margin:0; color: {risk_color};">{resp['risk_level']} RISK</h2>
                        <p style="color: #505a5f;">Primary Context: <b>{resp['context'].upper()}</b></p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Chart Section
                st.write("### 📈 Engagement Trajectory")
                patient_history = df[df['patient_id'] == target_id].sort_values('date')
                st.area_chart(patient_history.set_index('date')['engagement_drop_percent'])
                
                # AI Insights
                st.markdown("### 🤖 AI Insight Reasoning")
                for alert in resp['alerts']:
                    st.warning(f"**Alert:** {alert}")
                
                st.caption(f"🛡️ **Governance:** {resp['governance']}")
                
            except Exception as e:
                st.error("Connection to AI Engine failed. Please verify the Render backend is live.")

else:
    st.info("No data detected. Please use the sidebar to upload patient records.")
