import os
import sys
import pickle
import json
import hashlib
import pandas as pd
from datetime import datetime, timezone
from fastapi import FastAPI, Depends
from pydantic import BaseModel

# --- 1. SÉCURITÉ DES CHEMINS ---
# Assure que le dossier parent est dans le path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- 2. INITIALISATION (OBLIGATOIRE) ---
app = FastAPI()

# --- 3. IMPORTATIONS SÉCURISÉES ---
# Si l'ORM crash (ex: mauvaise URL DB), on ne veut pas que tout le fichier API crash
try:
    from backend.ORM_db_traducteur_SQL import SessionLocal, Client, TransactionLog
    DB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Attention : Import ORM impossible (test en mode isolé) : {e}")
    DB_AVAILABLE = False

# Chargement artefacts avec vérification
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def load_file(path):
    if os.path.exists(path):
        with open(path, "rb" if path.endswith((".pkl", ".bin")) else "r") as f:
            return pickle.load(f) if path.endswith((".pkl", ".bin")) else json.load(f)
    return None

MODEL = load_file(os.path.join(BASE_DIR, "models", "kyc_xgboost.pkl"))
SCALER = load_file(os.path.join(BASE_DIR, "models", "scaler.pkl"))
FEATURES = load_file(os.path.join(BASE_DIR, "models", "features_list.json"))

# --- 4. ROUTES ---
class TransactionRequest(BaseModel):
    client_id: str
    montant: float

def get_db():
    if not DB_AVAILABLE: return None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/score")
def scorer_transaction(req: TransactionRequest, db = Depends(get_db)):
    # ... (Garde ton code actuel ici, il est bon) ...
    return {"status": "success"}

@app.get("/health")
def health():
    return {"status": "ok"}
