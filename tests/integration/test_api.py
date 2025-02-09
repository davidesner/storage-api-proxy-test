import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from storage_api_proxy.main import app
from storage_api_proxy.schemas.models import WorkspaceData, WorkspaceCredentials


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_workspace_data():
    return WorkspaceData(
        workspace_id="123",
        workspace_name="test_workspace",
        credentials=WorkspaceCredentials(
            host="test.snowflakecomputing.com",
            port=443,
            database="TEST_DB",
            schema="TEST_SCHEMA",
            warehouse="TEST_WH",
            user="test_user",
            password="test_password"
        )
    )


def test_query_endpoint_requires_token(client):
    response = client.post("/query", json={"query": "SELECT 1"})
    assert response.status_code == 401
    assert "Storage API token is required" in response.json()["detail"]


@patch("storage_api_proxy.services.workspace_manager.WorkspaceManager.get_workspace")
@patch("storage_api_proxy.services.query_executor.QueryExecutor.execute_query")
def test_query_endpoint_success(mock_execute, mock_get_workspace, client, mock_workspace_data):
    # Setup mocks
    mock_get_workspace.return_value = mock_workspace_data
    mock_execute.return_value = {
        "columns": ["number"],
        "rows": [[1]]
    }

    # Make request
    response = client.post(
        "/query",
        json={"query": "SELECT 1 as number"},
        headers={"X-StorageApi-Token": "test-token"}
    )

    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert data["workspace_id"] == "123"
    assert data["workspace_name"] == "test_workspace"
    assert data["result"]["columns"] == ["number"]
    assert data["result"]["rows"] == [[1]] 