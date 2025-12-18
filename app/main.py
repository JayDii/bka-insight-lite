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
    """Transformer (mDeBERTa) basierte Text Analyse"""


    # Input Validierung: Kurze Text führen mit hoher wahrscheinlichkeit zu halluzinationen.
    if len(text.strip()) < 10:
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "risk_level": "NIEDRIG",
            "detected_entities": [],
            "summary": "Hinweis: Eingabetext ist zu kurz für eine verlässliche KI-Analyse (min. 10 Zeichen).",
            "raw_length": len(text)
        }


    ## Kandiaten, Kontexte die Relevant sein können in einem Bericht
    labels = ["Gefahr für Leib und Leben", "Waffengebrauch", "Drogenkriminalität", "Routineeinsatz", "Friedlich"]

    ## KI Anfrage
    result = classifier(text, labels, multi_label=True)

    # 3. Ergebnisse auswerten
    # result['scores'] und result['labels'] enthalten die Wahrscheinlichkeiten
    
    detected_entities = []
    risk_score = 0
    
    # Mapping für Risiko-Berechnung (Label -> Punkte)
    risk_map = {
        "Gefahr für Leib und Leben": 2,
        "Waffengebrauch": 2,
        "Drogenkriminalität": 1,
        "Routineeinsatz": 0,
        "Friedlich": 0
    }

    # Betrachte alle keywords mit score über 50%
    for label, score in zip(result['labels'], result['scores']):
        if score > 0.5:
            percent = int(score * 100)
            detected_entities.append(Entity(category="Kategorie", value=f"{label} ({percent}%)"))

            # Risiko Bewerten
            risk_score += risk_map.get(label, 0)

    # Risiko-Level bestimmen  
    if risk_score >= 2:
        risk_level = "HOCH"
    elif risk_score == 1:
        risk_level = "MITTEL"
    else:
       risk_level = "NIEDRIG"
    
    summary = f"KI-Scan abgeschlossen. Relevante Themen: {[e.value for e in detected_entities]}"

    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "risk_level": risk_level,
        "detected_entities": detected_entities,
        "summary": summary,
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

