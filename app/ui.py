import streamlit as st
import requests
import time
import json


# --- Konfiguration ---
# Hier definieren wir, wo das Backend zu finden ist.
# In der Cloud Umgebung dann mit Umgebungsvariablen
BACKEND_URL = "http://127.0.0.1:8000/analyze"

st.set_page_config(page_title="BKA-InSight Light", page_icon="🕵️‍♂️", layout="wide")


st.title("🕵️ BKA-InSight Lite: Berichts-Analyse")
st.markdown("---")

# Layout
col_input, col_output = st.columns([1,1])


# Linke Seite - Eingabe

with col_input:
    st.subheader("📝 Eingabe Polizeibericht")
    input_text = st.text_area(
        "Bitte Bericht hier einfügen",
        height=300,
        placeholder="Beispiel: Der Folgende Tathergang wurde vom Zeugen beschrieben...")
    
    analyze_btn = st.button("🔍 Bericht analysieren", type="primary")


# Rechte Seite - Analyse Ergebnis

with col_output:
    st.subheader("📊 Analyse-Ergebnis")

    if analyze_btn:
        if not input_text.strip():
            st.warning("Bitte fügen sie den Bericht zuerst ein.")
        else:
            # Ladebalken
            st.spinner("KI analysiert den Bericht...")
            try:
                # 1. Anfrage an das Backend
                payload = {"text": input_text, "officer_id": "demo_user"}
                response = requests.post(BACKEND_URL, json=payload)

                if response.status_code == 200:
                    data = response.json()

                    # Ergebnis Darstellung

                    ## Risiko-Level hervorheben
                    risk = data.get("risk_level", "UNBEKANNT")
                    if risk == "HOCH":
                        st.error(f"⚠️ GEFAHRENSTUFE: {risk}")
                    elif risk == "MITTEL":
                        st.warning(f"⚖️ GEFAHRENSTUFE: {risk}")
                    else:
                        st.success(f"✅ GEFAHRENSTUFE: {risk}")

                    ## Zusammenfassung
                    st.markdown("#### Zusammenfassung")
                    st.info(data.get("summary"))

                    ## Entitäten
                    st.markdown("#### Gefundene Indikatoren")
                    entities = data.get("detected_entities", [])

                    if entities:
                        # Entities als Tags anzeigen
                        for entity in entities:
                            st.code(f"{entity['category']}: {entity['value']}")
                    else:
                        st.caption("Keine spezifischen Indikatoren gefunden.")

                    # Metadaten optional anzeigen
                    with st.expander("Technische JSON-Antwort anzeigen"):
                        st.json(data)
                
                else:
                    st.error(f"Fehler vom Backend: {response.status_code}")
                    st.json(response.json())
            
            except requests.exceptions.ConnectionError:
                    st.error("🚨 Verbindungsfehler! Läuft das Backend (main.py)?")
