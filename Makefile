api:
	cd apps/api && source .venv/bin/activate && uvicorn main:app --reload --port 8000

test-api:
	cd apps/api && source .venv/bin/activate && pytest -q