@app.post("/score")
def scorer_transaction(req: TransactionRequest, db = Depends(get_db)):
    feat = {f: 0.0 for f in FEATURES}
    
    # 1. Lecture du profil client via PostgreSQL
    client_record = db.query(Client).filter(Client.client_id == str(req.client_id)).first()
    
    if client_record:
        client_dict = client_record.__dict__
        
        # Mappings pour transformer le texte en nombre (A AJUSTER SELON TON MODELE)
        secteur_map = {"Commerce": 1.0, "Banque": 2.0, "Industrie": 3.0, "Services": 4.0}
        type_map = {"Courant": 1.0, "Epargne": 0.0}

        for f in FEATURES:
            if f == "secteur_encode":
                # On mappe le texte de la base vers le chiffre attendu
                valeur_texte = client_dict.get('secteur_activite')
                feat[f] = float(secteur_map.get(valeur_texte, 0.0))
            
            elif f == "type_compte_encode":
                # On mappe le texte de la base vers le chiffre attendu
                valeur_texte = client_dict.get('type_compte')
                feat[f] = float(type_map.get(valeur_texte, 0.0))
                
            elif f in client_dict and client_dict[f] is not None: 
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
