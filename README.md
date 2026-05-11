# NHS AI Clinical Decision Support: Population Health Management

This repository contains a comprehensive **Clinical Decision Support (CDS)** system designed for NHS population health management. The platform integrates **FastAPI** for AI-driven risk inference and **Streamlit** for real-time caseload visualization, specifically targeting the identification of high-risk patients through behavioral metrics and **Zero-Shot NLP**.

---

## 📸 Media & Demo

To see the system in action, please refer to the following demonstration materials:

* **[🎥 Watch the Video Demo](https://www.google.com/search?q=https://github.com/Snazzy-devv/NHS-project/releases/tag/v1.0.0-demo)** – *Includes a walkthrough of patient deep-dives and AI alert reasoning.*
* **[🖼️ View Screenshot Gallery](https://www.google.com/search?q=https://github.com/Snazzy-devv/NHS-project/tree/main/assets/screenshots)** – *High-resolution captures of the population health dashboard and risk metrics.*

---

## 🛠️ Tech Stack & Architecture

### **Core Frameworks**

* 
**Frontend**: Streamlit (Python-based interactive dashboard).


* 
**Backend**: FastAPI (Asynchronous high-performance API).


* 
**AI Engine**: Hugging Face Transformers (`valhalla/distilbart-mnli-12-3`) for NLP classification.



### **Data & Machine Learning**

* 
**Processors**: Pandas and Numpy for data manipulation.


* 
**ML Models**: XGBoost, LightGBM, and Scikit-learn for advanced predictive capabilities.


* 
**Deep Learning**: PyTorch and Transformers for linguistic context analysis.



---

## 🚀 Key Features

### **1. AI-Driven Risk Stratification**

The system automatically triages patients by calculating a weighted risk score based on historical and behavioral data :

* 
**Behavioral Scoring**: Flags patients with $\ge 3$ missed appointments or a $\ge 40\%$ drop in engagement.


* 
**Contextual NLP**: Analyzes referral text to categorize patient needs as "Urgent Clinical Need," "Routine Monitoring," or "Emotional Distress".



### **2. Clinical Dashboard**

* 
**Caseload Overview**: Displays a real-time table of current patient status, engagement percentages, and contact history .


* 
**Patient Deep-Dive**: Select a specific patient to view their historical **Engagement Trajectory** via interactive line charts .


* 
**AI Alert Reasoning**: Provides transparent explanations for risk flags, detailing the specific reasons behind an AI-generated alert .



### **3. Scalable Data Management**

* Supports uploading patient data via **CSV, XLSX, and JSON** formats .


* Includes a **Synthetic Data Generator** to create mock patient histories for training and testing purposes .



---

## 🚦 Getting Started

### **Prerequisites**

Ensure you have Python installed, then set up the environment :

```bash
pip install fastapi uvicorn streamlit pandas numpy requests openpyxl xgboost lightgbm scikit-learn transformers torch spacy
python -m spacy download en_core_web_sm

```

### **Running the Project**

The application requires two concurrent processes:

1. **Launch the AI Backend**:
```bash
python main.py

```



*Starts the FastAPI server on `http://0.0.0.0:8000*`.


2. **Launch the Dashboard**:
```bash
streamlit run app.py

```



*Opens the visual interface in your default browser*.



---

## 📊 Triage Logic Table

| Risk Level | Score Criteria | NLP Context Trigger |
| --- | --- | --- |
| **HIGH** | Score $\ge 70$ | "Urgent Clinical Need" 

 |
| **MODERATE** | Score $\ge 40$ | Behavioral flags present 

 |
| **LOW** | Score $< 40$ | Routine status 

 |

---


## 📊 Clinical Visualizations

Engagement Trajectory: Interactive line charts showing a patient's historical engagement over time .  


AI Alert Reasoning: Detailed expanders that explain the "why" behind an AI-generated risk level to ensure transparency .  

## 📦 Installation & Setup
Prerequisites
Python 3.10+

FastAPI, Uvicorn, Streamlit, and Transformers libraries.

## 📊 Data Specifications
The system requires caseload files to contain the following columns for successful analysis:  

patient_id, date, missed_appointments, engagement_drop_percent, prev_crisis, and referral_text.

## 🛡️ Governance & Safety

This project is designed with a **Human-in-the-loop** mandate. All AI-generated alerts must be reviewed by qualified clinical staff. Every risk report includes a governance note emphasizing that professional oversight is mandatory for population health decisions.
