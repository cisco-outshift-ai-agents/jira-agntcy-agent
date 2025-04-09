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
import unittest
import logging

from dotenv import load_dotenv
from graph.graph import JiraGraph

from tests.helper import get_tools_executed

from agntcy_agents_common.config import Settings

from tests.helper import verify_llm_settings_for_test

# Initialize logger
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

# load environment variables from .env file
load_dotenv()

TEST_PROJECT_NAME="foo"
TEST_PROJECT_KEY="FOO"
TEST_PROJECT_LEAD_EMAIL="test_alfred_user@example.com"

@unittest.skipIf(not verify_llm_settings_for_test(), "Required test environment variables not set")
class TestPromptsProjects(unittest.TestCase):

    def get_mock_settings(self):
        return Settings(
            # We need real values for the following settings so the tool calling sequence can be tested. Either OpenAI or Azure settings must be set.
            # OpenAI Setting
            OPENAI_ENDPOINT=os.getenv("TEST_OPENAI_ENDPOINT"),
            OPENAI_API_KEY=os.getenv("TEST_OPENAI_API_KEY"),
            # Azure Setting
            AZURE_OPENAI_ENDPOINT=os.getenv("TEST_AZURE_OPENAI_ENDPOINT"),
            AZURE_OPENAI_API_KEY=os.getenv("TEST_AZURE_OPENAI_API_KEY"),
            AZURE_OPENAI_API_VERSION=os.getenv("TEST_AZURE_OPENAI_API_VERSION"),
            # Azure or OpenAI (default is Azure)
            LLM_PROVIDER=os.getenv("TEST_LLM_PROVIDER") or "azure",
        )

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_project_by_name(self):

        query = f"get details for my project {TEST_PROJECT_NAME}"
        graph = JiraGraph(self.get_mock_settings())
        output, result = graph.serve(query)
        self.assertIsNotNone(output)

        tools_executed, tools_executed_dict = get_tools_executed(result)

        # check if expected tools were executed
        tools_executed_expected = ['transfer_to_jira_projects_agent',
                                   'get_jira_project_by_name',
                                   'transfer_back_to_jira_supervisor']

        err_msg = (f"Tools executed do not match expected tools. "
                   f"Expected: {tools_executed_expected}, "
                   f"Actual: {tools_executed}")

        self.assertListEqual(tools_executed, tools_executed_expected, err_msg)

        # check if expected tools were executed with expected content
        self.assertRegex(tools_executed_dict['get_jira_project_by_name'], 'response=')

    def test_create_project_is_exists(self):

        query = (f"create a JIRA project for my venture {TEST_PROJECT_NAME} "
                 f"with key {TEST_PROJECT_KEY} "
                 f"and user {TEST_PROJECT_LEAD_EMAIL}")
        graph = JiraGraph(self.get_mock_settings())
        output, result = graph.serve(query)
        self.assertIsNotNone(output)

        tools_executed, _ = get_tools_executed(result)

        # create_project_tool must not be executed, as project already exists per mock response
        tools_not_expected = ['create_jira_project']

        err_msg = (f"Tools executed error. "
                   f"Tool Not Expected: {tools_not_expected}, "
                   f"Actual: {tools_executed}")

        self.assertTrue(not any(tool in tools_executed for tool in tools_not_expected), err_msg)

    def test_update_project_description(self):

        expected_description = "description updated by Alfred jira tests"
        query = f"update description for project {TEST_PROJECT_NAME} to {expected_description}"
        graph = JiraGraph(self.get_mock_settings())
        output, result = graph.serve(query)
        self.assertIsNotNone(output)

        tools_executed, tools_executed_dict = get_tools_executed(result)

        # check if expected tools were executed
        tools_executed_expected = ['transfer_to_jira_projects_agent',
                                   'get_jira_project_by_name',
                                   'update_jira_project_description',
                                   'transfer_back_to_jira_supervisor']

        err_msg = (f"Tools executed do not match expected tools. "
                   f"Expected: {tools_executed_expected}, "
                   f"Actual: {tools_executed}")

        self.assertListEqual(tools_executed, tools_executed_expected, err_msg)

        # check if expected tools were executed with expected content
        self.assertRegex(tools_executed_dict['get_jira_project_by_name'], 'response=')
        self.assertRegex(tools_executed_dict['update_jira_project_description'], 'response=')

    def test_update_project_lead(self):

        query = f"update lead for project {TEST_PROJECT_NAME} to {TEST_PROJECT_LEAD_EMAIL}"
        graph = JiraGraph(self.get_mock_settings())
        output, result = graph.serve(query)
        self.assertIsNotNone(output)

        tools_executed, tools_executed_dict = get_tools_executed(result)

        # check if expected tools were executed
        tools_executed_expected = ['transfer_to_jira_projects_agent',
                                   'get_jira_project_by_name',
                                   'update_jira_project_lead',
                                   'transfer_back_to_jira_supervisor']

        err_msg = (f"Tools executed do not match expected tools. "
                   f"Expected: {tools_executed_expected}, "
                   f"Actual: {tools_executed}")

        self.assertListEqual(tools_executed, tools_executed_expected, err_msg)

        # check if expected tools were executed with expected content
        self.assertRegex(tools_executed_dict['get_jira_project_by_name'], 'response=')
        self.assertRegex(tools_executed_dict['update_jira_project_lead'], 'response=')

if __name__ == '__main__':
  unittest.main()