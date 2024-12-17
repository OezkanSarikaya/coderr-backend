#!/bin/sh

# Stoppe das Skript bei Fehlern
set -e

# Migrationen ausführen
python manage.py migrate

# Optional: Initialdaten laden (falls vorhanden)
# python manage.py loaddata initial_data.json
python db_fill.py

# Entwicklungsserver starten
python manage.py runserver 0.0.0.0:8000
