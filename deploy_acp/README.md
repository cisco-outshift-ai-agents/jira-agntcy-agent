1. Install Workflow Server manager

Install workflow server manager
https://docs.agntcy.org/pages/agws/workflow_server_manager.html#getting-started

Check workflow server ok
sushroff@SUSHROFF-M-7MJQ % ./wfsm check
10:17PM INF Checking prerequisites for the command...
10:17PM INF excuting `/usr/local/bin/docker info` ...
10:17PM INF command `/usr/local/bin/docker info` succeeded
10:17PM INF Checking prerequisites check passed

2. Create/Modify Agent to be deployable via Workflow Server Manager

Ref: https://github.com/agntcy/acp-sdk/tree/main/examples/echo-agent)

- create manifest for the agent 
  1. use manifest generator script or follow the manifest format from the above example.
  2. update your input, output models, deployment type, langgraph entry point etc in the script)
  
- create env file for the agent (follow the format from the above example)

- agent code must follow the exact directory structure and naming similar to above example.
  (poetry setup with pyproject.toml and install the agent module)
  (agent name must match configs in manifest file)

3. Deploy the Agent using workflow Server Manager

```bash
sushroff@SUSHROFF-M-7MJQ echo-agent % ./wfsm deploy --manifestPath deploy_acp/jira_agent.json --envFilePath deploy_acp/jira_agent_env.yaml 

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
-> Note down the details of the agent. The details are also saved to a docker-compose file created on your local setup.
-> [APIs] (http://127.0.0.1:54316/agents/0ea38b60-12b7-41ea-88ed-f2e907a6411c/docs)
-> 54316 is API_PORT value to be used by clients


4. View logs
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