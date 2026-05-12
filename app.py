import streamlit as st
import pandas as pd
import requests
import time
from data_manager import get_patients, process_upload

# --- Page Configuration ---
st.set_page_config(
    page_title="NHS Sentinel AI | Clinical Support", 
    page_icon="🏥", 
    layout="wide"
)

# --- THE PREMIUM CSS CORE ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

        /* Global Font & Background */
        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif;
            background-color: #F3F2F1; /* Professional Clinical White */
        }

        /* Top Navigation Bar Simulation */
        .top-nav {
            background-color: white;
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 2rem;
            border-radius: 12px;
        }

        /* Sidebar Styling: Dark Professional */
        [data-testid="stSidebar"] {
            background-color: #002F5C !important;
            border-right: none;
        }
        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }

        /* High-End KPI Cards */
        .kpi-container {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        .kpi-card {
            flex: 1;
            background: white;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            border: 1px solid #E1E4E8;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        .kpi-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 30px rgba(0,94,184,0.1);
            border-color: #005EB8;
        }
        .kpi-label { color: #6E7781; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
        .kpi-value { color: #002F5C; font-size: 2.2rem; font-weight: 800; margin: 8px 0; }

        /* Status Badges */
        .badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
        }
        .badge-live { background: #E7F6EC; color: #09822D; }

        /* The Result Card */
        .analysis-box {
            background: white;
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.05);
            border-top: 8px solid #005EB8;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Top Navigation ---
st.markdown("""
    <div class="top-nav">
        <div style="display: flex; align-items: center;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/f/fa/NHS-Logo.svg" width="80" style="margin-right: 20px;">
            <span style="font-weight: 800; font-size: 1.2rem; color: #002F5C;">SENTINEL AI <span style="font-weight: 400; color: #6E7781;">| Population Health</span></span>
        </div>
        <div class="badge badge-live">● SYSTEM LIVE</div>
    </div>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### **Workspace Hub**")
    st.divider()
    file = st.file_uploader("📥 Upload New Caseload", type=['csv', 'xlsx', 'json'])
    if file:
        df_new, msg = process_upload(file)
        if df_new is not None: st.success("Data Synchronized")
        else: st.error(msg)
    
    st.divider()
    st.markdown("#### **Current Active Model**")
    st.code("distilbart-mnli-12-3", language="text")
    st.info("Human-in-the-loop oversight is active.")

# --- Main Logic ---
df = get_patients()

if not df.empty:
    latest_df = df.sort_values('date').groupby('patient_id').tail(1)
    
    # --- DYNAMIC KPI ROW ---
    total_patients = len(latest_df)
    risks = len(latest_df[latest_df['missed_appointments'] >= 3])
    avg_engagement = int(latest_df['engagement_drop_percent'].mean())

    st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-card"><p class="kpi-label">Active Caseload</p><p class="kpi-value">{total_patients}</p></div>
            <div class="kpi-card" style="border-bottom: 4px solid #D4351C;"><p class="kpi-label" style="color:#D4351C;">Critical Flags</p><p class="kpi-value">{risks}</p></div>
            <div class="kpi-card"><p class="kpi-label">Mean Engagement</p><p class="kpi-value">{avg_engagement}%</p></div>
        </div>
    """, unsafe_allow_html=True)

    # --- Dashboard Content ---
    left, right = st.columns([1, 1.8], gap="large")

    with left:
        st.markdown("### **Caseload Queue**")
        st.dataframe(
            latest_df[['patient_id', 'missed_appointments', 'engagement_drop_percent']], 
            use_container_width=True, 
            hide_index=True
        )
        st.divider()
        target_id = st.selectbox("🎯 Focus Patient Profile", latest_df['patient_id'])
        current_data = latest_df[latest_df['patient_id'] == target_id].iloc[0]

    with right:
        if st.button(f"🚀 Execute Deep-Dive Analysis for {target_id}", use_container_width=True):
            # Dynamic Loading Simulation
            with st.status("Engaging AI Neural Pathways...", expanded=True) as status:
                st.write("Extracting clinical biomarkers...")
                time.sleep(0.5)
                st.write("Verifying risk weights...")
                time.sleep(0.5)
                status.update(label="Analysis Sequence Complete", state="complete", expanded=False)

            payload = {
                "patient_id": str(current_data['patient_id']),
                "missed_appointments": int(current_data['missed_appointments']),
                "engagement_drop_percent": int(current_data['engagement_drop_percent']),
                "prev_crisis": bool(current_data['prev_crisis']),
                "referral_text": str(current_data['referral_text'])
            }
            
            try:
                resp = requests.post("https://nhs-ai-clinical-support-gl6v.onrender.com/analyze", json=payload).json()
                
                # Dynamic Logic for UI Colors
                risk_color = "#D4351C" if resp['risk_level'] == "HIGH" else "#FFDD00" if resp['risk_level'] == "MODERATE" else "#00703C"
                
                # --- PREMIUM ANALYSIS OUTPUT ---
                st.markdown(f"""
                    <div class="analysis-box" style="border-top-color: {risk_color};">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <p style="color: #6E7781; text-transform: uppercase; font-weight: 700; font-size: 0.8rem; margin:0;">AI Classification Result</p>
                                <h1 style="color: {risk_color}; margin: 5px 0 15px 0; font-size: 3rem; font-weight: 900;">{resp['risk_level']}</h1>
                            </div>
                            <div style="background: {risk_color}10; padding: 10px 20px; border-radius: 12px; border: 1px solid {risk_color};">
                                <span style="color: {risk_color}; font-weight: 800;">{resp['context'].upper()}</span>
                            </div>
                        </div>
                        <hr style="border: 0; border-top: 1px solid #EEE; margin: 20px 0;">
                        <h4 style="color: #002F5C;">Engagement Velocity (Historical)</h4>
                    </div>
                """, unsafe_allow_html=True)

                # Chart integrated just below
                hist = df[df['patient_id'] == target_id].sort_values('date')
                st.area_chart(hist.set_index('date')['engagement_drop_percent'], color="#005EB8")

                # Alerts Grid
                st.markdown("### **Neural Insights**")
                cols = st.columns(len(resp['alerts']) if resp['alerts'] else 1)
                for i, alert in enumerate(resp['alerts']):
                    with cols[i]:
                        st.info(f"**Alert:**\n{alert}")
                
                st.caption(f"🔒 **Governance Notice:** {resp['governance']}")

            except Exception as e:
                st.error("Error: Could not reach AI Backend on Render. Please verify the service is awake.")

else:
    st.info("Welcome to Sentinel AI. Use the sidebar to upload patient caseloads for triage.")
