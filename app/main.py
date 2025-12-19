from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from transformers import pipeline
import datetime


print("Lade KI-Modell... (das kann beim ersten Mal dauern)")
# Modell, das auch Deutsch verstehen sollte und Kategorien zuordnen kann.
# https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")

# Initialize
app = FastAPI(
    title="BKA-InSight Lite Backend",
    description="Backend Service zur Analyse von Polizeiberichten.",
    version="0.1.0"
              )

# Data model for inputs
class ReportRequest(BaseModel):
    text: str
    officer_id: Optional[str] = "unknown"

class Entity(BaseModel):
    category: str # z.B. Person, Ort, Waffe
    value: str

class AnalysisResponse(BaseModel):
    timestamp: str
    risk_level: str # "NIEDRIG", "MITTEL", "HOCH"
    detected_entities: List[Entity]
    summary: str
    raw_length: int

# Business Logic
def analyze_logic(text: str) -> dict:
    """
    veto-Logik: Safety First.
    Sobald eine 'Red Flag' erkannt wird, ist das Risiko HOCH
    """
    
    if len(text.strip()) < 10:
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "risk_level": "NIEDRIG",
            "detected_entities": [],
            "summary": "Text zu kurz.",
            "raw_length": len(text)
        }

    # Labels: Wir brauchen ein Label, das genau auf deinen Text passt (Bedrohung)
    labels = [
        "Bedrohung mit Waffen",       # (Red Flag)
        "Körperverletzung",           # (Red Flag)
        "Amoklage oder Terror",       # (Red Flag)
        "Einbruch oder Diebstahl",    # (Yellow Flag)
        "Vandalismus",                # (Yellow Flag)
        "Verkehrsdelikt",             # (Green Flag)
        "Ruhestörung / Streit",       # (Green Flag)
        "Friedlich / Routine"         # (Green Flag)
    ]
    
    # Wir lassen multi_label=True, damit er Waffe UND Bedrohung gleichzeitig erkennen kann
    result = classifier(text, labels, multi_label=True)
    
    detected_entities = []
    
    # Definition der Gefahrenklassen
    red_flags = ["Bedrohung mit Waffen", "Körperverletzung", "Amoklage oder Terror"]
    yellow_flags = ["Einbruch oder Diebstahl", "Vandalismus"]
    
    current_risk = "NIEDRIG"
    trigger_label = "Keine Gefahr"

    # Wir prüfen die Ergebnisse
    for label, score in zip(result['labels'], result['scores']):
        
        percent = int(score * 100)
        
        # Nur anzeigen, wenn relevant
        if score > 0.3:
            detected_entities.append(Entity(category="Detektion", value=f"{label} ({percent}%)"))

        # ---  VETO LOGIK ---
        
        # 1. Höchste Priorität: RED FLAGS
        if label in red_flags and score > 0.40:
            current_risk = "HOCH"
            trigger_label = label
            # Wir brechen hier nicht ab, wollen aber sicherstellen, dass HOCH bleibt
            
        # 2. Mittlere Priorität: YELLOW FLAGS
        elif label in yellow_flags and score > 0.50 and current_risk != "HOCH":
            current_risk = "MITTEL"
            trigger_label = label

    summary_text = f"Einstufung durch Trigger: '{trigger_label}'."

    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "risk_level": current_risk,
        "detected_entities": detected_entities,
        "summary": summary_text,
        "raw_length": len(text)
    }
# ENDPOINTS

## health testing endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "system": "bka-insight-backend"}

## analyse endpoint (aktuell dummy)
@app.post("/analyze", response_model=AnalysisResponse)
def analyze_report(request: ReportRequest):
    # TODO add AI endpoint
    if not request.text:
        raise HTTPException(status_code=400, detail="Bericht darf nicht leer sein.")
    
    result = analyze_logic(request.text)

    return result

