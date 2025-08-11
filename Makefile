DC=docker compose -f docker-compose.dev.yml

.PHONY: dev dev-up dev-down dev-restart logs backend frontend

dev:
	$(DC) up --build

dev-up:
	$(DC) up -d --build

dev-down:
	$(DC) down

dev-restart:
	$(DC) restart

logs:
	$(DC) logs -f

backend:
	$(DC) up -d --build backend

frontend:
	$(DC) up -d --build frontend
