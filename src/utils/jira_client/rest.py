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
import os
import threading
import traceback
from typing import Tuple, Union

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

from .utils import is_jira_cloud_url, get_url_with_proper_scheme

class JiraRESTClient:
  _auth_instance = None
  _jira_server_url = None
  _jira_headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
  }
  _lock = threading.Lock()

  @classmethod
  def get_auth_instance(cls) -> Tuple[str, HTTPBasicAuth, dict]:
    with cls._lock:
      if cls._auth_instance is None:
        user_email = os.getenv("JIRA_USERNAME")
        access_token = os.getenv("JIRA_API_TOKEN")
        cls._auth_instance = HTTPBasicAuth(user_email, access_token)

      if cls._jira_server_url is None:
        cls._jira_server_url = os.getenv("JIRA_INSTANCE") or os.getenv("JIRA_URL")
        if is_jira_cloud_url(cls._jira_server_url):
          cls._jira_server_url = get_url_with_proper_scheme(cls._jira_server_url)

    return cls._jira_server_url, cls._auth_instance, cls._jira_headers

  @staticmethod
  def _send_request(
          method: str, url_path: str, payload: Union[dict, str, None] = None
  ) -> str:
    try:
      jira_instance, auth, headers = JiraRESTClient.get_auth_instance()
      url = f"{jira_instance}{url_path}"
      logging.info(f"Sending {method} request to: {url}")

      response = requests.request(
        method, url, headers=headers, auth=auth, json=payload
      )
      response.raise_for_status()
      logging.info(f"Received response: {response.status_code}")

      return json.dumps(
        json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")
      )

    except (Timeout, ConnectionError) as conn_err:
      return json.dumps({"error": "Connection timeout or failure", "exception": str(conn_err)})

    except HTTPError as http_err:
      return json.dumps({"error": "HTTP request failed", "exception": str(http_err)})

    except RequestException as req_err:
      return json.dumps({"error": "Request failed", "exception": str(req_err)})

    except json.JSONDecodeError as json_err:
      return json.dumps({"error": "Invalid JSON response", "exception": str(json_err)})

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