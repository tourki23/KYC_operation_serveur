import os
import pickle
import json
import hashlib
import pandas as pd
from datetime import datetime, timezone
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from ORM_db_traducteur_SQL import SessionLocal, Client, TransactionLog

# --- 1. INITIALISATION (OBLIGATOIRE EN HAUT) ---
app = FastAPI()

# --- 2. CHARGEMENT ARTEFACTS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "models", "kyc_xgboost.pkl"), "rb") as f: MODEL = pickle.load(f)
with open(os.path.join(BASE_DIR, "models", "scaler.pkl"), "rb") as f: SCALER = pickle.load(f)
with open(os.path.join(BASE_DIR, "models", "features_list.json"), "r") as f: FEATURES = json.load(f)

# --- 3. DÉPENDANCES ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TransactionRequest(BaseModel):
    client_id: str
    montant: float

# --- 4. ROUTES (PLACÉES APRÈS L'INITIALISATION DE 'app') ---

@app.post("/score")
def scorer_transaction(req: TransactionRequest, db = Depends(get_db)):
    feat = {f: 0.0 for f in FEATURES}
    
    # Lecture du profil client
    client_record = db.query(Client).filter(Client.client_id == str(req.client_id)).first()
    
    if client_record:
        # Mappings sécurisés
        secteur_map = {"Commerce": 1.0, "Banque": 2.0, "Industrie": 3.0, "Services": 4.0}
        type_map = {"Courant": 1.0, "Epargne": 0.0}

        for f in FEATURES:
            if f == "secteur_encode":
                valeur = getattr(client_record, 'secteur_activite', None)
                feat[f] = float(secteur_map.get(valeur, 0.0))
            elif f == "type_compte_encode":
                valeur = getattr(client_record, 'type_compte', None)
                feat[f] = float(type_map.get(valeur, 0.0))
            elif hasattr(client_record, f):
                valeur = getattr(client_record, f)
                feat[f] = float(valeur) if valeur is not None else 0.0
    
    if "montant" in feat: 
        feat["montant"] = float(req.montant)

    # Inférence IA
    df_input = pd.DataFrame([feat])[FEATURES]
    prob = float(MODEL.predict_proba(SCALER.transform(df_input))[0][1])
    score = int(prob * 100)
    
    # Règles métier (Post-processing)
    if req.montant > 50000: score = min(score + 82, 99) 
    elif req.montant > 15000: score = min(score + 53, 75) 
    
    decision = "BLOQUÉE" if score >= 70 else "SURVEILLANCE" if score >= 40 else "APPROUVÉE"
    
    # Logging
    ts = datetime.now(timezone.utc).isoformat()
    hash_str = hashlib.sha256(f"{ts}{score}".encode()).hexdigest()[:12]
    
    nouvelle_transaction = TransactionLog(
        hash=hash_str, timestamp=ts, client_id=req.client_id, 
        score_risque=score, decision=decision
    )
    db.add(nouvelle_transaction)
    db.commit()

    return {"score": score, "score_risque": score, "decision": decision}

@app.get("/health")
def health():
    return {"status": "ok"}
