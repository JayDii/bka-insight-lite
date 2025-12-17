from fastapi import FastAPI
from pydantic import BaseModel

# Initialize
app = FastAPI(title="BKA-InSight Lite Backend")

# Data model for inputs
class ReportRequest(BaseModel):
    text: str


# simple testing endpoint
@app.get("/")
def read_root():
    return {"status": "Backend läuft", "system": "BKA-InSight"}

# analyse endpoint (aktuell dummy)
@app.post("/analyze")
def analyze_report(request: ReportRequest):
    # TODO add AI endpoint
    return {
        "message": "Report empfangen",
        "received_lenght": len(request.text),
        "alert": False
    }

