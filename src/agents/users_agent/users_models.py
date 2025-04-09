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

from pydantic import BaseModel


# response from a jira user tool
class JiraUserOutput(BaseModel):
    """
    The output.
        Attributes:
        response (str): detail response.
    """
    response: str


class GetJiraAccountIdByUserEmailInput(BaseModel):
    """
    The input for get Jira account ID by user email.
        Attributes:
        user_email (str): The email of the user.
    """
    user_email: str