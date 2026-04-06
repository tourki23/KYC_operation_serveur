🛡️ KYC - Operations Center V3
Ce projet est une architecture microservices complète (Backend, Frontend, Base de données) conçue pour la surveillance, l'analyse et la détection de fraudes (KYC - Know Your Customer) au sein d'une institution financière (Banque X).

🏗️ Architecture du Projet
L'application est découpée en plusieurs composants isolés pour garantir la scalabilité et la maintenance :

Base de données : PostgreSQL (Conteneur Docker avec volume persistant).

Backend (API) : FastAPI (Python) utilisant SQLAlchemy comme ORM pour la communication avec la base de données.

Frontend (Dashboard) : Plotly Dash + Bootstrap pour une interface interactive et réactive.

Orchestration : Docker Compose pour le déploiement multi-conteneurs simplifié.

🚀 Guide de Démarrage Rapide
Suivez ces étapes pour déployer l'application localement.

Prérequis
Docker & Docker Compose

Git

Étape 1 : Cloner le projet
Ouvrez votre terminal et récupérez le code source :

Bash
git clone <URL_DE_VOTRE_DEPOT_GITHUB>
cd kyc-project-cloud
Étape 2 : Lancer l'infrastructure
Construisez les images et démarrez les services en une seule commande :

Bash
docker compose up --build -d
Docker va automatiquement créer le réseau interne, monter le volume pour la base de données et démarrer les trois services.

Étape 3 : Initialiser les données (Migration)
Une fois les conteneurs opérationnels, lancez le script d'initialisation pour créer les tables SQL et injecter le jeu de données initial (1000 clients) :

Bash
docker compose exec api python Seed_script_migration_data_csv_to_postedreSQL.py
Étape 4 : Utilisation
L'application est maintenant accessible via votre navigateur :

📊 Tableau de Bord : http://localhost:8053

⚙️ API Swagger UI : http://localhost:8000/docs

🛠️ Fonctionnalités Clés
Monitoring Live : Visualisation des flux de transactions et détection automatique des profils suspects.

Vision Client 360 : Analyse détaillée des segments de clientèle par âge, revenu, nationalité et type de compte.

Performance Modèle : Suivi des métriques de l'algorithme de scoring (Précision, Recall, Accuracy, Courbe ROC).

Registre d'Audit : Historique immuable des décisions de blocage/validation avec empreinte (hash).

🛑 Arrêt du système
Pour stopper l'ensemble des services :

Bash
docker compose down
Developed by Mahmoud TOURKI :  
LinkedIn : https://www.linkedin.com/in/mahmoud-tourki-b228b9147/  
Email : mahmoud.tourki24@gmail.com