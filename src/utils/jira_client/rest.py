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

from .config import JiraConfig
from requests.auth import HTTPBasicAuth
from typing import Tuple, Union
import requests
import json
import logging
import traceback

class JiraRESTClient:
  _config = None
  _auth_instance = None
  _jira_headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
  }

  @classmethod
  def initialize(cls, config: JiraConfig = None):
    """Initialize the JiraRESTClient with a JiraConfig instance."""
    cls._config = config or JiraConfig()
    cls._setup_auth()

  @classmethod
  def _setup_auth(cls):
    """Set up authentication based on the JiraConfig."""
    if cls._config.JIRA_AUTH_TYPE == "basic":
      cls._auth_instance = HTTPBasicAuth(
        cls._config.JIRA_USERNAME, cls._config.JIRA_API_TOKEN
      )
    elif cls._config.JIRA_AUTH_TYPE == "token":
      cls._jira_headers["Authorization"] = f"Bearer {cls._config.JIRA_PERSONAL_ACCESS_TOKEN}"
    elif cls._config.JIRA_AUTH_TYPE == "oauth":
      cls._auth_instance = None  # OAuth logic can be added here
      cls._jira_headers.update(cls._config.JIRA_OAUTH_CREDENTIALS)
    else:
      raise ValueError("Unsupported authentication type.")

  @classmethod
  def get_auth_instance(cls) -> Tuple[str, Union[HTTPBasicAuth, None], dict]:
    """Return the Jira server URL, authentication, and headers."""
    if cls._config is None:
      logging.info("JiraRESTClient is not initialized. Initializing with default JiraConfig...")
      cls.initialize()
      # Automatically initialize with default JiraConfig
      logging.info(cls._config, cls._auth_instance, cls._jira_headers)
    return cls._config.JIRA_INSTANCE, cls._auth_instance, cls._jira_headers

  @staticmethod
  def _send_request(method: str, url_path: str, payload: Union[dict, str, None] = None) -> str:
    try:
      jira_instance, auth, headers = JiraRESTClient.get_auth_instance()
      url = f"{jira_instance}{url_path}"
      logging.info(f"Sending {method} request to: {url}")

      response = requests.request(
        method, url, headers=headers, auth=auth, data=payload
      )
      response.raise_for_status()
      logging.info(f"Received response: {response.status_code}")

      return json.dumps(
        json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")
      )

    except Exception as e:
      return json.dumps(
        {
          "error": "Unexpected failure",
          "exception": str(e),
          "stack_trace": traceback.format_exc(),
        }
      )

  @classmethod
  def jira_request_get(cls, url_path: str) -> str:
    return cls._send_request("GET", url_path)

  @classmethod
  def jira_request_post(cls, url_path: str, payload: Union[dict, str]) -> str:
    return cls._send_request("POST", url_path, payload)

  @classmethod
  def jira_request_put(cls, url_path: str, payload: Union[dict, str]) -> str:
    return cls._send_request("PUT", url_path, payload)