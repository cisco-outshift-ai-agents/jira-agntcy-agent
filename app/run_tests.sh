#!/bin/bash
#python3 -m venv myenv
#. myenv/bin/activate
#
#pip install --upgrade pip setuptools
#pip install -r requirements.txt

# The purpose of this test is to do a quick validation for the tools executed for user prompts.
# This test is run using a LLM and mock Jira responses.
# USAGE: ./run_tests.sh
# PREREQUISITES: Required env variables must be specified
# Ensure TEST_AZURE_OPENAI_API_VERSION, TEST_AZURE_OPENAI_ENDPOINT, TEST_AZURE_OPENAI_API_KEY and are set for Azure provider
# Ensure TEST_OPENAI_ENDPOINT and TEST_OPENAI_API_KEY are set for OpenAI provider
DRYRUN=true python3 -m unittest tests.test_prompts_projects
DRYRUN=true python3 -m unittest tests.test_prompts_issues