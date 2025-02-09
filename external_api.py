import requests
import json
from typing import Optional, Dict
import random
import string

class ExternalApiClient:
    def __init__(self, base_url: str = "https://connection.keboola.com/v2"):
        self.base_url = base_url

    def _get_headers(self, token: str) -> Dict[str, str]:
        return {
            "X-StorageApi-Token": token,
            "Content-Type": "application/json"
        }

    def get_token_details(self, token: str) -> Dict:
        """Verify token and get details"""
        response = requests.get(
            f"{self.base_url}/storage/tokens/verify",
            headers=self._get_headers(token)
        )
        
        if response.status_code != 200:
            error_data = response.json()
            raise Exception(error_data.get("message", "Failed to verify token"))
            
        return response.json()

    def get_workspace(self, workspace_name: str, token: str) -> Optional[Dict]:
        """Simulate getting workspace details"""
        response = requests.get(
            f"{self.base_url}/storage/workspaces/{workspace_name}",
            headers=self._get_headers(token)
        )
        
        if response.status_code == 404:
            return None
        elif response.status_code != 200:
            error_data = response.json()
            raise Exception(error_data.get("message", "Failed to get workspace"))
            
        return response.json()

    def create_workspace(self, token: str) -> Dict:
        """Create a new workspace"""
        # Get token details to create proper workspace name
        token_details = self.get_token_details(token)
        workspace_name = f"MCP_{token_details['id']}_{token_details.get('description', 'workspace')}"
        
        payload = {
            "name": workspace_name,
            "backend": "snowflake",
            "readOnlyStorageAccess": True
        }
        
        response = requests.post(
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

    def reset_password(self, workspace_name: str, token: str) -> Dict:
        """Reset workspace password"""
        response = requests.post(
            f"{self.base_url}/storage/workspaces/{workspace_name}/password",
            headers=self._get_headers(token)
        )
        
        if response.status_code != 200:
            error_data = response.json()
            raise Exception(error_data.get("message", "Failed to reset password"))
            
        workspace_data = response.json()
        return {
            "host": workspace_data.get("connection", {}).get("host"),
            "warehouse": workspace_data.get("connection", {}).get("warehouse"),
            "database": workspace_data.get("connection", {}).get("database"),
            "schema": workspace_data.get("connection", {}).get("schema"),
            "user": workspace_data.get("connection", {}).get("user"),
            "password": workspace_data.get("connection", {}).get("password")
        } 