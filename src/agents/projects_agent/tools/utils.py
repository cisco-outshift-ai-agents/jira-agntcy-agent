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
import re

from agents.projects_agent.models import LLMResponseOutput
from agents.projects_agent.models import (
  CreateJiraProjectInput,
  GetJiraProjectByNameInput,
  UpdateJiraProjectDescriptionInput,
  UpdateJiraProjectLeadInput
)
from .dryrun.mock_responses import (
  MOCK_GET_PROJECT_KEY_BY_NAME_RESPONSE,
  MOCK_CREATE_PROJECT_RESPONSE,
  MOCK_UPDATE_PROJECT_DESCRIPTION_RESPONSE,
  MOCK_UPDATE_PROJECT_LEAD_RESPONSE
)

from utils.jira_client.rest import JiraRESTClient
from utils.dryrun_utils import dryrun_response

from common.config import INTERNAL_ERROR_MESSAGE


############################## Tool helper functions ##############################

@dryrun_response(LLMResponseOutput(response=MOCK_GET_PROJECT_KEY_BY_NAME_RESPONSE))
def _get_jira_project_by_name(input: GetJiraProjectByNameInput) -> LLMResponseOutput:
  """
  Retrieves a Jira project by name.

  Args:
    input (GetJiraProjectByNameInput):
      The user-provided input that guides the retrieval of Jira projects.
      This input is serialized from a `GetJiraProjectByNameInput` object,
      which must have a `model_dump()` method for JSON conversion.

  Returns:
    LLMResponseOutput:
      A JSON representation of the response, serialized from an
      `LLMResponseOutput` object, which must have a `model_dump()`
      method for JSON conversion.
  """
  try:
    url_path = f"/rest/api/3/project/search?query={input.name}"
    jira_resp = JiraRESTClient.jira_request_get(url_path)
    jira_resp_json = json.loads(jira_resp)
    if 'error' in jira_resp_json and 'exception' in jira_resp_json:
      response_str = f"{INTERNAL_ERROR_MESSAGE}:{jira_resp}"
    else:
      project_urls = _parse_project_url_from_get_jira_project_by_name(jira_resp_json)
      # project_key = _parse_project_key_from_get_jira_project_by_name(jira_resp_json)
      if len(project_urls) == 0:
        response_str = f"{INTERNAL_ERROR_MESSAGE}:No projects found for {input.name}, {jira_resp}"
      elif len(project_urls) > 1:
        response_str = (f"{INTERNAL_ERROR_MESSAGE}:Multiple projects found for {input.name}, {jira_resp}. "
                        f"Please try using the unique project key instead of project name")
      else:
        response_str = f'{project_urls[0]}, {jira_resp}'

    return LLMResponseOutput(response=response_str)

  except Exception as e:
    return LLMResponseOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))

@dryrun_response(LLMResponseOutput(response=MOCK_CREATE_PROJECT_RESPONSE))
def _create_jira_project(input: CreateJiraProjectInput) -> LLMResponseOutput:
  """
  create a jira project and return the output.

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
  try:
    leadAccountId = input.leadAccountId
    if is_valid_email(input.leadAccountId):
      account_id = _get_jira_accountID_by_user_email(input.leadAccountId)
      if account_id:
        leadAccountId = account_id
      else:
        return LLMResponseOutput(response=f"{INTERNAL_ERROR_MESSAGE}: {input.leadAccountId} not found in Jira")

    url_path = "/rest/api/3/project"

    payload = json.dumps({
      "assigneeType": "PROJECT_LEAD",
      "description": input.description,
      "key": input.key,
      "leadAccountId": leadAccountId,
      "name": input.name,
      "projectTypeKey": input.projectTypeKey
    })

    jira_resp = JiraRESTClient.jira_request_post(url_path, payload)
    jira_resp_json = json.loads(jira_resp)
    if 'error' in jira_resp_json and 'exception' in jira_resp_json:
      response_str = f"{INTERNAL_ERROR_MESSAGE}:{jira_resp}"
    else:
      project_url = jira_resp_json['self']
      response_str = project_url

    return LLMResponseOutput(response=response_str)

  except Exception as e:
    return LLMResponseOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))

@dryrun_response(LLMResponseOutput(response=MOCK_UPDATE_PROJECT_DESCRIPTION_RESPONSE))
def _update_jira_project_description(input: UpdateJiraProjectDescriptionInput) -> LLMResponseOutput:
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
  try:
    url_path = "/rest/api/3/project/" + input.key

    payload = json.dumps({
      "description": input.description
    })

    jira_resp = JiraRESTClient.jira_request_put(url_path, payload)
    jira_resp_json = json.loads(jira_resp)
    if 'error' in jira_resp_json and 'exception' in jira_resp_json:
      response_str = f"{INTERNAL_ERROR_MESSAGE}:{jira_resp}"
    else:
      project_url = jira_resp_json['self']
      response_str = project_url

    return LLMResponseOutput(response=response_str)

  except Exception as e:
    return LLMResponseOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))

@dryrun_response(LLMResponseOutput(response=MOCK_UPDATE_PROJECT_LEAD_RESPONSE))
def _update_jira_project_lead(input: UpdateJiraProjectLeadInput) -> LLMResponseOutput:
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
  try:
    leadAccountId = input.leadAccountId
    if is_valid_email(input.leadAccountId):
      account_id = _get_jira_accountID_by_user_email(input.leadAccountId)
      if account_id:
        leadAccountId = account_id
      else:
        return LLMResponseOutput(response=f"{INTERNAL_ERROR_MESSAGE}: {input.leadAccountId} not found in Jira")

    url_path = "/rest/api/3/project/" + input.key

    payload = json.dumps({
      "leadAccountId": leadAccountId
    })

    jira_resp = JiraRESTClient.jira_request_put(url_path, payload)
    jira_resp_json = json.loads(jira_resp)
    if 'error' in jira_resp_json and 'exception' in jira_resp_json:
      response_str = f"{INTERNAL_ERROR_MESSAGE}:{jira_resp}"
    else:
      project_url = jira_resp_json['self']
      response_str = project_url

    return LLMResponseOutput(response=response_str)

  except Exception as e:
    return LLMResponseOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))


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
    url_path = f"/rest/api/3/groupuserpicker?query={user_email}"
    jira_resp = JiraRESTClient.jira_request_get(url_path)
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
