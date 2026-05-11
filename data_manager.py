import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def get_patients():
    if os.path.exists("patients.csv"):
        return pd.read_csv("patients.csv")
    return generate_mock_history()

def generate_mock_history(n_patients=100, entries_per_patient=5):
    """Creates a dataset with historical 'weeks' of data for each patient."""
    data = []
    base_date = datetime.now()
    
    for i in range(n_patients):
        p_id = f"NHS-{1000+i}"
        prev_crisis = np.random.choice([True, False], p=[0.15, 0.85])
        
        # Create a 'trend' for each patient
        trend_direction = np.random.choice([-5, 0, 5]) # Improving, Stable, or Declining
        
        for week in range(entries_per_patient):
            date = (base_date - timedelta(weeks=entries_per_patient-week)).strftime("%Y-%m-%d")
            
            # Engagement shifts over time based on the trend
            engagement = max(0, min(100, 20 + (week * trend_direction) + np.random.randint(-5, 5)))
            missed = 0 if engagement < 30 else np.random.randint(1, 4)
            
            data.append({
                "patient_id": p_id,
                "date": date,
                "missed_appointments": missed,
                "engagement_drop_percent": engagement,
                "prev_crisis": prev_crisis,
                "referral_text": f"Routine check-in for week {week}. Patient status recorded."
            })
            
    df = pd.DataFrame(data)
    df.to_csv("patients.csv", index=False)
    return df

def process_upload(file):
    ext = file.name.split('.')[-1].lower()
    try:
        if ext == 'csv': df = pd.read_csv(file)
        elif ext in ['xlsx', 'xls']: df = pd.read_excel(file)
        elif ext == 'json': df = pd.read_json(file)
        else: return None, "Unsupported format."
        
        # Verify required columns
        required = ['patient_id', 'date', 'missed_appointments', 'engagement_drop_percent', 'prev_crisis', 'referral_text']
        if not all(col in df.columns for col in required):
            return None, f"Missing columns. Required: {required}"
            
        df.to_csv("patients.csv", index=False)
        return df, "Success"
    except Exception as e:
        return None, str(e)
