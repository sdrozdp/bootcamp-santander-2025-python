# Makefile for managing the workout API project
run:
	@poetry run uvicorn workout_api.main:app --reloadpoetry run uvicorn workout_api.main:app --reload --host

create.migrations:
	@PYTHONPATH=$$PYTHONPATH:$(pwd) poetry run alembic revision --autogenerate -m "$(d)"

run.migrations:
	@PYTHONPATH=$$PYTHONPATH:$(pwd) poetry run alembic upgrade head
