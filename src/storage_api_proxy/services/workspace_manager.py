from ..services.database import WorkspaceDatabase
from ..services.locks import WorkspaceLocks
from ..services.external_api import ExternalApiClient
import hashlib

class WorkspaceManager:
    def __init__(self, db: WorkspaceDatabase):
        self.db = db
        self.locks = WorkspaceLocks()
        self.api_client = ExternalApiClient()

    async def generate_workspace_name(self, token: str) -> str:
        """Generate workspace name from token details"""
        token_details = await self.api_client.get_token_details(token)
        return f"MCP_{token_details['id']}_{token_details.get('description', 'workspace')}"

    async def get_or_create_workspace(self, token: str) -> dict:
        workspace_name = await self.generate_workspace_name(token)
        
        # First try to get credentials from cache
        workspace_data = await self.db.get_credentials(workspace_name)
        if workspace_data:
            return {
                "workspace_name": workspace_name,
                "workspace_id": str(workspace_data["id"]),
                "credentials": workspace_data["credentials"]
            }

        # Try to acquire lock
        if not await self.locks.acquire_lock(workspace_name):
            raise Exception("Timeout while waiting for workspace lock")

        try:
            # Check cache again after acquiring lock
            workspace_data = await self.db.get_credentials(workspace_name)
            if workspace_data:
                return {
                    "workspace_name": workspace_name,
                    "workspace_id": str(workspace_data["id"]),
                    "credentials": workspace_data["credentials"]
                }

            # Check if workspace exists
            workspace = await self.api_client.get_workspace(workspace_name, token)
            
            if workspace:
                # Workspace exists but credentials missing - reset password
                credentials = await self.api_client.reset_password(workspace_name, token)
                workspace_id = str(workspace.get("id"))
            else:
                # Create new workspace
                workspace_data = await self.api_client.create_workspace(token)
                credentials = workspace_data["credentials"]
                workspace_id = str(workspace_data["id"])

            # Store credentials in cache
            await self.db.store_credentials(workspace_name, workspace_id, credentials)
            return {
                "workspace_name": workspace_name,
                "workspace_id": workspace_id,
                "credentials": credentials
            }

        finally:
            await self.locks.release_lock(workspace_name) 