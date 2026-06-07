import os
from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"
    
    # Clé primaire
    client_id = Column(String, primary_key=True)
    
    # Colonnes identité
    age = Column(Integer)
    sexe = Column(String)
    pays_residence = Column(String)
    nationalite = Column(String)
    
    # Colonnes financières / risque
    revenu_annuel = Column(Float)
    solde_moyen = Column(Float)
    anciennete_compte = Column(Integer)
    profil_risque = Column(String)
    score_risque_reel = Column(Integer)
    
    # Colonnes profilage (pour tes graphiques)
    secteur_activite = Column(String)
    type_compte = Column(String)
    date_ouverture = Column(String)
    est_ppe = Column(String)
    pays_risque = Column(Integer)

class TransactionLog(Base):
    __tablename__ = "transactions_history"
    hash = Column(String, primary_key=True)
    timestamp = Column(String)
    client_id = Column(String)
    score_risque = Column(Integer)
    decision = Column(String)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
