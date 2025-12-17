from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import datetime

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
    """Simuliere KI Logik"""
    # TODO Place AI-Call Here
    text_lower = text.lower()
    entities = []
    risk_score = 0

    # Simple rule-based detection
    risk_keywords = ["waffe", "bombe", "sprengstoff", "angriff", "gefahr", "drogen"]

    for word in risk_keywords:
        if word in text_lower:
            risk_score += 1
            entities.append(Entity(category="Gefahrenbegriff", value=word))

    # Risiko-Bewertung
    if risk_score == 0:
        risk_level = "NIEDRIG"
    elif risk_score < 2:
        risk_level = "MITTEL"
    else:
        risk_level = "HOCH"

    # Dummy Zusammenfassung
    summary = f"Automatischer Report:  {text[:50]}..."

    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "risk_level": risk_level,
        "detected_entities": entities,
        "summary": summary,
        "raw_length": len(text)
    }


## ENDPOINTS

# health testing endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "system": "bka-insight-backend"}

# analyse endpoint (aktuell dummy)
@app.post("/analyze", response_model=AnalysisResponse)
def analyze_report(request: ReportRequest):
    # TODO add AI endpoint
    if not request.text:
        raise HTTPException(status_code=400, detail="Bericht darf nicht leer sein.")
    
    result = analyze_logic(request.text)

    return result

