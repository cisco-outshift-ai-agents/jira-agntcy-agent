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

from langchain_openai import AzureChatOpenAI, ChatOpenAI
from .config import Settings

def get_llm(settings: Settings):
    """
    Get the LLM provider based on the configuration.
    """
    provider = settings.LLM_PROVIDER.lower()
    temperature = settings.OPENAI_TEMPERATURE
    if provider == "azure":
        return AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            openai_api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            temperature=temperature,
        )

    if provider == "openai":
        return ChatOpenAI(
            model_name=settings.OPENAI_API_VERSION,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_ENDPOINT,
            temperature=temperature,
        )
    raise ValueError(f"Unsupported LLM provider: {provider}")
