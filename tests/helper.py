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

import os

def get_tools_executed(result):
  tools_executed = []
  tools_executed_dict = {}
  for message in result['messages']:
    if hasattr(message, 'tool_call_id'):
      if hasattr(message, 'name'):
        # print(f"\nTool: {message.name}, Content: {message.content}")
        tools_executed.append(message.name)
        tools_executed_dict[message.name] = message.content

  return tools_executed, tools_executed_dict

def verify_llm_settings_for_test():
  """
  Verifies that either OpenAI or Azure settings are set.

  Returns:
      bool: True if either OpenAI or Azure settings are set, False otherwise.
      str: Error message if neither settings are set.
  """
  print("DRYRUN: ", os.getenv("DRYRUN"))
  if not os.getenv("DRYRUN"):
    return False

  openai_settings = [
    os.getenv("OPENAI_ENDPOINT"),
    os.getenv("OPENAI_API_KEY"),
  ]

  azure_settings = [
    os.getenv("AZURE_OPENAI_ENDPOINT"),
    os.getenv("AZURE_OPENAI_API_KEY"),
    os.getenv("AZURE_OPENAI_API_VERSION")
  ]

  if all(openai_settings):
    return True, ""
  elif all(azure_settings):
    return True, ""
  else:
    return False, "Either OpenAI or Azure settings must be set."

def contains_all_elements(list1, list2):
  return all(elem in list1 for elem in list2)