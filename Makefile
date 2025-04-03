unamestr := $(shell uname)

AGENT_NAME := jira

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

docker-build:
	${docker} build --platform linux/amd64 -t ${AGENT_NAME}-agent:dev -f ./Dockerfile  .

run-docker-local: .env
	${docker} run -it \
		--env-file=.env \
		-e ALLOWED_ORIGINS=* \
		-e LANGGRAPH_CHECKPOINT_MEMORY_SAVER=memory \
		-p 8000:8000 \
		-v $(shell pwd)/src:/home/src \
		-v $(shell pwd)/.dockerconfigjson:/home/app/.dockerconfigjson \
		jarvis-agent:dev \
    python3 ./src/main.py --port 8000

docker-run: .env venv/bin/activate run-docker-local

lint: venv/bin/activate
	@echo "Running ruff..."
	. venv/bin/activate && ruff check app/src tests

pytest: venv/bin/activate
	@echo "Running pytest..."
	. venv/bin/activate && export PYTHONPATH=app/src && python3 -m pytest tests

test: venv/bin/activate lint pytest

graph: .env venv/bin/activate
	@echo "Running make graph..."
	ENABLE_KNOWLEDGE_GRAPH=false \
	venv/bin/dotenv run --no-override venv/bin/python3 app/src/jarvis_agent.py


clean:
	echo "" > .env
	${docker} image rm ${AGENT_NAME}-agent:dev

eval: eval-strict eval-llm-as-judge

eval-strict: .env venv/bin/activate
	@echo "Running Strict Evaluation Tests..."
	export PYTHONPATH=$(PWD):$(PWD)/src:$PYTHONPATH && \
	. .env && \
	echo "PYTHONPATH is set to: $(PYTHONPATH)" && \
	python3 eval/strict_match/test_strict_match.py $(ARGS)

eval-llm-as-judge: .env venv/bin/activate
	@echo "Running Strict Evaluation Tests with Dry-run Enabled..."
	. venv/bin/activate && pip install -r eval/requirements.txt && \
	DRY_RUN=true \
	export PYTHONPATH=$(PWD):$(PWD)/src:$PYTHONPATH && \
	. .env && \
	echo "PYTHONPATH is set to: $(PYTHONPATH)" && \
	python3 eval/llm_as_judge/test_jarvis_agent_llm_as_judge.py

langgraph-dev: .env venv/bin/activate
	@echo "Running langgraph dev..."
	export PYTHONPATH=$(PWD):$(PWD)/src && \
	echo "PYTHONPATH is set to: $(PYTHONPATH)" && \
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
	@echo "  venv                Set up virtual environment and install requirements"
	@echo "  docker-build        Build the Docker image"
	@echo "  run-docker-local    Run the agent locally in Docker"
	@echo "  docker-run          Run the agent in Docker with local source code"
	@echo "  lint                Run linter on the codebase"
	@echo "  pytest              Run tests using pytest"
	@echo "  test                Run linter and tests"
	@echo "  graph               Generate knowledge graph"
	@echo "  clean               Clean up Docker images and .env file"
	@echo "  eval                Run evaluation tests"
	@echo "  langgraph-dev       Run langgraph dev command"