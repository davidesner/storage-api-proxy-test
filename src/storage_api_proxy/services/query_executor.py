from typing import Dict
import snowflake.connector
from snowflake.connector.cursor import SnowflakeCursor

async def execute_query(credentials: Dict, query: str) -> Dict:
    """
    Execute SQL query in Snowflake workspace
    """
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user=credentials["user"],
        password=credentials["password"],
        account=credentials["host"].split('.')[0],  # Extract account from host
        warehouse=credentials["warehouse"],
        database=credentials["database"],
        schema=credentials["schema"]
    )
    
    try:
        # Execute query
        cursor: SnowflakeCursor = conn.cursor()
        cursor.execute(query)
        
        # Get column names
        columns = [col[0] for col in cursor.description] if cursor.description else []
        
        # Fetch results
        rows = cursor.fetchall()
        
        return {
            "columns": columns,
            "rows": rows
        }
        
    finally:
        conn.close() 