FROM python:3.9-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# Python ausgaben sofort anzeigen
ENV PYTHONUNBUFFERED=1

# System-Update und Installation von Curl (für Healthchecks nützlich)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

#CPU Only Torch (Smaller)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
# Zuerst nur die Requirements kopieren (Docker-Caching Trick)
COPY requirements.txt .

# Pakete installieren
# --no-cache-dir , um das Image klein zu halten
RUN pip install --no-cache-dir -r requirements.txt

# Jetzt den Rest des Codes kopieren
COPY . .

# Rechte für das Start-Skript setzen
RUN chmod +x entrypoint.sh

# Erstellen nicht-Root User
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Port 7860 freigeben (Standard Hugging Face Spaces)
EXPOSE 7860

# Startbefehl
CMD ["./entrypoint.sh"]