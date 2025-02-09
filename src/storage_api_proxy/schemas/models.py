from typing import List, Any
from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str


class QueryResult(BaseModel):
    columns: List[str]
    rows: List[List[Any]]


class QueryResponse(BaseModel):
    workspace_name: str
    workspace_id: str
    result: QueryResult


class WorkspaceCredentials(BaseModel):
    host: str
    port: int
    database: str
    schema: str
    warehouse: str
    user: str
    password: str


class WorkspaceData(BaseModel):
    workspace_id: str
    workspace_name: str
    credentials: WorkspaceCredentials 