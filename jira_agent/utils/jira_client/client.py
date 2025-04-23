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
from .config import JiraConfig

class JiraClient:
  _client = None
  _lock = threading.Lock()

  def __init__(self, config: JiraConfig | None = None):
    config = config or JiraConfig()
    if config.JIRA_AUTH_TYPE == "basic":
      self.client = JIRA(server=config.JIRA_INSTANCE, basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN))
    elif config.JIRA_AUTH_TYPE == "token":
      self.client = JIRA(server=config.JIRA_INSTANCE, token_auth=config.JIRA_PERSONAL_ACCESS_TOKEN)
    elif config.JIRA_AUTH_TYPE == "oauth":
      self.client = JIRA(server=config.JIRA_INSTANCE, oauth=config.JIRA_OAUTH_CREDENTIALS)
    else:
      raise ValueError("Unsupported authentication type.")

  @classmethod
  def get_jira_instance(cls, config: JiraConfig | None = None) -> JIRA:
    if cls._client is None:
      with cls._lock:
        if cls._client is None:
          config = config or JiraConfig()
          cls._client = JiraClient(config).client
    return cls._client

