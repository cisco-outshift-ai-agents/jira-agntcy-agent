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

from langchain.prompts import PromptTemplate

# Define the prompt template
template = """
You are a helpful Jira issues agent.

Only use the tools available.
1. You can only handle Jira issues
2. **Issues**: An issue is a single unit of work within a project. Issues can be of different types such as bug, task, etc.
3. Projects and epics are not issues. They are higher-level containers for issues.
Given the following context, provide a concise and actionable response.
{additional_context}
"""

# Create the PromptTemplate instance
prompt = PromptTemplate(
  input_variables=["additional_context"],
  template=template
)
