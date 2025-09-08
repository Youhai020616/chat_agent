# Makefile for SEO & GEO Optimization System

# Variables
DOCKER_COMPOSE = docker-compose
BACKEND_DIR = backend
FRONTEND_DIR = frontend
PYTHON = python3
NPM = npm

# Colors
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help
help:
	@echo "$(GREEN)SEO & GEO Optimization System - Available Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Docker Commands:$(NC)"
	@echo "  make up              - Start all services with docker-compose"
	@echo "  make down            - Stop all services"
	@echo "  make restart         - Restart all services"
	@echo "  make logs            - Show logs from all services"
	@echo "  make ps              - Show running services"
	@echo ""
	@echo "$(YELLOW)Backend Commands:$(NC)"
	@echo "  make backend-dev     - Run backend in development mode"
	@echo "  make backend-test    - Run backend tests"
	@echo "  make backend-lint    - Run backend linting"
	@echo "  make backend-format  - Format backend code"
	@echo ""
	@echo "$(YELLOW)Frontend Commands:$(NC)"
	@echo "  make frontend-dev    - Run frontend in development mode"
	@echo "  make frontend-build  - Build frontend for production"
	@echo "  make frontend-test   - Run frontend tests"
	@echo "  make frontend-lint   - Run frontend linting"
	@echo ""
	@echo "$(YELLOW)Database Commands:$(NC)"
	@echo "  make db-migrate      - Run database migrations"
	@echo "  make db-seed         - Seed database with test data"
	@echo "  make db-reset        - Reset database"
	@echo ""
	@echo "$(YELLOW)Utility Commands:$(NC)"
	@echo "  make clean           - Clean up generated files"
	@echo "  make install         - Install all dependencies"
	@echo "  make init            - Initialize project (first time setup)"

# Docker commands
.PHONY: up
up:
	@echo "$(GREEN)Starting all services...$(NC)"
	$(DOCKER_COMPOSE) up -d

.PHONY: down
down:
	@echo "$(YELLOW)Stopping all services...$(NC)"
	$(DOCKER_COMPOSE) down

.PHONY: restart
restart:
	@echo "$(YELLOW)Restarting all services...$(NC)"
	$(DOCKER_COMPOSE) restart

.PHONY: logs
logs:
	$(DOCKER_COMPOSE) logs -f

.PHONY: ps
ps:
	$(DOCKER_COMPOSE) ps

# Backend commands
.PHONY: backend-dev
backend-dev:
	@echo "$(GREEN)Starting backend development server...$(NC)"
	cd $(BACKEND_DIR) && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: backend-test
backend-test:
	@echo "$(GREEN)Running backend tests...$(NC)"
	cd $(BACKEND_DIR) && pytest tests/ -v --cov=.

.PHONY: backend-lint
backend-lint:
	@echo "$(GREEN)Linting backend code...$(NC)"
	cd $(BACKEND_DIR) && flake8 . && mypy .

.PHONY: backend-format
backend-format:
	@echo "$(GREEN)Formatting backend code...$(NC)"
	cd $(BACKEND_DIR) && black . && isort .

# Frontend commands
.PHONY: frontend-dev
frontend-dev:
	@echo "$(GREEN)Starting frontend development server...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) run dev

.PHONY: frontend-build
frontend-build:
	@echo "$(GREEN)Building frontend for production...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) run build

.PHONY: frontend-test
frontend-test:
	@echo "$(GREEN)Running frontend tests...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) test

.PHONY: frontend-lint
frontend-lint:
	@echo "$(GREEN)Linting frontend code...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) run lint

# Database commands
.PHONY: db-migrate
db-migrate:
	@echo "$(GREEN)Running database migrations...$(NC)"
	cd $(BACKEND_DIR) && alembic upgrade head

.PHONY: db-seed
db-seed:
	@echo "$(GREEN)Seeding database...$(NC)"
	cd $(BACKEND_DIR) && $(PYTHON) scripts/seed_db.py

.PHONY: db-reset
db-reset:
	@echo "$(RED)Resetting database...$(NC)"
	cd $(BACKEND_DIR) && alembic downgrade base && alembic upgrade head

# Utility commands
.PHONY: clean
clean:
	@echo "$(YELLOW)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true

.PHONY: install
install:
	@echo "$(GREEN)Installing dependencies...$(NC)"
	cd $(BACKEND_DIR) && pip install -r requirements.txt
	cd $(FRONTEND_DIR) && $(NPM) install

.PHONY: init
init:
	@echo "$(GREEN)Initializing project...$(NC)"
	@echo "$(YELLOW)1. Copying environment files...$(NC)"
	cp $(BACKEND_DIR)/.env.example $(BACKEND_DIR)/.env
	@echo "$(YELLOW)2. Setting up frontend...$(NC)"
	cd $(FRONTEND_DIR) && chmod +x setup.sh && ./setup.sh
	@echo "$(YELLOW)3. Starting services...$(NC)"
	$(DOCKER_COMPOSE) up -d postgres redis rabbitmq
	@echo "$(YELLOW)4. Waiting for services to be ready...$(NC)"
	sleep 10
	@echo "$(YELLOW)5. Running database migrations...$(NC)"
	cd $(BACKEND_DIR) && alembic upgrade head
	@echo "$(GREEN)✅ Project initialized successfully!$(NC)"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit $(BACKEND_DIR)/.env and add your API keys"
	@echo "2. Run 'make up' to start all services"
	@echo "3. Visit http://localhost:3000 for the frontend"
	@echo "4. Visit http://localhost:8000/docs for the API documentation"

# Development shortcuts
.PHONY: dev
dev:
	@echo "$(GREEN)Starting development environment...$(NC)"
	$(MAKE) up
	@echo ""
	@echo "$(GREEN)Services are starting up...$(NC)"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "RabbitMQ: http://localhost:15672 (admin/admin123)"
	@echo "Flower: http://localhost:5555"

.PHONY: stop
stop: down

.PHONY: test
test: backend-test frontend-test

.PHONY: lint
lint: backend-lint frontend-lint

.PHONY: format
format: backend-format
