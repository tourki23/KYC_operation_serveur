import os
from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Configuration de l'engine (C'est ce qui manquait pour corriger la NameError)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 2. Configuration de la session et base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Définition des modèles (SANS les colonnes qui causent des erreurs)
class Client(Base):
    __tablename__ = "clients"
    
    # Uniquement les colonnes strictement nécessaires
    client_id = Column(String, primary_key=True)
    age = Column(Float)
    revenu_annuel = Column(Float)
    solde_moyen = Column(Float)
    anciennete_compte = Column(Integer)

class TransactionLog(Base):
    __tablename__ = "transactions_history"
    hash = Column(String, primary_key=True)
    timestamp = Column(String)
    client_id = Column(String)
    score_risque = Column(Integer)
    decision = Column(String)

# 4. Création des tables
Base.metadata.create_all(bind=engine)
