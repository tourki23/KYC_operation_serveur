import sys
import os
import pytest
from fastapi.testclient import TestClient

# 1. Configuration des chemins pour localiser le backend
root_dir = os.path.abspath(os.path.dirname(__file__))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir) # On ajoute la racine au path

# 2. Import EXPLICITE
try:
    from backend.API import app
    client = TestClient(app)
except Exception as e:
    print(f"❌ ERREUR LORS DE L'IMPORT : {e}")
    sys.exit(1)

def test_api_is_alive():
    """Vérifie que l'API répond"""
    # On teste /health si tu l'as ajouté dans API.py
    response = client.get("/health")
    assert response.status_code == 200
