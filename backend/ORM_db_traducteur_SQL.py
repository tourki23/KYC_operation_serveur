import os
from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# ... (Garde la logique de connexion DATABASE_URL intacte) ...

Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"
    # NE GARDER QUE LE STRICT MINIMUM NÉCESSAIRE AU MODÈLE ET À L'AFFICHAGE
    client_id = Column(String, primary_key=True)
    # Les colonnes dont le modèle a besoin pour tourner sans crash
    age = Column(Float)
    revenu_annuel = Column(Float)
    solde_moyen = Column(Float)
    # AJOUTE UNIQUEMENT LES COLONNES QUE TU VEUX VRAIMENT AFFICHER
    sexe = Column(String) 
    # ON SUPPRIME date_ouverture et TOUT LE RESTE pour ne plus avoir d'UndefinedColumn
    
class TransactionLog(Base):
    __tablename__ = "transactions_history"
    hash = Column(String, primary_key=True)
    timestamp = Column(String)
    client_id = Column(String)
    score_risque = Column(Integer)
    decision = Column(String)

Base.metadata.create_all(bind=engine)
