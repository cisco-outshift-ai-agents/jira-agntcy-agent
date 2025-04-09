# Copyright 2025 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import os
import requests

from agntcy_agents_common.config import INTERNAL_ERROR_MESSAGE
from .dryrun.mock_responses import (
  MOCK_ADD_NEW_LABEL_TO_ISSUE_RESPONSE,
  MOCK_ASSIGN_JIRA_RESPONSE,
  MOCK_CREATE_JIRA_ISSUE_RESPONSE,
  MOCK_GET_ACCOUNT_ID_FROM_EMAIL_RESPONSE,
  MOCK_GET_JIRA_ISSUE_DETAILS_RESPONSE,
  MOCK_GET_SUPPORTED_JIRA_ISSUE_TYPES_RESPONSE,
  MOCK_UPDATE_ISSUE_REPORTER_RESPONSE,
)
from agents.issues_agent.models import CreateJiraIssueInput, LLMResponseOutput
from utils.jira_client.client import JiraClient
from utils.jira_client.rest import JiraRESTClient
from utils.dryrun_utils import dryrun_response

@dryrun_response(MOCK_CREATE_JIRA_ISSUE_RESPONSE)
def _create_jira_issue(input_data: CreateJiraIssueInput) -> str:
  """
  Create a new Jira issue.

  Args:
      input_data (CreateJiraIssueInput): The input model containing the details for creating the issue.

  Returns:
      str: The URL of the created Jira issue.
  """
  logging.info(f"Creating a new Jira issue in project: {input_data.project_key}")

  try:
    supported_issue_types = _get_supported_issue_types(input_data.project_key)
    if input_data.issue_type not in supported_issue_types:
      raise ValueError(f"Unsupported issue type: {input_data.issue_type}. Supported issue types are: {supported_issue_types}")

    issue_dict = {
      'project': {'key': input_data.project_key},
      'summary': input_data.summary,
      'description': input_data.description,
      'issuetype': {'name': input_data.issue_type},
    }

    if input_data.assignee_email:
      issue_dict['assignee'] = {'id': _get_account_id_from_email(input_data.assignee_email)}

    jira_api = JiraClient.get_jira_instance()
    new_issue = jira_api.create_issue(fields=issue_dict)
    return _urlify_jira_issue_id(new_issue.key)

  except Exception as e:
    raise ValueError(e)


def create_jira_issue(input_data: CreateJiraIssueInput) -> LLMResponseOutput:
  """
  Create a new Jira issue.

  Args:
      input_data (CreateJiraIssueInput): The input model containing the details for creating the issue.

  Returns:
      LLMResponseOutput: The output model containing the URL of the created Jira issue.
  """
  logging.info(f"Creating a new Jira issue in project: {input_data.project_key}")

  try:
    issue_url = _create_jira_issue(input_data)
    return LLMResponseOutput(response=issue_url)
  except Exception as e:
    return LLMResponseOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))


@dryrun_response(MOCK_ASSIGN_JIRA_RESPONSE)
def _assign_jira(issue_key: str, assignee_email: str) -> str:
  """
  Assign a Jira ticket to a specified user.

  Args:
      issue_key (str): The key of the Jira issue to assign.
      assignee_email (str): The email of the user to assign the issue to.

  Returns:
      str: A message indicating the result of the assignment.
  """
  logging.info(f"Assigning Jira ticket {issue_key} to {assignee_email}")

  jira_server_url, auth, headers = JiraRESTClient.get_auth_instance()
  try:
    assignee_url = f'{jira_server_url}/rest/api/3/issue/{issue_key}/assignee'
    payload = json.dumps({
      'accountId': _get_account_id_from_email(assignee_email)
    })
    response = requests.put(assignee_url, headers=headers, data=payload, auth=auth)
    if response.status_code == 204:
      urlify_jira_issue_id = _urlify_jira_issue_id(issue_key)
      logging.info(f'Jira ticket {issue_key} assigned to {assignee_email} successfully.')
      return f"Jira ticket assigned successfully {urlify_jira_issue_id}."
    else:
      logging.error(f'Failed to assign Jira ticket {issue_key} to {assignee_email}. Status code: {response.status_code}, Response: {response.text}')
      return "Failed to assign Jira ticket."
  except Exception as e:
    logging.error(f'Failed to assign Jira ticket {issue_key} to {assignee_email}. Error: {e}')
    return INTERNAL_ERROR_MESSAGE + ":" + str(e)

