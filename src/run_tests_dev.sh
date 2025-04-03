#!/bin/bash
#python3 -m venv myenv
#. myenv/bin/activate
#
#pip install --upgrade pip setuptools
#pip install -r requirements.txt

# The purpose of this test is to do a quick validation for the user prompts.
# This test is run *using a LLM* and a *valid Jira instance*.
# USAGE: ./run_tests_dev.sh
# PREREQUISITES: Required env variables must be specified in tests/dev/.env.
# NOTE: These tests *run updates* on the Jira Project. Please use a *test jira project* for this test.
DEV_TEST=true python3 -m unittest tests.dev.test_prompts_projects_dev