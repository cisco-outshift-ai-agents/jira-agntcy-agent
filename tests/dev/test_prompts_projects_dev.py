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
from tests.dev.projects_helper import get_project_by_key, project_update_description

from agents.projects_agent.tools.utils import _get_jira_accountID_by_user_email
from agntcy_agents_common.config import Settings

# Initialize logger
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

# load environment variables from .env file
load_dotenv()


def validate_env_vars():
    """
    Verifies that either OpenAI or Azure settings are set.
    Verifies that Jira settings are set.

    Returns:
        bool: True if settings are correct, False otherwise.
        str: Error message if neither settings are set.
    """

    print("DEV_TEST: ", os.getenv("DEV_TEST"))
    if not os.getenv("DEV_TEST"):
        return False, "DEV_TEST env variable is not set"

    openai_settings = [
        os.getenv("TEST_OPENAI_ENDPOINT"),
        os.getenv("TEST_OPENAI_API_KEY"),
    ]

    azure_settings = [
        os.getenv("TEST_AZURE_OPENAI_ENDPOINT"),
        os.getenv("TEST_AZURE_OPENAI_API_KEY"),
        os.getenv("TEST_AZURE_OPENAI_API_VERSION")
    ]

    jira_settings = [
        os.getenv("JIRA_INSTANCE"),
        os.getenv("JIRA_USERNAME"),
        os.getenv("JIRA_API_TOKEN"),
        os.getenv("TEST_PROJECT_NAME"),
        os.getenv("TEST_PROJECT_KEY"),
        os.getenv("TEST_PROJECT_LEAD_EMAIL")
    ]

    if all(openai_settings) and all(jira_settings):
        return True, ""
    elif all(azure_settings) and all(jira_settings):
        return True, ""
    else:
        return False, "Either OpenAI or Azure settings must be set. Jira settings must be set"

    return True, ""


@unittest.skipIf(not validate_env_vars(), "Required test environment variables not set")
class TestPromptsProjectsDev(unittest.TestCase):

    def get_settings(self):
        return Settings(
            OPENAI_TEMPERATURE=0.7,
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

    def setUp(self):

        # common setup for all tests
        self.TEST_PROJECT_NAME = os.getenv("TEST_PROJECT_NAME")
        self.TEST_PROJECT_KEY = os.getenv("TEST_PROJECT_KEY")
        self.TEST_PROJECT_LEAD_EMAIL = os.getenv("TEST_PROJECT_LEAD_EMAIL")

        # project name and key validation
        response = get_project_by_key(self.TEST_PROJECT_KEY)
        if response.status_code == 404:
            self.fail(
                "TestSetupFailure: Please use a valid jira project key. Project with key does not exist: " + self.TEST_PROJECT_KEY)
        project = response.json()
        self.assertEqual(project['name'], self.TEST_PROJECT_NAME,
                         "env var must contain a valid jira project key and associated project name.")

        print("Test setup complete")

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_project_by_name(self):

        query = f"get details for my project {self.TEST_PROJECT_NAME}"
        graph = JiraGraph(self.get_settings())
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

        response = get_project_by_key(self.TEST_PROJECT_KEY)
        if response.status_code == 404:
            self.fail("Project with key does not exist: " + self.TEST_PROJECT_KEY)
        project = response.json()

        # check if the correct project url was returned in the tool response
        expected_regex = ".*" + project['self'] + ".*"
        self.assertRegex(tools_executed_dict['get_jira_project_by_name'], expected_regex,
                         "did not get the correct project")

    def test_create_project_is_exists(self):
        # Test - create a project that already exists - Implemented

        # Test - create a project that does not exist - Skipped
        # - intend to reuse same key for project creation testing-to avoid creating new projects each time.
        # - so we need to archive / delete the project after the testcase is run.
        # - but project archival/deletion will not allow creating project with same key for a timelimit(set by jira).
        # - even restoring the project reuses the key, so we cannot create a project with the same key again.

        query = (f"create a project for my venture {self.TEST_PROJECT_NAME} "
                 f"with key {self.TEST_PROJECT_KEY} "
                 f"and user {self.TEST_PROJECT_LEAD_EMAIL}")
        graph = JiraGraph(self.get_settings())
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

        # setup for this test - initialize project description to empty
        response = project_update_description(self.TEST_PROJECT_KEY, "")
        if response.status_code != 200:
            self.fail(
                "TestSetupFailure: Project description could not be initialized for project with key: " + self.TEST_PROJECT_KEY)

        # Run the test
        expected_description = "description updated by Alfred jira tests"
        query = f"update description for project {self.TEST_PROJECT_NAME} to {expected_description}"
        graph = JiraGraph(self.get_settings())
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

        # check if project description was updated as expected in jira
        response = get_project_by_key(self.TEST_PROJECT_KEY)
        if response.status_code == 404:
            self.fail("Project with key does not exist: " + self.TEST_PROJECT_KEY)

        project = response.json()
        self.assertEqual(project['description'], expected_description, "Project description was not updated")

    def test_update_project_lead(self):

        # setup for this test. check project lead valid
        expected_account_id = _get_jira_accountID_by_user_email(self.TEST_PROJECT_LEAD_EMAIL)
        if not expected_account_id:
            self.fail(
                "TestSetupFailure: Please use a valid user email. Jira User does not exist: " + self.TEST_PROJECT_LEAD_EMAIL)

        # Run the test
        query = f"update lead for project {self.TEST_PROJECT_NAME} to {self.TEST_PROJECT_LEAD_EMAIL}"
        graph = JiraGraph(self.get_settings())
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

        # check if project lead was updated as expected in jira
        response = get_project_by_key(self.TEST_PROJECT_KEY)
        if response.status_code == 404:
            self.fail("Project with key does not exist: " + self.TEST_PROJECT_KEY)
        project = response.json()

        self.assertEqual(project['lead']['accountId'], expected_account_id, "Project lead was not updated")
