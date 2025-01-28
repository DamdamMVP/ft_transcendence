# Image de base Node.js
FROM node:20-alpine

# Définition du répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY package*.json ./

# Installation des dépendances
RUN npm install

# Copie du code source
COPY . .

# Exposition du port pour Vite (5173 par défaut)
EXPOSE 5173

# Commande pour lancer le serveur de développement
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]