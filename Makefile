.PHONY: env setup lint test run-api run-dashboard clean

# 1) Create the environment from environment.yaml
env:
	conda env create -f environment.yaml || conda env update -f environment.yaml --prune

# 2) Setup project tools (requires env already created)
setup:
	conda run -n smart-iiot pre-commit install

# 3) Quality checks
lint:
	conda run -n smart-iiot black .
	conda run -n smart-iiot isort .
	conda run -n smart-iiot flake8 .
	conda run -n smart-iiot bandit -r src/ api/

# 4) Run all tests
test:
	conda run -n smart-iiot pytest tests/

# 5) Run FastAPI backend
run-api:
	conda run -n smart-iiot uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 6) Run Streamlit Dashboard
run-dashboard:
	conda run -n smart-iiot streamlit run dashboard/app.py

# 7) Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
