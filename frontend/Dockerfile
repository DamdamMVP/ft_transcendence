# Stage de build
FROM node:18-alpine as build-stage

# Définition du répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY package*.json ./

# Installation des dépendances
RUN npm install

# Copie du code source
COPY . .

# Build de l'application
RUN npm run build

# Stage de production
FROM nginx:stable-alpine as production-stage

# Copie du build depuis l'étape précédente
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Exposition du port 80
EXPOSE 80

# Démarrage de nginx
CMD ["nginx", "-g", "daemon off;"]
