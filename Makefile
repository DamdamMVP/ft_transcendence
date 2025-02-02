NAME = ft_transcendence
# Par défaut, l'environnement est "dev" (développement). Pour la production, utilisez ENV=prod.
ENV ?= dev

# Si l'environnement est prod, on charge le fichier d'override production.
ifeq ($(ENV),prod)
  DC = docker-compose -f docker-compose.yml -f docker-compose.prod.yml
else
  DC = docker-compose -f docker-compose.yml
endif

all: build

build:
	@echo "Building Docker containers for $(ENV) environment..."
	$(DC) up --build

up:
	@echo "Starting Docker containers for $(ENV) environment..."
	$(DC) up -d

down:
	@echo "Stopping Docker containers for $(ENV) environment..."
	$(DC) down

clean: down
	@echo "Cleaning project containers and images for $(ENV) environment..."
	$(DC) down --rmi local

fclean: down
	@echo "Full cleanup for $(ENV) environment..."
	$(DC) down -v --rmi all
	@echo "Cleaning media folder..."
	find backend/media -type f ! -name 'default.jpg' -delete

re: fclean build
	@echo "Waiting for database to be ready..."
	sleep 5
	@echo "Applying migrations..."
	$(DC) exec -T djangoapp python manage.py migrate

ps:
	$(DC) ps

logs:
	$(DC) logs

db:
	@echo "Connecting to database..."
	$(DC) exec db psql -U postgres

# Cibles pour lancer en production ou en développement
prod:
	$(MAKE) ENV=prod all

dev:
	$(MAKE) ENV=dev all

.PHONY: all build up down clean fclean re ps logs db prod dev
