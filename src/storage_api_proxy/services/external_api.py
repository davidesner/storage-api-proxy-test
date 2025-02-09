import httpx
import json
from typing import Optional, Dict
import random
import string
import aiohttp
from ..core.config import get_settings

class ExternalApiClient:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = f"https://{self.settings.storage_api_host}/v2"
        self.client = httpx.AsyncClient()

    def _get_headers(self, token: str) -> Dict[str, str]:
        return {
            "X-StorageApi-Token": token,
            "Content-Type": "application/json"
        }

    async def get_token_details(self, token: str) -> Dict:
        """Verify token and get details"""
        response = await self.client.get(
            f"{self.base_url}/storage/tokens/verify",
            headers=self._get_headers(token)
        )
        
        if response.status_code != 200:
            error_data = response.json()
            raise Exception(error_data.get("message", "Failed to verify token"))
            
        return response.json()

    async def get_workspace(self, workspace_name: str, token: str) -> Optional[Dict]:
        """Simulate getting workspace details"""
        response = await self.client.get(
            f"{self.base_url}/storage/workspaces/{workspace_name}",
            headers=self._get_headers(token)
        )
        
        if response.status_code == 404:
            return None
        elif response.status_code != 200:
            error_data = response.json()
            raise Exception(error_data.get("message", "Failed to get workspace"))
            
        return response.json()

    async def create_workspace(self, token: str) -> Dict:
        """Create a new workspace"""
        # Get token details to create proper workspace name
        token_details = await self.get_token_details(token)
        workspace_name = f"MCP_{token_details['id']}_{token_details.get('description', 'workspace')}"
        
        payload = {
            "name": workspace_name,
            "backend": "snowflake",
            "readOnlyStorageAccess": True
        }
        
        response = await self.client.post(
            f"{self.base_url}/storage/workspaces?async=false",
            headers=self._get_headers(token),
            json=payload
        )
        
        if response.status_code != 201:
            error_data = response.json()
            raise Exception(error_data.get("message", "Failed to create workspace"))
            
        workspace_data = response.json()
        return {
            "id": workspace_data.get("id"),
            "name": workspace_data.get("name"),
            "credentials": {
                "host": workspace_data.get("connection", {}).get("host"),
                "warehouse": workspace_data.get("connection", {}).get("warehouse"),
                "database": workspace_data.get("connection", {}).get("database"),
                "schema": workspace_data.get("connection", {}).get("schema"),
                "user": workspace_data.get("connection", {}).get("user"),
                "password": workspace_data.get("connection", {}).get("password")
            }
        }

    async def reset_password(self, workspace_id: str, token: str) -> str:
        """Reset workspace password"""
        response = await self.client.post(
            f"{self.base_url}/storage/workspaces/{workspace_id}/password",
            headers=self._get_headers(token)
        )
        
        if response.status_code != 201:
            error_data = response.json()
            raise Exception(error_data.get("message", "Failed to reset password"))
            
        workspace_data = response.json()
        return workspace_data.get("password")
        

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose() 