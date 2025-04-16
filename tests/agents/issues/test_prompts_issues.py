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

import unittest
import logging

from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt
from graph.graph import JiraGraph
from tests.helper import contains_all_elements
from tests.helper import get_tools_executed, verify_llm_settings_for_test
# Initialize logger
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

# load environment variables from .env file
load_dotenv()

TEST_PROMPT_ISSUES_RETRY_COUNT = 5
@unittest.skipIf(not verify_llm_settings_for_test(), "Required test environment variables not set")
class TestPromptsIssues(unittest.TestCase):
  @classmethod
  def tearDownClass(cls):
    pass

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_add_new_label_to_issue(self):
    query = "add a new label 'urgent' to jira issue TEST-123"
    graph = JiraGraph()
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'add_new_label_to_issue']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_get_jira_issue_details(self):
    query = "get details of jira issue TEST-123"
    graph = JiraGraph()
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'get_jira_issue_details']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_create_jira_epic(self):
    query = "create an EPIC with title 'Epic 1' in project FOO"
    graph = JiraGraph()
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'create_jira_issue']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_perform_jira_transition(self):
    query = "transition jira issue TEST-123 to 'In Progress'"
    graph = JiraGraph()
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'perform_jira_transition']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_retrieve_multiple_jira_issues(self):
    query = "retrieve the latest 5 jira issues for user samuyang@cisco.com in project FOO"
    graph = JiraGraph()
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'search_jira_issues_using_jql']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_get_all_jira_issues_for_user_using_jql(self):
    query = "find a list of all my jiras (asked by user_email: samuyang@cisco.com)"
    graph = JiraGraph()
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'search_jira_issues_using_jql']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_search_jira_issues_using_jql(self):
    query = "search jira issues using JQL 'project = FOO AND status = Open'"
    graph = JiraGraph()
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'search_jira_issues_using_jql']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_create_jira_issue(self):
    query = "create a jira sushroff-custom-issue issue in project Foo, summary will be TBD, and then assign it to samuyang@cisco.com"
    graph = JiraGraph()
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'create_jira_issue']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_assign_jira(self):
    query = "for project FOO, assign the jira issue TEST-123 to samuyang@cisco.com"
    graph = JiraGraph()
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'assign_jira']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_update_issue_reporter(self):
    query = "for project FOO, update the reporter of jira issue TEST-123 to samuyang@cisco.com"
    graph = JiraGraph()
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'update_issue_reporter']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_get_jira_transitions(self):
    query = "for project FOO, get transitions for jira issue TEST-123"
    graph = JiraGraph()
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'get_jira_transitions']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

if __name__ == '__main__':
  unittest.main()