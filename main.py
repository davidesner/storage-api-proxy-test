from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from workspace_management import WorkspaceManager
from execute_query import execute_query
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
workspace_manager = WorkspaceManager()

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def run_query(
    request: QueryRequest,
    x_storageapi_token: str = Header(..., alias="X-StorageApi-Token")
):
    try:
        # Get or create workspace
        logger.debug(f"Getting workspace for query: {request.query}")
        workspace_data = workspace_manager.get_or_create_workspace(x_storageapi_token)
        logger.debug(f"Got workspace data: {workspace_data}")
        
        # Execute query
        logger.debug("Executing query...")
        result = execute_query(
            workspace_data["credentials"], 
            request.query
        )
        logger.debug(f"Query result: {result}")
        
        return {
            "workspace_name": workspace_data["workspace_name"],
            "workspace_id": workspace_data["workspace_id"],
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        if "invalid_token" in str(e):
            raise HTTPException(status_code=401, detail=str(e))
        elif "timeout" in str(e).lower():
            raise HTTPException(status_code=504, detail=str(e))
        else:
            raise HTTPException(status_code=502, detail=str(e)) 