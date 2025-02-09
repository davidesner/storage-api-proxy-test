import pytest
from unittest.mock import AsyncMock, patch

from storage_api_proxy.services.workspace_manager import WorkspaceManager
from storage_api_proxy.schemas.models import WorkspaceData, WorkspaceCredentials


@pytest.fixture
def workspace_manager():
    return WorkspaceManager("test-token")


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


@pytest.mark.asyncio
async def test_get_workspace_creates_new_workspace(workspace_manager, mock_workspace_data):
    with patch("storage_api_proxy.services.workspace_manager.create_workspace", 
              new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_workspace_data
        
        result = await workspace_manager.get_workspace()
        
        assert result == mock_workspace_data
        mock_create.assert_called_once_with("test-token") 