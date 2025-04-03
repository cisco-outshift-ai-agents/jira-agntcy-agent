from agntcy_agents_common.setup_logging import logging

from agents.projects_agent.models import LLMResponseOutput

from agents.projects_agent.models import (
    CreateJiraProjectInput,
    GetJiraProjectByNameInput,
    UpdateJiraProjectDescriptionInput,
    UpdateJiraProjectLeadInput
)

from .utils import (
    _get_jira_project_by_name,
    _create_jira_project,
    _update_jira_project_description,
    _update_jira_project_lead
)


def get_jira_project_by_name(input: GetJiraProjectByNameInput) -> LLMResponseOutput:
    """get a jira project by name.
         Args:
         input (GetJiraProjectByNameInput):
             The user-provided input that guides the jira projects retrieval.
             This request is serialized from a `GetJiraProjectByNameInput` object,
             which must have a `model_dump()` method for JSON conversion.

     Returns:
         LLMResponseOutput:
             A JSON representation of the LLMResponseOutput.
             This response is serialized from a `LLMResponseOutput` object,
             which must have a `model_dump()` method for JSON conversion.
    """
    logging.info(f"tool input:{input}")
    resp = _get_jira_project_by_name(input)
    logging.info(f"tool output:{resp}")
    return resp


def create_jira_project(input: CreateJiraProjectInput) -> LLMResponseOutput:
    """create a jira project and return the output.
         Args:
         input (CreateJiraProjectInput):
             The user-provided input that guides the jira project creation.
             This request is serialized from a `CreateJiraProjectInput` object,
             which must have a `model_dump()` method for JSON conversion.

     Returns:
         LLMResponseOutput:
             A JSON representation of the LLMResponseOutput.
             This response is serialized from a `LLMResponseOutput` object,
             which must have a `model_dump()` method for JSON conversion.
    """
    logging.info(f"tool input:{input}")
    resp = _create_jira_project(input)
    logging.info(f"tool output:{resp}")
    return resp


def update_jira_project_description(input: UpdateJiraProjectDescriptionInput) -> LLMResponseOutput:
    """update a jira project description and return the output.
         Args:
         input (UpdateJiraProjectDescriptionInput):
             The user-provided input that guides the jira project description updation.
             This request is serialized from a `UpdateJiraProjectDescriptionInput` object,
             which must have a `model_dump()` method for JSON conversion.

     Returns:
         LLMResponseOutput:
             A JSON representation of the LLMResponseOutput.
             This response is serialized from a `LLMResponseOutput` object,
             which must have a `model_dump()` method for JSON conversion.
    """
    logging.info(f"tool input:{input}")
    resp = _update_jira_project_description(input)
    logging.info(f"tool output:{resp}")
    return resp


def update_jira_project_lead(input: UpdateJiraProjectLeadInput) -> LLMResponseOutput:
    """update a jira project lead and return the output.
         Args:
         input (UpdateJiraProjectLeadInput):
             The user-provided input that guides the jira project lead updation.
             This request is serialized from a `UpdateJiraProjectLeadInput` object,
             which must have a `model_dump()` method for JSON conversion.

     Returns:
         LLMResponseOutput:
             A JSON representation of the LLMResponseOutput.
             This response is serialized from a `LLMResponseOutput` object,
             which must have a `model_dump()` method for JSON conversion.
    """
    logging.info(f"tool input:{input}")
    resp = _update_jira_project_lead(input)
    logging.info(f"tool output:{resp}")
    return resp
