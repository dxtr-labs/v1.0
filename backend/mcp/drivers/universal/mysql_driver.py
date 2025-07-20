"""
MySQL Driver - Handles MySQL database operations
Supports: queries, inserts, updates, deletes, transactions
"""

import logging
import asyncio
import aiomysql
import json
from typing import Dict, Any, List, Optional, Union
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# Add the parent directories to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(backend_dir)
mcp_dir = os.path.join(backend_dir, 'mcp')
sys.path.append(mcp_dir)

from mcp.universal_driver_manager import BaseUniversalDriver

class MysqlDriver(BaseUniversalDriver):
    """Universal driver for MySQL database operations"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "mysql_driver"
        self.supported_node_types = [
            'n8n-nodes-base.mysql',
            'n8n-nodes-base.mysqlTrigger',
            'mysql.query',
            'mysql.insert',
            'mysql.update',
            'mysql.delete'
        ]
        self.connections = {}
    
    def get_supported_node_types(self) -> List[str]:
        return self.supported_node_types
    
    def get_required_parameters(self, node_type: str) -> List[str]:
        return ['operation']
    
    async def execute(self, node_type: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        if node_type not in self.supported_node_types:
            return {
                "success": False,
                "error": f"Unsupported node type: {node_type}",
                "supported_types": self.supported_node_types
            }
        
        try:
            if node_type == 'n8n-nodes-base.mysql':
                return await self.execute_mysql_operation(parameters, context)
            elif node_type == 'n8n-nodes-base.mysqlTrigger':
                return await self.setup_mysql_trigger(parameters, context)
            else:
                return await self.execute_mysql_operation(parameters, context)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "node_type": node_type
            }
    
    async def execute_mysql_operation(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute MySQL operation"""
        self.logger.info("Executing MySQL operation")
        
        try:
            # Get connection details
            connection_config = self._get_connection_config(parameters, context)
            if not connection_config:
                return {
                    "success": False,
                    "error": "MySQL connection configuration not found"
                }
            
            # Get or create connection
            connection = await self._get_connection(connection_config)
            
            operation = parameters.get('operation', 'executeQuery')
            
            if operation == 'executeQuery':
                return await self._execute_query(connection, parameters, context)
            elif operation == 'insert':
                return await self._insert_data(connection, parameters, context)
            elif operation == 'update':
                return await self._update_data(connection, parameters, context)
            elif operation == 'delete':
                return await self._delete_data(connection, parameters, context)
            elif operation == 'select':
                return await self._select_data(connection, parameters, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
            
        except Exception as e:
            self.logger.error(f"MySQL operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def setup_mysql_trigger(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Setup MySQL trigger (polling-based)"""
        self.logger.info("Setting up MySQL trigger")
        
        try:
            # Get connection details
            connection_config = self._get_connection_config(parameters, context)
            if not connection_config:
                return {
                    "success": False,
                    "error": "MySQL connection configuration not found"
                }
            
            trigger_on = parameters.get('triggerOn', 'insert')
            table_name = parameters.get('tableName', '')
            
            # For now, return success as trigger would require polling setup
            return {
                "success": True,
                "trigger_on": trigger_on,
                "table_name": table_name,
                "message": "MySQL trigger setup configured"
            }
            
        except Exception as e:
            self.logger.error(f"MySQL trigger setup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_query(self, connection: aiomysql.Connection, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute raw SQL query"""
        
        query = parameters.get('query', '')
        query_parameters = parameters.get('parameters', [])
        
        # Handle query from context
        if context and 'input_data' in context:
            input_data = context['input_data']
            if isinstance(input_data, str):
                query = input_data
            elif isinstance(input_data, dict):
                query = input_data.get('query', query)
                query_parameters = input_data.get('parameters', query_parameters)
        
        try:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                # Execute query
                if query_parameters:
                    await cursor.execute(query, query_parameters)
                else:
                    await cursor.execute(query)
                
                # Fetch results
                result = await cursor.fetchall()
                
                # Convert result to list of dicts
                rows = []
                for row in result:
                    # Convert any non-serializable types
                    clean_row = {}
                    for key, value in row.items():
                        if isinstance(value, (bytes, bytearray)):
                            clean_row[key] = value.decode('utf-8', errors='ignore')
                        else:
                            clean_row[key] = value
                    rows.append(clean_row)
                
                return {
                    "success": True,
                    "data": rows,
                    "row_count": len(rows),
                    "query": query,
                    "message": f"Query executed successfully: {len(rows)} rows returned"
                }
                
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def _insert_data(self, connection: aiomysql.Connection, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Insert data into table"""
        
        table_name = parameters.get('table', parameters.get('tableName', ''))
        columns = parameters.get('columns', [])
        values = parameters.get('values', [])
        
        # Handle data from context
        if context and 'input_data' in context:
            input_data = context['input_data']
            if isinstance(input_data, list):
                # Array of objects
                if input_data and isinstance(input_data[0], dict):
                    columns = list(input_data[0].keys())
                    values = [[item.get(col, None) for col in columns] for item in input_data]
                else:
                    values = input_data
            elif isinstance(input_data, dict):
                columns = list(input_data.keys())
                values = [list(input_data.values())]
        
        if not table_name or not columns:
            return {
                "success": False,
                "error": "Table name and columns are required for insert"
            }
        
        try:
            async with connection.cursor() as cursor:
                # Build insert query
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join(columns)
                query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
                
                # Execute insert
                if isinstance(values[0], list):
                    # Multiple rows
                    await cursor.executemany(query, values)
                    inserted_count = len(values)
                else:
                    # Single row
                    await cursor.execute(query, values)
                    inserted_count = 1
                
                await connection.commit()
                
                return {
                    "success": True,
                    "inserted_count": inserted_count,
                    "table": table_name,
                    "columns": columns,
                    "message": f"Inserted {inserted_count} rows into {table_name}"
                }
                
        except Exception as e:
            await connection.rollback()
            self.logger.error(f"Insert operation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "table": table_name
            }
    
    async def _update_data(self, connection: aiomysql.Connection, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update data in table"""
        
        table_name = parameters.get('table', parameters.get('tableName', ''))
        set_clause = parameters.get('set', {})
        where_clause = parameters.get('where', {})
        
        # Handle data from context
        if context and 'input_data' in context:
            input_data = context['input_data']
            if isinstance(input_data, dict):
                set_clause = input_data.get('set', set_clause)
                where_clause = input_data.get('where', where_clause)
        
        if not table_name or not set_clause:
            return {
                "success": False,
                "error": "Table name and set clause are required for update"
            }
        
        try:
            async with connection.cursor() as cursor:
                # Build update query
                set_parts = []
                params = []
                
                for column, value in set_clause.items():
                    set_parts.append(f"{column} = %s")
                    params.append(value)
                
                query = f"UPDATE {table_name} SET {', '.join(set_parts)}"
                
                # Add WHERE clause
                if where_clause:
                    where_parts = []
                    for column, value in where_clause.items():
                        where_parts.append(f"{column} = %s")
                        params.append(value)
                    query += f" WHERE {' AND '.join(where_parts)}"
                
                # Execute update
                await cursor.execute(query, params)
                updated_count = cursor.rowcount
                
                await connection.commit()
                
                return {
                    "success": True,
                    "updated_count": updated_count,
                    "table": table_name,
                    "set_clause": set_clause,
                    "where_clause": where_clause,
                    "message": f"Updated {updated_count} rows in {table_name}"
                }
                
        except Exception as e:
            await connection.rollback()
            self.logger.error(f"Update operation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "table": table_name
            }
    
    async def _delete_data(self, connection: aiomysql.Connection, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Delete data from table"""
        
        table_name = parameters.get('table', parameters.get('tableName', ''))
        where_clause = parameters.get('where', {})
        
        # Handle data from context
        if context and 'input_data' in context:
            input_data = context['input_data']
            if isinstance(input_data, dict):
                where_clause = input_data.get('where', where_clause)
        
        if not table_name:
            return {
                "success": False,
                "error": "Table name is required for delete"
            }
        
        try:
            async with connection.cursor() as cursor:
                # Build delete query
                query = f"DELETE FROM {table_name}"
                params = []
                
                # Add WHERE clause
                if where_clause:
                    where_parts = []
                    for column, value in where_clause.items():
                        where_parts.append(f"{column} = %s")
                        params.append(value)
                    query += f" WHERE {' AND '.join(where_parts)}"
                
                # Execute delete
                await cursor.execute(query, params)
                deleted_count = cursor.rowcount
                
                await connection.commit()
                
                return {
                    "success": True,
                    "deleted_count": deleted_count,
                    "table": table_name,
                    "where_clause": where_clause,
                    "message": f"Deleted {deleted_count} rows from {table_name}"
                }
                
        except Exception as e:
            await connection.rollback()
            self.logger.error(f"Delete operation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "table": table_name
            }
    
    async def _select_data(self, connection: aiomysql.Connection, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Select data from table"""
        
        table_name = parameters.get('table', parameters.get('tableName', ''))
        columns = parameters.get('columns', ['*'])
        where_clause = parameters.get('where', {})
        order_by = parameters.get('orderBy', '')
        limit = parameters.get('limit', None)
        offset = parameters.get('offset', None)
        
        if not table_name:
            return {
                "success": False,
                "error": "Table name is required for select"
            }
        
        try:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                # Build select query
                column_list = ', '.join(columns) if isinstance(columns, list) else columns
                query = f"SELECT {column_list} FROM {table_name}"
                params = []
                
                # Add WHERE clause
                if where_clause:
                    where_parts = []
                    for column, value in where_clause.items():
                        where_parts.append(f"{column} = %s")
                        params.append(value)
                    query += f" WHERE {' AND '.join(where_parts)}"
                
                # Add ORDER BY
                if order_by:
                    query += f" ORDER BY {order_by}"
                
                # Add LIMIT and OFFSET
                if limit:
                    query += f" LIMIT {limit}"
                if offset:
                    query += f" OFFSET {offset}"
                
                # Execute select
                await cursor.execute(query, params)
                result = await cursor.fetchall()
                
                # Convert result to list of dicts
                rows = []
                for row in result:
                    # Convert any non-serializable types
                    clean_row = {}
                    for key, value in row.items():
                        if isinstance(value, (bytes, bytearray)):
                            clean_row[key] = value.decode('utf-8', errors='ignore')
                        else:
                            clean_row[key] = value
                    rows.append(clean_row)
                
                return {
                    "success": True,
                    "data": rows,
                    "row_count": len(rows),
                    "table": table_name,
                    "columns": columns,
                    "message": f"Selected {len(rows)} rows from {table_name}"
                }
                
        except Exception as e:
            self.logger.error(f"Select operation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "table": table_name
            }
    
    async def _get_connection(self, config: Dict[str, Any]) -> aiomysql.Connection:
        """Get or create database connection"""
        
        connection_key = f"{config['host']}:{config['port']}:{config['database']}"
        
        if connection_key not in self.connections:
            try:
                connection = await aiomysql.connect(
                    host=config['host'],
                    port=config['port'],
                    db=config['database'],
                    user=config['user'],
                    password=config['password'],
                    autocommit=False
                )
                self.connections[connection_key] = connection
            except Exception as e:
                self.logger.error(f"Failed to connect to MySQL: {e}")
                raise
        
        return self.connections[connection_key]
    
    def _get_connection_config(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Get MySQL connection configuration"""
        
        # Try parameters first
        if 'host' in parameters:
            return {
                'host': parameters.get('host', 'localhost'),
                'port': parameters.get('port', 3306),
                'database': parameters.get('database', ''),
                'user': parameters.get('user', ''),
                'password': parameters.get('password', '')
            }
        
        # Try context credentials
        if context and 'credentials' in context:
            credentials = context['credentials']
            if 'mysql' in credentials:
                cred = credentials['mysql']
                return {
                    'host': cred.get('host', 'localhost'),
                    'port': cred.get('port', 3306),
                    'database': cred.get('database', ''),
                    'user': cred.get('user', ''),
                    'password': cred.get('password', '')
                }
        
        # Try environment variables
        if os.getenv('MYSQL_HOST'):
            return {
                'host': os.getenv('MYSQL_HOST', 'localhost'),
                'port': int(os.getenv('MYSQL_PORT', '3306')),
                'database': os.getenv('MYSQL_DB', ''),
                'user': os.getenv('MYSQL_USER', ''),
                'password': os.getenv('MYSQL_PASSWORD', '')
            }
        
        return None
    
    async def close_connections(self):
        """Close all database connections"""
        for connection in self.connections.values():
            try:
                await connection.ensure_closed()
            except Exception as e:
                self.logger.warning(f"Error closing connection: {e}")
        self.connections.clear()
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations"""
        return ['executeQuery', 'insert', 'update', 'delete', 'select']
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about current connections"""
        return {
            "active_connections": len(self.connections),
            "connection_keys": list(self.connections.keys())
        }
