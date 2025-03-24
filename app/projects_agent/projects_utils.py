import json
import logging
import os
import re

from projects_agent.projects_models import JiraProjectOutput
from projects_agent.projects_models import (CreateJiraProjectInput,
                                            GetJiraProjectByNameInput,
                                            UpdateJiraProjectDescriptionInput,
                                            UpdateJiraProjectLeadInput)

from utils.jira_utils import jira_request_get, jira_request_post, jira_request_put

from core.config import INTERNAL_ERROR_MESSAGE


############################## Tool helper functions ##############################


def _get_jira_project_by_name(input: GetJiraProjectByNameInput) -> JiraProjectOutput:
    """get a jira project by name.
         Args:
         input (GetJiraProjectByNameInput):
             The user-provided input that guides the jira projects retrieval.
             This request is serialized from a `GetJiraProjectByNameInput` object,
             which must have a `model_dump()` method for JSON conversion.

     Returns:
         JiraProjectOutput:
             A JSON representation of the JiraProjectOutput.
             This response is serialized from a `JiraProjectOutput` object,
             which must have a `model_dump()` method for JSON conversion.
    """
    try:
        url_path = f"/rest/api/3/project/search?query=" + input.name
        jira_resp = jira_request_get(url_path)
        jira_resp_json = json.loads(jira_resp)
        if 'error' in jira_resp_json and 'exception' in jira_resp_json:
            response_str = f"{INTERNAL_ERROR_MESSAGE}:{jira_resp}"
        else:
            project_urls = _parse_project_url_from_get_jira_project_by_name(jira_resp_json)
            project_key = _parse_project_key_from_get_jira_project_by_name(jira_resp_json)
            if len(project_urls) == 0:
                response_str = f"{INTERNAL_ERROR_MESSAGE}:No projects found for {input.name}, {jira_resp}"
            elif len(project_urls) > 1:
                response_str = (f"{INTERNAL_ERROR_MESSAGE}:Multiple projects found for {input.name}, {jira_resp}. "
                                f"Please try using the unique project key instead of project name")
            else:
                response_str = f'{project_urls[0]}, {jira_resp}'

        return JiraProjectOutput(response=response_str)

    except Exception as e:
        return JiraProjectOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))


def _create_jira_project(input: CreateJiraProjectInput) -> JiraProjectOutput:
    """create a jira project and return the output.
         Args:
         input (CreateJiraProjectInput):
             The user-provided input that guides the jira project creation.
             This request is serialized from a `CreateJiraProjectInput` object,
             which must have a `model_dump()` method for JSON conversion.

     Returns:
         JiraProjectOutput:
             A JSON representation of the JiraProjectOutput.
             This response is serialized from a `JiraProjectOutput` object,
             which must have a `model_dump()` method for JSON conversion.
    """
    try:
        leadAccountId = input.leadAccountId
        if is_valid_email(input.leadAccountId):
            account_id = _get_jira_accountID_by_user_email(input.leadAccountId)
            if account_id:
                leadAccountId = account_id
            else:
                return JiraProjectOutput(response=f"{INTERNAL_ERROR_MESSAGE}: {input.leadAccountId} not found in Jira")

        if os.getenv("USE_MOCK_RESP") == "true":
            response_str = f"Created Jira project id:123 with owner: John Doe"
        else:
            url_path = "/rest/api/3/project"

            payload = json.dumps({
                "assigneeType": "PROJECT_LEAD",
                "description": input.description,
                "key": input.key,
                "leadAccountId": leadAccountId,
                "name": input.name,
                "projectTypeKey": input.projectTypeKey
            })

            jira_resp = jira_request_post(url_path, payload)
            jira_resp_json = json.loads(jira_resp)
            if 'error' in jira_resp_json and 'exception' in jira_resp_json:
                response_str = f"{INTERNAL_ERROR_MESSAGE}:{jira_resp}"
            else:
                project_url = jira_resp_json['self']
                response_str = project_url

        return JiraProjectOutput(response=response_str)

    except Exception as e:
        return JiraProjectOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))


