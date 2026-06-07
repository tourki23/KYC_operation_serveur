import os
from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# 1. Chargement critique du fichier .env
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# 2. Logique de connexion robuste
if os.getenv("GITHUB_ACTIONS") == "true":
    DATABASE_URL = "sqlite:///:memory:"
    print("🚀 MODE TEST : SQLite en mémoire")
else:
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'")
        print("🌐 MODE PROD : Connexion PostgreSQL activée")
    else:
        print("⚠️ DATABASE_URL non trouvée ! Passage en mode SQLite.")
        DATABASE_URL = "sqlite:///:memory:"

# 3. Création du moteur
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. Modèles (Colonne 'sexe' retirée)
class Client(Base):
    __tablename__ = "clients"
    client_id = Column(String, primary_key=True)
    age = Column(Float)
    revenu_annuel = Column(Float)
    solde_moyen = Column(Float)
    profil_risque = Column(String)
    nationalite = Column(String)
    pays_residence = Column(String)
    secteur_activite = Column(String)
    type_compte = Column(String)
    # sexe = Column(String)  <-- RETIRÉ
    date_ouverture = Column(String)
    anciennete_compte = Column(Integer)
    est_ppe = Column(String)
    pays_risque = Column(Integer)
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

# Synchronisation finale
Base.metadata.create_all(bind=engine)