def assign_jira(issue_key: str, assignee_email: str) -> LLMResponseOutput:
  """
  Assign a Jira ticket to a specified user.

  Args:
      issue_key (str): The key of the Jira issue to assign.
      assignee_email (str): The email of the user to assign the issue to.

  Returns:
      LLMResponseOutput: The output model containing the result of the assignment.
  """
  logging.info(f"Assigning Jira ticket {issue_key} to {assignee_email}")

  try:
    result = _assign_jira(issue_key, assignee_email)
    return LLMResponseOutput(response=result)
  except Exception as e:
    logging.error(f'Failed to assign Jira ticket {issue_key} to {assignee_email}. Error: {e}')
    return LLMResponseOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))

@dryrun_response(MOCK_UPDATE_ISSUE_REPORTER_RESPONSE)
def _update_jira_reporter(issue_key: str, reporter_email: str) -> str:
  """
  Update the reporter of a Jira issue.

  Args:
      issue_key (str): The key of the Jira issue.
      reporter_email (str): The email of the new reporter.

  Returns:
      str: A message indicating the result of the update.
  """
  logging.info(f"Updating reporter of ticket: {issue_key}")

  try:
    jira_api = JiraClient.get_jira_instance()
    reporter_id = _get_account_id_from_email(reporter_email)
    issue = jira_api.issue(issue_key)
    issue.update(reporter={'id': reporter_id})
    logging.info("Reporter updated successfully.")
    urlify_jira_issue_id = _urlify_jira_issue_id(issue_key)
    return f"Reporter updated successfully on Jira {urlify_jira_issue_id}."
  except Exception as e:
    logging.error(f"Error updating reporter: {e}")
    raise ValueError(INTERNAL_ERROR_MESSAGE + ":" + str(e))

def update_issue_reporter(issue_key: str, reporter_email: str) -> LLMResponseOutput:
  """
  Update the reporter of a Jira issue.

  Args:
      issue_key (str): The key of the Jira issue.
      reporter_email (str): The email of the new reporter.

  Returns:
      LLMResponseOutput: The output model containing the result of the update.
  """
  try:
    result = _update_jira_reporter(issue_key, reporter_email)
    return LLMResponseOutput(response=result)
  except Exception as e:
    return LLMResponseOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))

def add_new_label_to_issue(issue_key: str, label: str) -> LLMResponseOutput:
  """
  Add a new label to a Jira issue.

  Args:
      issue_key (str): The key of the Jira issue.
      label (str): The label to add.

  Returns:
      LLMResponseOutput: The output model containing the result of the operation.
  """
  try:
    issue_url =  _add_new_label_to_issue(issue_key, label)
    return LLMResponseOutput(response=issue_url)
  except Exception as e:
    return LLMResponseOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))

@dryrun_response(MOCK_GET_JIRA_ISSUE_DETAILS_RESPONSE)
def _get_jira_issue_details(issue_key: str) -> dict:
  """
  Retrieve the details of a Jira issue.

  Args:
      issue_key (str): The key of the Jira issue.

  Returns:
      dict: A dictionary containing the details of the issue.
  """
  logging.info(f"Retrieving details for ticket: {issue_key}")

  try:
    jira_api = JiraClient.get_jira_instance()
    issue = jira_api.issue(issue_key)
    urlify_jira_issue_id = _urlify_jira_issue_id(issue.key)
    ticket_details = {
      "key": urlify_jira_issue_id,
      "summary": issue.fields.summary,
      "description": issue.fields.description,
      "status": issue.fields.status.name,
      "priority": issue.fields.priority.name,
      "reporter": issue.fields.reporter.displayName,
      "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None,
      "created": issue.fields.created,
      "updated": issue.fields.updated,
    }
    return ticket_details

  except Exception as e:
    logging.error(f"Error retrieving Jira issue details: {e}")
    raise ValueError(INTERNAL_ERROR_MESSAGE + ":" + str(e))

def get_jira_issue_details(issue_key: str) -> LLMResponseOutput:
  """
  Retrieve the details of a Jira issue.

  Args:
      issue_key (str): The key of the Jira issue.

  Returns:
      LLMResponseOutput: The output model containing the details of the issue.
  """
  try:
    ticket_details = _get_jira_issue_details(issue_key)
    resp_str = f"Jira Issue Details: {ticket_details}"
    return LLMResponseOutput(response=resp_str)
  except Exception as e:
    return LLMResponseOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))

