import os
import unittest
import logging
from unittest import TestCase
from graph.graph import JiraGraph

from tests.projects_helper import validate_env_vars
from tests.utils import get_tools_executed
from tests.projects_helper import get_project_by_key, project_update_description

from core.logging_config import configure_logging

from projects_agent.projects_utils import _get_jira_accountID_by_user_email

# Initialize logger
logger = configure_logging()


class TestPromptsProjects(unittest.TestCase):

    def setUp(self):

        # common setup for all tests

        # 1. Env var validation
        isEnvValid, msg = validate_env_vars()
        self.assertTrue(isEnvValid, msg)

        self.TEST_PROJECT_NAME = os.getenv("TEST_PROJECT_NAME")
        self.TEST_PROJECT_KEY = os.getenv("TEST_PROJECT_KEY")
        self.TEST_PROJECT_LEAD_EMAIL = os.getenv("TEST_PROJECT_LEAD_EMAIL")

        # 2. project name and key validation
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
        graph = JiraGraph()
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
        graph = JiraGraph()
        output, result = graph.serve(query)
        self.assertIsNotNone(output)

        tools_executed, tools_executed_dict = get_tools_executed(result)

        # check if expected tools were executed
        # create_project_tool not executed, as project already exists
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

    def test_update_project_description(self):

        # setup for this test - initialize project description to empty
        response = project_update_description(self.TEST_PROJECT_KEY, "")
        if response.status_code != 200:
            self.fail(
                "TestSetupFailure: Project description could not be initialized for project with key: " + self.TEST_PROJECT_KEY)

        # Run the test
        expected_description = "description updated by Alfred jira tests"
        query = f"update description for project {self.TEST_PROJECT_NAME} to {expected_description}"
        graph = JiraGraph()
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
        query = f"update lead for {self.TEST_PROJECT_NAME} to {self.TEST_PROJECT_LEAD_EMAIL}"
        graph = JiraGraph()
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
