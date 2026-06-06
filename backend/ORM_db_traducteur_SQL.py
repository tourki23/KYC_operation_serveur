import os
from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. On cherche la variable d'environnement (configurée sur GitHub ou Render)
# Si elle n'existe pas, on bascule automatiquement sur SQLite (mode test)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Mode Production : On utilise ta vraie URL
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    # Mode Test / CI : On utilise SQLite en mémoire
    print("⚠️ Mode Test/Offline détecté : utilisation de SQLite.")
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- TES CLASSES RESTENT IDENTIQUES ---
class Client(Base):
    __tablename__ = "clients"
    client_id = Column(String, primary_key=True)
    age = Column(Integer)
    # ... (le reste de tes colonnes)
    sexe = Column(String)
    pays_residence = Column(String)
    nationalite = Column(String)
    secteur_activite = Column(String)
    type_compte = Column(String)
    date_ouverture = Column(String)
    revenu_annuel = Column(Float)
    solde_moyen = Column(Float)
    anciennete_compte = Column(Integer)
    est_ppe = Column(String)
    pays_risque = Column(Integer)
    profil_risque = Column(String)
    score_risque_reel = Column(Integer)
    nb_comptes_lies = Column(Integer)
    litige_anterieur = Column(String)
    kyc_valide = Column(String)
    nb_transactions = Column(Integer)
    montant_moyen = Column(Float)
    montant_max = Column(Float)
    montant_total = Column(Float)
    montant_std = Column(Float)
    montant_median = Column(Float)
    nb_internationales = Column(Integer)
    nb_pays_risques = Column(Integer)
    nb_virements_intl = Column(Integer)
    nb_crypto = Column(Integer)
    nb_retraits = Column(Integer)
    nb_smurfing = Column(Integer)
    jours_actif = Column(Integer)
    velocite_tx_par_jour = Column(Float)
    ratio_international = Column(Float)
    ratio_smurfing = Column(Float)
    ratio_crypto = Column(Float)
    ratio_intl_risque = Column(Float)
    pays_residence_risque = Column(Integer)

class TransactionLog(Base):
    __tablename__ = "transactions_history"
    hash = Column(String, primary_key=True)
    timestamp = Column(String)
    client_id = Column(String)
    score_risque = Column(Integer)
    decision = Column(String)
