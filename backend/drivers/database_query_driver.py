"""
Database Query Driver - Secure Implementation
Handles SQL queries and internal API calls for automation workflows
"""

import logging
import asyncpg
import json
import requests
import uuid
import re
from typing import Dict, Any, List, Optional
from drivers.base_driver import BaseDriver

logger = logging.getLogger(__name__)

class DatabaseQueryDriver(BaseDriver):
    """
    Driver for executing database queries and internal API calls.
    Supports both direct SQL execution and HTTP API endpoints.
    """
    
    def __init__(self, db_pool=None):
        super().__init__()
        self.db_pool = db_pool
        self.allowed_sql_patterns = [
            r'^SELECT\s+.*',  # Allow SELECT queries
            r'^WITH\s+.*',    # Allow CTE queries
        ]
        self.blocked_sql_patterns = [
            r'DROP\s+',
            r'DELETE\s+',
            r'UPDATE\s+',
            r'INSERT\s+',
            r'ALTER\s+',
            r'CREATE\s+',
            r'TRUNCATE\s+',
            r'EXEC\s+',
            r'EXECUTE\s+',
            r'xp_\w+',  # SQL Server extended procedures
            r'sp_\w+',  # SQL Server system procedures
        ]
    
    async def execute(self, parameters: dict, input_data: dict, user_id: str, engine_instance=None) -> dict:
        """
        Execute database query or API call
        
        Parameters:
        - sql_query: Direct SQL query string (SELECT only for security)
        - api_endpoint: Internal API endpoint URL
        - method: HTTP method for API calls
        - query_params: Parameters for SQL or API body
        """
        logger.info(f"🗃️ DatabaseQueryDriver: Executing for user {user_id}")
        
        try:
            # 1. Parameter Validation
            sql_query = parameters.get("sql_query")
            api_endpoint = parameters.get("api_endpoint")
            method = parameters.get("method", "GET")
            query_params = parameters.get("query_params", {})
            
            # Require either sql_query OR api_endpoint
            if not sql_query and not api_endpoint:
                logger.error("DatabaseQueryDriver: Missing required parameters")
                return {
                    "status": "failed",
                    "error": "Must provide either 'sql_query' or 'api_endpoint'"
                }
            
            # 2. Execute based on type
            if sql_query:
                return await self._execute_sql_query(sql_query, query_params, user_id)
            elif api_endpoint:
                return await self._execute_api_request(api_endpoint, method, query_params, user_id)
            
        except Exception as e:
            logger.error(f"❌ DatabaseQueryDriver error: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": f"Database operation failed: {str(e)}"
            }
    
    async def _execute_sql_query(self, sql_query: str, query_params: dict, user_id: str) -> dict:
        """Execute SQL query with security validation"""
        try:
            # Security validation - only allow safe queries
            if not self._is_safe_sql_query(sql_query):
                logger.warning(f"🚨 Unsafe SQL query blocked for user {user_id}")
                return {
                    "status": "failed",
                    "error": "Query blocked for security reasons. Only SELECT and WITH queries are allowed."
                }
            
            # Get database connection
            if not self.db_pool:
                # Import db_manager if not provided
                from db.postgresql_manager import db_manager
                self.db_pool = db_manager.pool
            
            async with self.db_pool.acquire() as conn:
                # Set Row Level Security context
                await self._set_rls_context(conn, user_id)
                
                try:
                    # Execute parameterized query safely
                    if query_params:
                        rows = await self._execute_parameterized_query(conn, sql_query, query_params)
                    else:
                        rows = await conn.fetch(sql_query)
                    
                    # Convert to JSON-serializable format
                    result_data = []
                    for row in rows:
                        row_dict = {}
                        for key, value in row.items():
                            if isinstance(value, uuid.UUID):
                                row_dict[key] = str(value)
                            elif hasattr(value, 'isoformat'):  # datetime objects
                                row_dict[key] = value.isoformat()
                            else:
                                row_dict[key] = value
                        result_data.append(row_dict)
                    
                    logger.info(f"✅ SQL query executed successfully. Rows: {len(result_data)}")
                    return {
                        "status": "success",
                        "data": result_data,
                        "row_count": len(result_data),
                        "query_type": "sql"
                    }
                    
                except Exception as e:
                    logger.error(f"❌ SQL execution error: {e}")
                    return {
                        "status": "failed",
                        "error": f"SQL query failed: {str(e)}"
                    }
                finally:
                    await self._reset_rls_context(conn)
                    
        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")
            return {
                "status": "failed",
                "error": f"Database connection failed: {str(e)}"
            }
    
    async def _execute_api_request(self, api_endpoint: str, method: str, query_params: dict, user_id: str) -> dict:
        """Execute HTTP request to internal API"""
        try:
            # Validate API endpoint is internal
            if not self._is_internal_api(api_endpoint):
                logger.warning(f"🚨 External API blocked for user {user_id}: {api_endpoint}")
                return {
                    "status": "failed",
                    "error": "Only internal API endpoints are allowed"
                }
            
            # Prepare request
            headers = {
                "Content-Type": "application/json",
                "X-User-ID": user_id,  # Pass user context
                "X-Internal-Request": "true"
            }
            
            request_kwargs = {
                "method": method.upper(),
                "url": api_endpoint,
                "headers": headers,
                "timeout": 30  # 30 second timeout
            }
            
            # Add parameters based on method
            if method.upper() in ['POST', 'PUT', 'PATCH'] and query_params:
                request_kwargs["json"] = query_params
            elif method.upper() == 'GET' and query_params:
                request_kwargs["params"] = query_params
            
            # Execute request
            response = requests.request(**request_kwargs)
            response.raise_for_status()
            
            # Parse response
            try:
                response_data = response.json()
            except ValueError:
                response_data = {"text": response.text}
            
            logger.info(f"✅ API request to {api_endpoint} succeeded. Status: {response.status_code}")
            return {
                "status": "success",
                "data": response_data,
                "status_code": response.status_code,
                "query_type": "api"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API request error: {e}")
            return {
                "status": "failed",
                "error": f"API request failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"❌ Unexpected API error: {e}")
            return {
                "status": "failed",
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _is_safe_sql_query(self, sql_query: str) -> bool:
        """Validate SQL query for security"""
        sql_upper = sql_query.strip().upper()
        
        # Check blocked patterns first
        for pattern in self.blocked_sql_patterns:
            if re.search(pattern, sql_upper, re.IGNORECASE):
                logger.warning(f"🚨 Blocked SQL pattern detected: {pattern}")
                return False
        
        # Check allowed patterns
        for pattern in self.allowed_sql_patterns:
            if re.match(pattern, sql_upper, re.IGNORECASE):
                return True
        
        # If no allowed pattern matches, block it
        logger.warning(f"🚨 SQL query doesn't match allowed patterns")
        return False
    
    def _is_internal_api(self, api_endpoint: str) -> bool:
        """Check if API endpoint is internal/allowed"""
        internal_domains = [
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "::1",
            "api.internal",
            "db.internal"
        ]
        
        # Parse URL to check domain
        from urllib.parse import urlparse
        parsed = urlparse(api_endpoint)
        domain = parsed.hostname
        
        if not domain:
            return False
        
        # Check if it's an internal domain
        for internal_domain in internal_domains:
            if domain == internal_domain or domain.endswith(f".{internal_domain}"):
                return True
        
        # Check for internal IP ranges
        import ipaddress
        try:
            ip = ipaddress.ip_address(domain)
            return ip.is_private or ip.is_loopback
        except ValueError:
            pass
        
        return False
    
    async def _execute_parameterized_query(self, conn, sql_query: str, query_params: dict) -> List:
        """Execute parameterized query safely"""
        try:
            # Convert named parameters to positional parameters
            # This is a simplified approach - in production, use a proper SQL parser
            param_values = []
            modified_query = sql_query
            
            # Replace named parameters with positional ones
            for i, (key, value) in enumerate(query_params.items(), 1):
                placeholder = f"${i}"
                modified_query = modified_query.replace(f":{key}", placeholder)
                modified_query = modified_query.replace(f"{{{key}}}", placeholder)
                param_values.append(value)
            
            # Execute with positional parameters
            if param_values:
                rows = await conn.fetch(modified_query, *param_values)
            else:
                rows = await conn.fetch(modified_query)
            
            return rows
            
        except Exception as e:
            logger.error(f"❌ Parameterized query error: {e}")
            raise
    
    async def _set_rls_context(self, conn, user_id: str):
        """Set Row Level Security context"""
        try:
            # Check current user
            current_db_user = await conn.fetchval("SELECT current_user;")
            is_superuser = (current_db_user == 'postgres')
            
            # Set user context for RLS
            await conn.execute(f"SET app.current_user_id = '{user_id}';")
            
            if not is_superuser:
                await conn.execute("SET ROLE app_user;")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not set RLS context: {e}")
    
    async def _reset_rls_context(self, conn):
        """Reset Row Level Security context"""
        try:
            await conn.execute("RESET ROLE;")
            await conn.execute("RESET app.current_user_id;")
        except Exception as e:
            logger.warning(f"⚠️ Could not reset RLS context: {e}")
    
    def get_driver_info(self) -> dict:
        """Get driver information for automation engine"""
        return {
            "name": "database_query",
            "description": "Execute database queries and internal API calls",
            "parameters": {
                "sql_query": {
                    "type": "string",
                    "description": "SQL query to execute (SELECT and WITH only)",
                    "required": False
                },
                "api_endpoint": {
                    "type": "string", 
                    "description": "Internal API endpoint URL",
                    "required": False
                },
                "method": {
                    "type": "string",
                    "description": "HTTP method for API calls",
                    "default": "GET",
                    "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"]
                },
                "query_params": {
                    "type": "object",
                    "description": "Parameters for SQL query or API request body",
                    "required": False
                }
            },
            "security_features": [
                "SQL injection prevention",
                "Query type restrictions (SELECT only)",
                "Internal API validation",
                "Row Level Security support",
                "Request timeouts"
            ]
        }

# Create global instance for easy importing
database_query_driver = DatabaseQueryDriver()
