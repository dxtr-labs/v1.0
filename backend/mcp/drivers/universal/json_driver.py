"""
JSON Driver - Handles JSON file operations
Supports: read, write, merge, validate, transform, query
"""

import logging
import asyncio
import json
import os
from typing import Dict, Any, List, Optional, Union
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# Add the parent directories to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(backend_dir)
mcp_dir = os.path.join(backend_dir, 'mcp')
sys.path.append(mcp_dir)

from mcp.universal_driver_manager import BaseUniversalDriver

try:
    import jsonpath_ng
    import jsonschema
    ADVANCED_DEPENDENCIES_AVAILABLE = True
except ImportError:
    ADVANCED_DEPENDENCIES_AVAILABLE = False

class JsonDriver(BaseUniversalDriver):
    """Universal driver for JSON file operations"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "json_driver"
        self.supported_node_types = [
            'n8n-nodes-base.json',
            'json.read',
            'json.write',
            'json.merge',
            'json.validate',
            'json.transform',
            'json.query',
            'json.format',
            'json.minify'
        ]
    
    def get_supported_node_types(self) -> List[str]:
        return self.supported_node_types
    
    def get_required_parameters(self, node_type: str) -> List[str]:
        if node_type in ['json.read', 'json.validate', 'json.format', 'json.minify']:
            return ['file_path']
        elif node_type in ['json.write']:
            return ['file_path', 'data']
        elif node_type in ['json.merge']:
            return ['file_paths']
        elif node_type in ['json.query']:
            return ['data', 'query']
        return ['operation']
    
    async def execute(self, node_type: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        if node_type not in self.supported_node_types:
            return {
                "success": False,
                "error": f"Unsupported node type: {node_type}",
                "supported_types": self.supported_node_types
            }
        
        try:
            operation = parameters.get('operation', node_type.split('.')[-1] if '.' in node_type else 'read')
            
            if operation == 'read':
                return await self.read_json(parameters, context)
            elif operation == 'write':
                return await self.write_json(parameters, context)
            elif operation == 'merge':
                return await self.merge_json(parameters, context)
            elif operation == 'validate':
                return await self.validate_json(parameters, context)
            elif operation == 'transform':
                return await self.transform_json(parameters, context)
            elif operation == 'query':
                return await self.query_json(parameters, context)
            elif operation == 'format':
                return await self.format_json(parameters, context)
            elif operation == 'minify':
                return await self.minify_json(parameters, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "node_type": node_type
            }
    
    async def read_json(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Read JSON file"""
        self.logger.info("Reading JSON file")
        
        try:
            file_path = parameters.get('file_path', '')
            encoding = parameters.get('encoding', 'utf-8')
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    file_path = input_data.get('file_path', file_path)
                    encoding = input_data.get('encoding', encoding)
                    if 'json_content' in input_data:
                        # Handle direct JSON content
                        json_content = input_data['json_content']
                        if isinstance(json_content, str):
                            data = json.loads(json_content)
                        else:
                            data = json_content
                        
                        return {
                            "success": True,
                            "data": data,
                            "source": "context",
                            "data_type": type(data).__name__,
                            "message": "Successfully read JSON from context"
                        }
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            with open(file_path, 'r', encoding=encoding) as f:
                data = json.load(f)
            
            return {
                "success": True,
                "file_path": file_path,
                "data": data,
                "encoding": encoding,
                "data_type": type(data).__name__,
                "message": "Successfully read JSON file"
            }
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return {
                "success": False,
                "error": f"Invalid JSON format: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"JSON read failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def write_json(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Write JSON file"""
        self.logger.info("Writing JSON file")
        
        try:
            file_path = parameters.get('file_path', '')
            data = parameters.get('data', {})
            encoding = parameters.get('encoding', 'utf-8')
            indent = parameters.get('indent', 2)
            sort_keys = parameters.get('sort_keys', False)
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    if 'file_path' not in input_data:
                        data = input_data
                    else:
                        data = input_data.get('data', input_data)
                        file_path = input_data.get('file_path', file_path)
                        encoding = input_data.get('encoding', encoding)
                        indent = input_data.get('indent', indent)
                        sort_keys = input_data.get('sort_keys', sort_keys)
                else:
                    data = input_data
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            if data is None:
                return {
                    "success": False,
                    "error": "Data is required"
                }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                json.dump(data, f, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
            
            return {
                "success": True,
                "file_path": file_path,
                "data_type": type(data).__name__,
                "encoding": encoding,
                "indent": indent,
                "sort_keys": sort_keys,
                "message": "Successfully wrote JSON file"
            }
            
        except Exception as e:
            self.logger.error(f"JSON write failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def merge_json(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Merge multiple JSON files"""
        self.logger.info("Merging JSON files")
        
        try:
            file_paths = parameters.get('file_paths', [])
            output_path = parameters.get('output_path', 'merged.json')
            merge_strategy = parameters.get('merge_strategy', 'deep')  # deep, shallow, array
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, list):
                    file_paths = input_data
                elif isinstance(input_data, dict):
                    file_paths = input_data.get('file_paths', file_paths)
                    output_path = input_data.get('output_path', output_path)
                    merge_strategy = input_data.get('merge_strategy', merge_strategy)
            
            if not file_paths or len(file_paths) < 2:
                return {
                    "success": False,
                    "error": "At least 2 file paths are required for merging"
                }
            
            # Verify all files exist
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    return {
                        "success": False,
                        "error": f"File not found: {file_path}"
                    }
            
            # Read all JSON files
            json_data = []
            for file_path in file_paths:
                read_result = await self.read_json({'file_path': file_path}, context)
                if not read_result['success']:
                    return read_result
                json_data.append(read_result['data'])
            
            # Merge data based on strategy
            if merge_strategy == 'array':
                # Combine all data into an array
                merged_data = json_data
            elif merge_strategy == 'shallow':
                # Shallow merge (only top level)
                merged_data = {}
                for data in json_data:
                    if isinstance(data, dict):
                        merged_data.update(data)
                    else:
                        # Handle non-dict data
                        merged_data[f"data_{len(merged_data)}"] = data
            elif merge_strategy == 'deep':
                # Deep merge
                merged_data = {}
                for data in json_data:
                    if isinstance(data, dict):
                        merged_data = self._deep_merge(merged_data, data)
                    else:
                        # Handle non-dict data
                        merged_data[f"data_{len(merged_data)}"] = data
            
            # Write merged data
            write_result = await self.write_json({
                'file_path': output_path,
                'data': merged_data
            }, context)
            if not write_result['success']:
                return write_result
            
            return {
                "success": True,
                "input_files": file_paths,
                "output_file": output_path,
                "merged_files_count": len(file_paths),
                "merge_strategy": merge_strategy,
                "data": merged_data,
                "message": f"Successfully merged {len(file_paths)} JSON files"
            }
            
        except Exception as e:
            self.logger.error(f"JSON merge failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_json(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate JSON file"""
        self.logger.info("Validating JSON file")
        
        try:
            file_path = parameters.get('file_path', '')
            schema = parameters.get('schema', None)
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    file_path = input_data.get('file_path', file_path)
                    schema = input_data.get('schema', schema)
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            # Read JSON data
            read_result = await self.read_json({'file_path': file_path}, context)
            if not read_result['success']:
                return read_result
            
            data = read_result['data']
            validation_errors = []
            
            # Basic JSON validation (already done by read_json)
            # Schema validation if provided
            if schema and ADVANCED_DEPENDENCIES_AVAILABLE:
                try:
                    jsonschema.validate(data, schema)
                except jsonschema.ValidationError as e:
                    validation_errors.append(f"Schema validation error: {e.message}")
                except jsonschema.SchemaError as e:
                    validation_errors.append(f"Schema error: {e.message}")
            
            # Basic structure validation
            if isinstance(data, dict):
                structure_info = self._analyze_dict_structure(data)
            elif isinstance(data, list):
                structure_info = self._analyze_list_structure(data)
            else:
                structure_info = {"type": type(data).__name__, "value": data}
            
            is_valid = len(validation_errors) == 0
            
            return {
                "success": True,
                "file_path": file_path,
                "is_valid": is_valid,
                "validation_errors": validation_errors,
                "structure_info": structure_info,
                "schema_provided": schema is not None,
                "message": f"JSON validation {'passed' if is_valid else 'failed'}"
            }
            
        except Exception as e:
            self.logger.error(f"JSON validation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def transform_json(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Transform JSON data"""
        self.logger.info("Transforming JSON data")
        
        try:
            file_path = parameters.get('file_path', '')
            transformations = parameters.get('transformations', {})
            output_path = parameters.get('output_path', '')
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    if 'file_path' in input_data:
                        file_path = input_data.get('file_path', file_path)
                        transformations = input_data.get('transformations', transformations)
                        output_path = input_data.get('output_path', output_path)
                    else:
                        # Direct data transformation
                        data = input_data
                        file_path = None
            
            if file_path:
                # Read JSON data
                read_result = await self.read_json({'file_path': file_path}, context)
                if not read_result['success']:
                    return read_result
                data = read_result['data']
            elif 'data' not in locals():
                return {
                    "success": False,
                    "error": "File path or data is required"
                }
            
            if not transformations:
                return {
                    "success": False,
                    "error": "Transformations are required"
                }
            
            # Apply transformations
            transformed_data = self._apply_transformations(data, transformations)
            
            # Write transformed data if output path provided
            if output_path:
                write_result = await self.write_json({
                    'file_path': output_path,
                    'data': transformed_data
                }, context)
                if not write_result['success']:
                    return write_result
            
            return {
                "success": True,
                "input_file": file_path,
                "output_file": output_path if output_path else None,
                "data": transformed_data,
                "transformations": transformations,
                "message": "Successfully transformed JSON data"
            }
            
        except Exception as e:
            self.logger.error(f"JSON transform failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def query_json(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Query JSON data"""
        self.logger.info("Querying JSON data")
        
        try:
            data = parameters.get('data', {})
            query = parameters.get('query', '')
            file_path = parameters.get('file_path', '')
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    data = input_data.get('data', data)
                    query = input_data.get('query', query)
                    file_path = input_data.get('file_path', file_path)
            
            # Read from file if path provided
            if file_path and not data:
                read_result = await self.read_json({'file_path': file_path}, context)
                if not read_result['success']:
                    return read_result
                data = read_result['data']
            
            if not data:
                return {
                    "success": False,
                    "error": "Data is required"
                }
            
            if not query:
                return {
                    "success": False,
                    "error": "Query is required"
                }
            
            # Simple query implementation
            results = []
            
            if ADVANCED_DEPENDENCIES_AVAILABLE:
                # Use jsonpath for advanced queries
                try:
                    jsonpath_expr = jsonpath_ng.parse(query)
                    matches = jsonpath_expr.find(data)
                    results = [match.value for match in matches]
                except Exception as e:
                    # Fall back to simple query
                    results = self._simple_query(data, query)
            else:
                # Simple query implementation
                results = self._simple_query(data, query)
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "result_count": len(results),
                "message": f"Query returned {len(results)} results"
            }
            
        except Exception as e:
            self.logger.error(f"JSON query failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def format_json(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format JSON file"""
        self.logger.info("Formatting JSON file")
        
        try:
            file_path = parameters.get('file_path', '')
            output_path = parameters.get('output_path', '')
            indent = parameters.get('indent', 2)
            sort_keys = parameters.get('sort_keys', True)
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    file_path = input_data.get('file_path', file_path)
                    output_path = input_data.get('output_path', output_path)
                    indent = input_data.get('indent', indent)
                    sort_keys = input_data.get('sort_keys', sort_keys)
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            # Read JSON data
            read_result = await self.read_json({'file_path': file_path}, context)
            if not read_result['success']:
                return read_result
            
            data = read_result['data']
            
            # Write formatted data
            if not output_path:
                output_path = file_path
            
            write_result = await self.write_json({
                'file_path': output_path,
                'data': data,
                'indent': indent,
                'sort_keys': sort_keys
            }, context)
            if not write_result['success']:
                return write_result
            
            return {
                "success": True,
                "input_file": file_path,
                "output_file": output_path,
                "indent": indent,
                "sort_keys": sort_keys,
                "message": "Successfully formatted JSON file"
            }
            
        except Exception as e:
            self.logger.error(f"JSON formatting failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def minify_json(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Minify JSON file"""
        self.logger.info("Minifying JSON file")
        
        try:
            file_path = parameters.get('file_path', '')
            output_path = parameters.get('output_path', '')
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    file_path = input_data.get('file_path', file_path)
                    output_path = input_data.get('output_path', output_path)
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            # Read JSON data
            read_result = await self.read_json({'file_path': file_path}, context)
            if not read_result['success']:
                return read_result
            
            data = read_result['data']
            
            # Write minified data
            if not output_path:
                output_path = file_path
            
            write_result = await self.write_json({
                'file_path': output_path,
                'data': data,
                'indent': None,
                'sort_keys': False
            }, context)
            if not write_result['success']:
                return write_result
            
            return {
                "success": True,
                "input_file": file_path,
                "output_file": output_path,
                "message": "Successfully minified JSON file"
            }
            
        except Exception as e:
            self.logger.error(f"JSON minification failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _deep_merge(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _analyze_dict_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dictionary structure"""
        structure = {
            "type": "object",
            "key_count": len(data),
            "keys": list(data.keys())
        }
        
        # Analyze value types
        value_types = {}
        for key, value in data.items():
            value_type = type(value).__name__
            if value_type in value_types:
                value_types[value_type] += 1
            else:
                value_types[value_type] = 1
        
        structure["value_types"] = value_types
        return structure
    
    def _analyze_list_structure(self, data: List[Any]) -> Dict[str, Any]:
        """Analyze list structure"""
        structure = {
            "type": "array",
            "length": len(data),
            "element_types": {}
        }
        
        for item in data:
            item_type = type(item).__name__
            if item_type in structure["element_types"]:
                structure["element_types"][item_type] += 1
            else:
                structure["element_types"][item_type] = 1
        
        return structure
    
    def _apply_transformations(self, data: Any, transformations: Dict[str, Any]) -> Any:
        """Apply transformations to data"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key in transformations:
                    transformation = transformations[key]
                    if transformation == 'remove':
                        continue
                    elif isinstance(transformation, dict):
                        if 'rename' in transformation:
                            result[transformation['rename']] = value
                        elif 'default' in transformation and value is None:
                            result[key] = transformation['default']
                        else:
                            result[key] = self._apply_transformations(value, transformation)
                    else:
                        result[key] = value
                else:
                    result[key] = value
            return result
        elif isinstance(data, list):
            return [self._apply_transformations(item, transformations) for item in data]
        else:
            return data
    
    def _simple_query(self, data: Any, query: str) -> List[Any]:
        """Simple query implementation"""
        results = []
        
        # Simple key-based query
        if isinstance(data, dict):
            if query in data:
                results.append(data[query])
            else:
                # Search nested
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        results.extend(self._simple_query(value, query))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    results.extend(self._simple_query(item, query))
        
        return results
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations"""
        return ['read', 'write', 'merge', 'validate', 'transform', 'query', 'format', 'minify']
