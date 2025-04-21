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
import sys
from pathlib import Path
from agntcy_acp.manifest import (
    AgentManifest,
    AgentDeployment,
    DeploymentOptions,
    LangGraphConfig,
    EnvVar,
    AgentMetadata,
    AgentACPSpec,
    AgentRef,
    Capabilities,
    SourceCodeDeployment
)
# Get the absolute path of the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "./.."))
sys.path.insert(0, parent_dir)
from src.models.models import JiraRequest, JiraResponse, Config


manifest = AgentManifest(
    metadata=AgentMetadata(
        ref=AgentRef(name="org.agntcy.jira-agent", version="0.0.1", url=None),
        description="Agent that automates JIRA operations in response to natural language queries using LLM and domain specific sub-agents."),
    specs=AgentACPSpec(
        input=JiraRequest.model_json_schema(),
        output=JiraResponse.model_json_schema(),
        config=Config.model_json_schema(),
        capabilities=Capabilities(
            threads=None,
            callbacks=None,
            interrupts=None,
            streaming=None
        ),
        custom_streaming_update=None,
        thread_state=None,
        interrupts=None
    ),
    deployment=AgentDeployment(
        deployment_options=[
            DeploymentOptions(
                root = SourceCodeDeployment(
                    type="source_code",
                    name="src",
                    url="https://github.com/cisco-outshift-ai-agents/jira-agntcy-agent",
                    framework_config=LangGraphConfig(
                        framework_type="langgraph",
                        graph="clients.ap_client.client:build_graph"
                    )
                )
            )
        ],
        env_vars=[EnvVar(name="OPENAI_API_KEY", desc="Open AI API Key"),
                EnvVar(name="OPENAI_API_VERSION", desc="Open AI Version"),
                EnvVar(name="OPENAI_ENDPOINT", desc="Open AI Endpoint"),
                EnvVar(name="OPENAI_TEMPERATURE", desc="Open AI Temperature"),
                EnvVar(name="AZURE_OPENAI_API_KEY", desc="AZURE Open AI API Key"),
                EnvVar(name="AZURE_OPENAI_ENDPOINT", desc="AZURE Open AI Endpoint"),
                EnvVar(name="AZURE_OPENAI_DEPLOYMENT", desc="AZURE Open AI Deployment Name"),
                EnvVar(name="AZURE_OPENAI_API_VERSION", desc="AZURE Open AI API Version"),
                EnvVar(name="AZURE_OPENAI_TEMPERATURE", desc="AZURE Open AI Temperature"),
                EnvVar(name="LLM_PROVIDER", desc="LLM Provider"),
                EnvVar(name="JIRA_INSTANCE", desc="JIRA Instance"),
                EnvVar(name="JIRA_USERNAME", desc="JIRA Username"),
                EnvVar(name="JIRA_API_TOKEN", desc="JIRA Api Token"),]
    )
)

with open(f"{Path(__file__).parent}/jira_agent_manifest.json", "w") as f:
    f.write(manifest.model_dump_json(
        exclude_unset=True,
        exclude_none=True,
        indent=2
    ))
