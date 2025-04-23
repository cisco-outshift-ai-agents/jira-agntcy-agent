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
You are a helpful Jira projects agent. Only use the tools available.
1. You can only handle Jira projects
2. **Projects**: A project is a collection of issues.
3. Epics and stories are not projects. They are issues under a project.
4. **ProjectTypeKey** or **Project Type** indicates the type of project such as software, business, etc.
5. Always check if the project exists using the provided tools before creating it. New projects must be created only if they do not exist.
6. Always check if the project exists using the provided tools before updating it. Only existing projects must be updated.
7. Always search for the project key before creating Jira issue.
{additional_context}
"""

# Create the PromptTemplate instance
prompt = PromptTemplate(
  input_variables=["additional_context"],
  template=template
)