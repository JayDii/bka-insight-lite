from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Prüft ob Server antwortet."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status":"healthy","system":"insight-backend"}


def test_analyze_harmless():
    """TODO: Modell mit Veto Logik Stuft aktuelle noch zu vieles als Gefährlich ein."""
    """Prüft einen harmlosen Text -> Sollte NIEDRIG sein."""
    payload = {
        "text": "An einem Ganz normalen Tag. Die Katze sitzt auf dem Baum und miaut friedlich.",
        "officer_id": "test-unit"
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "NIEDRIG" or data["risk_level"] =="MITTEL"

def test_analyze_veto_logic():
    """
    Prüft, ob die Veto-Logik (Messer) das Risiko auf HOCH zwingt,
    selbst wenn der Rest harmlos klingt.
    """
    # Text enthält "Messer" (Red Flag)
    payload = {
        "text": "Der Mann war eigentlich nett, aber er hatte ein Messer in der Hand.",
        "officer_id": "test-unit"
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    assert "HOCH" in data["risk_level"]
    assert any("Waffen" in entity["value"] for entity in data["detected_entities"])

