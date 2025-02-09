# Storage API Proxy

A FastAPI-based proxy service for executing SQL queries in Keboola Storage API workspaces. The service automatically manages workspace creation, credentials caching, and query execution.

## Features

- Automatic workspace creation and management
- Credential caching for improved performance
- Concurrent access handling with workspace locking
- Snowflake query execution
- SQLite-based credential storage
- Docker containerization
- GCP Cloud Run deployment support

## Prerequisites

- Python 3.8 or higher
- Poetry for dependency management
- Docker (for containerized deployment)
- Google Cloud SDK (for GCP deployment)

## Local Installation

### Using Poetry

1. Clone the repository:
```bash
git clone git@github.com:davidesner/storage-api-proxy-test.git
cd storage-api-proxy-test
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Create a `.env` file from the template:
```bash
cp .env.example .env
```

4. Start the server:
```bash
poetry run uvicorn src.main:app --reload
```

### Using Docker

1. Clone the repository and navigate to it:
```bash
git clone git@github.com:davidesner/storage-api-proxy-test.git
cd storage-api-proxy-test
```

2. Build and run using docker-compose:
```bash
docker-compose up --build
```

## GCP Deployment

### Prerequisites
- Google Cloud SDK installed and configured
- Docker installed
- GCP project created and selected

### Deployment Steps

1. Enable required APIs:
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

2. Build and push the container to Google Container Registry:
```bash
# Set your project ID
export PROJECT_ID=your-project-id

# Build the container
gcloud builds submit --tag gcr.io/${PROJECT_ID}/storage-api-proxy

# Or build locally and push
docker build -t gcr.io/${PROJECT_ID}/storage-api-proxy .
docker push gcr.io/${PROJECT_ID}/storage-api-proxy
```

3. Deploy to Cloud Run:
```bash
gcloud run deploy storage-api-proxy \
  --image gcr.io/${PROJECT_ID}/storage-api-proxy \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Security Considerations

1. Enable Cloud Run Authentication:
```bash
# Deploy with authentication required
gcloud run deploy storage-api-proxy \
  --image gcr.io/${PROJECT_ID}/storage-api-proxy \
  --platform managed \
  --region us-central1 \
  --no-allow-unauthenticated
```

## Usage

### Local Usage

Execute a query:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -H "X-StorageApi-Token: your-keboola-storage-api-token" \
  -d '{"query": "SELECT current_timestamp() as now"}'
```

### Cloud Run Usage

Execute a query (with authentication):
```bash
# Get the URL
export SERVICE_URL=$(gcloud run services describe storage-api-proxy --format='value(status.url)')

# Get authentication token
export ID_TOKEN=$(gcloud auth print-identity-token)

# Execute query
curl -X POST "${SERVICE_URL}/query" \
  -H "Authorization: Bearer ${ID_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-StorageApi-Token: your-keboola-storage-api-token" \
  -d '{"query": "SELECT current_timestamp() as now"}'
```

### Example Response

```json
{
    "workspace_name": "MCP_123456_example@keboola.com",
    "workspace_id": "1234567890",
    "result": {
        "columns": ["NOW"],
        "rows": [["2025-02-09T07:45:21.247000-08:00"]]
    }
}
```

## API Documentation

### POST /query

Executes a SQL query in a Snowflake workspace.

**Headers:**
- `X-StorageApi-Token`: Your Keboola Storage API token (required)
- `Authorization`: Bearer token (required for Cloud Run with authentication)

**Request Body:**
```json
{
    "query": "string"  // SQL query to execute
}
```

**Response:**
```json
{
    "workspace_name": "string",  // Name of the workspace
    "workspace_id": "string",    // ID of the workspace
    "result": {
        "columns": ["string"],   // Array of column names
        "rows": [["string"]]     // Array of rows with values
    }
}
```

## Development

The project uses:
- FastAPI for the web framework
- SQLite for credential caching
- Poetry for dependency management
- Snowflake Connector for query execution

### Project Structure

- `src/main.py` - FastAPI application and endpoints
- `src/storage_api_proxy/` - Main package
  - `api/` - FastAPI routes
  - `core/` - Configuration and base classes
  - `schemas/` - Pydantic models
  - `services/` - Business logic

### Running Tests

```bash
poetry run pytest
```

## License

This project is licensed under the MIT License. 