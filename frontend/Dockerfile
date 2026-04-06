FROM python:3.10-slim

# 1. Dossier de travail
WORKDIR /app

# 2. On copie d'abord le requirements pour profiter du cache Docker
COPY requirements.txt .

# 3. Installation des librairies
RUN pip install --no-cache-dir -r requirements.txt

# 4. On copie le reste du code
COPY . .

# Note : Pas de CMD ici, c'est le docker-compose qui pilote