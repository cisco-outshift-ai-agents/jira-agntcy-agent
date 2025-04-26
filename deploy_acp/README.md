## Deploying and building an ACP compliant agent

This guide provides details for:
- Deploying an ACP compliant agent via workflow server manager. 
- Building/Modifying an agent to be ACP compliant, so it can be deployed and used via workflow server manager.

### Deploy an agent that is ACP compliant

1. Install Workflow Server manager (if not already installed on your system)

https://docs.agntcy.org/pages/agws/workflow_server_manager.html#getting-started


2. Deploy the Agent using workflow Server Manager

```bash
sushroff@SUSHROFF-M-7MJQ jira-agntcy-agent % ./wfsm deploy --manifestPath deploy_acp/jira_agent.json --envFilePath deploy_acp/jira_agent_env.yaml 

2025-04-22T17:08:57-07:00 INF compose file generated at: /Users/sushroff/.wfsm/compose-org.agntcy.jiraagent.yaml
...
2025-04-22T17:08:57-07:00 INF ---------------------------------------------------------------------
2025-04-22T17:08:57-07:00 INF ACP agent deployment name: org.agntcy.jiraagent
2025-04-22T17:08:57-07:00 INF ACP agent running in container: org.agntcy.jiraagent, listening for ACP requests on: http://127.0.0.1:54316
2025-04-22T17:08:57-07:00 INF Agent ID: 0ea38b60-12b7-41ea-88ed-f2e907a6411c
2025-04-22T17:08:57-07:00 INF API Key: b7a82c6f-428d-4db3-be39-09a22ca754f5
2025-04-22T17:08:57-07:00 INF API Docs: http://127.0.0.1:54316/agents/0ea38b60-12b7-41ea-88ed-f2e907a6411c/docs
2025-04-22T17:08:57-07:00 INF ---------------------------------------------------------------------
```
- Save the details of the agent. The details are also saved to a docker-compose file created on your local setup as indicated in the logs above.
- [Server APIs] (http://127.0.0.1:54316/agents/0ea38b60-12b7-41ea-88ed-f2e907a6411c/docs).
- '54316' is API_PORT value to be used by clients accessing the agents endpoints via ACP and workflow server.


3. View logs

The deploy command above, creates a docker container with the workflow server and the embedded agent code and exposes the ACP endpoints.
```bash
sushroff@SUSHROFF-M-7MJQ % docker ps
CONTAINER ID   IMAGE                                                                                                COMMAND                CREATED       STATUS       PORTS                     NAMES
548cb2722924   agntcy/wfsm-org.agntcy.jiraagent:5a9c590f17bd07e5a3476455633ae10d2b4de7ca5e4589c364d2a57809197c48    "/opt/start_agws.sh"   6 hours ago   Up 6 hours   0.0.0.0:54316->8000/tcp   orgagntcyjiraagent-org.agntcy.jiraagent-1

sushroff@SUSHROFF-M-7MJQ jira % docker logs -f 548cb2722924
2025-04-23 00:09:04 [agntcy_agents_common] [INFO] [configure_logging] Logging has been configured successfully.
2025-04-23 00:09:05 [root] [INFO] [_build_azure_llm] [LLM] AzureOpenAI deployment=gpt-4o api_version=2024-08-01-preview
2025-04-23 00:09:05 [root] [INFO] [_build_azure_llm] [LLM] AzureOpenAI deployment=gpt-4o api_version=2024-08-01-preview
2025-04-23 00:09:05 [root] [INFO] [_build_azure_llm] [LLM] AzureOpenAI deployment=gpt-4o api_version=2024-08-01-preview
2025-04-23 00:09:05 [agent_workflow_server.agents.load] [INFO] [_read_manifest] Loaded Agent Manifest from /opt/spec/manifest.json
2025-04-23 00:09:06 [agent_workflow_server.agents.load] [INFO] [_resolve_agent] Loaded Agent from /opt/agent-workflow-server/.venv/lib/python3.12/site-packages/jira_agent/build_graph.py
2025-04-23 00:09:06 [agent_workflow_server.agents.load] [INFO] [_resolve_agent] Agent Type: LangGraphAgent
2025-04-23 00:09:06 [agent_workflow_server.agents.load] [INFO] [load_agents] Registered Agent: '0ea38b60-12b7-41ea-88ed-f2e907a6411c'
2025-04-23 00:09:06 [agent_workflow_server.services.queue] [INFO] [start_workers] Starting 5 workers
INFO:     Started server process [7]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
2025-04-23 00:10:57 [agent_workflow_server.services.queue] [INFO] [log_run] (Worker 1) Background Run 24f99e0a-e399-467d-aaf5-5e7bb5c78c31 started
2025-04-23 00:10:59 [httpx] [INFO] [_send_single_request] HTTP Request: POST https://smith-project-agents.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview "HTTP/1.1 200 OK"
2025-04-23 00:10:59 [agent_workflow_server.services.queue] [INFO] [log_run] (Worker 1) Background Run 24f99e0a-e399-467d-aaf5-5e7bb5c78c31 succeeded: {'exec_s': 1.681283950805664, 'queue_s': 0.00820612907409668, 'attempts': 1}

```

4. Send a request to the Agent
- ACP request can be sent directly to the server via 'Server API' link provided in step 3 above.
- ACP requests can be sent via clients similar to jira_agntcy_agents/clients/acp_client 

### Create an Agent that is ACP complaint and can be deployed via Workflow Server Manager

Ref: https://github.com/agntcy/acp-sdk/tree/main/examples/echo-agent)

1. create manifest for the agent similar to [this manifest](https://github.com/agntcy/acp-sdk/blob/main/examples/echo-agent/deploy/echo-agent.json)
- Follow the manifest format from the above example.
- update the langgraph entry point as part of the deployment options in the manifest.
- update the env variables in the manifest, based on the env variables required by your agent.
  Note - manifest file uses these [models](https://github.com/agntcy/acp-sdk/blob/main/examples/echo-agent/echo_agent/state.py)
2. create env file for the agent based on [this env file](https://github.com/agntcy/acp-sdk/blob/main/examples/echo-agent/deploy/echo_agent_example.yaml)
3. agent code must follow the exact directory structure and naming similar to above example.
4. use poetry setup with pyproject.toml and install the agent module. 
5. agent name must match configs in manifest file.
