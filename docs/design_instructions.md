# API Endpoint Functionality Summary

This API endpoint acts as a proxy to execute SQL queries on a dedicated workspace for each user. Here's what it does:

- **Authentication via Header:**  
  The endpoint expects an API token to be provided in the request header named `X-StorageApi-Token`. This token is used to identify the user and to authenticate API calls to external services.

- **Workspace Management:**  
  Each user is associated with a unique workspace. The endpoint:
  - Generates a unique workspace name based on the user's token.
  - Checks an in-memory SQLite cache for stored workspace credentials.
  - If no credentials are found, it calls external APIs to either retrieve or create the workspace.
  - If the workspace exists but credentials are missing, it resets the workspace password to obtain new credentials.
  - Uses a simple locking mechanism to avoid race conditions when multiple requests for the same workspace occur simultaneously.

- **Query Execution:**  
  Once the workspace credentials are available:
  - The endpoint executes the provided SQL query using these credentials.
  - It simulates query execution and returns the results along with the workspace name.

- **Response:**  
  The endpoint responds with a JSON object containing:
  - The workspace name.
  - The result of the executed query.

Overall, the endpoint abstracts the complexity of workspace creation, credential management, and query execution, allowing users to simply submit their SQL queries with a valid API token.


# Instructions for Building a FastAPI Proxy Endpoint

This guide describes how to build a simple Python API using FastAPI. The endpoint will:

- Cache workspace credentials in an‑memory SQLite database.
- Use a simple locking mechanism to prevent race conditions.
- Include the API token in the header (`X-StorageApi-Token`) rather than in the request body.
- Reset the workspace password (and store new credentials) if the workspace exists but cached credentials are missing.

---

## 1. Project Structure

Organize your project with the following modules:

- **main.py:** Contains the FastAPI app and endpoint definitions.
- **database.py:** Handles the in‑memory SQLite database and related functions.
- **locks.py:** Implements a simple locking mechanism using Python's threading.
- **external_api.py:** Contains functions that simulate calls to external APIs (get workspace, create workspace, reset password).
- **workspace_management.py:** Contains business logic to retrieve or create a workspace and handle credentials.
- **execute_query.py:** Contains the function to execute the SQL query using workspace credentials.

---

## 2. Database Module (database.py)

**Objective:**  
Cache the workspace credentials using an in‑memory SQLite database.

**Instructions:**

- Use Python's built‑in `sqlite3` module to create an in‑memory database.
- Configure the connection with `check_same_thread=False` so that it can be accessed by multiple threads.
- Create a table (for example, `workspace_credentials`) with the following columns:
  - `workspace_name` (TEXT, set as the primary key)
  - `credentials` (TEXT)
  - `updated_at` (DATETIME)
- Write one function that retrieves credentials by workspace name and another function that stores (or updates) the credentials along with a timestamp.

---

## 3. Locking Module (locks.py)

**Objective:**  
Prevent multiple concurrent requests from creating or resetting a workspace simultaneously.

**Instructions:**

- Import Python's `threading` module.
- Maintain a global dictionary (or similar structure) that maps keys (such as workspace names) to individual locks.
- Create a function that accepts a key (e.g., the workspace name) and returns an associated lock. If the lock does not exist for that key, the function should create one and store it in the dictionary.
- Implement 10-second timeout for lock acquisition
- Add timeout handling in lock acquisition logic
- Note: Thread-based locking may not work with multiple FastAPI workers

---

## 4. External API Module (external_api.py)

**Objective:**  
Simulate interaction with an external API that handles workspace operations.

**Instructions:**

- Write a function to simulate retrieving a workspace by name. This function should include the API token in the request header (use the header name `X-StorageApi-Token` in your implementation) when making an HTTP GET request.
- Write a function to simulate creating a workspace. This function should generate random credentials (for example, a random string) and return a response that includes the workspace name and the credentials. Ensure the API token is sent in the header.
- Write a function to simulate resetting the workspace password. This function should also generate new credentials and return them in a simulated response.
- *Note:* In a real-world scenario, you would use a library like `requests` to make actual HTTP calls, ensuring the API token is passed via the header.
- Propagate external API errors directly to client
- Simulate error responses matching Keboola API formats:
  ```json
  {
    "error": "invalid_token",
    "message": "Provided token is invalid"
  }
  ```
