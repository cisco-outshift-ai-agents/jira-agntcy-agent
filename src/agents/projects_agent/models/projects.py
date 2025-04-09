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


# response from a jira projects tool
class LLMResponseOutput(BaseModel):
  """
  The output.
      Attributes:
      response (str): detail response.
  """
  response: str


class GetJiraProjectByNameInput(BaseModel):
  """
  The input for get/search Jira project by name.
  https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-search-get
  https://<your instance>.atlassian.net/rest/api/3/project/search?query={{ProjectName}}
      Attributes:
      name (str): The name of the project.
  """
  name: str


class CreateJiraProjectInput(BaseModel):
  """
  The input for creating a Jira project.
      Attributes:
      name (str): The name of the project.
      key (str): The key of the project.
      leadAccountId: (str) : lead account ID.
      projectTypeKey: Optional[str] = "software" : project type.
      description: Optional[str] = "This project was created by the Jira Agent." : project description.
  """
  name: str
  key: str
  leadAccountId: str
  projectTypeKey: Optional[str] = "software"
  description: Optional[str] = "This project was created by the Jira Agent."


class UpdateJiraProjectDescriptionInput(BaseModel):
  """
  The input for updating a Jira project description.
      Attributes:
      key (str): The key of the project.
      description: (str) : description.
  """
  key: str
  description: str

class UpdateJiraProjectLeadInput(BaseModel):
  """
  The input for updating a Jira project lead.
      Attributes:
      key (str): The key of the project.
      leadAccountId: str : lead account ID. (Eg. 5b10a2844c20165700ede21g)
  """
  key: str
  leadAccountId: str
