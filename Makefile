# Makefile for AI Blog Explorer
# Usage: make [command]

.PHONY: help dev up down build logs clean test shell db-migrate setup

# Default command
help:
	@echo "Available commands:"
	@echo "  make setup       - Initial setup (install dependencies, build images)"
	@echo "  make dev         - Start all services in development mode"
	@echo "  make up          - Start all services in production mode"
	@echo "  make down        - Stop all services"
	@echo "  make build       - Build all Docker images"
	@echo "  make logs        - View logs from all services"
	@echo "  make clean       - Remove all containers, volumes, and images"
	@echo "  make test        - Run tests"
	@echo "  make shell-[service] - Open shell in service (frontend/backend/postgres)"
	@echo "  make db-migrate  - Run database migrations"
	@echo "  make railway-deploy - Deploy to Railway"

# Initial setup
setup:
	@echo "Setting up AI Blog Explorer..."
	@cp -n .env.example .env || true
	@docker-compose build
	@echo "Setup complete! Run 'make dev' to start development."

# Development mode with hot reload
dev:
	@echo "Starting services in development mode..."
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Development mode in background
dev-bg:
	@echo "Starting services in development mode (background)..."
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "Services started! Run 'make logs' to view logs."

# Production mode
up:
	@echo "Starting services in production mode..."
	@docker-compose up -d
	@echo "Services started! Visit http://localhost:3000"

# Stop all services
down:
	@echo "Stopping all services..."
	@docker-compose down

# Build Docker images
build:
	@echo "Building Docker images..."
	@docker-compose build

# Build specific service
build-%:
	@echo "Building $* service..."
	@docker-compose build $*

# View logs from all services
logs:
	@docker-compose logs -f

# View logs from specific service
logs-%:
	@docker-compose logs -f $*

# Remove all containers, volumes, and images
clean:
	@echo "Cleaning up Docker resources..."
	@docker-compose down -v
	@docker system prune -af
	@echo "Cleanup complete!"

# Run tests
test:
	@echo "Running tests..."
	@docker-compose exec frontend npm test
	@docker-compose exec backend pytest

# Shell access to frontend
shell-frontend:
	@docker-compose exec frontend sh

# Shell access to backend
shell-backend:
	@docker-compose exec backend bash

# Shell access to PostgreSQL
shell-postgres:
	@docker-compose exec postgres psql -U bloguser -d blogdb

# Shell access to Redis
shell-redis:
	@docker-compose exec redis redis-cli

# Run database migrations
db-migrate:
	@echo "Running database migrations..."
	@docker-compose exec frontend npx prisma migrate dev

# Generate Prisma client
db-generate:
	@docker-compose exec frontend npx prisma generate

# Open Prisma Studio
db-studio:
	@docker-compose exec frontend npx prisma studio

# Check service health
health:
	@echo "Checking service health..."
	@curl -s http://localhost:3000/api/health | jq '.' || echo "Frontend not responding"
	@curl -s http://localhost:8000/health | jq '.' || echo "Backend not responding"

# Railway deployment commands
railway-login:
	@railway login

railway-link:
	@railway link

railway-deploy:
	@echo "Deploying to Railway..."
	@railway up

railway-logs:
	@railway logs

railway-status:
	@railway status

# Development tools (optional)
tools:
	@echo "Starting development tools..."
	@docker-compose --profile tools up -d
	@echo "pgAdmin: http://localhost:5050 (admin@blog.local / admin)"
	@echo "Redis Commander: http://localhost:8081"

# Quick restart
restart:
	@make down
	@make dev

# Check Docker and Docker Compose versions
version:
	@docker --version
	@docker-compose --version
	@railway --version 2>/dev/null || echo "Railway CLI not installed"