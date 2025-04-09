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

import threading

from jira import JIRA
from .config import JiraClientConfig, AUTH_TYPE_BASIC, AUTH_TYPE_TOKEN, AUTH_TYPE_OAUTH
from .utils import is_jira_cloud_url, get_url_with_proper_scheme

class JiraClient:
  _client = None
  _lock = threading.Lock()

  def __init__(self, config: JiraClientConfig | None = None):
    config = config or JiraClientConfig.from_env()
    if not config.url:
      raise ValueError("JIRA URL is required")

    if is_jira_cloud_url(config.url):
      config.url = get_url_with_proper_scheme(config.url)

    if config.auth_type.lower() == AUTH_TYPE_BASIC:
      if not config.username or not config.api_token:
        raise ValueError("Username and API token are required for basic authentication")
      self.client = JIRA(server=config.url, basic_auth=(config.username, config.api_token))

    elif config.auth_type.lower() == AUTH_TYPE_TOKEN:
      if not config.username or not config.personal_access_token:
        raise ValueError("Username and personal access token are required for token authentication")
      self.client = JIRA(server=config.url, token_auth=config.personal_access_token)

    elif config.auth_type.lower() == AUTH_TYPE_OAUTH:
      if not config.oauth_credentials:
        raise ValueError("OAuth credentials are required for OAuth authentication")
      self.client = JIRA(server=config.url, oauth=config.oauth_credentials)

    else:
      raise ValueError("Unsupported authentication type. Use 'basic', 'token', or 'oauth'.")

  @classmethod
  def get_jira_instance(cls, client_config=None):
    if cls._client is None:
      with cls._lock:
        if cls._client is None:
          config = client_config or JiraClientConfig.from_env()
          cls._client = JiraClient(config).client
    return cls._client

