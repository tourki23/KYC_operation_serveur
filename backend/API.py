import os
import sys
import pickle
import json
import hashlib
import pandas as pd
import subprocess
from datetime import datetime, timezone
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import text  # <-- NOUVEL IMPORT AJOUTÉ ICI

# --- 1. SÉCURITÉ DES CHEMINS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# --- 2. INITIALISATION ---
app = FastAPI()
simulator_process = None 

# --- 3. IMPORTATIONS ET SYNCHRONISATION DB ---
try:
    from ORM_db_traducteur_SQL import SessionLocal, Client, TransactionLog, engine, Base
    Base.metadata.create_all(bind=engine)
    print("✅ Base de données prête : Tables vérifiées.")
    DB_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Attention : Problème ORM/Base : {e}")
    DB_AVAILABLE = False

# Chargement artefacts
def load_file(path):
    try:
        with open(path, "rb" if path.endswith((".pkl", ".bin")) else "r") as f:
            return pickle.load(f) if path.endswith((".pkl", ".bin")) else json.load(f)
    except: return None

FEATURES = load_file(os.path.join(BASE_DIR, "models", "features_list.json"))

# --- LOGIQUE DE CHARGEMENT ---
# 1. On tente d'abord la Régression Logistique
MODEL = load_file(os.path.join(BASE_DIR, "models", "LogisticRegression_model.pkl"))
SCALER = load_file(os.path.join(BASE_DIR, "models", "LogisticRegression_scaler.pkl"))
MODEL_NAME = "LogisticRegression"

# 2. Si ça échoue, on bascule sur XGBoost
if MODEL is None or SCALER is None:
    print("⚠️ LogisticRegression non trouvé, bascule sur XGBoost...")
    MODEL = load_file(os.path.join(BASE_DIR, "models", "kyc_xgboost.pkl"))
    SCALER = load_file(os.path.join(BASE_DIR, "models", "scaler.pkl"))
    MODEL_NAME = "kyc_xgboost"

# Log de vérification
if MODEL and SCALER:
    print(f"✅ MODÈLE CHARGÉ : {MODEL_NAME}")
else:
    print("❌ ERREUR CRITIQUE : Aucun modèle n'a pu être chargé.")

# --- 4. ROUTES ---
def get_db():
    if not DB_AVAILABLE: yield None
    else:
        db = SessionLocal()
        try: yield db
        finally: db.close()

class TransactionRequest(BaseModel):
    client_id: str
    montant: float

@app.post("/score")
def scorer_transaction(req: TransactionRequest, db = Depends(get_db)):
    feat = {f: 0.0 for f in FEATURES}
    
    # 1. Lecture profil client
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

    # 2. Inférence IA
    score_ia = 0
    if MODEL and SCALER:
        df_input = pd.DataFrame([feat])[FEATURES]
        prob = float(MODEL.predict_proba(SCALER.transform(df_input))[0][1])
        score_ia = int(prob * 100)
    
    # Règles métier
    score_risque = score_ia
    if req.montant > 50000: score_risque = min(score_ia + 82, 99)
    elif req.montant > 15000: score_risque = min(score_ia + 53, 75)
    
    decision = "BLOQUÉE" if score_risque >= 70 else "SURVEILLANCE" if score_risque >= 40 else "APPROUVÉE"
    ts = datetime.now(timezone.utc).isoformat()
    hash_str = hashlib.sha256(f"{ts}{score_risque}{req.client_id}".encode()).hexdigest()[:12]

    # 3. Sauvegarde sécurisée
    if db:
        try:
            nouvelle_transaction = TransactionLog(hash=hash_str, timestamp=ts, client_id=req.client_id, score_risque=score_risque, decision=decision)
            db.add(nouvelle_transaction)
            db.commit()
            print(f"✅ Transaction enregistrée : {hash_str}")
        except Exception as e:
            db.rollback()
            print(f"❌ ERREUR DB : {e}")

    return {"score": score_ia, "score_risque": score_risque, "decision": decision, "model": MODEL_NAME}

# --- ROUTES SIMULATEUR ---
@app.post("/simulator/start")
def start_simulator():
    global simulator_process
    
    # Vérification anti-doublon
    if simulator_process and simulator_process.poll() is None:
        return {"status": "⚠️ Simulateur déjà en cours. Requête ignorée."}
        
    sim_script_path = os.path.join(BASE_DIR, "Transaction_simulator.py")
    simulator_process = subprocess.Popen(["python", sim_script_path, "--duration", "36000"])
    return {"status": "🚀 Simulateur démarré."}

@app.post("/simulator/stop")
def stop_simulator():
    global simulator_process
    if simulator_process:
        simulator_process.terminate()
        # On attend que le processus se termine proprement
        simulator_process.wait()
        simulator_process = None # On réinitialise la variable
        return {"status": "🛑 Simulateur arrêté."}
    return {"status": "Aucun simulateur en cours."}

# --- ROUTE NETTOYAGE DB ---
@app.post("/simulator/truncate")
def truncate_history(db = Depends(get_db)):
    if db:
        try:
            # Commande native PostgreSQL pour vider rapidement la table
            db.execute(text("TRUNCATE TABLE transactions_history;"))
            db.commit()
            return {"status": "🧹 Base de données nettoyée avec succès."}
        except Exception as e:
            db.rollback()
            # Fallback en DELETE si tu testes un jour en SQLite local
            try:
                db.execute(text("DELETE FROM transactions_history;"))
                db.commit()
                return {"status": "🧹 Base nettoyée (Delete fallback)."}
            except Exception as fallback_e:
                return {"error": str(fallback_e)}
    return {"error": "Connexion DB impossible"}

@app.get("/health")
def health():
    return {"status": "ok", "loaded_model": MODEL_NAME}
