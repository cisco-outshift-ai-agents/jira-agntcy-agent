unamestr := $(shell uname)

AGENT_NAME := jira

ROOT_DIR := $(shell pwd)

# Define ${docker} as docker or podman based on availability
docker := $(shell command -v docker >/dev/null 2>&1 && echo docker || echo podman)

# .env is the build artifact of this step, so name the target so that make can do what make does.
.env:
	@echo "Checking if .env file exists..."
	@if [ ! -f ".env" ]; then \
		echo ".env file does not exist. Please create it before proceeding."; \
		exit 1; \
	fi

deps: PYTHON-exists CARGO-exists
.PHONY: deps PYTHON-exists CARGO-exists .env LANGGRAPH-exists RUFF-exists
# Check if the required dependencies are installed
PYTHON-exists: ; @which python3 > /dev/null
# The uuid_utils package is written in rust and requires cargo to build.
CARGO-exists: ; @which cargo > /dev/null
LANGGRAPH-exists: ; @which langgraph > /dev/null
RUFF-exists: ; @which ruff > /dev/null

venv/bin/activate:
	@echo "Setting up virtual environment..."
	@if [ ! -d "venv" ]; then \
		python3 -m venv venv; \
	fi
	@echo "Activating virtual environment and installing requirements..."
	. venv/bin/activate && pip install -r requirements.txt

run: .env venv/bin/activate
	@echo "Running the application with Uvicorn reload on port 8125..."
	. venv/bin/activate && export PYTHONPATH=$PYTHONPATH:$(ROOT_DIR)/src && python src/main.py

docker-build:
	${docker} build --platform linux/amd64 -t ${AGENT_NAME}-agent:dev -f ./Dockerfile  .

run-docker-local: .env
	${docker} run -it \
		--env-file=.env \
		-e ALLOWED_ORIGINS=* \
		-e LANGGRAPH_CHECKPOINT_MEMORY_SAVER=memory \
		-p 8125:8125 \
		-v $(shell pwd)/src:/home/src \
		-v $(shell pwd)/.dockerconfigjson:/home/app/.dockerconfigjson \
		jira-agent:dev \
    python3 ./src/main.py --port 8125

docker-run: .env venv/bin/activate run-docker-local

lint: venv/bin/activate
	@echo "Running ruff..."
	. venv/bin/activate && ruff check src tests

pytest: venv/bin/activate
	@echo "Running pytest..."
	. venv/bin/activate && export PYTHONPATH=app/src && python3 -m pytest tests

test: venv/bin/activate lint run-test

run-test: .env venv/bin/activate
	@echo "Setting up environment variables for tests..."
	echo "Running quick validation tests..." && \
	. venv/bin/activate && \
	DRYRUN=true python3 -m unittest tests.agents.issues.test_prompts_issues && \
	DRYRUN=true python3 -m unittest tests.agents.projects.test_prompts_projects

run-test-dev: .env venv/bin/activate
	@echo "Running dev validation tests..."
	. venv/bin/activate && \
	DEV_TEST=true python3 -m unittest tests.dev.test_prompts_projects_dev

clean:
	echo "" > .env
	${docker} image rm ${AGENT_NAME}-agent:dev

eval: eval-strict

eval-strict: .env venv/bin/activate
	@echo "Running evaluation with LLM and mock Jira responses..."
	. venv/bin/activate && \
	. .env && \
	pip install --upgrade pip setuptools && \
	pip install -r eval/requirements.txt && \
	export PYTHONPATH=$(PWD):$(PWD)/src:$PYTHONPATH && \
	export DRYRUN=true && \
	export LANGSMITH_TRACING=true && \
	python3 -m pytest eval/strict_match/test_strict_match.py

eval-llm-as-judge: .env venv/bin/activate
	@echo "Running Strict Evaluation Tests with Dry-run Enabled..."
	. venv/bin/activate && pip install -r eval/requirements.txt && \
	DRY_RUN=true \
	export PYTHONPATH=$(PWD):$(PWD)/src:$PYTHONPATH && \
	. .env && \
	echo "PYTHONPATH is set to: $(PYTHONPATH)" && \
	python3 eval/llm_as_judge/test_llm_as_judge.py

langgraph-dev: .env venv/bin/activate
	@echo "Running server langgraph dev..."
	export PYTHONPATH=$(PWD):$(PWD)/src && \
	echo "PYTHONPATH is set to: $(PYTHONPATH)" && \
	cd src && \
	langgraph dev

graph-ap: .env venv/bin/activate
	@echo "Running client (agent protocol) langgraph dev..."
	export PYTHONPATH=$(PWD):$(PWD)/src && \
	echo "PYTHONPATH is set to: $(PYTHONPATH)" && \
	cd clients/ap_client && \
	langgraph dev

######################
# HELP
######################

help:
	@echo "Makefile for ${AGENT_NAME} agent"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  deps                Check if required dependencies are installed"
	@echo "  venv/bin/activate   Set up virtual environment and install requirements"
	@echo "  docker-build        Build the Docker image"
	@echo "  run-docker-local    Run the agent locally in Docker"
	@echo "  docker-run          Run the agent in Docker with local source code"
	@echo "  lint                Run linter on the codebase"
	@echo "  pytest              Run tests using pytest"
	@echo "  test                Run linter and tests"
	@echo "  graph-ap            Generate knowledge graph (Langgraph Agent Protocol)"
	@echo "  clean               Clean up Docker images and .env file"
	@echo "  eval                Run evaluation tests"
	@echo "  langgraph-dev       Run langgraph dev command"