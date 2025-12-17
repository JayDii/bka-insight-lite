import streamlit as st
import requests

# Konfiguration der Seite
st.set_page_config(page_title="BKA-InSight Light", layout="wide")

st.title("🕵️ BKA-InSight Lite: Berichts-Analyse")
st.markdown("---")

# Eingabebereich
col1, col2 = st.columns(2)

with col1:
    st.subheader("Eingabe Polizeibericht")
    report_text = st.text_area("Bitte Bericht hier einfügen", height=300)

    if st.button("Analyse starten"):
        if report_text:
            st.info("Sende Daten an Backend")
            # TODO Backend connect to Frontend
            st.success("Verbindung steht noch aus")
        else:
            st.warning("Bitte erst Text eingeben.")

with col2:
    st.subheader("Analyse-Ergebnis")
    # TODO add AI
    st.write("Hier KI Auswertung einfügen")