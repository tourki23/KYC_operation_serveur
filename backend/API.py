import os, pickle, json, hashlib, subprocess
import pandas as pd
from datetime import datetime, timezone
from fastapi import FastAPI, Depends
from pydantic import BaseModel
import uvicorn

# Import de notre base de données
from ORM_db_traducteur_SQL import SessionLocal, Client, TransactionLog

# Chargement artefacts IA
with open("models/kyc_xgboost.pkl", "rb") as f: MODEL = pickle.load(f)
with open("models/scaler.pkl", "rb") as f: SCALER = pickle.load(f)
with open("models/features_list.json", "r") as f: FEATURES = json.load(f)

app = FastAPI()

# --- VARIABLE GLOBALE POUR LE SIMULATEUR ---
# Cette variable va garder en mémoire le "processus" du simulateur
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
                # On s'assure de bien convertir en float pour le modèle
                feat[f] = float(client_dict[f])
    
    if "montant" in feat: 
        feat["montant"] = float(req.montant)

    # 2. Prédiction IA
    df_input = pd.DataFrame([feat])[FEATURES]
    prob = float(MODEL.predict_proba(SCALER.transform(df_input))[0][1])
    score = int(prob * 100)
    
    # Règle métier : On ajoute une pénalité au lieu d'écraser
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

    return {"score": score, "score_risque": score, "decision": decision}


# ==========================================================
# --- ROUTES : TÉLÉCOMMANDE DU SIMULATEUR ---
# ==========================================================

@app.post("/simulator/start")
def start_simulator():
    global simulator_process
    # On vérifie si le simulateur tourne déjà pour ne pas en lancer deux en même temps
    if simulator_process is not None and simulator_process.poll() is None:
        return {"status": "Simulateur déjà en cours d'exécution."}
    
    # On lance le script en arrière-plan (pour 10 heures : 36000 secondes)
    # Assure-toi que "Transaction_simulator.py" est bien dans le même dossier
    simulator_process = subprocess.Popen(["python", "Transaction_simulator.py", "--duration", "36000"])
    
    return {"status": "🚀 Simulateur démarré avec succès !"}

@app.post("/simulator/stop")
def stop_simulator():
    global simulator_process
    # On vérifie s'il y a bien un simulateur à arrêter
    if simulator_process is not None and simulator_process.poll() is None:
        simulator_process.terminate() # On "tue" le processus proprement
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
    uvicorn.run(app, host="0.0.0.0", port=8000)