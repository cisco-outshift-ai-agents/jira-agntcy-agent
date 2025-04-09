import os
import requests
import json

from src.utils.jira_client.client import JiraRESTClient


def get_project_by_key(project_key: str):
    jira_server_url, auth, headers = JiraRESTClient.get_auth_instance()
    url = f"{jira_server_url}/rest/api/3/project/{project_key}"
    response = requests.get(url, headers=headers, auth=auth)
    return response


def project_update_description(project_key: str, description: str):
    jira_server_url, auth, headers = JiraRESTClient.get_auth_instance()
    url = f"{jira_server_url}/rest/api/3/project/{project_key}"
    payload = json.dumps({
        "description": description,
    })
    response = requests.put(url=url, data=payload, headers=headers, auth=auth)
    return response