def _update_jira_project_description(input: UpdateJiraProjectDescriptionInput) -> JiraProjectOutput:
    """update a jira project description and return the output.
         Args:
         input (UpdateJiraProjectDescriptionInput):
             The user-provided input that guides the jira project description updation.
             This request is serialized from a `UpdateJiraProjectDescriptionInput` object,
             which must have a `model_dump()` method for JSON conversion.

     Returns:
         JiraProjectOutput:
             A JSON representation of the JiraProjectOutput.
             This response is serialized from a `JiraProjectOutput` object,
             which must have a `model_dump()` method for JSON conversion.
    """
    try:
        if os.getenv("USE_MOCK_RESP") == "true":
            response_str = f"Updated Jira project id:123 with description: description"
        else:
            url_path = "/rest/api/3/project/" + input.key

            payload = json.dumps({
                "description": input.description
            })

            jira_resp = jira_request_put(url_path, payload)
            jira_resp_json = json.loads(jira_resp)
            if 'error' in jira_resp_json and 'exception' in jira_resp_json:
                response_str = f"{INTERNAL_ERROR_MESSAGE}:{jira_resp}"
            else:
                project_url = jira_resp_json['self']
                response_str = project_url

        return JiraProjectOutput(response=response_str)

    except Exception as e:
        return JiraProjectOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))


def _update_jira_project_lead(input: UpdateJiraProjectLeadInput) -> JiraProjectOutput:
    """update a jira project lead and return the output.
         Args:
         input (UpdateJiraProjectLeadInput):
             The user-provided input that guides the jira project lead updation.
             This request is serialized from a `UpdateJiraProjectLeadInput` object,
             which must have a `model_dump()` method for JSON conversion.

     Returns:
         JiraProjectOutput:
             A JSON representation of the JiraProjectOutput.
             This response is serialized from a `JiraProjectOutput` object,
             which must have a `model_dump()` method for JSON conversion.
    """
    try:
        leadAccountId = input.leadAccountId
        if is_valid_email(input.leadAccountId):
            account_id = _get_jira_accountID_by_user_email(input.leadAccountId)
            if account_id:
                leadAccountId = account_id
            else:
                return JiraProjectOutput(response=f"{INTERNAL_ERROR_MESSAGE}: {input.leadAccountId} not found in Jira")

        if os.getenv("USE_MOCK_RESP") == "true":
            response_str = f"Updated Jira project id:123 with lead: xxxx"
        else:
            url_path = "/rest/api/3/project/" + input.key

            payload = json.dumps({
                "leadAccountId": leadAccountId
            })

            jira_resp = jira_request_put(url_path, payload)
            jira_resp_json = json.loads(jira_resp)
            if 'error' in jira_resp_json and 'exception' in jira_resp_json:
                response_str = f"{INTERNAL_ERROR_MESSAGE}:{jira_resp}"
            else:
                project_url = jira_resp_json['self']
                response_str = project_url

        return JiraProjectOutput(response=response_str)

    except Exception as e:
        return JiraProjectOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))


################################ Util Helper functions ################################
def _parse_project_url_from_get_jira_project_by_name(jira_resp_json):
    project_urls = []
    if 'total' in jira_resp_json and jira_resp_json['total'] != 0:
        if 'values' in jira_resp_json:
            for project in jira_resp_json['values']:
                if 'self' in project:
                    project_urls.append(project['self'])

    return project_urls

def _parse_project_key_from_get_jira_project_by_name(jira_resp_json):
    if 'total' in jira_resp_json and jira_resp_json['total'] != 0:
        if 'values' in jira_resp_json:
            for project in jira_resp_json['values']:
                if 'key' in project:
                    return project['key']

    return ""


def is_valid_email(email):
    """
    Checks if a string is a valid email address using regular expression.

    Args:
        email: The string to check.

    Returns:
        True if the string is a valid email address, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if re.match(pattern, email):
        return True
    else:
        return False


def _get_jira_accountID_by_user_email(user_email):
    try:
        url_path = f"/rest/api/3/groupuserpicker?query=" + user_email
        jira_resp = jira_request_get(url_path)
        user_data = json.loads(jira_resp)

        # Extract accountId from the response
        if 'users' in user_data:
            if 'total' in user_data['users'] and user_data['users']['total'] == 0:
                logging.error(f"User email: {user_email} not found in Jira")
                return None
            else:
                if 'users' in user_data['users']:
                    # unique email - will have only one user
                    for user in user_data['users']['users']:
                        account_id = user['accountId']
                        return account_id

    except Exception as e:
        logging.error(f"Error getting Jira account ID for user email: {user_email}, error: {str(e)}")

    return None
