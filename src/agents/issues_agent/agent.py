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

from langgraph.prebuilt import create_react_agent

from agntcy_agents_common.llm import get_llm
from agntcy_agents_common.config import get_settings_from_env

from .models import LLMResponseOutput
from .tools import TOOLS
from .prompt import prompt

class IssuesAgent:
  def __init__(self, settings=None):
    self.settings = settings or get_settings_from_env()
    self.name = "jira_issues_agent"
    self.tools = TOOLS
    self.prompt = prompt.format(additional_context="")

  def agent(self):
    agent = create_react_agent(
      name=self.name,
      model=get_llm(self.settings),
      tools=self.tools,
      prompt=self.prompt,
      response_format=LLMResponseOutput
    )
    return agent