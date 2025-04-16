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

from cisco_outshift_agent_utils.llm_factory import LLMFactory
import os
from dotenv import load_dotenv

def get_llm():
    """
    Get the LLM provider based on the configuration using LLMFactory.
    """
    load_dotenv()
    factory = LLMFactory(
        provider=os.getenv("LLM_PROVIDER"),
    )
    return factory.get_llm()
