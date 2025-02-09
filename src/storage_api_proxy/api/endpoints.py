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
    x_storageapi_token: Optional[str] = Header(None)
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
    workspace_data = await workspace_manager.get_or_create_workspace(storage_token)
    result = await execute_query(
        workspace_data["credentials"], 
        query_request.query
    )

    return QueryResponse(
        workspace_name=workspace_data["workspace_name"],
        workspace_id=workspace_data["workspace_id"],
        result=result
    )


@router.post("/workspace")
async def create_workspace(
    x_storageapi_token: str = Header(..., alias="X-StorageApi-Token")
):
    try:
        workspace_manager = get_workspace_manager()
        return await workspace_manager.get_or_create_workspace(x_storageapi_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 