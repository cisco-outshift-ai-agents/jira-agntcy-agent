import os
import unittest
import logging

from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt
from graph.graph import JiraGraph
from agntcy_agents_common.config import Settings
from tests.helper import contains_all_elements
from tests.helper import get_tools_executed, verify_llm_settings_for_test
# Initialize logger
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

# load environment variables from .env file
load_dotenv()

TEST_PROMPT_ISSUES_RETRY_COUNT = 3
@unittest.skipIf(not verify_llm_settings_for_test(), "Required test environment variables not set")
class TestPromptsIssues(unittest.TestCase):
  def get_mock_settings(self):
    return Settings(
      JIRA_INSTANCE="https://mock.jira.instance.test",
      TEST_USER_EMAIL="test_user@example.com",
      TEST_PROJECT_KEY="TEST",
      NUM_JIRA_ISSUES_TO_RETRIEVE=5,
      LANGCHAIN_TRACING_V2=False,
      LANGCHAIN_ENDPOINT="",
      LANGCHAIN_API_KEY="",
      LANGCHAIN_PROJECT="",
      LANGSMITH_API_KEY="",
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
      LLM_PROVIDER= os.getenv("TEST_LLM_PROVIDER") or "azure",
    )

  @classmethod
  def tearDownClass(cls):
    pass

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_add_new_label_to_issue(self):
    query = "add a new label 'urgent' to jira issue TEST-123"
    graph = JiraGraph(self.get_mock_settings())
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'add_new_label_to_issue']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_get_jira_issue_details(self):
    query = "get details of jira issue TEST-123"
    graph = JiraGraph(self.get_mock_settings())
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'get_jira_issue_details']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_perform_jira_transition(self):
    query = "transition jira issue TEST-123 to 'In Progress'"
    graph = JiraGraph(self.get_mock_settings())
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'perform_jira_transition']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_retrieve_multiple_jira_issues(self):
    query = "retrieve the latest 5 jira issues for user samuyang@cisco.com in project TEST"
    graph = JiraGraph(self.get_mock_settings())
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'search_jira_issues_using_jql']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_search_jira_issues_using_jql(self):
    query = "search jira issues using JQL 'project = TEST AND status = Open'"
    graph = JiraGraph(self.get_mock_settings())
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'search_jira_issues_using_jql']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_create_jira_issue(self):
    query = "create a jira issue in project TEST with summary 'Test Issue' and description 'This is a test issue.'"
    graph = JiraGraph(self.get_mock_settings())
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'create_jira_issue']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_assign_jira(self):
    query = "assign the jira issue TEST-123 to samuyang@cisco.com"
    graph = JiraGraph(self.get_mock_settings())
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'assign_jira']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_update_issue_reporter(self):
    query = "update the reporter of jira issue TEST-123 to samuyang@cisco.com"
    graph = JiraGraph(self.get_mock_settings())
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'update_issue_reporter']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

  @retry(stop=stop_after_attempt(TEST_PROMPT_ISSUES_RETRY_COUNT))
  def test_get_jira_transitions(self):
    query = "get transitions for jira issue TEST-123"
    graph = JiraGraph(self.get_mock_settings())
    output, result = graph.serve(query)
    self.assertIsNotNone(output)

    tools_executed, _ = get_tools_executed(result)
    logging.info(f"tools_executed: {tools_executed}")
    tools_executed_expected = ['transfer_to_jira_issues_agent', 'get_jira_transitions']
    self.assertTrue(contains_all_elements(tools_executed, tools_executed_expected))

if __name__ == '__main__':
  unittest.main()