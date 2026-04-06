import os
from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from urllib.parse import quote_plus

# --- CONFIGURATION DYNAMIQUE (BEST PRACTICE) ---

# 1. On récupère les variables d'environnement (si Docker les envoie)
# Sinon, on utilise des valeurs par défaut pour ton test local.
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "dryres1")
DB_HOST = os.getenv("POSTGRES_HOST", "db")  # Par défaut 'db' pour Docker
DB_NAME = os.getenv("POSTGRES_DB", "kyc_db")

# 2. Encodage du mot de passe pour gérer les caractères spéciaux comme $
encoded_password = quote_plus(DB_PASS)

# 3. Construction de l'URL
# Cette URL marchera dans Docker car l'hôte sera "db"
DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:5432/{DB_NAME}"

# 4. Création du moteur SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- DÉFINITION DES TABLES (MODÈLES) ---

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

class TransactionLog(Base):
    __tablename__ = "transactions_history"
    
    hash = Column(String, primary_key=True)
    timestamp = Column(String)
    client_id = Column(String)
    score_risque = Column(Integer)
    decision = Column(String)