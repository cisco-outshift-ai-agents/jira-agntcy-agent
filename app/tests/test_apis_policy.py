import json
import os
import pytest
import httpx
from fastapi.testclient import TestClient
from api.routes.policy import router, POLICY_DIR, POLICY_FILE_NAME

# python3 -m pytest tests/test_apis_policy.py

TEST_POLICY_DIR = POLICY_DIR
TEST_POLICY_FILE_NAME = POLICY_FILE_NAME

client = TestClient(router)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: Create the policy directory if it doesn't exist
    os.makedirs(TEST_POLICY_DIR, exist_ok=True)
    yield
    # Teardown: Remove the policy file if it exists
    policy_file = os.path.join(TEST_POLICY_DIR, TEST_POLICY_FILE_NAME)
    if os.path.exists(policy_file):
        os.remove(policy_file)


def test_policy_create(mocker):
    mocker.patch("api.routes.policy.validate_jira_auth", return_value=(True, ""))
    policy_data = {
        "jira_instance": "example.atlassian.net",
        "jira_auth": {
            "username": "JIRA User Email",
            "api_token": "JIRA Api Token"
        },
        "policy": "optional customer jira configuration information to be sent to the agent"
    }
    files = {"file": ("policy_sample.json", json.dumps(policy_data), "application/json")}
    response = client.post("/policy", files=files)
    assert response.status_code == 200
    assert response.json()["jira_instance"] == policy_data["jira_instance"]
    assert response.json()["jira_auth"]["username"] == policy_data["jira_auth"]["username"]
    assert response.json()["jira_auth"]["api_token"] == policy_data["jira_auth"]["api_token"]
    assert response.json()["policy"] == policy_data["policy"]


def test_policy_get(mocker):
    mocker.patch("api.routes.policy.validate_jira_auth", return_value=(True, ""))
    policy_data = {
        "jira_instance": "example.atlassian.net",
        "jira_auth": {
            "username": "JIRA User Email",
            "api_token": "JIRA Api Token"
        },
        "policy": "optional customer jira configuration information to be sent to the agent"
    }
    policy_file = os.path.join(TEST_POLICY_DIR, TEST_POLICY_FILE_NAME)
    with open(policy_file, "w") as f:
        f.write(json.dumps(policy_data))

    response = client.get("/policy")
    assert response.status_code == 200
    assert response.json()["jira_instance"] == policy_data["jira_instance"]
    assert response.json()["jira_auth"]["username"] == policy_data["jira_auth"]["username"]
    assert response.json()["jira_auth"]["api_token"] == policy_data["jira_auth"]["api_token"]
    assert response.json()["policy"] == policy_data["policy"]


def test_policy_delete():
    policy_data = {
        "jira_instance": "example.atlassian.net",
        "jira_auth": {
            "username": "JIRA User Email",
            "api_token": "JIRA Api Token"
        },
        "policy": "optional customer jira configuration information to be sent to the agent"
    }
    policy_file = os.path.join(TEST_POLICY_DIR, TEST_POLICY_FILE_NAME)
    with open(policy_file, "w") as f:
        f.write(json.dumps(policy_data))

    response = client.delete("/policy")
    assert response.status_code == 200
    assert response.json()["message"] == "Policy file deleted successfully"
    assert not os.path.exists(policy_file)
