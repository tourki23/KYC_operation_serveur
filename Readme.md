🛡️ KYC - Operations Center V3 (Cloud & Live Simulation)
Un centre d'opérations anti-fraude complet (Know Your Customer) bâti sur une architecture microservices. Il intègre un flux de transactions en temps réel, un moteur de scoring IA et une base de données Serverless.

🌟 Présentation du projet
Ce projet reproduit le système nerveux central d'une institution financière moderne. Il permet aux équipes d'investigation (Ops) de surveiller les transactions en direct, d'analyser les profils clients à 360° et d'auditer les décisions de blocage grâce à une interface fluide et un registre sécurisé.

🏗️ Architecture Technique (Stack)
L'application est découpée en microservices pour garantir des performances optimales et un déploiement cloud facilité :

🎨 Frontend (Dashboard) : Plotly Dash & Dash Bootstrap Components (Thème Cyborg). Interface réactive "Full Black" sans bordures.

⚙️ Backend (API & Simulateur) : FastAPI (Python) gérant la logique métier, le scoring IA et la génération de flux de données continus.

🗄️ Base de données (Cloud) : PostgreSQL hébergée sur Neon.tech (Serverless), assurant une disponibilité 24/7 et supprimant le besoin de stockage local.

ORM : SQLAlchemy pour des requêtes sécurisées vers le Cloud.

🐳 Orchestration : Docker & Docker Compose pour un déploiement "Zero-Config" en local comme en production.

🚀 Guide de Démarrage Rapide
Déployez l'application sur votre machine en quelques minutes.

1. Prérequis
Docker Desktop installé et lancé.

Git installé.

2. Installation
Ouvrez votre terminal et clonez le dépôt :

Bash
git clone <URL_DE_VOTRE_DEPOT_GITHUB>
cd kyc-project-cloud
3. Sécurité et Connexion au Cloud (.env)
Le projet se connecte à une base de données distante sécurisée. Créez un fichier .env à la racine du projet et configurez votre accès :

Plaintext
DATABASE_URL="postgresql://<USER>:<PASSWORD>@<URL_NEON>/neondb?sslmode=require"
(Note : Le fichier .env est volontairement ignoré par Git pour des raisons de sécurité).

4. Lancement de l'infrastructure
Construisez les images Docker et lancez l'API et l'UI en arrière-plan :

Bash
docker compose up --build -d
5. Migration Initiale (Data Seeding)
Au premier lancement, peuplez la base de données Cloud avec les 1000 profils clients initiaux en exécutant ce script :

Bash
docker compose exec api python Seed_script_migration_data_csv_to_postedreSQL.py
🕹️ Utilisation et Fonctionnalités
Une fois les services lancés, ouvrez votre navigateur :

📊 Dashboard KYC : http://localhost:8053

⚙️ Documentation API (Swagger) : http://localhost:8000/docs

🔥 Le Moteur de Simulation Live
C'est le cœur interactif du projet.

Allez sur le Dashboard, onglet "📊 MONITORING LIVE".

Cliquez sur "▶️ START SIMULATION".

L'API va instantanément générer un flux de nouvelles transactions (virements offshore, retraits crypto, etc.). Le moteur de scoring va les classer en temps réel (Approuvée 🟢, Surveillance 🟡, Bloquée 🔴) et animer vos graphiques en direct !

🔍 Vision Client 360 & Audit
Analyse Macro : Répartition des risques (Normal, Suspect, Fraudeur, PPE) et statistiques démographiques.

Ledger d'Audit : Registre immuable des décisions de l'algorithme avec hachage cryptographique pour la traçabilité de conformité.

🛑 Arrêt des services
Pour couper proprement l'application et stopper le réseau Docker :

Bash
docker compose down
👨‍💻 Développé par Mahmoud TOURKI

💼 LinkedIn : Mahmoud Tourki

📧 Email : mahmoud.tourki24@gmail.com