- Workspace creation API specification:
  Use this documentation @https://keboola.docs.apiary.io/#reference/workspaces/workspaces-collection/create-workspace
  Required parameters:
  ```json
  {
    "backend": "snowflake",
    "readOnlyStorageAccess": true
  }
  ```
  Query parameter: `async=false`

---

## 5. Workspace Management Logic (workspace_management.py)

**Objective:**  
Implement the logic to retrieve an existing workspace or create a new one, including handling of cached credentials.

**Instructions:**

- Create a function that generates a unique workspace name using a hash of the user token. This name will be used as a key in the database.
- First, try to retrieve the credentials for the generated workspace name from the SQLite cache.
- If credentials are found, return them along with the workspace name.
- If no credentials are found, call the external API function to check if the workspace already exists.
- If the workspace exists but the credentials are missing in your cache, call the reset password API to obtain new credentials, store these new credentials in the cache, and then return them.
- If the workspace does not exist, acquire a lock for the workspace name to prevent concurrent creation:
  - Inside the lock, re-check the cache and workspace existence.
  - If still missing, call the create workspace API to create the workspace, cache the returned credentials, and return them.

---

## 6. Query Execution Function (execute_query.py)

**Objective:**  
Simulate executing a SQL query using the workspace credentials.

**Instructions:**

- Write a function that accepts two parameters: the workspace credentials and a SQL query string.
- In a production implementation, this function would use the credentials to establish a connection to the actual database (for example, Snowflake) and execute the SQL query.
- For simulation purposes, have the function return a JSON-like response that includes the executed query, the credentials used, and a sample or simulated query result.
- Return structured response format:
  ```json
  {
    "columns": ["id", "name"],
    "rows": [
      [1, "example"],
      [2, "test"]
    ]
  }
  ```
- No SQL validation required in simulation

---

## 7. FastAPI Endpoint (main.py)

**Objective:**  
Implement the FastAPI endpoint that ties everything together.

**Instructions:**

- Import FastAPI and necessary modules such as `HTTPException` and `Header` from FastAPI.
- Create a new FastAPI app instance.
- Define a Pydantic model for the request body. This model should include the SQL query string only (do not include the API token here).
- Define a POST endpoint (e.g., `/query`) that:
  - Reads the SQL query from the request body.
  - Reads the API token from the request header named `X-StorageApi-Token`.
  - Validates that the API token is present; if not, return an appropriate error (e.g., 401 Unauthorized).
  - Calls the workspace management logic to either retrieve or create the workspace. Use the API token for any external API calls.
  - Calls the query execution function to simulate executing the provided SQL query with the obtained workspace credentials.
  - Returns a response that includes the workspace name and the result of the executed query.

---

By following these instructions, you will build a FastAPI application that:

- Caches credentials in an in‑memory SQLite database.
- Uses a simple locking mechanism to manage concurrency.
- Reads the API token from the header (`X-StorageApi-Token`).
- Resets and caches credentials if a workspace exists but credentials are missing.

# Updates to Design Instructions

## 1. Workspace Name Generation (Updated)
- Format: `MCP_{token_id}_{token_description}`
- Obtain token details from Keboola's Token Verification API:
  ```text
  GET https://keboola.docs.apiary.io/#reference/tokens-and-permissions/token-verification/token-verification
  ```

## 2. Credential Storage (Clarified)
- Encryption/decryption flow:
  ```python
  # Before storage
  encrypted_username = xor_cipher(raw_username, key)
  
  # When retrieving
  raw_username = xor_cipher(encrypted_username, key)
  ```

## 3. Error Handling (Updated)
- Use standard HTTP codes:
  - 401 Unauthorized: Missing/invalid token
  - 504 Gateway Timeout: External API timeout
  - 502 Bad Gateway: External API error
- No automatic retries for transient failures

## 4. Query Execution (Updated)
- No SQL validation required in simulation

## 5. Security (Updated)
- Password complexity handled by Keboola API
- Reference: Password Reset API
  ```text
  POST https://keboola.docs.apiary.io/#reference/workspaces/password-reset/password-reset
  ```

## 6. Database (Updated)
- Change from in-memory to file-based SQLite:
  ```python
  # database.py
  conn = sqlite3.connect('workspaces.db', check_same_thread=False)
  ```

## 7. Concurrency (Clarified)
- Locking mechanism designed for low concurrency (<100 concurrent requests)
- No special optimizations required

## 8. Testing (Clarified)
- Basic functional tests sufficient for initial implementation
- Performance testing deferred