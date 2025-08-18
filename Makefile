# Makefile for Semantic Segmentation App
# Supports both local development and CI/CD environments

# Default values
DOCKER_IMAGE_NAME ?= semantic-segmentation-app
DOCKER_TAG ?= latest
CONTAINER_NAME ?= semantic-segmentation-container
PORT ?= 8501
REGISTRY ?=

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Helper functions
define print_status
	@echo -e "$(BLUE)[INFO]$(NC) $1"
endef

define print_success
	@echo -e "$(GREEN)[SUCCESS]$(NC) $1"
endef

define print_warning
	@echo -e "$(YELLOW)[WARNING]$(NC) $1"
endef

define print_error
	@echo -e "$(RED)[ERROR]$(NC) $1"
endef

# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help: ## Show this help message
	@echo "Semantic Segmentation App - Makefile"
	@echo "====================================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "Environment Variables:"
	@echo "  DOCKER_IMAGE_NAME    Docker image name (default: semantic-segmentation-app)"
	@echo "  DOCKER_TAG          Docker tag (default: latest)"
	@echo "  CONTAINER_NAME      Container name (default: semantic-segmentation-container)"
	@echo "  PORT                Port mapping (default: 8501)"
	@echo "  REGISTRY            Docker registry prefix (for ECR)"
	@echo ""
	@echo "Examples:"
	@echo "  make build                    # Build Docker image"
	@echo "  make run                      # Run container"
	@echo "  make build-run                # Build and run"
	@echo "  make stop                     # Stop container"
	@echo "  make logs                     # Show container logs"
	@echo "  make clean                    # Clean up everything"

# Development targets
.PHONY: build
build: ## Build Docker image
	$(call print_status,Building Docker image...)
	@chmod +x scripts/build-and-run.sh
	@./scripts/build-and-run.sh build

.PHONY: run
run: ## Run Docker container
	$(call print_status,Running Docker container...)
	@chmod +x scripts/build-and-run.sh
	@./scripts/build-and-run.sh run

.PHONY: build-run
build-run: ## Build and run Docker container (default)
	$(call print_status,Building and running Docker container...)
	@chmod +x scripts/build-and-run.sh
	@./scripts/build-and-run.sh build-run

.PHONY: stop
stop: ## Stop and remove Docker container
	$(call print_status,Stopping Docker container...)
	@chmod +x scripts/build-and-run.sh
	@./scripts/build-and-run.sh stop

.PHONY: logs
logs: ## Show container logs
	$(call print_status,Showing container logs...)
	@chmod +x scripts/build-and-run.sh
	@./scripts/build-and-run.sh logs

.PHONY: status
status: ## Show container status
	$(call print_status,Showing container status...)
	@chmod +x scripts/build-and-run.sh
	@./scripts/build-and-run.sh status

# DVC targets
.PHONY: dvc-setup
dvc-setup: ## Set up DVC with S3
	$(call print_status,Setting up DVC with S3...)
	@chmod +x scripts/setup-dvc.sh
	@./scripts/setup-dvc.sh

.PHONY: dvc-push
dvc-push: ## Push data to S3
	$(call print_status,Pushing data to S3...)
	@dvc push

.PHONY: dvc-pull
dvc-pull: ## Pull data from S3
	$(call print_status,Pulling data from S3...)
	@dvc pull

.PHONY: dvc-status
dvc-status: ## Show DVC status
	$(call print_status,Showing DVC status...)
	@dvc status

# Testing targets
.PHONY: test
test: ## Run tests
	$(call print_status,Running tests...)
	@pytest tests/ -v

.PHONY: test-coverage
test-coverage: ## Run tests with coverage
	$(call print_status,Running tests with coverage...)
	@pytest tests/ --cov=app --cov-report=term-missing --cov-report=html:htmlcov --cov-fail-under=40

.PHONY: test-html
test-html: ## Run tests with HTML report
	$(call print_status,Running tests with HTML report...)
	@pytest tests/ --html=test-report.html --self-contained-html

# Code quality targets
.PHONY: lint
lint: ## Run linting
	$(call print_status,Running linting...)
	@flake8 app/ tests/ --max-line-length=88 --extend-ignore=E203,W503

.PHONY: format
format: ## Format code
	$(call print_status,Formatting code...)
	@black app/ tests/
	@isort app/ tests/

.PHONY: format-check
format-check: ## Check code formatting
	$(call print_status,Checking code formatting...)
	@black --check app/ tests/
	@isort --check-only app/ tests/

.PHONY: security-scan
security-scan: ## Run security scan
	$(call print_status,Running security scan...)
	@bandit -r app/ -f json -o bandit-report.json

.PHONY: type-check
type-check: ## Run type checking
	$(call print_status,Running type checking...)
	@mypy app/ --ignore-missing-imports

.PHONY: quality-check
quality-check: ## Run all quality checks
	$(call print_status,Running quality checks...)
	@make lint
	@make format-check
	@make test-coverage
	@make security-scan

.PHONY: quick-quality
quick-quality: ## Quick quality check (without tests)
	$(call print_status,Running quick quality check...)
	@make lint
	@make format-check
	@make security-scan

.PHONY: full-quality
full-quality: ## Full quality check with tests
	$(call print_status,Running full quality check...)
	@make quality-check
	@make test-html

