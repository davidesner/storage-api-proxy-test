from fastapi import APIRouter, Depends, Header, HTTPException
from typing import Optional

from ..core.config import get_settings, Settings
from ..schemas.models import QueryRequest, QueryResponse
from ..services.workspace_manager import WorkspaceManager
from ..services.query_executor import execute_query
from ..services.database import WorkspaceDatabase

router = APIRouter()
db = WorkspaceDatabase()


async def get_storage_token(
    x_storageapi_token: Optional[str] = Header(None, alias="X-StorageApi-Token")
) -> str:
    """Get and validate the Storage API token from the request header."""
    if not x_storageapi_token:
        raise HTTPException(
            status_code=401,
            detail="Storage API token is required"
        )
    return x_storageapi_token


def get_workspace_manager() -> WorkspaceManager:
    """Get the workspace manager instance."""
    return WorkspaceManager(db)


@router.post("/query", response_model=QueryResponse)
async def run_query(
    query_request: QueryRequest,
    storage_token: str = Depends(get_storage_token),
    workspace_manager: WorkspaceManager = Depends(get_workspace_manager),
    settings: Settings = Depends(get_settings)
) -> QueryResponse:
    """Execute a SQL query in a Snowflake workspace."""
    try:
        workspace_data = await workspace_manager.get_or_create_workspace(storage_token)
    except Exception as e:
        if "Failed to verify token" in str(e):
            raise HTTPException(
                status_code=401,
                detail="Invalid Storage API token"
            )
        if "Timeout while waiting for workspace lock" in str(e):
            raise HTTPException(
                status_code=409,
                detail="Workspace is currently locked. Please try again in a few moments."
            )
        if "Failed to create workspace" in str(e):
            raise HTTPException(
                status_code=503,
                detail="Failed to create Keboola workspace. The service might be temporarily unavailable."
            )
        raise HTTPException(
            status_code=500,
            detail=f"Workspace error: {str(e)}"
        )

    try:
        result = await execute_query(
            workspace_data["credentials"], 
            query_request.query
        )
    except Exception as e:
        error_str = str(e).lower()
        if "incorrect username or password" in error_str or "is empty" in error_str:
            try:
                # Reset password and update credentials
                new_password = await workspace_manager.api_client.reset_password(
                    workspace_data["workspace_id"], 
                    storage_token
                )
                # Update credentials in database with new password
                new_credentials = {**workspace_data["credentials"], "password": new_password}
                await workspace_manager.db.store_credentials(
                    workspace_data["workspace_name"],
                    workspace_data["workspace_id"], 
                    new_credentials
                )
                # Retry query with new credentials
                result = await execute_query(new_credentials, query_request.query)
            except Exception as retry_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Query execution failed even after password reset: {str(retry_error)}"
                )
        elif "syntax error" in error_str:
            raise HTTPException(
                status_code=400,
                detail=f"SQL syntax error: {str(e)}"
            )
        elif "permission denied" in error_str:
            raise HTTPException(
                status_code=403,
                detail="Permission denied while executing query"
            )
        elif "timeout" in error_str:
            raise HTTPException(
                status_code=504,
                detail="Query execution timed out"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Query execution error: {str(e)}"
            )

    return QueryResponse(
        workspace_name=workspace_data["workspace_name"],
        workspace_id=workspace_data["workspace_id"],
        result=result
    )


@router.post("/workspace")
async def create_workspace(
    storage_token: str = Depends(get_storage_token),
    workspace_manager: WorkspaceManager = Depends(get_workspace_manager)
):
    """Create or get existing workspace."""
    try:
        return await workspace_manager.get_or_create_workspace(storage_token)
    except Exception as e:
        if "Failed to verify token" in str(e):
            raise HTTPException(
                status_code=401,
                detail="Invalid Storage API token"
            )
        if "Timeout while waiting for workspace lock" in str(e):
            raise HTTPException(
                status_code=409,
                detail="Workspace is currently locked. Please try again in a few moments."
            )
        if "Failed to create workspace" in str(e):
            raise HTTPException(
                status_code=503,
                detail="Failed to create Keboola workspace. The service might be temporarily unavailable."
            )
        raise HTTPException(
            status_code=500,
            detail=f"Workspace error: {str(e)}"
        ) 