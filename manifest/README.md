## Overview
To create a manifest json for the jira agent that describes all the ACP specs of an agent, including schemas and protocol features.

## Requirements
- Python 3.12+
- A virtual environment is recommended for isolating dependencies.

## Installation
1. Clone the repository:

   ```bash
   git clone https://github.com/cisco-outshift-ai-agents/jira-agntcy-agent
   cd jira-agntcy-agent/manifest
   ```

2. Install the dependencies in your virtual env:

   ```bash
   pip install -r requirements-manifest.txt
   ```

## Running the Application

```bash
python generate_manifest.py
```

This will create a jira_agent_manifest.json for the jira agent.