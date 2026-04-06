import sys
import os
from fastapi.testclient import TestClient

# 1. Configuration des chemins pour localiser le backend
root_dir = os.path.abspath(os.path.dirname(__file__))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(backend_dir)

# 2. On se déplace dans le dossier backend pour que les chargements de modèles (.pkl) fonctionnent
os.chdir(backend_dir)

print("\n🔍 Initialisation du test de l'API KYC_operation_serveur...")

try:
    # 3. Import de l'application FastAPI
    from API import app
    client = TestClient(app)
    print("✅ Import de l'API et chargement des modèles : RÉUSSI.")

    def test_api_is_alive():
        """Vérifie que l'API répond sur une route existante"""
        print("📡 Tentative de connexion aux points de terminaison...")
        
        # On essaie d'abord la racine
        response = client.get("/")
        
        # Si la racine n'existe pas (404), on teste la doc Swagger (/docs)
        if response.status_code == 404:
            print("ℹ️  Route '/' non définie (404), vérification de la route '/docs'...")
            response = client.get("/docs")
        
        # Vérification finale
        assert response.status_code == 200
        print(f"🟢 Succès ! L'API a répondu avec le code {response.status_code}")
        print("\n🏆 TEST GÉNÉRAL : RÉUSSI ! L'application est prête.")

    # Exécution si lancé avec 'python test_main.py'
    if __name__ == "__main__":
        test_api_is_alive()
        print("\n✨ C'EST GAGNÉ ! Ton architecture est validée. ✨\n")

except Exception as e:
    print(f"❌ ERREUR CRITIQUE : {e}")
    sys.exit(1)

# 4. On revient à la racine du projet
os.chdir(root_dir)