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

MOCK_CREATE_JIRA_ISSUE_RESPONSE = "http://mock.jira.instance.test/browse/TEST-123"
MOCK_ASSIGN_JIRA_RESPONSE = "JIRA ticket assigned successfully http://mock.jira.instance.test/browse/TEST-123."
MOCK_UPDATE_ISSUE_REPORTER_RESPONSE = "Reporter updated successfully on Jira http://mock.jira.instance.test/browse/TEST-123."
MOCK_ADD_NEW_LABEL_TO_ISSUE_RESPONSE = "Label added successfully on Jira http://mock.jira.instance.test/browse/TEST-123."
MOCK_GET_JIRA_ISSUE_DETAILS_RESPONSE = {
  "key": "TEST-123",
  "summary": "Mock issue summary",
  "description": "Mock issue description",
  "status": "Open",
  "priority": "High",
  "reporter": "Mock Reporter",
  "assignee": "Mock Assignee",
  "created": "2023-01-01T00:00:00.000Z",
  "updated": "2023-01-02T00:00:00.000Z"
}
MOCK_RETRIEVE_MULTIPLE_JIRA_ISSUES_RESPONSE = [
  "[TEST-123: Mock issue summary](http://mock.jira.instance.test/browse/TEST-123)"
]
MOCK_SEARCH_JIRA_ISSUES_USING_JQL_RESPONSE = [
  "[TEST-123: Mock issue summary](http://mock.jira.instance.test/browse/TEST-123)"
]
MOCK_GET_ACCOUNT_ID_FROM_EMAIL_RESPONSE = "mock_account_id"
MOCK_GET_SUPPORTED_JIRA_ISSUE_TYPES_RESPONSE = [
  "Bug",
  "Task",
  "Story"
]
MOCK_PERFORM_JIRA_TRANSITION_RESPONSE = "JIRA issue transitioned successfully. id: TEST-123"
MOCK_GET_REQUIRED_FIELDS_FOR_TRANSITION_RESPONSE = ["field1", "field2"]
MOCK_GET_JIRA_TRANSITIONS_RESPONSE = [
  {"id": "1", "name": "Start Progress"},
  {"id": "2", "name": "Resolve Issue"}
]