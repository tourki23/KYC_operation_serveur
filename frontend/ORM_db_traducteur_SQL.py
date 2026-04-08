import os
from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# ==========================================
# --- CONFIGURATION DE LA CONNEXION ---
# ==========================================

# 1. MÉTHODE BAZOOKA POUR LE LOCAL
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")

if os.path.exists(env_path):
    print(f"🔍 Le radar pointe exactement sur ce fichier : {env_path}")
    load_dotenv(env_path)
else:
    print("ℹ️ Aucun fichier .env détecté à la racine. Utilisation des variables système (Docker/Cloud).")

# 2. Récupération et NETTOYAGE de l'URL
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # On enlève les espaces et les guillemets (") ou (') qui font planter SQLAlchemy
    DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'")
else:
    print("⚠️ DATABASE_URL non trouvée, utilisation de l'URL locale par défaut.")
    DATABASE_URL = "postgresql://postgres:dryres1@db:5432/kyc_db"

# --- VÉRIFICATION DE SÉCURITÉ ---
if "neon.tech" in DATABASE_URL:
    print("✅ BINGO ! Connexion au Cloud NEON activée avec succès !")
else:
    print("🔗 Connexion établie sur la base de données locale ou Docker.")

# 3. Création du moteur SQLAlchemy
# On ajoute pool_pre_ping pour éviter les déconnexions intempestives avec le Cloud
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ==========================================
# --- DÉFINITION DES TABLES (MODÈLES) ---
# ==========================================

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