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

from langgraph_supervisor import create_supervisor

from common.llm import get_llm

from agents.projects_agent.agent import ProjectsAgent
from agents.issues_agent.agent import IssuesAgent

from .prompt import prompt

# SupervisorAgent acts as a router for the Jira agents.
class SupervisorAgent:

    def __init__(self):
        self.name = "jira_supervisor"
        self.tools = []
        self.agents = [ProjectsAgent().agent(), IssuesAgent().agent()]
        self.prompt = (prompt.format(additional_context=""))

    def agent(self):

        prompt = self.prompt

        # returns a state graph
        graph = create_supervisor(
            supervisor_name=self.name,
            tools=self.tools,
            agents=self.agents,
            model=get_llm(),
            prompt=prompt,
            add_handoff_back_messages=True,
            output_mode="full_history",
        )

        return graph
