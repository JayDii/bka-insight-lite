#!/bin/bash

# Beide Dienste in einem Container startens

# 1. Backend im Hintergrund starten 
# Auf 127.0.0.1, damit es nur innerhalb des Containers erreichbar ist.
uvicorn app.main:app --host 127.0.0.1 --port 8000 &

# 2. Frontend starten
# Das Frontend muss auf 0.0.0.0 hören, damit es von außen erreichbar ist.
# Port 7860, für Hugging Face Spaces
streamlit run app/ui.py --server.port 7860 --server.address 0.0.0.0