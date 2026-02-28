api:
	cd apps/api && ./.venv/bin/python -m uvicorn app.main:app --reload --port 8000

test-api:
	cd apps/api && ./.venv/bin/python -m pytest -q

alembic-init:
	cd apps/api && ./.venv/bin/python -m alembic init alembic

alembic:
	cd apps/api && ./.venv/bin/python -m alembic $(cmd)