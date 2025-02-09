from fastapi.security import APIKeyHeader
from ..core.config import settings

api_key_header = APIKeyHeader(
    name="X-StorageApi-Token",
    auto_error=True,
    description="Storage API authentication token"
)

async def validate_token(token: str = Depends(api_key_header)):
    # Example: Validate against GCP Secret Manager
    valid_tokens = await get_valid_tokens_from_secret_manager()
    
    if token not in valid_tokens:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    return token 