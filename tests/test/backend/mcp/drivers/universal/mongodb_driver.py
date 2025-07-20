"""
MongoDB Driver - Handles MongoDB database operations
Supports: find, insert, update, delete, aggregation
"""

import logging
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json
from typing import Dict, Any, List, Optional, Union
from bson import ObjectId
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# Add the parent directories to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(backend_dir)
mcp_dir = os.path.join(backend_dir, 'mcp')
sys.path.append(mcp_dir)

from mcp.universal_driver_manager import BaseUniversalDriver

class MongodbDriver(BaseUniversalDriver):
    """Universal driver for MongoDB database operations"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "mongodb_driver"
        self.supported_node_types = [
            'n8n-nodes-base.mongodb',
            'n8n-nodes-base.mongodbTrigger',
            'mongodb.find',
            'mongodb.insert',
            'mongodb.update',
            'mongodb.delete',
            'mongodb.aggregate'
        ]
        self.clients = {}
    
    def get_supported_node_types(self) -> List[str]:
        return self.supported_node_types
    
    def get_required_parameters(self, node_type: str) -> List[str]:
        return ['operation', 'collection']
    
    async def execute(self, node_type: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        if node_type not in self.supported_node_types:
            return {
                "success": False,
                "error": f"Unsupported node type: {node_type}",
                "supported_types": self.supported_node_types
            }
        
        try:
            if node_type == 'n8n-nodes-base.mongodb':
                return await self.execute_mongodb_operation(parameters, context)
            elif node_type == 'n8n-nodes-base.mongodbTrigger':
                return await self.setup_mongodb_trigger(parameters, context)
            else:
                return await self.execute_mongodb_operation(parameters, context)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "node_type": node_type
            }
    
    async def execute_mongodb_operation(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute MongoDB operation"""
        self.logger.info("Executing MongoDB operation")
        
        try:
            # Get connection details
            connection_config = self._get_connection_config(parameters, context)
            if not connection_config:
                return {
                    "success": False,
                    "error": "MongoDB connection configuration not found"
                }
            
            # Get or create client
            client = await self._get_client(connection_config)
            database = client[connection_config['database']]
            collection_name = parameters.get('collection', '')
            
            if not collection_name:
                return {
                    "success": False,
                    "error": "Collection name is required"
                }
            
            collection = database[collection_name]
            operation = parameters.get('operation', 'find')
            
            if operation == 'find':
                return await self._find_documents(collection, parameters, context)
            elif operation == 'insert':
                return await self._insert_documents(collection, parameters, context)
            elif operation == 'update':
                return await self._update_documents(collection, parameters, context)
            elif operation == 'delete':
                return await self._delete_documents(collection, parameters, context)
            elif operation == 'aggregate':
                return await self._aggregate_documents(collection, parameters, context)
            elif operation == 'count':
                return await self._count_documents(collection, parameters, context)
            elif operation == 'findOne':
                return await self._find_one_document(collection, parameters, context)
            elif operation == 'insertOne':
                return await self._insert_one_document(collection, parameters, context)
            elif operation == 'updateOne':
                return await self._update_one_document(collection, parameters, context)
            elif operation == 'deleteOne':
                return await self._delete_one_document(collection, parameters, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
            
        except Exception as e:
            self.logger.error(f"MongoDB operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def setup_mongodb_trigger(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Setup MongoDB trigger (change stream)"""
        self.logger.info("Setting up MongoDB trigger")
        
        try:
            # Get connection details
            connection_config = self._get_connection_config(parameters, context)
            if not connection_config:
                return {
                    "success": False,
                    "error": "MongoDB connection configuration not found"
                }
            
            trigger_on = parameters.get('triggerOn', 'insert')
            collection_name = parameters.get('collection', '')
            
            # For now, return success as trigger would require change stream setup
            return {
                "success": True,
                "trigger_on": trigger_on,
                "collection": collection_name,
                "message": "MongoDB trigger setup configured"
            }
            
        except Exception as e:
            self.logger.error(f"MongoDB trigger setup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _find_documents(self, collection, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Find documents in collection"""
        
        query = parameters.get('query', {})
        projection = parameters.get('projection', {})
        sort = parameters.get('sort', {})
        limit = parameters.get('limit', None)
        skip = parameters.get('skip', None)
        
        # Handle query from context
        if context and 'input_data' in context:
            input_data = context['input_data']
            if isinstance(input_data, dict):
                query = input_data.get('query', query)
                projection = input_data.get('projection', projection)
                sort = input_data.get('sort', sort)
                limit = input_data.get('limit', limit)
                skip = input_data.get('skip', skip)
        
        try:
            # Convert string query to dict if needed
            if isinstance(query, str):
                query = json.loads(query)
            
            # Build cursor
            cursor = collection.find(query, projection)
            
            # Apply sorting
            if sort:
                cursor = cursor.sort(list(sort.items()))
            
            # Apply skip and limit
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            # Execute query
            documents = []
            async for doc in cursor:
                # Convert ObjectId to string
                doc = self._convert_objectid_to_string(doc)
                documents.append(doc)
            
            return {
                "success": True,
                "data": documents,
                "document_count": len(documents),
                "query": query,
                "message": f"Found {len(documents)} documents"
            }
            
        except Exception as e:
            self.logger.error(f"Find operation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def _insert_documents(self, collection, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Insert documents into collection"""
        
        documents = parameters.get('documents', [])
        
        # Handle data from context
        if context and 'input_data' in context:
            input_data = context['input_data']
            if isinstance(input_data, list):
                documents = input_data
            elif isinstance(input_data, dict):
                documents = [input_data]
        
        if not documents:
            return {
                "success": False,
                "error": "No documents provided for insert"
            }
        
        try:
            # Convert string documents to dict if needed
            if isinstance(documents, str):
                documents = json.loads(documents)
            
            # Add timestamps if not present
            for doc in documents:
                if 'created_at' not in doc:
                    doc['created_at'] = datetime.utcnow()
                if 'updated_at' not in doc:
                    doc['updated_at'] = datetime.utcnow()
            
            # Insert documents
            if len(documents) == 1:
                result = await collection.insert_one(documents[0])
                inserted_ids = [str(result.inserted_id)]
            else:
                result = await collection.insert_many(documents)
                inserted_ids = [str(id) for id in result.inserted_ids]
            
            return {
                "success": True,
                "inserted_count": len(inserted_ids),
                "inserted_ids": inserted_ids,
                "message": f"Inserted {len(inserted_ids)} documents"
            }
            
        except Exception as e:
            self.logger.error(f"Insert operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _update_documents(self, collection, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update documents in collection"""
        
        filter_query = parameters.get('filter', {})
        update_data = parameters.get('update', {})
        upsert = parameters.get('upsert', False)
        
        # Handle data from context
        if context and 'input_data' in context:
            input_data = context['input_data']
            if isinstance(input_data, dict):
                filter_query = input_data.get('filter', filter_query)
                update_data = input_data.get('update', update_data)
                upsert = input_data.get('upsert', upsert)
        
        if not filter_query or not update_data:
            return {
                "success": False,
                "error": "Filter and update data are required"
            }
        
        try:
            # Convert string queries to dict if needed
            if isinstance(filter_query, str):
                filter_query = json.loads(filter_query)
            if isinstance(update_data, str):
                update_data = json.loads(update_data)
            
            # Ensure update operations are properly formatted
            if not any(key.startswith('$') for key in update_data.keys()):
                update_data = {'$set': update_data}
            
            # Add updated timestamp
            if '$set' in update_data:
                update_data['$set']['updated_at'] = datetime.utcnow()
            else:
                update_data['$set'] = {'updated_at': datetime.utcnow()}
            
            # Update documents
            result = await collection.update_many(filter_query, update_data, upsert=upsert)
            
            return {
                "success": True,
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_count": len(result.upserted_ids) if result.upserted_ids else 0,
                "upserted_ids": [str(id) for id in result.upserted_ids] if result.upserted_ids else [],
                "filter": filter_query,
                "update": update_data,
                "message": f"Updated {result.modified_count} documents"
            }
            
        except Exception as e:
            self.logger.error(f"Update operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _delete_documents(self, collection, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Delete documents from collection"""
        
        filter_query = parameters.get('filter', {})
        
        # Handle data from context
        if context and 'input_data' in context:
            input_data = context['input_data']
            if isinstance(input_data, dict):
                filter_query = input_data.get('filter', filter_query)
        
        if not filter_query:
            return {
                "success": False,
                "error": "Filter query is required for delete"
            }
        
        try:
            # Convert string query to dict if needed
            if isinstance(filter_query, str):
                filter_query = json.loads(filter_query)
            
            # Delete documents
            result = await collection.delete_many(filter_query)
            
            return {
                "success": True,
                "deleted_count": result.deleted_count,
                "filter": filter_query,
                "message": f"Deleted {result.deleted_count} documents"
            }
            
        except Exception as e:
            self.logger.error(f"Delete operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _aggregate_documents(self, collection, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate documents in collection"""
        
        pipeline = parameters.get('pipeline', [])
        
        # Handle pipeline from context
        if context and 'input_data' in context:
            input_data = context['input_data']
            if isinstance(input_data, list):
                pipeline = input_data
            elif isinstance(input_data, dict):
                pipeline = input_data.get('pipeline', pipeline)
        
        if not pipeline:
            return {
                "success": False,
                "error": "Aggregation pipeline is required"
            }
        
        try:
            # Convert string pipeline to list if needed
            if isinstance(pipeline, str):
                pipeline = json.loads(pipeline)
            
            # Execute aggregation
            documents = []
            async for doc in collection.aggregate(pipeline):
                # Convert ObjectId to string
                doc = self._convert_objectid_to_string(doc)
                documents.append(doc)
            
            return {
                "success": True,
                "data": documents,
                "document_count": len(documents),
                "pipeline": pipeline,
                "message": f"Aggregated {len(documents)} documents"
            }
            
        except Exception as e:
            self.logger.error(f"Aggregation operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _count_documents(self, collection, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Count documents in collection"""
        
        filter_query = parameters.get('filter', {})
        
        # Handle query from context
        if context and 'input_data' in context:
            input_data = context['input_data']
            if isinstance(input_data, dict):
                filter_query = input_data.get('filter', filter_query)
        
        try:
            # Convert string query to dict if needed
            if isinstance(filter_query, str):
                filter_query = json.loads(filter_query)
            
            # Count documents
            count = await collection.count_documents(filter_query)
            
            return {
                "success": True,
                "count": count,
                "filter": filter_query,
                "message": f"Found {count} documents"
            }
            
        except Exception as e:
            self.logger.error(f"Count operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _find_one_document(self, collection, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Find one document in collection"""
        
        filter_query = parameters.get('filter', {})
        projection = parameters.get('projection', {})
        
        # Handle query from context
        if context and 'input_data' in context:
            input_data = context['input_data']
            if isinstance(input_data, dict):
                filter_query = input_data.get('filter', filter_query)
                projection = input_data.get('projection', projection)
        
        try:
            # Convert string query to dict if needed
            if isinstance(filter_query, str):
                filter_query = json.loads(filter_query)
            
            # Find one document
            document = await collection.find_one(filter_query, projection)
            
            if document:
                # Convert ObjectId to string
                document = self._convert_objectid_to_string(document)
                
                return {
                    "success": True,
                    "data": document,
                    "found": True,
                    "filter": filter_query,
                    "message": "Document found"
                }
            else:
                return {
                    "success": True,
                    "data": None,
                    "found": False,
                    "filter": filter_query,
                    "message": "No document found"
                }
            
        except Exception as e:
            self.logger.error(f"Find one operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _insert_one_document(self, collection, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Insert one document into collection"""
        
        document = parameters.get('document', {})
        
        # Handle data from context
        if context and 'input_data' in context:
            input_data = context['input_data']
            if isinstance(input_data, dict):
                document = input_data
        
        if not document:
            return {
                "success": False,
                "error": "No document provided for insert"
            }
        
        try:
            # Convert string document to dict if needed
            if isinstance(document, str):
                document = json.loads(document)
            
            # Add timestamps if not present
            if 'created_at' not in document:
                document['created_at'] = datetime.utcnow()
            if 'updated_at' not in document:
                document['updated_at'] = datetime.utcnow()
            
            # Insert document
            result = await collection.insert_one(document)
            
            return {
                "success": True,
                "inserted_id": str(result.inserted_id),
                "message": f"Inserted document with ID: {result.inserted_id}"
            }
            
        except Exception as e:
            self.logger.error(f"Insert one operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _update_one_document(self, collection, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update one document in collection"""
        
        filter_query = parameters.get('filter', {})
        update_data = parameters.get('update', {})
        upsert = parameters.get('upsert', False)
        
        # Handle data from context
        if context and 'input_data' in context:
            input_data = context['input_data']
            if isinstance(input_data, dict):
                filter_query = input_data.get('filter', filter_query)
                update_data = input_data.get('update', update_data)
                upsert = input_data.get('upsert', upsert)
        
        if not filter_query or not update_data:
            return {
                "success": False,
                "error": "Filter and update data are required"
            }
        
        try:
            # Convert string queries to dict if needed
            if isinstance(filter_query, str):
                filter_query = json.loads(filter_query)
            if isinstance(update_data, str):
                update_data = json.loads(update_data)
            
            # Ensure update operations are properly formatted
            if not any(key.startswith('$') for key in update_data.keys()):
                update_data = {'$set': update_data}
            
            # Add updated timestamp
            if '$set' in update_data:
                update_data['$set']['updated_at'] = datetime.utcnow()
            else:
                update_data['$set'] = {'updated_at': datetime.utcnow()}
            
            # Update document
            result = await collection.update_one(filter_query, update_data, upsert=upsert)
            
            return {
                "success": True,
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_id": str(result.upserted_id) if result.upserted_id else None,
                "filter": filter_query,
                "update": update_data,
                "message": f"Updated {result.modified_count} document"
            }
            
        except Exception as e:
            self.logger.error(f"Update one operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _delete_one_document(self, collection, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Delete one document from collection"""
        
        filter_query = parameters.get('filter', {})
        
        # Handle data from context
        if context and 'input_data' in context:
            input_data = context['input_data']
            if isinstance(input_data, dict):
                filter_query = input_data.get('filter', filter_query)
        
        if not filter_query:
            return {
                "success": False,
                "error": "Filter query is required for delete"
            }
        
        try:
            # Convert string query to dict if needed
            if isinstance(filter_query, str):
                filter_query = json.loads(filter_query)
            
            # Delete document
            result = await collection.delete_one(filter_query)
            
            return {
                "success": True,
                "deleted_count": result.deleted_count,
                "filter": filter_query,
                "message": f"Deleted {result.deleted_count} document"
            }
            
        except Exception as e:
            self.logger.error(f"Delete one operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_client(self, config: Dict[str, Any]) -> AsyncIOMotorClient:
        """Get or create MongoDB client"""
        
        connection_key = f"{config['host']}:{config['port']}:{config['database']}"
        
        if connection_key not in self.clients:
            try:
                # Build connection string
                if config.get('username') and config.get('password'):
                    connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
                else:
                    connection_string = f"mongodb://{config['host']}:{config['port']}/{config['database']}"
                
                client = AsyncIOMotorClient(connection_string)
                self.clients[connection_key] = client
            except Exception as e:
                self.logger.error(f"Failed to connect to MongoDB: {e}")
                raise
        
        return self.clients[connection_key]
    
    def _get_connection_config(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Get MongoDB connection configuration"""
        
        # Try parameters first
        if 'host' in parameters:
            return {
                'host': parameters.get('host', 'localhost'),
                'port': parameters.get('port', 27017),
                'database': parameters.get('database', ''),
                'username': parameters.get('username', ''),
                'password': parameters.get('password', '')
            }
        
        # Try context credentials
        if context and 'credentials' in context:
            credentials = context['credentials']
            if 'mongodb' in credentials:
                cred = credentials['mongodb']
                return {
                    'host': cred.get('host', 'localhost'),
                    'port': cred.get('port', 27017),
                    'database': cred.get('database', ''),
                    'username': cred.get('username', ''),
                    'password': cred.get('password', '')
                }
        
        # Try environment variables
        if os.getenv('MONGODB_HOST'):
            return {
                'host': os.getenv('MONGODB_HOST', 'localhost'),
                'port': int(os.getenv('MONGODB_PORT', '27017')),
                'database': os.getenv('MONGODB_DB', ''),
                'username': os.getenv('MONGODB_USERNAME', ''),
                'password': os.getenv('MONGODB_PASSWORD', '')
            }
        
        return None
    
    def _convert_objectid_to_string(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ObjectId fields to strings for JSON serialization"""
        
        if isinstance(document, dict):
            for key, value in document.items():
                if isinstance(value, ObjectId):
                    document[key] = str(value)
                elif isinstance(value, dict):
                    document[key] = self._convert_objectid_to_string(value)
                elif isinstance(value, list):
                    document[key] = [self._convert_objectid_to_string(item) if isinstance(item, dict) else str(item) if isinstance(item, ObjectId) else item for item in value]
        
        return document
    
    def close_connections(self):
        """Close all MongoDB connections"""
        for client in self.clients.values():
            try:
                client.close()
            except Exception as e:
                self.logger.warning(f"Error closing connection: {e}")
        self.clients.clear()
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations"""
        return ['find', 'insert', 'update', 'delete', 'aggregate', 'count', 'findOne', 'insertOne', 'updateOne', 'deleteOne']
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about current connections"""
        return {
            "active_connections": len(self.clients),
            "connection_keys": list(self.clients.keys())
        }
