# Use the official Python image
FROM python:3

# Set the working directory
WORKDIR /usr/src/app

# Copy the dependencies file to the working directory
COPY requirements.txt ./
COPY poetry.lock pyproject.toml ./

RUN poetry --version

# Install Rust (required for some Python packages)
RUN apt-get update && apt-get install -y curl && curl https://sh.rustup.rs -sSf | sh -s -- -y && \
	export PATH="/root/.cargo/bin:$PATH" && \
	pip install --no-cache-dir -r requirements.txt

# Copy the content of the local app directory to the working directory
COPY . .

RUN poetry install

# Command to run on container start
CMD ["python", "./jira_agent/main.py"]
