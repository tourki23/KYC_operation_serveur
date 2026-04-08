import os, pickle, json, hashlib, subprocess
import pandas as pd
from datetime import datetime, timezone
from fastapi import FastAPI, Depends
from pydantic import BaseModel
import uvicorn

# --- CONFIGURATION DES CHEMINS (BAZOOKA) ---
# On récupère le dossier où se trouve ce fichier API.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Import de notre base de données (Import relatif avec le point)
try:
    from .ORM_db_traducteur_SQL import SessionLocal, Client, TransactionLog
except ImportError:
    from ORM_db_traducteur_SQL import SessionLocal, Client, TransactionLog

# Chargement artefacts IA avec chemins absolus
MODEL_PATH = os.path.join(BASE_DIR, "models", "kyc_xgboost.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "models", "features_list.json")

with open(MODEL_PATH, "rb") as f: MODEL = pickle.load(f)
with open(SCALER_PATH, "rb") as f: SCALER = pickle.load(f)
with open(FEATURES_PATH, "r") as f: FEATURES = json.load(f)

app = FastAPI()

# --- VARIABLE GLOBALE POUR LE SIMULATEUR ---
simulator_process = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TransactionRequest(BaseModel):
    client_id: str
    montant: float
    pays_destination: str = "France"
    type_transaction: str = "virement"

@app.post("/score")
def scorer_transaction(req: TransactionRequest, db = Depends(get_db)):
    feat = {f: 0.0 for f in FEATURES}
    
    # 1. Lecture du profil client via PostgreSQL
    client_record = db.query(Client).filter(Client.client_id == str(req.client_id)).first()
    
    if client_record:
        client_dict = client_record.__dict__
        for f in FEATURES:
            if f in client_dict and client_dict[f] is not None: 
                feat[f] = float(client_dict[f])
    
    if "montant" in feat: 
        feat["montant"] = float(req.montant)

    # 2. Prédiction IA
    df_input = pd.DataFrame([feat])[FEATURES]
    prob = float(MODEL.predict_proba(SCALER.transform(df_input))[0][1])
    score = int(prob * 100)
    
    if req.montant > 50000: 
        score = min(score + 82, 99) 
    elif req.montant > 15000: 
        score = min(score + 53, 75) 
    
    decision = "BLOQUÉE" if score >= 70 else "SURVEILLANCE" if score >= 40 else "APPROUVÉE"
    ts = datetime.now(timezone.utc).isoformat()
    hash_str = hashlib.sha256(f"{ts}{score}".encode()).hexdigest()[:12]

    # 3. Sauvegarde de la décision dans PostgreSQL
    nouvelle_transaction = TransactionLog(
        hash=hash_str, timestamp=ts, client_id=req.client_id, 
        score_risque=score, decision=decision
    )
    db.add(nouvelle_transaction)
    db.commit()

    # Log console pour debug Docker
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {'🔴' if score >= 70 else '🟡' if score >= 40 else '🟢'} {decision} | ID: {req.client_id} | {req.montant:,.2f}€ | Score {score}")

    return {"score": score, "score_risque": score, "decision": decision}


# ==========================================================
# --- ROUTES : TÉLÉCOMMANDE DU SIMULATEUR ---
# ==========================================================

@app.post("/simulator/start")
def start_simulator():
    global simulator_process
    if simulator_process is not None and simulator_process.poll() is None:
        return {"status": "Simulateur déjà en cours d'exécution."}
    
    # Correction du chemin pour le simulateur (Bazooka Path)
    sim_script_path = os.path.join(BASE_DIR, "Transaction_simulator.py")
    
    # On lance le script
    simulator_process = subprocess.Popen(["python", sim_script_path, "--duration", "36000"])
    
    return {"status": "🚀 Simulateur démarré avec succès !"}

@app.post("/simulator/stop")
def stop_simulator():
    global simulator_process
    if simulator_process is not None and simulator_process.poll() is None:
        simulator_process.terminate()
        simulator_process = None
        return {"status": "🛑 Simulateur arrêté."}
    
    return {"status": "Aucun simulateur en cours."}

@app.get("/simulator/status")
def status_simulator():
    global simulator_process
    is_running = simulator_process is not None and simulator_process.poll() is None
    return {"is_running": is_running}

# ==========================================================

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    