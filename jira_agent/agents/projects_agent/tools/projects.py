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

from langchain_core.tools import tool

from jira_agent.common.logging_config import logging

from jira_agent.agents.projects_agent.models import LLMResponseOutput

from jira_agent.agents.projects_agent.models import (
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

@tool
def get_jira_project_by_name(input: GetJiraProjectByNameInput) -> LLMResponseOutput:
  """
  Get a Jira Project by name.

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
  logging.debug(f"tool input:{input}")
  resp = _get_jira_project_by_name(input)
  logging.debug(f"tool output:{resp}")
  return resp

@tool
def create_jira_project(input: CreateJiraProjectInput) -> LLMResponseOutput:
  """
  Create a jira project and return the output.

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
  logging.debug(f"tool input:{input}")
  resp = _create_jira_project(input)
  logging.debug(f"tool output:{resp}")
  return resp

@tool
def update_jira_project_description(input: UpdateJiraProjectDescriptionInput) -> LLMResponseOutput:
  """
  Update a jira project description and return the output.
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
  logging.debug(f"tool input:{input}")
  resp = _update_jira_project_description(input)
  logging.debug(f"tool output:{resp}")
  return resp

@tool
def update_jira_project_lead(input: UpdateJiraProjectLeadInput) -> LLMResponseOutput:
  """
  Update a jira project lead and return the output.

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
  logging.debug(f"tool input:{input}")
  resp = _update_jira_project_lead(input)
  logging.debug(f"tool output:{resp}")
  return resp
