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

from jira_agent.common.llm import get_llm

from langgraph.prebuilt import create_react_agent

from users_models import JiraUserOutput

from users_tools import get_jira_accountID_by_user_email


# NOT TO BE USED CURRENTLY
class UsersAgent:

    def __init__(self):
        self.name = "jira_users_agent"
        self.tools = [get_jira_accountID_by_user_email]
        self.prompt = ("You are a helpful agent. Only use the tools available."
                       "1. you can only handle users\n")

    def agent(self):
        agent = create_react_agent(
            name=self.name,
            model=get_llm(),
            tools=self.tools,
            prompt=self.prompt,
            response_format=JiraUserOutput
        )
        return agent
