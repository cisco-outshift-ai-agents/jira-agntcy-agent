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

from typing import Any, Callable, List

from .issues import (
  create_jira_issue,
  assign_jira,
  update_issue_reporter,
  add_new_label_to_issue,
  get_jira_issue_details,
  _get_account_id_from_email,
  _create_jira_urlified_list,
)

from .transitions import (
  perform_jira_transition,
  get_jira_transitions
)

from .search import (
  search_jira_issues_using_jql
)

TOOLS: List[Callable[..., Any]] = [
  create_jira_issue,
  assign_jira,
  update_issue_reporter,
  add_new_label_to_issue,
  get_jira_issue_details,
  perform_jira_transition,
  get_jira_transitions,
  search_jira_issues_using_jql
]

__all__ = [
  "_get_account_id_from_email",
  "_create_jira_urlified_list",
]