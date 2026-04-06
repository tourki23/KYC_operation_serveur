import os
from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from urllib.parse import quote_plus  # Import indispensable pour le symbole $

# --- CONFIGURATION DE LA CONNEXION ---

# 1. Ton mot de passe brut (mets bien ton mot de passe avec le $)
raw_password = "dryres1" 

# 2. Encodage du mot de passe pour qu'il soit lisible dans l'URL
# Le symbole $ sera transformé en %24 automatiquement
encoded_password = quote_plus(raw_password)

# 3. Construction de l'URL avec l'IP de ton Windows (WSL Gateway)


DATABASE_URL = f"postgresql://postgres:{encoded_password}@db:5432/kyc_db"

# 4. Création du moteur SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- DÉFINITION DES TABLES (MODÈLES) ---

# La table Clients (Anciennement clients_static.csv)
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

# La table Transactions (Anciennement transactions_history.csv)
class TransactionLog(Base):
    __tablename__ = "transactions_history"
    
    hash = Column(String, primary_key=True)
    timestamp = Column(String)
    client_id = Column(String)
    score_risque = Column(Integer)
    decision = Column(String)