#!/bin/bash
#python3 -m venv myenv
#. myenv/bin/activate
#
#pip install --upgrade pip setuptools
#pip install -r requirements.txt

# The purpose of this test is to do a quick validation for the user prompts related to projects.
# This test is run using a LLM and against an actual Jira instance.
# USAGE: ./run_tests.sh
# PREREQUISITES: Required env variables must be specified in .env based on the .env.sample file.
# NOTE: These tests *run updates* on the Jira Project. Please use a *test jira project* for this test.
# source tests/.env
python3 -m unittest tests.test_prompts_projects
