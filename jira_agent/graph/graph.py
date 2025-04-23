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

import logging
import os
import uuid
from typing import Optional

from jira_agent.agents.supervisor_agent.supervisor_agent import SupervisorAgent
from langgraph.checkpoint.memory import InMemorySaver
from jira_agent.utils.jira_client.config import JiraConfig

# If DRYRUN is set, we don't want to initialize Jira settings
def _init_jira_config() -> Optional[JiraConfig]:
  if os.getenv("DRYRUN"):
    return None
  return JiraConfig()

class JiraGraph:
  def __init__(self):
    """
    Initialize the JiraGraph as a LangGraph.
    """
    self.jira_config = _init_jira_config() # This is just for validation purposes
    self.graph = self.build_graph()

  def build_graph(self):
    """
    Build a LangGraph instance of the Jira graph.

    Returns:
      CompiledGraph: A compiled LangGraph instance.
    """
    graph = SupervisorAgent().agent()

    checkpointer = InMemorySaver()
    return graph.compile(checkpointer=checkpointer)

  def get_graph(self):
    return self.graph

  def serve(self, user_prompt: str):
    """
    Runs the LangGraph for Jira operations.

    Args:
      user_prompt str: user_prompt to serve.

    Returns:
      dict: Output data containing `jira_output`.
    """
    try:
      logging.info("Got user prompt: " + user_prompt)
      result = self.graph.invoke({
        "messages": [
          {
            "role": "user",
            "content": user_prompt
          }
        ],
      }, {"configurable": {"thread_id": uuid.uuid4()}})
      if logging.getLogger().isEnabledFor(logging.DEBUG):
        for m in result["messages"]:
          m.pretty_print()

      return result["messages"][-1].content, result

    except Exception as e:
      raise Exception("Jira operation failed: " + str(e))
