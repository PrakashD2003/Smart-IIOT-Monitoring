.PHONY: env setup setup-dashboard lint test run-api run-dashboard run-all clean help

# Default target
help:
	@echo "Smart IIoT Monitoring System - Makefile Commands"
	@echo "================================================"
	@echo "  make install-all    - Complete setup (env + dashboard dependencies)"
	@echo "  make env            - Create/update conda environment"
	@echo "  make setup          - Setup Python tools (pre-commit)"
	@echo "  make setup-dashboard - Install Node.js dependencies for dashboard"
	@echo "  make lint           - Run Python code quality checks"
	@echo "  make test           - Run Python tests"
	@echo "  make run-api        - Start FastAPI backend server (port 8000)"
	@echo "  make run-dashboard  - Start React dashboard dev server (port 5173)"
	@echo "  make run-all        - Start both API and dashboard concurrently"
	@echo "  make clean          - Clean Python cache files"
	@echo "  make clean-all      - Clean Python cache and node_modules"

# 1) Complete installation - sets up everything
install-all: env setup setup-dashboard
	@echo "✓ Complete setup finished!"
	@echo "  Run 'make run-api' in one terminal and 'make run-dashboard' in another"
	@echo "  Or use 'make run-all' to start both services"

# 2) Create the environment from environment.yaml
env:
	@echo "Creating/updating conda environment..."
	conda env create -f environment.yaml || conda env update -f environment.yaml --prune
	@echo "✓ Conda environment ready!"

# 3) Setup project tools (requires env already created)
setup:
	@echo "Setting up Python tools..."
	conda run -n smart-iiot pre-commit install
	@echo "✓ Python tools setup complete!"

# 4) Setup Node.js dependencies for React dashboard
setup-dashboard:
	@echo "Setting up dashboard dependencies..."
	@if ! command -v node >/dev/null 2>&1; then \
		echo "ERROR: Node.js is not installed. Please install Node.js (v18+) from https://nodejs.org/"; \
		exit 1; \
	fi
	@if ! command -v npm >/dev/null 2>&1; then \
		echo "ERROR: npm is not installed. Please install Node.js (v18+) from https://nodejs.org/"; \
		exit 1; \
	fi
	cd dashboard && npm install
	@echo "✓ Dashboard dependencies installed!"

# 5) Quality checks
lint:
	conda run -n smart-iiot black .
	conda run -n smart-iiot isort .
	conda run -n smart-iiot flake8 .
	conda run -n smart-iiot bandit -r src/ api/

# 6) Run all tests
test:
	conda run -n smart-iiot pytest tests/

# 7) Run FastAPI backend
run-api:
	@echo "Starting FastAPI backend on http://localhost:8000"
	conda run -n smart-iiot uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 8) Run React Dashboard (Vite dev server)
run-dashboard:
	@echo "Starting React dashboard on http://localhost:5173"
	cd dashboard && npm run dev

# 9) Run both API and Dashboard concurrently (requires 'make' with job server)
run-all:
	@echo "Starting both API and Dashboard..."
	@echo "API will run on http://localhost:8000"
	@echo "Dashboard will run on http://localhost:5173"
	@$(MAKE) -j2 run-api run-dashboard

# 10) Cleanup Python cache
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "✓ Python cache cleaned!"

# 11) Clean everything including node_modules
clean-all: clean
	rm -rf dashboard/node_modules
	rm -rf dashboard/.vite
	rm -rf dashboard/dist
	@echo "✓ All cache and dependencies cleaned!"
