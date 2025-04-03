unamestr := $(shell uname)
docker=docker
# docker=podman # uncomment for podman
# include .env

# .env is the build artifact of this step, so name the target so that make can do what make does.
.env:
	@echo "Fetching secrets from Vault..."
	@if [ -z "$$VAULT_TOKEN" ]; then \
		echo "VAULT_TOKEN env var is not set or invalid"; \
		exit 1; \
	else \
		echo "VAULT_TOKEN is already set and valid."; \
	fi
	@touch .env
	@echo "Fetching current username..."
	@if [ "$$SETUP_LOCAL_USER_SECRETS" = "true" ]; then \
		CURRENT_USER=$$(whoami); \
		echo "Fetching local user secrets for $$CURRENT_USER..."; \
		APP_CONFIG=$$(VAULT_ADDR=https://keeper.cisco.com VAULT_NAMESPACE=eticloud VAULT_TOKEN=$$VAULT_TOKEN vault kv get -format=json secret/projects/jarvis-agent/local/$$CURRENT_USER/app-config) && \
		echo "$$APP_CONFIG" | jq -r '.data.data |to_entries | map("\(.key|tostring|ascii_upcase)=\(.value|tostring)") | .[]' > .env; \
	else \
		echo "Fetching default app secrets..."; \
		APP_CONFIG=$$(VAULT_ADDR=https://keeper.cisco.com VAULT_NAMESPACE=eticloud VAULT_TOKEN=$$VAULT_TOKEN vault kv get -format=json secret/projects/jarvis-agent/dev/app-config) && \
		echo "$$APP_CONFIG" | jq -r '.data.data |to_entries | map("\(.key|tostring|ascii_upcase)=\(.value|tostring)") | .[]' > .env; \
	fi
	@if [ $$? -ne 0 ]; then \
		echo "Failed to fetch secrets"; \
		exit 1; \
	fi

deps: PYTHON-exists CARGO-exists CUE-exists
.PHONY: deps PYTHON-exists CARGO-exists .env CUE-exists
PYTHON-exists: ; @which python3 > /dev/null
# The uuid_utils package is written in rust and requires cargo to build.
CARGO-exists: ; @which cargo > /dev/null
CUE-exists: ; @which cue > /dev/null

venv/bin/activate:
	@echo "Setting up virtual environment..."
	@if [ ! -d "venv" ]; then \
		python3 -m venv venv; \
	fi
	@echo "Activating virtual environment and installing requirements..."
	. venv/bin/activate && pip install -r requirements.txt

build-docker-local:
	${docker} build --platform linux/amd64 -t jarvis-agent:dev --build-arg BASE_IMAGE=containers.cisco.com/eti-sre/sre-python-docker:v3.12.5-hardened-debian-12 -f ./Dockerfile  .

build: build-docker-local

run-docker-local: .env
	${docker} run -it \
		--env-file=.env \
		-e ALLOWED_ORIGINS=* \
		-e LANGGRAPH_CHECKPOINT_MEMORY_SAVER=memory \
		-e ENABLE_KNOWLEDGE_GRAPH=false \
		-p 8000:8000 \
		-v $(shell pwd)/app/src:/home/app/src \
		-v $(shell pwd)/.dockerconfigjson:/home/app/.dockerconfigjson \
		jarvis-agent:dev \
    python3 -m fastapi dev ./src/main.py --port 8000 --proxy-headers

run-docker-local-host-network: .env
	${docker} run -it --network host \
		--env-file=.env \
		-e ALLOWED_ORIGINS=* \
		-e LANGGRAPH_CHECKPOINT_MEMORY_SAVER=memory \
		-e ENABLE_KNOWLEDGE_GRAPH=false \
		-v $(shell pwd)/app/src:/home/app/src \
		-v $(shell pwd)/.dockerconfigjson:/home/app/.dockerconfigjson \
		jarvis-agent:dev \
    python3 -m fastapi dev ./src/main.py --port 8000 --proxy-headers

run-eval-local: .env
	${docker} run -it \
		--env-file=.env \
		-e ALLOWED_ORIGINS=* \
		-e LANGGRAPH_CHECKPOINT_MEMORY_SAVER=memory \
		-e ENABLE_KNOWLEDGE_GRAPH=false \
		-p 8000:8000 \
		-v $(shell pwd)/app/src:/home/app/src \
		-v $(shell pwd)/.dockerconfigjson:/home/app/.dockerconfigjson \
		jarvis-agent:dev \
		python3 ./src/evaluate.py --min-prompts 5 --max-prompts 10 --num_tests 5

build-and-run-docker-local: .env build-docker-local run-docker-local

build-and-docker-run: .env venv/bin/activate build-docker-local run-docker-local

docker-run: .env venv/bin/activate run-docker-local

run: run-docker-local

evaluate: run-eval-local

run-host-network: run-docker-local-host-network

run-local: .env venv/bin/activate
	@echo "Running FastAPI development server..."
	LANGGRAPH_CHECKPOINT_MEMORY_SAVER=memory \
	ENABLE_KNOWLEDGE_GRAPH=false \
	CUE_MODULE_PATH=${PWD}/data/cue_module \
	venv/bin/dotenv run --no-override venv/bin/fastapi dev app/src/main.py

build-k8s: build-docker-local
	docker tag jarvis-agent:dev 192.168.68.1:32001/jarvis-agent:latest && \
  docker push 192.168.68.1:32001/jarvis-agent:latest

run-k8s:
	kubectl create configmap jarvis-agent-env --from-env-file .env && \
	kubectl apply -f k8s.yaml

postgres:
	@echo "Starting PostgreSQL using docker-compose..."
	@cd postgres && ${docker} compose up -d

lint: venv/bin/activate
	@echo "Running ruff..."
	. venv/bin/activate && ruff check app/src tests

test: venv/bin/activate lint pytest

graph: .env venv/bin/activate
	@echo "Running make graph..."
	ENABLE_KNOWLEDGE_GRAPH=false \
	venv/bin/dotenv run --no-override venv/bin/python3 app/src/jarvis_agent.py


pytest: venv/bin/activate
	@echo "Running pytest..."
	. venv/bin/activate && export PYTHONPATH=app/src && python3 -m pytest tests

clean:
	echo "" > .env
	${docker} image rm jarvis-agent:dev

eval: eval-strict eval-llm-as-judge

eval-strict: .env venv/bin/activate
	@echo "Adding ENABLE_KNOWLEDGE_GRAPH=false to .env..."
	@echo "ENABLE_KNOWLEDGE_GRAPH=false" >> .env
	@echo "Running Jarvis Strict Evaluation Tests with Dry-run Enabled..."
	JARVIS_DRYRUN=true \
	export PYTHONPATH=$(PWD):$(PWD)/app/src:$PYTHONPATH && \
	. .env && \
	echo "PYTHONPATH is set to: $(PYTHONPATH)" && \
	python3 eval/strict_match/test_strict_match.py $(ARGS)

eval-llm-as-judge: .env venv/bin/activate
	@echo "Adding ENABLE_KNOWLEDGE_GRAPH=false to .env..."
	@echo "ENABLE_KNOWLEDGE_GRAPH=false" >> .env
	@echo "Running Jarvis Strict Evaluation Tests with Dry-run Enabled..."
	. venv/bin/activate && pip install -r eval/requirements.txt && \
	JARVIS_DRYRUN=true \
	export PYTHONPATH=$(PWD):$(PWD)/app/src:$PYTHONPATH && \
	. .env && \
	echo "PYTHONPATH is set to: $(PYTHONPATH)" && \
	python3 eval/llm_as_judge/test_jarvis_agent_llm_as_judge.py

langgraph-dev: .env venv/bin/activate
	@echo "Adding ENABLE_KNOWLEDGE_GRAPH=false to .env..."
	@echo "ENABLE_KNOWLEDGE_GRAPH=false" >> .env
	@echo "Running langgraph dev..."
	export PYTHONPATH=$(PWD):$(PWD)/app/src && \
	echo "PYTHONPATH is set to: $(PYTHONPATH)" && \
	langgraph dev
