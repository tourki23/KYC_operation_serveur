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
# On ajoute le dossier courant au path pour que Python trouve ORM_db_traducteur_SQL
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- 2. INITIALISATION ---
app = FastAPI()

# --- 3. IMPORTATIONS CORRIGÉES ---
try:
    # IMPORT DIRECT : On enlève 'backend.' car on est DÉJÀ dans le dossier backend
    from ORM_db_traducteur_SQL import SessionLocal, Client, TransactionLog, engine, Base
    
    # Création automatique des tables
    Base.metadata.create_all(bind=engine)
    print("✅ Base de données prête : Tables vérifiées.")
    DB_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Attention : Problème ORM/Base : {e}")
    DB_AVAILABLE = False

# Chargement artefacts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def load_file(path):
    try:
        with open(path, "rb" if path.endswith((".pkl", ".bin")) else "r") as f:
            return pickle.load(f) if path.endswith((".pkl", ".bin")) else json.load(f)
    except: return None

MODEL = load_file(os.path.join(BASE_DIR, "models", "kyc_xgboost.pkl"))
SCALER = load_file(os.path.join(BASE_DIR, "models", "scaler.pkl"))
FEATURES = load_file(os.path.join(BASE_DIR, "models", "features_list.json"))

# --- 4. ROUTES ---
class TransactionRequest(BaseModel):
    client_id: str
    montant: float

def get_db():
    if not DB_AVAILABLE: yield None
    else:
        db = SessionLocal()
        try: yield db
        finally: db.close()

@app.post("/score")
def scorer_transaction(req: TransactionRequest, db = Depends(get_db)):
    feat = {f: 0.0 for f in FEATURES}
    
    if db:
        try:
            client_record = db.query(Client).filter(Client.client_id == str(req.client_id)).first()
            if client_record:
                secteur_map = {"Commerce": 1.0, "Banque": 2.0, "Industrie": 3.0, "Services": 4.0}
                type_map = {"Courant": 1.0, "Epargne": 0.0}
                for f in FEATURES:
                    if f == "secteur_encode": feat[f] = float(secteur_map.get(getattr(client_record, 'secteur_activite', None), 0.0))
                    elif f == "type_compte_encode": feat[f] = float(type_map.get(getattr(client_record, 'type_compte', None), 0.0))
                    elif hasattr(client_record, f): feat[f] = float(getattr(client_record, f)) if getattr(client_record, f) is not None else 0.0
        except Exception as e:
            print(f"DEBUG: Erreur lecture client : {e}")
    
    if "montant" in feat: feat["montant"] = float(req.montant)

    score = 0
    if MODEL and SCALER:
        df_input = pd.DataFrame([feat])[FEATURES]
        prob = float(MODEL.predict_proba(SCALER.transform(df_input))[0][1])
        score = int(prob * 100)
    
    if req.montant > 50000: score = min(score + 82, 99)
    elif req.montant > 15000: score = min(score + 53, 75)
    
    decision = "BLOQUÉE" if score >= 70 else "SURVEILLANCE" if score >= 40 else "APPROUVÉE"
    
    if db:
        try:
            ts = datetime.now(timezone.utc).isoformat()
            hash_str = hashlib.sha256(f"{ts}{score}{req.client_id}".encode()).hexdigest()[:12]
            nouvelle_transaction = TransactionLog(hash=hash_str, timestamp=ts, client_id=req.client_id, score_risque=score, decision=decision)
            db.add(nouvelle_transaction)
            db.commit()
            print(f"✅ Transaction enregistrée : {hash_str}")
        except Exception as e:
            db.rollback()
            print(f"❌ ERREUR DB : {e}")

    return {"score": score, "score_risque": score, "decision": decision}

@app.get("/health")
def health():
    return {"status": "ok"}
