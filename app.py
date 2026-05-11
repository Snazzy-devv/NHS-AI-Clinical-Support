# %%
import streamlit as st
import pandas as pd
import requests
from data_manager import get_patients, process_upload


# %%
st.set_page_config(page_title="NHS AI Decision Support", layout="wide")

# %%
st.markdown("<h1 style='color: #005eb8;'>🏥 Clinical Decision Support: Population Health</h1>", unsafe_allow_html=True)

# %%
# --- Data Loading & Sidebar ---

# %%

st.sidebar.subheader("Import Caseload")
file = st.sidebar.file_uploader("Upload CSV/XLSX/JSON", type=['csv', 'xlsx', 'json'])
if file:
    df_new, msg = process_upload(file)
    if df_new is not None: st.sidebar.success("Sync Complete")
    else: st.sidebar.error(msg)

df = get_patients()

# --- Main Dashboard ---
if not df.empty:


# %%
    # Filter for the most recent entry for each patient to show in the 'Current Queue'

# %%

    latest_df = df.sort_values('date').groupby('patient_id').tail(1)
    
    col_list, col_detail = st.columns([1, 1.5])
    
    with col_list:
        st.subheader("Current Caseload (100+)")
        # Show a summary table
        st.dataframe(latest_df[['patient_id', 'missed_appointments', 'engagement_drop_percent']], use_container_width=True)
        
        st.divider()
        target_id = st.selectbox("Select Patient to Deep-Dive", latest_df['patient_id'])
        current_data = latest_df[latest_df['patient_id'] == target_id].iloc[0]

    with col_detail:
        if st.button(f"Analyze {target_id} Trends"):
            payload = {
                "patient_id": str(current_data['patient_id']),
                "missed_appointments": int(current_data['missed_appointments']),
                "engagement_drop_percent": int(current_data['engagement_drop_percent']),
                "prev_crisis": bool(current_data['prev_crisis']),
                "referral_text": str(current_data['referral_text'])
            }
            
            resp = requests.post("http://localhost:8000/analyze", json=payload).json()
            
            

# %%
# Risk Display
            st.metric("Risk Level", resp['risk_level'], delta=resp['context'])
            
            # Historical Progress Chart
            st.write("### Engagement Trajectory (Historical)")
            patient_history = df[df['patient_id'] == target_id].sort_values('date')
            st.line_chart(patient_history.set_index('date')['engagement_drop_percent'])
            
            with st.expander("AI Alert Reasoning"):
                for alert in resp['alerts']:
                    st.write(f"⚠️ {alert}")
                st.caption(f"Governance Note: {resp['governance']}")
else:
    st.info("Please upload or generate patient data.")



