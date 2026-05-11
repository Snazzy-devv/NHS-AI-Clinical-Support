# %%
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
import uvicorn
import pandas as pd



# %%
app = FastAPI()

# %%

# Zero-Shot Classification for Contextual Urgency


# %%
nlp_engine = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-3")

class PatientData(BaseModel):
    patient_id: str
    missed_appointments: int
    engagement_drop_percent: int
    prev_crisis: bool
    referral_text: str

@app.post("/analyze")
async def analyze_patient(data: PatientData):
    score = 0
    alerts = []
    


# %%
    # 1. Behavioral Scoring

# %%
    if data.missed_appointments >= 3:
        score += 40
        alerts.append("Frequent missed contacts")
    if data.engagement_drop_percent >= 40:
        score += 35
        alerts.append("Sharp decline in service engagement")
    if data.prev_crisis:
        score += 15



# %%
    # 2. NLP Context
    categories = ["urgent clinical need", "routine monitoring", "emotional distress"]
    nlp_res = nlp_engine(data.referral_text, categories)
    top_label = nlp_res['labels'][0]


# %%
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
    uvicorn.run(app, host="0.0.0.0", port=8000)




# %%



