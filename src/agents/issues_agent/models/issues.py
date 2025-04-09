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

from typing import Optional
from pydantic import BaseModel

class LLMResponseOutput(BaseModel):
  """
  The output for JIRA issues.

  Attributes:
      response (str): Detailed response.
  """
  response: str

class CreateJiraIssueInput(BaseModel):
  """
  The input for creating a Jira issue.

  Attributes:
      project_key (str): Jira Project Key.
      summary (str): The summary of the issue.
      description (str): The description of the issue.
      issue_type (Optional[str]): The type of the issue (e.g., "Bug", "Task").
      assignee_email (Optional[str]): The email of the assignee.
      reporter_email (Optional[str]): The email of the reporter.
  """
  project_key: str
  summary: str
  description: str
  issue_type: Optional[str] = "Task"
  reporter_email: Optional[str] = ""
  assignee_email: Optional[str] = ""

class GetJiraIssueInput(BaseModel):
  """
  The input for getting a JIRA issue.

  Attributes:
      issueIdOrKey (str): The ID or key of the issue.
  """
  issueIdOrKey: str