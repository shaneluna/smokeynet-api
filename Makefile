.DEFAULT_GOAL := dev
SHELL = /bin/sh

.PHONY: dev
dev:
	@echo "Starting uvicorn main:app..."
	. .env && \
	export SYNOPTIC_TOKEN=$$SYNOPTIC_TOKEN && \
	uvicorn main:app --reload --host=0.0.0.0 --port=8000

.PHONY: build
build:
	docker build -t wifire/smokeynet-api .

.PHONY: run
run:
	docker run -p 8000:8000 --env-file .env wifire/smokeynet-api