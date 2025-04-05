#!/bin/bash
# This evaluation is run using a LLM and mock Jira responses.
# this script can be invoked from Makefile or code moved to Makefile as required

#python3 -m venv myenv
#. myenv/bin/activate
#
#pip install --upgrade pip setuptools
#pip install -r eval/requirements.txt

# USAGE: ./run_eval.sh
# PREREQUISITES: Required env variables must be specified
# Ensure TEST_AZURE_OPENAI_API_VERSION, TEST_AZURE_OPENAI_ENDPOINT, TEST_AZURE_OPENAI_API_KEY, TEST_AZURE_OPENAI_DEPLOYMENT_NAME (default=gpt-4o) are set for Azure provider
# Ensure TEST_OPENAI_ENDPOINT, TEST_OPENAI_API_KEY, OPENAI_API_VERSION (default=gpt-4o) are set for OpenAI provider
# Ensure LANGCHAIN_API_KEY is set
DRYRUN=true LANGSMITH_TRACING='true' python3 -m pytest eval/strict_match/test_strict_match.py

#pytest tests/eval/strict_match/test_strict_match.py
