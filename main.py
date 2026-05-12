from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import requests
import os

app = FastAPI()

# --- CONFIGURATION ---
# 1. Get a free API token from: https://huggingface.co/settings/tokens
# 2. Add it to Render "Environment Variables" as HF_TOKEN
HF_TOKEN = os.environ.get("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/typeform/distilbert-base-uncased-mnli"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

class PatientData(BaseModel):
    patient_id: str
    missed_appointments: int
    engagement_drop_percent: int
    prev_crisis: bool
    referral_text: str

@app.get("/")
def home():
    return {"status": "Sentinel AI Online", "mode": "Inference API"}

@app.post("/analyze")
async def analyze_patient(data: PatientData):
    score = 0
    alerts = []
    
    # 1. Behavioral Scoring (Logic remains local and fast)
    if data.missed_appointments >= 3:
        score += 40
        alerts.append("Frequent missed contacts")
    if data.engagement_drop_percent >= 40:
        score += 35
        alerts.append("Sharp decline in service engagement")
    if data.prev_crisis:
        score += 15
        
    # 2. NLP Context (Offloaded to Hugging Face)
    payload = {
        "inputs": data.referral_text,
        "parameters": {"candidate_labels": ["urgent clinical need", "routine monitoring", "emotional distress"]}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload).json()
        # Handle API errors or model loading
        if "error" in response:
            top_label = "routine monitoring" # Fallback
        else:
            top_label = response['labels'][0]
    except:
        top_label = "routine monitoring"

    # 3. Final Triage logic
    if score >= 70 or top_label == "urgent clinical need":
        level = "HIGH"
    elif score >= 40:
        level = "MODERATE"
    else:
        level = "LOW"

    return {
        "risk_level": level,
        "score": score,
        "context": top_label,
        "alerts": alerts,
        "governance": "Human-in-the-loop oversight mandatory."
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
