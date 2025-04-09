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

from agents.supervisor_agent.supervisor_agent import SupervisorAgent
from langgraph.checkpoint.memory import InMemorySaver

# To run the standalone LangGraph Server:
# % pip install --upgrade "langgraph-cli[inmem]"
# % langgraph dev

# Builds the graph for use with LangGraph Studio

def graph():
  """
  Constructs and compiles a LangGraph instance.

  This function initializes a `SupervisorAgent` to create the base graph structure
  and uses an `InMemorySaver` as the checkpointer for the compilation process.

  The resulting compiled graph can be used to execute Supervisor workflow in LangGraph Studio.

  Returns:
  CompiledGraph: A fully compiled LangGraph instance ready for execution.
  """
  graph = SupervisorAgent().agent()

  checkpointer = InMemorySaver()
  return graph.compile(checkpointer=checkpointer)
