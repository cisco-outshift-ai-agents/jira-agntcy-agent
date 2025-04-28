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
from typing import List

from jira_agent.common.config import INTERNAL_ERROR_MESSAGE

from .dryrun.mock_responses import (
  MOCK_RETRIEVE_MULTIPLE_JIRA_ISSUES_RESPONSE,
  MOCK_SEARCH_JIRA_ISSUES_USING_JQL_RESPONSE
)

from jira_agent.agents.issues_agent.models import LLMResponseOutput
from jira_agent.agents.issues_agent.tools import _get_account_id_from_email, _create_jira_urlified_list

from jira_agent.utils.jira_client.client import JiraClient
from jira_agent.utils.dryrun_utils import dryrun_response

@dryrun_response(MOCK_RETRIEVE_MULTIPLE_JIRA_ISSUES_RESPONSE)
def _retrieve_multiple_jira_issues(user_email: str, project: str, num_jira_issues_to_retrieve: int) -> List:
  """
  Retrieve the latest Jira issues for a given user and project.

  Args:
    user_email (str): The email of the user.
    project (str): The Jira project to search in.
    num_jira_issues_to_retrieve (int, optional): The number of tickets to retrieve.

  Returns:
    List: A list of the top n Jira issues.
  """
  logging.info(f"Retrieving top {num_jira_issues_to_retrieve} Jira issues in Project {project} for user: {user_email}")

  if "@" not in user_email or "." not in user_email:
    raise ValueError("Invalid email address.")

  try:
    jira_api = JiraClient.get_jira_instance()
    account_id = _get_account_id_from_email(user_email)
    logging.info(f"Account ID for user {user_email}: {account_id}")
    issues = jira_api.search_issues(
      f"project={project} AND (reporter='{account_id}' OR assignee='{account_id}') ORDER BY created DESC",
      maxResults=num_jira_issues_to_retrieve,
    )
    issues_md_list = _create_jira_urlified_list(issues)
    return issues_md_list
  except Exception as e:
    raise ValueError(f"Error retrieving service desk tickets: {e}")

@dryrun_response(MOCK_SEARCH_JIRA_ISSUES_USING_JQL_RESPONSE)
def _search_jira_issues_using_jql(jql_query: str, user_email: str) -> List:
  """
  Search for Jira tickets based on a JQL query and user_email.

  Args:
    jql_query (str): The JQL query string.
    user_email (str): The email of the user.

  Returns:
    list: List of Jira issue IDs in a markdown format.
  """
  logging.info(f"Searching tickets with JQL: {jql_query} for user: {user_email}")
  try:
    jira_api = JiraClient.get_jira_instance()
    issues = jira_api.search_issues(jql_query)
    logging.info(f"Issues found: {issues}")
    if not issues:
      raise ValueError("Seems like there are no tickets to display with your query.")
    issues_md_list = _create_jira_urlified_list(issues)
    return issues_md_list
  except Exception as e:
    raise ValueError(f"Error searching Jira tickets: {e}")

def search_jira_issues_using_jql(jql_query: str, user_email: str) -> LLMResponseOutput:
  """
  Search for Jira tickets based on a JQL query and user_email.

  Args:
    jql_query (str): The JQL query string.
    user_email (str): The email of the user.

  Returns:
    LLMResponseOutput: List of Jira issue IDs in a markdown format.
  """
  try:
    resp_str = _search_jira_issues_using_jql(jql_query, user_email)
    return LLMResponseOutput(response=json.dumps(resp_str, indent=2))
  except ValueError as e:
    return LLMResponseOutput(response=INTERNAL_ERROR_MESSAGE + ":" + str(e))