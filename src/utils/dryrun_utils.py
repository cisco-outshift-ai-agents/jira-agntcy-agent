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
import logging
import asyncio


def dryrun_response(mock_response):
  def dryrun_response_decorator(func):
    async def dryrun_response_wrapper(*args, **kwargs):
      if os.getenv("DRYRUN") == "true":
        logging.info("Running in dry-run mode, returning mock data.")
        return mock_response
      return await func(*args, **kwargs)

    def sync_dryrun_response_wrapper(*args, **kwargs):
      if os.getenv("DRYRUN") == "true":
        logging.info("Running in dry-run mode, returning mock data.")
        return mock_response
      return func(*args, **kwargs)

    if asyncio.iscoroutinefunction(func):
      return dryrun_response_wrapper
    else:
      return sync_dryrun_response_wrapper

  return dryrun_response_decorator