@dryrun_response(MOCK_ADD_NEW_LABEL_TO_ISSUE_RESPONSE)
def _add_new_label_to_issue(issue_key: str, label: str) -> str:
  """
  Add a new label to a Jira issue.

  Args:
      issue_key (str): The key of the Jira issue.
      label (str): The label to add.

  Returns:
      str: A message indicating the result of the operation.
  """
  logging.info(f"Adding label '{label}' to ticket: {issue_key}")
  try:
    jira_api = JiraClient.get_jira_instance()
    issue = jira_api.issue(issue_key)
    issue.fields.labels.append(label)
    issue.update(fields={"labels": issue.fields.labels})
    logging.info("Label added successfully.")
    urlify_jira_issue_id = _urlify_jira_issue_id(issue_key)
    return f"Label added successfully on Jira {urlify_jira_issue_id}."
  except Exception as e:
    raise ValueError(f"Error adding label: {e}")

def _urlify_jira_issue_id(issue_id: str) -> str:
  """
  Convert a Jira issue ID to a URL.

  Args:
      issue_id (str): The Jira issue ID.

  Returns:
      str: The URL of the Jira issue.
  """
  jira_server =  os.getenv("JIRA_URL") or os.getenv("JIRA_INSTANCE")
  return f"{jira_server}/browse/{issue_id}"

def _create_jira_urlified_list(issues) -> list:
  """
  Create a list of Jira issues in Markdown format with clickable links.

  Args:
      issues (list): A list of Jira issue objects. Each object is expected to have a 'key' attribute
                     representing the issue key (e.g., "PROJECT-123").

  Returns:
      list: A list of strings, where each string is a Markdown-formatted link to a Jira issue.
            The format is "[ISSUE_KEY](ISSUE_URL)".
  """
  issues_md = []
  for issue in issues:
    issue_link = _urlify_jira_issue_id(issue.key)
    issue_summary = issue.fields.summary
    issues_md.append(f"[{issue.key}: {issue_summary}]({issue_link})")
  return issues_md

@dryrun_response(MOCK_GET_ACCOUNT_ID_FROM_EMAIL_RESPONSE)
def _get_account_id_from_email(email: str) -> str:
  """
  Retrieve the account ID associated with a given email address in Jira.

  Args:
      email (str): The email address of the user whose account ID is to be retrieved.

  Returns:
      str: The account ID of the user, as a string. Returns None if the user is not found or if an error occurs.

  Raises:
      Exception: If the Jira API request fails or encounters an error.
  """
  try:
    jira_server_url, auth, headers = JiraRESTClient.get_auth_instance()
    search_url = f'{jira_server_url}/rest/api/3/user/search'

    query = {
      'query': email
    }

    user_search_response = requests.get(
      search_url,
      headers=headers,
      params=query,
      auth=auth
    )

    if user_search_response.status_code == 200:
      users_data = user_search_response.json()
      if users_data:
        account_id = users_data[0].get('accountId')
        logging.info(f'Account ID found for email {email}: {account_id}')
        return account_id
      else:
        logging.warning(f'No users found with email {email}.')
        return ""
    else:
      logging.error(f'Failed to retrieve user details for email {email}. Status code: {user_search_response.status_code}, Response: {user_search_response.text}')
      return ""
  except Exception as e:
    logging.error(f'Failed to get account ID for email {email}. Error: {e}')
    return ""

def get_account_id_from_email(email: str) -> str:
  """
  Retrieve the account ID associated with a given email address in Jira.

  Args:
      email (str): The email address of the user whose account ID is to be retrieved.

  Returns:
      str: The account ID of the user, as a string. Returns None if the user is not found or if an error occurs.

  Raises:
      Exception: If the Jira API request fails or encounters an error.
  """
  return _get_account_id_from_email(email)

@dryrun_response(MOCK_GET_SUPPORTED_JIRA_ISSUE_TYPES_RESPONSE)
def _get_supported_issue_types(project_key: str) -> list[str]:
  """
  Retrieve supported issue types for Jira issues in a specific project.

  Args:
      project_key (str): The key of the project to get issue metadata for.

  Returns:
      list[str]: A list of supported issue types.

  Raises:
      ValueError: If there is an error retrieving the metadata.
  """
  try:
    jira_api = JiraClient.get_jira_instance()
    issue_metadata = jira_api.createmeta(projectKeys=project_key, expand='projects.issuetypes.fields')
    supported_issue_types = []
    for project in issue_metadata['projects']:
      for issue in project['issuetypes']:
        supported_issue_types.append(issue['name'])

    return supported_issue_types
  except Exception as e:
    raise ValueError(f"Error getting Jira issue metadata: {e}") from e