# Jira AI Agent

## About the Project

This repository contains a Jira AI Agent Protocol FastAPI application. It also includes examples of JSON-based logging, CORS configuration, and route tagging.

## Prerequisites

- Python 3.12+
- A virtual environment is recommended for isolating dependencies.

## Installation

1. Clone the repository:

   ```bash
   git clone TODO
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

- LLM_PROVIDER: The language model provider (e.g., azure or openai).
- OPENAI_TEMPERATURE: The temperature setting for the language model (e.g., 0.7).
- AZURE_OPENAI_DEPLOYMENT_NAME: The deployment name for Azure OpenAI (required if using azure as LLM_PROVIDER).
- AZURE_OPENAI_ENDPOINT: The endpoint URL for Azure OpenAI (required if using azure as LLM_PROVIDER).
- AZURE_OPENAI_API_KEY: Your Azure OpenAI API key (required if using azure as LLM_PROVIDER).
- AZURE_OPENAI_API_VERSION: The API version for Azure OpenAI (required if using azure as LLM_PROVIDER).
- OPENAI_API_KEY: Your OpenAI API key (required if using openai as LLM_PROVIDER).
- OPENAI_API_VERSION: The model version for OpenAI (default is usually set to gpt-4o or similar).
##### TODO Required currently. These may be removed later, once policy is used to populate jira instance and token
- JIRA_INSTANCE: Your Jira base URL.
- JIRA_BASIC_AUTH_TOKEN: Your Jira Basic Auth token with adequate permissions to the Jira instance.

Make sure your .env file includes these keys with the appropriate values. For example:

```dotenv
LLM_PROVIDER=azure
OPENAI_TEMPERATURE=0.7
OPENAI_API_VERSION=gpt-4o
AZURE_OPENAI_ENDPOINT=https://your-azure-endpoint.com/
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_API_VERSION=2023-03-15-preview
# For OpenAI (if used)
OPENAI_API_KEY=your-openai-api-key

JIRA_INSTANCE=your-jira-instance.net
JIRA_BASIC_AUTH_TOKEN=your-jira-basic-auth-token
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

### Client

Change to `client` folder

```bash
python rest.py
```

On a successful remote graph run you should see logs in your terminal similar to the snippet below:

```bash
{"timestamp": "2025-03-14 17:58:29,328", "level": "INFO", "message": "{'event': 'final_result', 'result': {'messages': [HumanMessage(content='is Alfred Plus Test a business project', additional_kwargs={}, response_metadata={}, id='6ddcc789-0196-4e24-86fc-f2119be43cdf'), HumanMessage(content='The project \"Alfred Plus Test\" is a software project, not a business project.', additional_kwargs={}, response_metadata={}, id='140ef897-cdb6-459d-914c-b5d2d2fd8281')]}}", "module": "rest", "function": "main", "line": 203, "logger": "graph_client", "pid": 51728}
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

(Adjust the host and port if you override them via environment variables.)

## Running as a LangGraph Studio

You need to install Rust: <https://www.rust-lang.org/tools/install>

Run the server

```bash
langgraph dev
```

Upon successful execution, you should see:

![Langgraph Studio](./docs/imgs/remote-graph-1.png "Studio")

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
