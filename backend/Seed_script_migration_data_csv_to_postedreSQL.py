import os
import pandas as pd
from ORM_db_traducteur_SQL import SessionLocal, Client, engine, Base

# ==========================================
# --- GESTION DU CHEMIN DU FICHIER CSV ---
# ==========================================

# On récupère le dossier où se trouve ce script (le dossier 'backend')
DOSSIER_BACKEND = os.path.dirname(os.path.abspath(__file__))

# On construit le chemin vers le fichier CSV de manière "blindée"
CHEMIN_CSV = os.path.join(DOSSIER_BACKEND, "data", "clients_static.csv")

# ==========================================
# --- LOGIQUE D'IMPORTATION ---
# ==========================================

# 1. On s'assure que les tables vides sont bien créées dans PostgreSQL (Neon)
Base.metadata.create_all(bind=engine)

def importer_clients():
    db = SessionLocal()
    try:
        # 2. Sécurité : On compte combien de clients sont déjà dans la table
        nb_clients = db.query(Client).count()
        if nb_clients > 0:
            print(f"⚠️ La base contient déjà {nb_clients} clients. Importation annulée pour éviter les doublons.")
            return

        print(f"⏳ Lecture du fichier CSV : {CHEMIN_CSV}")
        
        # On utilise le chemin absolu qu'on a calculé plus haut
        df = pd.read_csv(CHEMIN_CSV)

        print("🚀 Importation dans PostgreSQL (Neon Cloud) en cours...")
        
        # 3. On boucle sur chaque ligne du CSV
        for index, row in df.iterrows():
            nouveau_client = Client(
                client_id=str(row['client_id']),
                age=float(row['age']),
                revenu_annuel=float(row['revenu_annuel']),
                solde_moyen=float(row['solde_moyen']),
                profil_risque=str(row['profil_risque']),
                nationalite=str(row['nationalite']),
                pays_residence=str(row['pays_residence']),
                secteur_activite=str(row['secteur_activite']),
                type_compte=str(row['type_compte'])
            )
            db.add(nouveau_client)

        # 4. On valide l'envoi global vers la base de données
        db.commit()
        print(f"✅ Succès ! {len(df)} clients ont été insérés dans le Cloud Neon.")

    except Exception as e:
        db.rollback() 
        print(f"❌ Erreur lors de l'importation : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    importer_clients()