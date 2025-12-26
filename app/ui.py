import streamlit as st
import requests
import time
import json


# --- Konfiguration ---
# Hier definieren wir, wo das Backend zu finden ist.
# In der Cloud Umgebung dann mit Umgebungsvariablen
BACKEND_URL = "http://127.0.0.1:8000/analyze"

st.set_page_config(page_title="InSight Light", page_icon="🕵️‍♂️", layout="wide")

# --- Session State für Textfeld initialisieren ---
if 'report_text' not in st.session_state:
    st.session_state['report_text'] = ""

st.title("InSight Lite: Berichts-Analyse")
st.markdown("---")

# Layout
col_input, col_output = st.columns([1,1])


# Linke Seite - Eingabe

with col_input:
    st.subheader("📝 Eingabe Polizeibericht")

    # Beispiel-Buttons
    st.markdown("Schnellwahl (Demo-Szenarien):")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    if btn_col1.button("🔴 Akute Bedrohung"):
        st.session_state['report_text'] = (
            "Am heutigen Nachmittag gingen mehrere Notrufe ein. Eine männliche Person "
            "attackierte Passanten am Bahnhofsvorplatz verbal und bedrohte sie mit einem "
            "ca. 20 cm langen Messer. Der Verdächtige verhielt sich hochaggressiv."
        )
    
    if btn_col2.button("🟡 Einbruch"):
        st.session_state['report_text'] = (
            "In der Nacht löste die Alarmanlage eines Elektronikmarktes aus. "
            "Vor Ort wurde ein aufgehebeltes Fenster festgestellt. "
            "Zwei dunkel gekleidete Personen flohen vermutlich mit einem Kombi vom Tatort."
        )
        
    if btn_col3.button("🟢 Harmlos / Kontext"):
        st.session_state['report_text'] = (
            "Zwei Jugendliche mit Kapuzen wurden im Baumarkt gemeldet, die sich dort "
            "auffällig verhielten. Bei der Kontrolle stellte sich heraus, dass sie "
            "lediglich Halloween-Kostüme anprobierten und spielten. Keine Straftat."
        )

    # Textfeld (Verknüpft mit Session State)
    input_text = st.text_area(
        "Fügen Sie hier den Berichtstext ein:",
        height=300,
        placeholder="Beispiel: Am Tatort wurde eine Waffe gefunden...",
        key="report_text" # <--- Das verbindet das Feld mit den Buttons
    )
    
    analyze_btn = st.button("🔍 Bericht analysieren", type="primary")


# Rechte Seite - Analyse Ergebnis

with col_output:
    st.subheader("📊 Analyse-Ergebnis")

    if analyze_btn:
        if not input_text.strip():
            st.warning("Bitte fügen sie den Bericht zuerst ein.")
        else:
            # Langsam auf Free Tier Warnung
            st.info("ℹ️ Hinweis: Da dieser Prototyp auf einer kostenlosen CPU-Cloud-Instanz läuft, kann die Analyse wenige Minuten dauern. Bitte haben Sie einen Moment Geduld.")
            # Ladebalken
            with st.spinner("KI analysiert den Bericht..."):
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
