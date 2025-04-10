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

from pydantic_settings import BaseSettings
from pydantic import Field, model_validator

class JiraSettings(BaseSettings):
  JIRA_INSTANCE: str = Field(..., description="Jira instance URL")
  JIRA_USERNAME: str = Field(..., description="Jira username")
  JIRA_API_TOKEN: str = Field(..., description="Jira API token")

  class Config:
    env_file = ".env"
    extra = "ignore"

  @model_validator(mode="after")
  def validate_jira_settings(self):
    instance = self.JIRA_INSTANCE
    username = self.JIRA_USERNAME
    token = self.JIRA_API_TOKEN

    if not instance:
      raise ValueError("JIRA_INSTANCE is required")
    if not instance.startswith("https://") and not instance.startswith("http://"):
      raise ValueError("JIRA_INSTANCE must start with 'https://' or 'http://'")
    if not username:
      raise ValueError("JIRA_USERNAME is required")
    if not token:
      raise ValueError("JIRA_API_TOKEN is required")
    return self
