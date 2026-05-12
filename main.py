from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
import uvicorn
import os

app = FastAPI(title="NHS Sentinel AI Backend")

# Optimization: Use a smaller model to stay under 512MB RAM
# 'typeform/distilbert-base-uncased-mnli' is significantly lighter than BART
nlp_engine = pipeline(
    "zero-shot-classification", 
    model="typeform/distilbert-base-uncased-mnli",
    model_kwargs={"torch_dtype": "auto"}
)

class PatientData(BaseModel):
    patient_id: str
    missed_appointments: int
    engagement_drop_percent: int
    prev_crisis: bool
    referral_text: str

@app.get("/")
def health_check():
    return {"status": "online", "model": "distilbert-mnli"}

@app.post("/analyze")
async def analyze_patient(data: PatientData):
    score = 0
    alerts = []
    
    # 1. Behavioral Scoring
    if data.missed_appointments >= 3:
        score += 40
        alerts.append("Frequent missed contacts")
    if data.engagement_drop_percent >= 40:
        score += 35
        alerts.append("Sharp decline in service engagement")
    if data.prev_crisis:
        score += 15
        
    # 2. NLP Context
    categories = ["urgent clinical need", "routine monitoring", "emotional distress"]
    # The engine runs on the optimized DistilBERT model
    nlp_res = nlp_engine(data.referral_text, categories)
    top_label = nlp_res['labels'][0]

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
    # Use environment variable for port to satisfy Render's dynamic binding
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
