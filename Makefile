.DEFAULT_GOAL := start
SHELL = /bin/sh

start:
	@echo "Starting uvicorn main:app..."
	uvicorn main:app --reload --host=0.0.0.0 --port=8000