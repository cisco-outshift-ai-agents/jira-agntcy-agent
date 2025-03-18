import json
import logging
import os

from projects_agent.projects_models import JiraProjectOutput
from projects_agent.projects_models import CreateJiraProjectInput, GetJiraProjectByNameInput

from utils.jira_utils import jira_request_get, jira_request_post


def get_jira_project_by_name(input: GetJiraProjectByNameInput) -> JiraProjectOutput:
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
    logging.info(f"tool input:{input}")
    if not input or input is None:
        return JiraProjectOutput(response="error performing the operation")

    url_path = f"/rest/api/3/project/search?query=" + input.name
    jira_resp = jira_request_get(url_path)
    response_str = f"Got Jira project by name: {input.name}, project details: {jira_resp}"
    resp = JiraProjectOutput(response=response_str)
    logging.info(f"tool output:{resp}")

    return resp


def create_jira_project(input: CreateJiraProjectInput) -> JiraProjectOutput:
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
    logging.info(f"tool input:{input}")
    if not input or input is None:
        return JiraProjectOutput(response="error performing the operation")

    if os.getenv("USE_MOCK_RESP") == "true":
        response_str = f"Created Jira project id:123 with owner: John Doe"
    else:
        url_path = "/rest/api/3/project"

        payload = json.dumps({
            "assigneeType": input.assignee_type,
            "description": input.description,
            "key": input.key,
            "leadAccountId": input.leadAccountId,
            "name": input.name,
            "projectTypeKey": input.projectTypeKey
        })

        jira_resp = jira_request_post(url_path, payload)
        response_str = f"Created Jira project: {jira_resp}"

    resp = JiraProjectOutput(response=response_str)
    logging.info(f"tool output:{resp}")

    return resp