.PHONY: test-local
test-local: ## Test local Streamlit app
	$(call print_status,Testing local Streamlit app...)
	@source env/bin/activate && streamlit run app.py --server.headless true --server.port 8502 &
	@sleep 10
	@curl -f http://localhost:8502/_stcore/health || (echo "Health check failed" && exit 1)
	@pkill -f "streamlit run app.py" || true
	$(call print_success,Local test completed successfully)

# CI/CD targets
.PHONY: ci-build
ci-build: ## Build for CI/CD (uses GitHub secrets)
	$(call print_status,Building for CI/CD...)
	@chmod +x scripts/build-and-run.sh
	@GITHUB_ACTIONS=true ./scripts/build-and-run.sh build

.PHONY: ci-deploy
ci-deploy: ## Deploy for CI/CD
	$(call print_status,Deploying for CI/CD...)
	@chmod +x scripts/deploy.sh
	@./scripts/deploy.sh

# Utility targets
.PHONY: clean
clean: ## Clean up Docker containers and images
	$(call print_status,Cleaning up Docker resources...)
	@docker stop $(CONTAINER_NAME) 2>/dev/null || true
	@docker rm $(CONTAINER_NAME) 2>/dev/null || true
	@docker rmi $(DOCKER_IMAGE_NAME):$(DOCKER_TAG) 2>/dev/null || true
	@docker system prune -f
	$(call print_success,Cleanup completed)

.PHONY: clean-test
clean-test: ## Clean up test artifacts
	$(call print_status,Cleaning up test artifacts...)
	@rm -rf htmlcov/
	@rm -rf .pytest_cache/
	@rm -rf __pycache__/
	@rm -rf app/__pycache__/
	@rm -rf tests/__pycache__/
	@rm -f .coverage
	@rm -f coverage.xml
	@rm -f test-report.html
	@rm -f bandit-report.json
	$(call print_success,Test artifacts cleaned)

.PHONY: clean-all
clean-all: ## Clean up everything including data and test artifacts
	$(call print_status,Cleaning up everything...)
	@make clean
	@make clean-test
	@rm -rf .dvc/cache
	@rm -f *.dvc
	$(call print_success,Complete cleanup finished)



.PHONY: info
info: ## Show build information
	$(call print_status,Build Information:)
	@echo "  Image Name: $(DOCKER_IMAGE_NAME)"
	@echo "  Tag: $(DOCKER_TAG)"
	@echo "  Container: $(CONTAINER_NAME)"
	@echo "  Port: $(PORT)"
	@echo "  Registry: $(REGISTRY)"
	@echo ""
	$(call print_status,Environment:)
	@if [ -f ".env/.env" ]; then \
		echo "  .env file: Found"; \
		echo "  S3 Bucket: $$(grep DVC_S3_BUCKET .env/.env | cut -d'=' -f2)"; \
	else \
		echo "  .env file: Not found"; \
	fi
	@echo ""
	$(call print_status,Docker Status:)
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep $(CONTAINER_NAME) || echo "  Container not running"

.PHONY: shell
shell: ## Open shell in running container
	$(call print_status,Opening shell in container...)
	@docker exec -it $(CONTAINER_NAME) /bin/bash

.PHONY: restart
restart: ## Restart container
	$(call print_status,Restarting container...)
	@make stop
	@make run

# Development workflow
.PHONY: dev
dev: ## Development workflow: setup, build, run
	$(call print_status,Starting development workflow...)
	@make dvc-setup
	@make build-run
	$(call print_success,Development environment ready!)

.PHONY: dev-stop
dev-stop: ## Stop development environment
	$(call print_status,Stopping development environment...)
	@make stop
	$(call print_success,Development environment stopped)

# Production targets
.PHONY: prod-build
prod-build: ## Build production image
	$(call print_status,Building production image...)
	@DOCKER_TAG=production make build

.PHONY: prod-run
prod-run: ## Run production container
	$(call print_status,Running production container...)
	@DOCKER_TAG=production make run

# Monitoring targets
.PHONY: monitor
monitor: ## Monitor container resources
	$(call print_status,Monitoring container resources...)
	@docker stats $(CONTAINER_NAME)

.PHONY: health
health: ## Check container health
	$(call print_status,Checking container health...)
	@curl -f http://localhost:$(PORT)/_stcore/health || (echo "Health check failed" && exit 1)
	$(call print_success,Container is healthy)

# Documentation targets
.PHONY: docs
docs: ## Generate documentation
	$(call print_status,Generating documentation...)
	@echo "# Semantic Segmentation App" > docs/README.md
	@echo "" >> docs/README.md
	@echo "## Build Information" >> docs/README.md
	@echo "- Image: $(DOCKER_IMAGE_NAME):$(DOCKER_TAG)" >> docs/README.md
	@echo "- Container: $(CONTAINER_NAME)" >> docs/README.md
	@echo "- Port: $(PORT)" >> docs/README.md
	$(call print_success,Documentation generated)

# Install dependencies
.PHONY: install
install: ## Install development dependencies
	$(call print_status,Installing dependencies...)
	@pip install -r requirements.txt
	@pip install dvc[s3]
	$(call print_success,Dependencies installed)

# Setup project
.PHONY: setup
setup: ## Initial project setup
	$(call print_status,Setting up project...)
	@make install
	@make dvc-setup
	@make build-run
	$(call print_success,Project setup completed!)