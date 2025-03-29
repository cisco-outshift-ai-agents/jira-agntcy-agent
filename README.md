# Jira AI Agent

## About the Project

This repository contains a Jira AI Agent Protocol FastAPI application. It also includes examples of JSON-based logging, CORS configuration, and route tagging.

## Prerequisites

- Python 3.12+
- A virtual environment is recommended for isolating dependencies.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/cisco-outshift-alfred/jira-agntcy-agent.git
   cd jira-agent
   ```

2. Install the dependencies in your virtual environment:

   ```bash
   python -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```

## Usage

### Required Environment Variables
Before running the application, ensure you have the following environment variables set in your .env file or in your environment:

#### **🔹 OpenAI API Configuration**

If configuring your AI agent to use OpenAI as its LLM provider, set these variables:

```dotenv
# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_API_VERSION=gpt-4o  # Specify the model name
OPENAI_TEMPERATURE=0.7    # Adjust temperature for response randomness
```

---

#### **🔹 Azure OpenAI API Configuration**

If configuring your AI agent to use Azure OpenAI as its LLM provider, set these variables:

```dotenv
# Azure OpenAI API Configuration
AZURE_OPENAI_API_KEY=your-azure-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name  # Deployment name in Azure
AZURE_OPENAI_API_VERSION=your-azure-openai-api-version  # API version
OPENAI_TEMPERATURE=0.7 # Adjust temperature for response randomness
```

---

#### **🔹 Jira Configuration**

TODO Cleanup.

```dotenv
JIRA_INSTANCE=Your Jira domain (Eg. example.atlassian.net).
JIRA_USERNAME=Your Jira email wih appropriate permissions.
JIRA_API_TOKEN=Your Jira API token.
JIRA_BASIC_AUTH_TOKEN=Your Jira Basic Auth token obtained as base64 encoded string of JIRA_USERNAME:JIRA_API_TOKEN.
```
```bash
echo -n user@example.com:api_token_string | base64
```

### Server

You can run the application by executing:

```bash
python app/main.py
```

### Expected Console Output

On a successful run, you should see logs in your terminal similar to the snippet below. The exact timestamps, process IDs, and file paths will vary:

```bash
python app/main.py
{"timestamp": "2025-03-14 18:04:29,821", "level": "INFO", "message": "Logging is initialized. This should appear in the log file.", "module": "logging_config", "function": "configure_logging", "line": 158, "logger": "app", "pid": 53852}
{"timestamp": "2025-03-14 18:04:29,821", "level": "INFO", "message": "Starting FastAPI application...", "module": "main", "function": "main", "line": 197, "logger": "app", "pid": 53852}
{"timestamp": "2025-03-14 18:04:29,822", "level": "INFO", "message": ".env file loaded from /Users/sushroff/Documents/AI/jira-agent/.env", "module": "main", "function": "load_environment_variables", "line": 47, "logger": "root", "pid": 53852}
INFO:     Started server process [53852]
INFO:     Waiting for application startup.
{"timestamp": "2025-03-14 18:04:29,851", "level": "INFO", "message": "Starting Jira Agent...", "module": "main", "function": "lifespan", "line": 71, "logger": "root", "pid": 53852}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8125 (Press CTRL+C to quit)
```

This output confirms that:

1. Logging is properly initialized.
2. The server is listening on `0.0.0.0:8125`.
3. Your environment variables (like `.env file loaded`) are read.


## Docker

Alternatively, you can run the application with Docker by building the Docker image and running the container.

- **Build the Docker Image**: Create a Docker image from the Dockerfile in the current directory.

  ```bash
  docker build -t your_docker_image_name .
  ```

- **Run the Docker Container**: Start a container from the built image, using the `.env` file for environment variables and mapping port 8125.

  ```bash
  docker run --env-file .env -p 8125:8125 your_docker_image_name
  ```


## AP REST Client

*Change to `client` folder*

*Update the user_prompt in `rest.py` to the desired prompt (sample prompts available in sample_prompts/*

The REST client connects to the AP endpoint for the Server running at the default port 8125

```bash
python rest.py
```
On a successful remote graph run you should see logs in your terminal similar to the snippet below:

```bash
{"timestamp": "2025-03-14 17:58:29,328", "level": "INFO", "message": "{'event': 'final_result', 'result': {'messages': [HumanMessage(content='is Alfred Plus Test a business project', additional_kwargs={}, response_metadata={}, id='6ddcc789-0196-4e24-86fc-f2119be43cdf'), HumanMessage(content='The project \"Alfred Plus Test\" is a software project, not a business project.', additional_kwargs={}, response_metadata={}, id='140ef897-cdb6-459d-914c-b5d2d2fd8281')]}}", "module": "rest", "function": "main", "line": 203, "logger": "graph_client", "pid": 51728}
```

Sample API request and response for running a remote graph AP request can be sent via:

*http://0.0.0.0:8125/docs#/Stateless%20Runs/Stateless%20Runs-run_stateless_runs_post*

```bash
curl -X 'POST' \
  'http://0.0.0.0:8125/api/v1/runs' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": "remote_agent",
    "input": {
        "query": "create a jira issue in project Alfred Plus Test, to implement an Agent"
    },
    "metadata": {
        "id": "c303282d-f2e6-46ca-a04a-35d3d873712d"
    }
}'

200 OK
{
  "agent_id": "remote_agent",
  "output": "The Jira issue to implement an Agent has been successfully created in the \"Alfred Plus Test\" project. You can view and manage the issue at [this link](https://cisco-eti-sandbox-858.atlassian.net/browse/APT-13).",
  "model": "gpt-4o",
  "metadata": {}
}
```


## Logging

- **Format**: The application is configured to use JSON logging by default. Each log line provides a timestamp, log level, module name, and the message.
- **Location**: Logs typically go to stdout when running locally. If you configure a file handler or direct logs to a centralized logging solution, they can be written to a file (e.g., `logs/app.log`) or shipped to another service.
- **Customization**: You can change the log level (`info`, `debug`, etc.) or format by modifying environment variables or the logger configuration in your code. If you run in Docker or Kubernetes, ensure the logs are captured properly and aggregated where needed.

## API Endpoints

By default, the API documentation is available at:

```bash
http://0.0.0.0:8125/docs
```

(Adjust the host and port if you override them via environment variable JIRA_AGENT_PORT.)

## Running as a LangGraph Studio 

You need to install Rust: <https://www.rust-lang.org/tools/install>

Run the server

*To see the graph for the end client using LangGraph AP*
```bash
cd client
langgraph dev
```
Upon successful execution, you should see:

![Langgraph Studio](./docs/imgs/remote-graph-1.png "Studio")


*To see the graph for the entire jira workflow server*
```bash
cd app
langgraph dev
```

Upon successful execution, you should see:

![Langgraph Studio](./docs/imgs/search-issues-readme.png "Studio")



## Roadmap

See the [open issues](TODO) for a list
of proposed features (and known issues).

## Contributing

Contributions are what make the open source community such an amazing place to
learn, inspire, and create. Any contributions you make are **greatly
appreciated**. For detailed contributing guidelines, please see
[CONTRIBUTING.md](CONTRIBUTING.md)

## License

Distributed under the Apache-2.0 License. See [LICENSE](LICENSE) for more
information.

## Contact

Sushama Shroff - @ssmails - sushroff@cisco.com
Samuel Yang - @samuyang - samuyang@cisco.com

Project Link: TODO

## Acknowledgements

This template was adapted from
[https://github.com/othneildrew/Best-README-Template](https://github.com/othneildrew/Best-README-Template).
