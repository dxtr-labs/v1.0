"""
CSV Driver - Handles CSV file operations
Supports: read, write, append, filter, transform, merge, split
"""

import logging
import asyncio
import csv
import os
from typing import Dict, Any, List, Optional, Union
import io
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# Add the parent directories to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(backend_dir)
mcp_dir = os.path.join(backend_dir, 'mcp')
sys.path.append(mcp_dir)

from mcp.universal_driver_manager import BaseUniversalDriver

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

class CsvDriver(BaseUniversalDriver):
    """Universal driver for CSV file operations"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "csv_driver"
        self.supported_node_types = [
            'n8n-nodes-base.csv',
            'csv.read',
            'csv.write',
            'csv.append',
            'csv.filter',
            'csv.transform',
            'csv.merge',
            'csv.split',
            'csv.validate'
        ]
    
    def get_supported_node_types(self) -> List[str]:
        return self.supported_node_types
    
    def get_required_parameters(self, node_type: str) -> List[str]:
        if node_type in ['csv.read', 'csv.filter', 'csv.transform']:
            return ['file_path']
        elif node_type in ['csv.write', 'csv.append']:
            return ['file_path', 'data']
        elif node_type in ['csv.merge']:
            return ['file_paths']
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
                return await self.read_csv(parameters, context)
            elif operation == 'write':
                return await self.write_csv(parameters, context)
            elif operation == 'append':
                return await self.append_csv(parameters, context)
            elif operation == 'filter':
                return await self.filter_csv(parameters, context)
            elif operation == 'transform':
                return await self.transform_csv(parameters, context)
            elif operation == 'merge':
                return await self.merge_csv(parameters, context)
            elif operation == 'split':
                return await self.split_csv(parameters, context)
            elif operation == 'validate':
                return await self.validate_csv(parameters, context)
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
    
    async def read_csv(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Read CSV file"""
        self.logger.info("Reading CSV file")
        
        try:
            file_path = parameters.get('file_path', '')
            delimiter = parameters.get('delimiter', ',')
            encoding = parameters.get('encoding', 'utf-8')
            has_header = parameters.get('has_header', True)
            max_rows = parameters.get('max_rows', None)
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    file_path = input_data.get('file_path', file_path)
                    delimiter = input_data.get('delimiter', delimiter)
                    encoding = input_data.get('encoding', encoding)
                    has_header = input_data.get('has_header', has_header)
                    max_rows = input_data.get('max_rows', max_rows)
            
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
            
            # Read CSV
            data = []
            headers = []
            
            with open(file_path, 'r', encoding=encoding, newline='') as f:
                reader = csv.reader(f, delimiter=delimiter)
                
                # Handle header
                if has_header:
                    headers = next(reader, [])
                
                # Read data
                for row_num, row in enumerate(reader):
                    if max_rows and row_num >= max_rows:
                        break
                    
                    if has_header:
                        row_dict = dict(zip(headers, row))
                        data.append(row_dict)
                    else:
                        data.append(row)
            
            return {
                "success": True,
                "file_path": file_path,
                "data": data,
                "headers": headers,
                "row_count": len(data),
                "delimiter": delimiter,
                "encoding": encoding,
                "has_header": has_header,
                "message": f"Successfully read {len(data)} rows from CSV"
            }
            
        except Exception as e:
            self.logger.error(f"CSV read failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def write_csv(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Write CSV file"""
        self.logger.info("Writing CSV file")
        
        try:
            file_path = parameters.get('file_path', '')
            data = parameters.get('data', [])
            delimiter = parameters.get('delimiter', ',')
            encoding = parameters.get('encoding', 'utf-8')
            include_header = parameters.get('include_header', True)
            headers = parameters.get('headers', [])
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, list):
                    data = input_data
                elif isinstance(input_data, dict):
                    data = input_data.get('data', data)
                    file_path = input_data.get('file_path', file_path)
                    delimiter = input_data.get('delimiter', delimiter)
                    encoding = input_data.get('encoding', encoding)
                    include_header = input_data.get('include_header', include_header)
                    headers = input_data.get('headers', headers)
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            if not data:
                return {
                    "success": False,
                    "error": "Data is required"
                }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write CSV
            with open(file_path, 'w', encoding=encoding, newline='') as f:
                writer = csv.writer(f, delimiter=delimiter)
                
                # Write header if needed
                if include_header:
                    if headers:
                        writer.writerow(headers)
                    elif data and isinstance(data[0], dict):
                        writer.writerow(data[0].keys())
                
                # Write data
                for row in data:
                    if isinstance(row, dict):
                        if headers:
                            writer.writerow([row.get(header, '') for header in headers])
                        else:
                            writer.writerow(row.values())
                    else:
                        writer.writerow(row)
            
            return {
                "success": True,
                "file_path": file_path,
                "rows_written": len(data),
                "delimiter": delimiter,
                "encoding": encoding,
                "include_header": include_header,
                "message": f"Successfully wrote {len(data)} rows to CSV"
            }
            
        except Exception as e:
            self.logger.error(f"CSV write failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def append_csv(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Append to CSV file"""
        self.logger.info("Appending to CSV file")
        
        try:
            file_path = parameters.get('file_path', '')
            data = parameters.get('data', [])
            delimiter = parameters.get('delimiter', ',')
            encoding = parameters.get('encoding', 'utf-8')
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, list):
                    data = input_data
                elif isinstance(input_data, dict):
                    data = input_data.get('data', data)
                    file_path = input_data.get('file_path', file_path)
                    delimiter = input_data.get('delimiter', delimiter)
                    encoding = input_data.get('encoding', encoding)
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            if not data:
                return {
                    "success": False,
                    "error": "Data is required"
                }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Append to CSV
            with open(file_path, 'a', encoding=encoding, newline='') as f:
                writer = csv.writer(f, delimiter=delimiter)
                
                # Write data
                for row in data:
                    if isinstance(row, dict):
                        writer.writerow(row.values())
                    else:
                        writer.writerow(row)
            
            return {
                "success": True,
                "file_path": file_path,
                "rows_appended": len(data),
                "delimiter": delimiter,
                "encoding": encoding,
                "message": f"Successfully appended {len(data)} rows to CSV"
            }
            
        except Exception as e:
            self.logger.error(f"CSV append failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def filter_csv(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Filter CSV data"""
        self.logger.info("Filtering CSV data")
        
        try:
            file_path = parameters.get('file_path', '')
            filter_conditions = parameters.get('filter_conditions', {})
            output_path = parameters.get('output_path', '')
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    file_path = input_data.get('file_path', file_path)
                    filter_conditions = input_data.get('filter_conditions', filter_conditions)
                    output_path = input_data.get('output_path', output_path)
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            if not filter_conditions:
                return {
                    "success": False,
                    "error": "Filter conditions are required"
                }
            
            # Read CSV data first
            read_result = await self.read_csv({'file_path': file_path}, context)
            if not read_result['success']:
                return read_result
            
            data = read_result['data']
            headers = read_result['headers']
            
            # Apply filters
            filtered_data = []
            for row in data:
                match = True
                for column, condition in filter_conditions.items():
                    if column not in row:
                        match = False
                        break
                    
                    value = row[column]
                    
                    # Simple condition checking
                    if isinstance(condition, dict):
                        if 'equals' in condition and value != condition['equals']:
                            match = False
                            break
                        if 'contains' in condition and condition['contains'] not in str(value):
                            match = False
                            break
                        if 'greater_than' in condition and float(value) <= float(condition['greater_than']):
                            match = False
                            break
                        if 'less_than' in condition and float(value) >= float(condition['less_than']):
                            match = False
                            break
                    else:
                        # Direct value comparison
                        if value != condition:
                            match = False
                            break
                
                if match:
                    filtered_data.append(row)
            
            # Write filtered data if output path provided
            if output_path:
                write_result = await self.write_csv({
                    'file_path': output_path,
                    'data': filtered_data,
                    'headers': headers
                }, context)
                if not write_result['success']:
                    return write_result
            
            return {
                "success": True,
                "input_file": file_path,
                "output_file": output_path if output_path else None,
                "original_count": len(data),
                "filtered_count": len(filtered_data),
                "data": filtered_data,
                "filter_conditions": filter_conditions,
                "message": f"Successfully filtered {len(data)} rows to {len(filtered_data)} rows"
            }
            
        except Exception as e:
            self.logger.error(f"CSV filter failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def transform_csv(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Transform CSV data"""
        self.logger.info("Transforming CSV data")
        
        try:
            file_path = parameters.get('file_path', '')
            transformations = parameters.get('transformations', {})
            output_path = parameters.get('output_path', '')
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    file_path = input_data.get('file_path', file_path)
                    transformations = input_data.get('transformations', transformations)
                    output_path = input_data.get('output_path', output_path)
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            if not transformations:
                return {
                    "success": False,
                    "error": "Transformations are required"
                }
            
            # Read CSV data first
            read_result = await self.read_csv({'file_path': file_path}, context)
            if not read_result['success']:
                return read_result
            
            data = read_result['data']
            headers = read_result['headers']
            
            # Apply transformations
            transformed_data = []
            for row in data:
                transformed_row = row.copy()
                
                for column, transformation in transformations.items():
                    if column in transformed_row:
                        value = transformed_row[column]
                        
                        if transformation == 'upper':
                            transformed_row[column] = str(value).upper()
                        elif transformation == 'lower':
                            transformed_row[column] = str(value).lower()
                        elif transformation == 'strip':
                            transformed_row[column] = str(value).strip()
                        elif transformation == 'float':
                            try:
                                transformed_row[column] = float(value)
                            except ValueError:
                                transformed_row[column] = 0.0
                        elif transformation == 'int':
                            try:
                                transformed_row[column] = int(float(value))
                            except ValueError:
                                transformed_row[column] = 0
                        elif isinstance(transformation, dict):
                            if 'replace' in transformation:
                                old_val = transformation['replace']['old']
                                new_val = transformation['replace']['new']
                                transformed_row[column] = str(value).replace(old_val, new_val)
                            elif 'prefix' in transformation:
                                transformed_row[column] = transformation['prefix'] + str(value)
                            elif 'suffix' in transformation:
                                transformed_row[column] = str(value) + transformation['suffix']
                
                transformed_data.append(transformed_row)
            
            # Write transformed data if output path provided
            if output_path:
                write_result = await self.write_csv({
                    'file_path': output_path,
                    'data': transformed_data,
                    'headers': headers
                }, context)
                if not write_result['success']:
                    return write_result
            
            return {
                "success": True,
                "input_file": file_path,
                "output_file": output_path if output_path else None,
                "row_count": len(transformed_data),
                "data": transformed_data,
                "transformations": transformations,
                "message": f"Successfully transformed {len(transformed_data)} rows"
            }
            
        except Exception as e:
            self.logger.error(f"CSV transform failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def merge_csv(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Merge multiple CSV files"""
        self.logger.info("Merging CSV files")
        
        try:
            file_paths = parameters.get('file_paths', [])
            output_path = parameters.get('output_path', 'merged.csv')
            merge_type = parameters.get('merge_type', 'concat')  # concat, join
            join_column = parameters.get('join_column', '')
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, list):
                    file_paths = input_data
                elif isinstance(input_data, dict):
                    file_paths = input_data.get('file_paths', file_paths)
                    output_path = input_data.get('output_path', output_path)
                    merge_type = input_data.get('merge_type', merge_type)
                    join_column = input_data.get('join_column', join_column)
            
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
            
            merged_data = []
            all_headers = set()
            
            if merge_type == 'concat':
                # Concatenate all files
                for file_path in file_paths:
                    read_result = await self.read_csv({'file_path': file_path}, context)
                    if not read_result['success']:
                        return read_result
                    
                    data = read_result['data']
                    headers = read_result['headers']
                    
                    all_headers.update(headers)
                    merged_data.extend(data)
                
                # Ensure all rows have all columns
                final_headers = list(all_headers)
                for row in merged_data:
                    for header in final_headers:
                        if header not in row:
                            row[header] = ''
            
            elif merge_type == 'join' and join_column:
                # Join files on specified column
                if not join_column:
                    return {
                        "success": False,
                        "error": "Join column is required for join merge type"
                    }
                
                # Read first file as base
                read_result = await self.read_csv({'file_path': file_paths[0]}, context)
                if not read_result['success']:
                    return read_result
                
                merged_data = read_result['data']
                all_headers.update(read_result['headers'])
                
                # Join with other files
                for file_path in file_paths[1:]:
                    read_result = await self.read_csv({'file_path': file_path}, context)
                    if not read_result['success']:
                        return read_result
                    
                    join_data = read_result['data']
                    join_headers = read_result['headers']
                    all_headers.update(join_headers)
                    
                    # Create lookup dict for join
                    join_lookup = {row[join_column]: row for row in join_data if join_column in row}
                    
                    # Merge data
                    for row in merged_data:
                        if join_column in row and row[join_column] in join_lookup:
                            join_row = join_lookup[row[join_column]]
                            for key, value in join_row.items():
                                if key != join_column:
                                    row[key] = value
                
                final_headers = list(all_headers)
            
            # Write merged data
            write_result = await self.write_csv({
                'file_path': output_path,
                'data': merged_data,
                'headers': final_headers
            }, context)
            if not write_result['success']:
                return write_result
            
            return {
                "success": True,
                "input_files": file_paths,
                "output_file": output_path,
                "merged_files_count": len(file_paths),
                "total_rows": len(merged_data),
                "merge_type": merge_type,
                "join_column": join_column if merge_type == 'join' else None,
                "message": f"Successfully merged {len(file_paths)} CSV files into {output_path}"
            }
            
        except Exception as e:
            self.logger.error(f"CSV merge failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def split_csv(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Split CSV file"""
        self.logger.info("Splitting CSV file")
        
        try:
            file_path = parameters.get('file_path', '')
            split_type = parameters.get('split_type', 'rows')  # rows, column_value
            rows_per_file = parameters.get('rows_per_file', 1000)
            split_column = parameters.get('split_column', '')
            output_dir = parameters.get('output_dir', 'split_files')
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    file_path = input_data.get('file_path', file_path)
                    split_type = input_data.get('split_type', split_type)
                    rows_per_file = input_data.get('rows_per_file', rows_per_file)
                    split_column = input_data.get('split_column', split_column)
                    output_dir = input_data.get('output_dir', output_dir)
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            # Read CSV data first
            read_result = await self.read_csv({'file_path': file_path}, context)
            if not read_result['success']:
                return read_result
            
            data = read_result['data']
            headers = read_result['headers']
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            output_files = []
            
            if split_type == 'rows':
                # Split by number of rows
                for i in range(0, len(data), rows_per_file):
                    chunk = data[i:i + rows_per_file]
                    output_file = os.path.join(output_dir, f"chunk_{i//rows_per_file + 1}.csv")
                    
                    write_result = await self.write_csv({
                        'file_path': output_file,
                        'data': chunk,
                        'headers': headers
                    }, context)
                    if not write_result['success']:
                        return write_result
                    
                    output_files.append(output_file)
            
            elif split_type == 'column_value' and split_column:
                # Split by column values
                if split_column not in headers:
                    return {
                        "success": False,
                        "error": f"Split column '{split_column}' not found in headers"
                    }
                
                # Group by column values
                groups = {}
                for row in data:
                    value = row[split_column]
                    if value not in groups:
                        groups[value] = []
                    groups[value].append(row)
                
                # Write each group to separate file
                for value, group_data in groups.items():
                    safe_filename = str(value).replace('/', '_').replace('\\', '_')
                    output_file = os.path.join(output_dir, f"{split_column}_{safe_filename}.csv")
                    
                    write_result = await self.write_csv({
                        'file_path': output_file,
                        'data': group_data,
                        'headers': headers
                    }, context)
                    if not write_result['success']:
                        return write_result
                    
                    output_files.append(output_file)
            
            return {
                "success": True,
                "input_file": file_path,
                "output_directory": output_dir,
                "output_files": output_files,
                "split_type": split_type,
                "total_rows": len(data),
                "split_files_count": len(output_files),
                "message": f"Successfully split CSV into {len(output_files)} files"
            }
            
        except Exception as e:
            self.logger.error(f"CSV split failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_csv(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate CSV file"""
        self.logger.info("Validating CSV file")
        
        try:
            file_path = parameters.get('file_path', '')
            required_columns = parameters.get('required_columns', [])
            data_types = parameters.get('data_types', {})
            
            # Handle data from context
            if context and 'input_data' in context:
                input_data = context['input_data']
                if isinstance(input_data, dict):
                    file_path = input_data.get('file_path', file_path)
                    required_columns = input_data.get('required_columns', required_columns)
                    data_types = input_data.get('data_types', data_types)
            
            if not file_path:
                return {
                    "success": False,
                    "error": "File path is required"
                }
            
            # Read CSV data first
            read_result = await self.read_csv({'file_path': file_path}, context)
            if not read_result['success']:
                return read_result
            
            data = read_result['data']
            headers = read_result['headers']
            
            validation_errors = []
            
            # Check required columns
            for column in required_columns:
                if column not in headers:
                    validation_errors.append(f"Required column '{column}' not found")
            
            # Check data types
            for column, expected_type in data_types.items():
                if column not in headers:
                    validation_errors.append(f"Data type column '{column}' not found")
                    continue
                
                for row_idx, row in enumerate(data):
                    value = row.get(column, '')
                    if value == '':
                        continue
                    
                    try:
                        if expected_type == 'int':
                            int(value)
                        elif expected_type == 'float':
                            float(value)
                        elif expected_type == 'date':
                            # Simple date validation
                            if not any(char in str(value) for char in ['-', '/', '.']):
                                validation_errors.append(f"Row {row_idx + 1}: '{column}' is not a valid date")
                    except ValueError:
                        validation_errors.append(f"Row {row_idx + 1}: '{column}' is not a valid {expected_type}")
            
            is_valid = len(validation_errors) == 0
            
            return {
                "success": True,
                "file_path": file_path,
                "is_valid": is_valid,
                "validation_errors": validation_errors,
                "total_rows": len(data),
                "headers": headers,
                "required_columns": required_columns,
                "data_types": data_types,
                "message": f"CSV validation {'passed' if is_valid else 'failed'}"
            }
            
        except Exception as e:
            self.logger.error(f"CSV validation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations"""
        return ['read', 'write', 'append', 'filter', 'transform', 'merge', 'split', 'validate']
