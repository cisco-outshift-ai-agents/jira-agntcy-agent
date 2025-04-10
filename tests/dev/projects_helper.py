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

import requests
import json

from src.utils.jira_client.rest import JiraRESTClient


def get_project_by_key(project_key: str):
    jira_server_url, auth, headers = JiraRESTClient.get_auth_instance()
    url = f"{jira_server_url}/rest/api/3/project/{project_key}"
    response = requests.get(url, headers=headers, auth=auth)
    return response


def project_update_description(project_key: str, description: str):
    jira_server_url, auth, headers = JiraRESTClient.get_auth_instance()
    url = f"{jira_server_url}/rest/api/3/project/{project_key}"
    payload = json.dumps({
        "description": description,
    })
    response = requests.put(url=url, data=payload, headers=headers, auth=auth)
    return response
