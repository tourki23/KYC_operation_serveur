import pandas as pd
from ORM_db_traducteur_SQL import SessionLocal, Client, engine, Base

# 1. On s'assure que les tables vides sont bien créées dans PostgreSQL
Base.metadata.create_all(bind=engine)

def importer_clients():
    db = SessionLocal()
    try:
        # 2. Sécurité : On compte combien de clients sont déjà dans la table
        nb_clients = db.query(Client).count()
        if nb_clients > 0:
            print(f"⚠️ La base contient déjà {nb_clients} clients. Importation annulée pour éviter les doublons.")
            return

        print("⏳ Lecture du fichier CSV local...")
        # Assure-toi que le chemin pointe bien vers ton dossier "data"
        df = pd.read_csv("data/clients_static.csv")

        print("🚀 Importation dans PostgreSQL en cours...")
        
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
                # (Si tu as d'autres colonnes dans la classe Client de ton ORM, ajoute-les ici)
            )
            # On donne la traduction à SQLAlchemy
            db.add(nouveau_client)

        # 4. On valide l'envoi global vers la base de données
        db.commit()
        print(f"✅ Succès ! {len(df)} clients ont été insérés dans PostgreSQL.")
        print("🗑️ Vous pouvez maintenant vous passer du fichier clients_static.csv !")

    except Exception as e:
        db.rollback() # En cas de crash, on annule tout pour ne pas corrompre la base
        print(f"❌ Erreur lors de l'importation : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    importer_clients()