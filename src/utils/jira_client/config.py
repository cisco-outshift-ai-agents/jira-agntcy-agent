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
from typing import Literal, Optional, Any, Dict
import os

class JiraConfig(BaseSettings):
  JIRA_INSTANCE: str = Field(..., description="Jira instance URL")
  JIRA_AUTH_TYPE: Literal["basic", "token", "oauth"] = Field("basic", description="Authentication type")
  JIRA_USERNAME: Optional[str] = Field(None, description="Jira username")
  JIRA_API_TOKEN: Optional[str] = Field(None, description="Jira API token")
  JIRA_PERSONAL_ACCESS_TOKEN: Optional[str] = Field(None, description="Personal access token")
  JIRA_OAUTH_CREDENTIALS: Optional[Dict[str, Any]] = Field(None, description="OAuth credentials")

  class Config:
    env_file = ".env"
    extra = "ignore"

  @model_validator(mode="after")
  def validate_jira_config(self):
    if not self.JIRA_INSTANCE.startswith("https://") or self.JIRA_INSTANCE.endswith("/"):
      raise ValueError("JIRA_INSTANCE must be a valid HTTPS URL without trailing slash.")

    if self.JIRA_AUTH_TYPE == "basic":
      if not self.JIRA_USERNAME or not self.JIRA_API_TOKEN:
        raise ValueError("Both JIRA_USERNAME and JIRA_API_TOKEN are required for basic authentication.")
    elif self.JIRA_AUTH_TYPE == "token":
      if not self.JIRA_PERSONAL_ACCESS_TOKEN:
        raise ValueError("JIRA_PERSONAL_ACCESS_TOKEN is required for token authentication.")
    elif self.JIRA_AUTH_TYPE == "oauth":
      self.JIRA_OAUTH_CREDENTIALS = self.get_oauth_credentials()
      if not self.JIRA_OAUTH_CREDENTIALS:
        raise ValueError("OAuth credentials are required for OAuth authentication.")
    else:
      raise ValueError("Unsupported authentication type. Use 'basic', 'token', or 'oauth'.")
    return self

  @staticmethod
  def get_oauth_credentials() -> Dict[str, Any]:
    credentials = {
      "access_token": os.getenv("JIRA_OAUTH_ACCESS_TOKEN"),
      "access_token_secret": os.getenv("JIRA_OAUTH_ACCESS_TOKEN_SECRET"),
      "consumer_key": os.getenv("JIRA_OAUTH_CONSUMER_KEY"),
      "key_cert": os.getenv("JIRA_OAUTH_KEY_CERT"),
      "signature_method": os.getenv("JIRA_OAUTH_SIGNATURE_METHOD", "oauthlib.oauth1.SIGNATURE_HMAC_SHA1"),
    }

    missing_vars = [key for key, value in credentials.items() if value is None]
    if missing_vars:
      raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    return credentials