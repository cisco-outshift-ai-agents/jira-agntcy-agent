import os

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import json


def validate_env_vars():
    load_dotenv()  # take environment variables from tests/.env.

    if not os.getenv("LLM_PROVIDER") or os.getenv("LLM_PROVIDER") == "":
        return False, "LLM_PROVIDER env variable is not set"
    if not os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") == "":
        return False, "AZURE_OPENAI_DEPLOYMENT_NAME env variable is not set"
    if not os.getenv("AZURE_OPENAI_API_VERSION") or os.getenv("AZURE_OPENAI_API_VERSION") == "":
        return False, "AZURE_OPENAI_API_VERSION env variable is not set"
    if not os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT") == "":
        return False, "AZURE_OPENAI_ENDPOINT env variable is not set"
    if not os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY") == "":
        return False, "AZURE_OPENAI_API_KEY env variable is not set"
    if not os.getenv("AZURE_OPENAI_TEMPERATURE") or os.getenv("AZURE_OPENAI_TEMPERATURE") == "":
        return False, "AZURE_OPENAI_TEMPERATURE env variable is not set"

    if not os.getenv("JIRA_INSTANCE") or os.getenv("JIRA_INSTANCE") == "":
        return False, "JIRA_INSTANCE env variable is not set"
    if not os.getenv("JIRA_BASIC_AUTH_TOKEN") or os.getenv("JIRA_BASIC_AUTH_TOKEN") == "":
        return False, "JIRA_BASIC_AUTH_TOKEN env variable is not set"
    if not os.getenv("TEST_PROJECT_NAME") or os.getenv("TEST_PROJECT_NAME") == "":
        return False, "TEST_PROJECT_NAME env variable is not set"
    if not os.getenv("TEST_PROJECT_KEY") or os.getenv("TEST_PROJECT_KEY") == "":
        return False, "TEST_PROJECT_KEY env variable is not set"
    if not os.getenv("TEST_PROJECT_LEAD_EMAIL") or os.getenv("TEST_PROJECT_LEAD_EMAIL") == "":
        return False, "TEST_PROJECT_LEAD_EMAIL env variable is not set"

    return True, ""

def get_project_by_key(project_key: str):
    jira_instance = os.getenv("JIRA_INSTANCE")
    jira_basic_auth_token = os.getenv("JIRA_BASIC_AUTH_TOKEN")

    headers = {
        "Accept": "application/json",
        "Authorization": "Basic " + jira_basic_auth_token
    }
    url = f"https://{jira_instance}/rest/api/3/project/{project_key}"
    response = requests.request(
        "GET",
        headers=headers,
        url=url
    )
    return response


def project_update_description(project_key: str, description: str):
    jira_instance = os.getenv("JIRA_INSTANCE")
    jira_basic_auth_token = os.getenv("JIRA_BASIC_AUTH_TOKEN")

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Basic " + jira_basic_auth_token
    }
    url = f"https://{jira_instance}/rest/api/3/project/{project_key}"

    payload = json.dumps({
        "description": description,
    })

    response = requests.request(
        "PUT",
        data=payload,
        headers=headers,
        url=url
    )
    return response

# def create_test_project(project_name, project_key, lead_account_id):
#
#     url = f"https://{jira_instance}/rest/api/3/project/{project_key}"
#
#     payload = json.dumps({
#         "assigneeType": "PROJECT_LEAD",
#         "description": "This is a test project for the Jira Agent",
#         "key": input.key,
#         "leadAccountId": leadAccountId,
#         "name": input.name,
#         "projectTypeKey": input.projectTypeKey
#     })
#     headers = {
#         "Accept": "application/json",
#         "Content-Type": "application/json"
#         "Authorization": "Basic " + jira_basic_auth_token
#     }
#     response = requests.request(
#         "POST",
#         data=payload,
#         headers=headers,
#         url=url
#     )

def contains_all_elements(list1, list2):
    return all(elem in list1 for elem in list2)
