NAME = ft_transcendence

all: build

build:
	@echo "Building Docker containers..."
	docker-compose up --build

up:
	@echo "Starting Docker containers..."
	docker-compose up -d

down:
	@echo "Stopping Docker containers..."
	docker-compose down

clean: down
	@echo "Cleaning project containers and images..."
	docker-compose down --rmi local

fclean:
	@echo "Full cleanup..."
	docker-compose down -v --rmi all
	@echo "Cleaning media folder..."
	find backend/media -type f ! -name 'default.jpg' -delete

re: fclean all
	@echo "Waiting for database to be ready..."
	sleep 5
	@echo "Applying migrations..."
	docker-compose exec -T djangoapp python manage.py migrate

ps:
	docker-compose ps

logs:
	docker-compose logs

db:
	@echo "Connecting to database..."
	docker-compose exec db psql -U postgres

.PHONY: all build up down clean fclean re ps logs db