import os
import requests
import json


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
