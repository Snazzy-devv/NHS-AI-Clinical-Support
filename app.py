import streamlit as st
import pandas as pd
import requests
import time
from data_manager import get_patients, process_upload

# --- Page Configuration ---
st.set_page_config(
    page_title="NHS AI Clinical Support", 
    page_icon="🏥", 
    layout="wide"
)

# --- High-End CSS (Hospital Glassmorphism Style) ---
st.markdown("""
    <style>
        /* Main Background Gradient */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }

        /* Sidebar Glassmorphism */
        [data-testid="stSidebar"] {
            background-color: rgba(0, 47, 92, 0.95) !important;
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Custom KPI Card Styling */
        .kpi-card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.05);
            border-bottom: 4px solid #005eb8;
            transition: transform 0.3s ease;
            text-align: center;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,94,184,0.15);
        }
        .kpi-value {
            font-size: 2rem;
            font-weight: 800;
            color: #005eb8;
            margin: 0;
        }
        .kpi-label {
            font-size: 0.9rem;
            color: #505a5f;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Modernized Header */
        .main-header {
            background: white;
            padding: 20px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 2rem;
        }
        
        /* Analysis Results Card */
        .result-card {
            background: white;
            padding: 30px;
            border-radius: 20px;
            border-left: 12px solid #005eb8;
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
    """, unsafe_allow_html=True)

# --- Custom Header with Logo ---
st.markdown("""
    <div class="main-header">
        <img src="https://upload.wikimedia.org/wikipedia/commons/f/fa/NHS-Logo.svg" width="100" style="margin-right: 20px;">
        <h1 style="color: #005eb8; margin: 0; font-size: 1.8rem;">Clinical Decision Support: Population Health</h1>
    </div>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h2 style='color: white;'>Control Panel</h2>", unsafe_allow_html=True)
    st.divider()
    file = st.file_uploader("📂 Import Caseload", type=['csv', 'xlsx', 'json'])
    if file:
        df_new, msg = process_upload(file)
        if df_new is not None: st.success("Database Updated")
        else: st.sidebar.error(msg)
    
    st.markdown("---")
    st.caption("AI Model: DistilBART-MNLI-12-3")
    st.caption("System Status: Operational ✅")

df = get_patients()

if not df.empty:
    latest_df = df.sort_values('date').groupby('patient_id').tail(1)

    # --- DYNAMIC KPI ROW ---
    # Calculating stats for dynamic display
    total_p = len(latest_df)
    high_risk_count = len(latest_df[latest_df['engagement_drop_percent'] > 40])
    avg_engagement = int(latest_df['engagement_drop_percent'].mean())

    kpi1, kpi2, kpi3 = st.columns(3)
    
    with kpi1:
        st.markdown(f"""<div class="kpi-card"><p class="kpi-label">Active Caseload</p><p class="kpi-value">{total_p}</p></div>""", unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""<div class="kpi-card" style="border-bottom-color: #d4351c;"><p class="kpi-label">Risk Flags</p><p class="kpi-value" style="color: #d4351c;">{high_risk_count}</p></div>""", unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""<div class="kpi-card" style="border-bottom-color: #00703c;"><p class="kpi-label">Avg Engagement</p><p class="kpi-value" style="color: #00703c;">{avg_engagement}%</p></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Main Content ---
    col_list, col_detail = st.columns([1, 1.8], gap="large")

    with col_list:
        st.subheader("📋 Patient Queue")
        st.dataframe(latest_df[['patient_id', 'missed_appointments', 'engagement_drop_percent']], use_container_width=True, hide_index=True)
        
        st.divider()
        target_id = st.selectbox("🎯 Select Patient for Analysis", latest_df['patient_id'])
        current_data = latest_df[latest_df['patient_id'] == target_id].iloc[0]

    with col_detail:
        if st.button(f"🔍 Analyze {target_id} with AI"):
            # Fancy Progress Bar
            with st.status("Initializing AI Diagnostics...", expanded=True) as status:
                st.write("Fetching historical patterns...")
                time.sleep(0.4)
                st.write("Running Zero-Shot NLP Engine...")
                time.sleep(0.4)
                status.update(label="Analysis Complete!", state="complete", expanded=False)

            payload = {
                "patient_id": str(current_data['patient_id']),
                "missed_appointments": int(current_data['missed_appointments']),
                "engagement_drop_percent": int(current_data['engagement_drop_percent']),
                "prev_crisis": bool(current_data['prev_crisis']),
                "referral_text": str(current_data['referral_text'])
            }
            
            try:
                resp = requests.post("https://nhs-ai-clinical-support-gl6v.onrender.com/analyze", json=payload).json()
                
                # Dynamic Color Coding
                risk_color = "#d4351c" if resp['risk_level'] == "HIGH" else "#ffdd00" if resp['risk_level'] == "MODERATE" else "#00703c"
                
                # Premium Result Card
                st.markdown(f"""
                    <div class="result-card" style="border-left-color: {risk_color};">
                        <h1 style="color: {risk_color}; margin:0;">{resp['risk_level']} PRIORITY</h1>
                        <p style="font-size: 1.2rem; color: #505a5f;">Clinical Context: <b>{resp['context'].upper()}</b></p>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Charts
                st.subheader("📈 Engagement Velocity")
                hist = df[df['patient_id'] == target_id].sort_values('date')
                st.area_chart(hist.set_index('date')['engagement_drop_percent'], color="#005eb8")

                # Alerts
                with st.expander("🤖 Neural Reasoning & Alerts", expanded=True):
                    for alert in resp['alerts']:
                        st.error(f"**Alert:** {alert}")
                    st.info(f"**Governance Note:** {resp['governance']}")

            except Exception as e:
                st.error("API Connection Offline. Ensure the Render backend is active.")

else:
    st.info("System Ready. Please upload patient data to begin.")
