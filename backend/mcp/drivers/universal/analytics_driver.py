"""
Analytics Driver - Handles analytics and monitoring operations
Supports: Google Analytics, custom metrics, performance tracking
"""

import logging
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Union
import json
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# Add the parent directories to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(backend_dir)
mcp_dir = os.path.join(backend_dir, 'mcp')
sys.path.append(mcp_dir)

from mcp.universal_driver_manager import BaseUniversalDriver

class AnalyticsDriver(BaseUniversalDriver):
    """Universal driver for analytics and monitoring operations"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "analytics_driver"
        self.supported_node_types = [
            'n8n-nodes-base.googleAnalytics',
            'analytics.report',
            'analytics.metric',
            'analytics.event',
            'analytics.pageview',
            'analytics.custom'
        ]
        self.ga_base_url = "https://analyticsreporting.googleapis.com/v4/reports:batchGet"
        self.ga4_base_url = "https://analyticsdata.googleapis.com/v1beta"
        self.metrics_store = {}
    
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
            resource = node_type.split('.')[-1] if '.' in node_type else 'report'
            operation = parameters.get('operation', 'get')
            
            if resource == 'googleAnalytics' or resource == 'report':
                return await self._handle_analytics_operations(operation, parameters, context)
            elif resource == 'metric':
                return await self._handle_metric_operations(operation, parameters, context)
            elif resource == 'event':
                return await self._handle_event_operations(operation, parameters, context)
            elif resource == 'pageview':
                return await self._handle_pageview_operations(operation, parameters, context)
            elif resource == 'custom':
                return await self._handle_custom_operations(operation, parameters, context)
            else:
                return await self._handle_analytics_operations(operation, parameters, context)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "node_type": node_type
            }
    
    async def _handle_analytics_operations(self, operation: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle Google Analytics operations"""
        self.logger.info(f"Handling analytics operation: {operation}")
        
        try:
            if operation == 'getReport':
                return await self._get_analytics_report(parameters, context)
            elif operation == 'getRealtimeReport':
                return await self._get_realtime_report(parameters, context)
            elif operation == 'getAudienceReport':
                return await self._get_audience_report(parameters, context)
            elif operation == 'getTrafficReport':
                return await self._get_traffic_report(parameters, context)
            elif operation == 'getConversionReport':
                return await self._get_conversion_report(parameters, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown analytics operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Analytics operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_metric_operations(self, operation: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle custom metric operations"""
        self.logger.info(f"Handling metric operation: {operation}")
        
        try:
            if operation == 'track':
                return await self._track_metric(parameters, context)
            elif operation == 'get':
                return await self._get_metric(parameters, context)
            elif operation == 'getAll':
                return await self._get_all_metrics(parameters, context)
            elif operation == 'aggregate':
                return await self._aggregate_metrics(parameters, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown metric operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Metric operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_event_operations(self, operation: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle event tracking operations"""
        self.logger.info(f"Handling event operation: {operation}")
        
        try:
            if operation == 'track':
                return await self._track_event(parameters, context)
            elif operation == 'batch':
                return await self._batch_track_events(parameters, context)
            elif operation == 'get':
                return await self._get_events(parameters, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown event operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Event operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_pageview_operations(self, operation: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle pageview tracking operations"""
        self.logger.info(f"Handling pageview operation: {operation}")
        
        try:
            if operation == 'track':
                return await self._track_pageview(parameters, context)
            elif operation == 'get':
                return await self._get_pageviews(parameters, context)
            elif operation == 'getPopularPages':
                return await self._get_popular_pages(parameters, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown pageview operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Pageview operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_custom_operations(self, operation: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle custom analytics operations"""
        self.logger.info(f"Handling custom operation: {operation}")
        
        try:
            if operation == 'createDashboard':
                return await self._create_dashboard(parameters, context)
            elif operation == 'getDashboard':
                return await self._get_dashboard(parameters, context)
            elif operation == 'alert':
                return await self._create_alert(parameters, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown custom operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Custom operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_analytics_report(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Google Analytics report"""
        
        # Get credentials
        access_token = self._get_access_token(parameters, context)
        if not access_token:
            return {
                "success": False,
                "error": "Google Analytics access token is required"
            }
        
        view_id = parameters.get('view_id', '')
        start_date = parameters.get('start_date', '7daysAgo')
        end_date = parameters.get('end_date', 'today')
        metrics = parameters.get('metrics', ['sessions', 'users'])
        dimensions = parameters.get('dimensions', ['date'])
        
        if not view_id:
            return {
                "success": False,
                "error": "View ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Build request body
        request_body = {
            "reportRequests": [
                {
                    "viewId": view_id,
                    "dateRanges": [
                        {
                            "startDate": start_date,
                            "endDate": end_date
                        }
                    ],
                    "metrics": [{"expression": f"ga:{metric}"} for metric in metrics],
                    "dimensions": [{"name": f"ga:{dimension}"} for dimension in dimensions]
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.ga_base_url, headers=headers, json=request_body) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Process the response
                    if 'reports' in data and data['reports']:
                        report = data['reports'][0]
                        processed_data = self._process_analytics_report(report)
                        
                        return {
                            "success": True,
                            "data": processed_data,
                            "raw_data": data,
                            "message": "Analytics report retrieved successfully"
                        }
                    else:
                        return {
                            "success": False,
                            "error": "No data found in report"
                        }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('error', {}).get('message', 'Unknown error')
                    }
    
    async def _get_realtime_report(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get Google Analytics realtime report"""
        
        # Get credentials
        access_token = self._get_access_token(parameters, context)
        if not access_token:
            return {
                "success": False,
                "error": "Google Analytics access token is required"
            }
        
        view_id = parameters.get('view_id', '')
        metrics = parameters.get('metrics', ['activeUsers'])
        dimensions = parameters.get('dimensions', ['country'])
        
        if not view_id:
            return {
                "success": False,
                "error": "View ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Build query parameters
        params = {
            'ids': f'ga:{view_id}',
            'metrics': ','.join([f'rt:{metric}' for metric in metrics]),
            'dimensions': ','.join([f'rt:{dimension}' for dimension in dimensions])
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.googleapis.com/analytics/v3/data/realtime', 
                                 headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "success": True,
                        "data": data,
                        "message": "Realtime report retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('error', {}).get('message', 'Unknown error')
                    }
    
    async def _track_metric(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Track a custom metric"""
        
        metric_name = parameters.get('metric_name', '')
        value = parameters.get('value', 0)
        timestamp = parameters.get('timestamp', datetime.utcnow().isoformat())
        tags = parameters.get('tags', {})
        
        if not metric_name:
            return {
                "success": False,
                "error": "Metric name is required"
            }
        
        # Store metric in memory (in production, use a proper database)
        if metric_name not in self.metrics_store:
            self.metrics_store[metric_name] = []
        
        metric_data = {
            'value': value,
            'timestamp': timestamp,
            'tags': tags
        }
        
        self.metrics_store[metric_name].append(metric_data)
        
        # Keep only last 1000 entries per metric
        if len(self.metrics_store[metric_name]) > 1000:
            self.metrics_store[metric_name] = self.metrics_store[metric_name][-1000:]
        
        return {
            "success": True,
            "metric_name": metric_name,
            "value": value,
            "timestamp": timestamp,
            "tags": tags,
            "message": f"Metric '{metric_name}' tracked successfully"
        }
    
    async def _get_metric(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a specific metric"""
        
        metric_name = parameters.get('metric_name', '')
        start_time = parameters.get('start_time', '')
        end_time = parameters.get('end_time', '')
        
        if not metric_name:
            return {
                "success": False,
                "error": "Metric name is required"
            }
        
        if metric_name not in self.metrics_store:
            return {
                "success": False,
                "error": f"Metric '{metric_name}' not found"
            }
        
        metrics = self.metrics_store[metric_name]
        
        # Filter by time range if provided
        if start_time or end_time:
            filtered_metrics = []
            for metric in metrics:
                metric_time = metric['timestamp']
                if start_time and metric_time < start_time:
                    continue
                if end_time and metric_time > end_time:
                    continue
                filtered_metrics.append(metric)
            metrics = filtered_metrics
        
        return {
            "success": True,
            "metric_name": metric_name,
            "data": metrics,
            "count": len(metrics),
            "message": f"Retrieved {len(metrics)} data points for metric '{metric_name}'"
        }
    
    async def _get_all_metrics(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get all tracked metrics"""
        
        metrics_summary = {}
        
        for metric_name, data in self.metrics_store.items():
            if data:
                latest_value = data[-1]['value']
                count = len(data)
                
                # Calculate average
                avg_value = sum(item['value'] for item in data) / count
                
                metrics_summary[metric_name] = {
                    'latest_value': latest_value,
                    'average_value': avg_value,
                    'data_points': count,
                    'latest_timestamp': data[-1]['timestamp']
                }
        
        return {
            "success": True,
            "metrics": metrics_summary,
            "total_metrics": len(metrics_summary),
            "message": f"Retrieved {len(metrics_summary)} metrics"
        }
    
    async def _aggregate_metrics(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate metrics data"""
        
        metric_name = parameters.get('metric_name', '')
        aggregation_type = parameters.get('aggregation_type', 'sum')  # sum, avg, min, max, count
        group_by = parameters.get('group_by', 'hour')  # hour, day, week, month
        
        if not metric_name:
            return {
                "success": False,
                "error": "Metric name is required"
            }
        
        if metric_name not in self.metrics_store:
            return {
                "success": False,
                "error": f"Metric '{metric_name}' not found"
            }
        
        metrics = self.metrics_store[metric_name]
        
        # Group metrics by time period
        grouped_data = {}
        for metric in metrics:
            timestamp = datetime.fromisoformat(metric['timestamp'].replace('Z', '+00:00'))
            
            if group_by == 'hour':
                key = timestamp.strftime('%Y-%m-%d %H:00:00')
            elif group_by == 'day':
                key = timestamp.strftime('%Y-%m-%d')
            elif group_by == 'week':
                key = timestamp.strftime('%Y-W%W')
            elif group_by == 'month':
                key = timestamp.strftime('%Y-%m')
            else:
                key = timestamp.isoformat()
            
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append(metric['value'])
        
        # Apply aggregation
        aggregated_data = {}
        for key, values in grouped_data.items():
            if aggregation_type == 'sum':
                aggregated_data[key] = sum(values)
            elif aggregation_type == 'avg':
                aggregated_data[key] = sum(values) / len(values)
            elif aggregation_type == 'min':
                aggregated_data[key] = min(values)
            elif aggregation_type == 'max':
                aggregated_data[key] = max(values)
            elif aggregation_type == 'count':
                aggregated_data[key] = len(values)
        
        return {
            "success": True,
            "metric_name": metric_name,
            "aggregation_type": aggregation_type,
            "group_by": group_by,
            "data": aggregated_data,
            "message": f"Aggregated metric '{metric_name}' by {group_by} using {aggregation_type}"
        }
    
    async def _track_event(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Track an event"""
        
        event_name = parameters.get('event_name', '')
        event_category = parameters.get('event_category', 'general')
        event_action = parameters.get('event_action', '')
        event_label = parameters.get('event_label', '')
        event_value = parameters.get('event_value', 1)
        properties = parameters.get('properties', {})
        
        if not event_name:
            return {
                "success": False,
                "error": "Event name is required"
            }
        
        event_data = {
            'event_name': event_name,
            'event_category': event_category,
            'event_action': event_action,
            'event_label': event_label,
            'event_value': event_value,
            'properties': properties,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store event (in production, send to analytics service)
        if 'events' not in self.metrics_store:
            self.metrics_store['events'] = []
        
        self.metrics_store['events'].append(event_data)
        
        # Keep only last 1000 events
        if len(self.metrics_store['events']) > 1000:
            self.metrics_store['events'] = self.metrics_store['events'][-1000:]
        
        return {
            "success": True,
            "event_data": event_data,
            "message": f"Event '{event_name}' tracked successfully"
        }
    
    async def _track_pageview(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Track a pageview"""
        
        page_url = parameters.get('page_url', '')
        page_title = parameters.get('page_title', '')
        user_id = parameters.get('user_id', '')
        session_id = parameters.get('session_id', '')
        referrer = parameters.get('referrer', '')
        
        if not page_url:
            return {
                "success": False,
                "error": "Page URL is required"
            }
        
        pageview_data = {
            'page_url': page_url,
            'page_title': page_title,
            'user_id': user_id,
            'session_id': session_id,
            'referrer': referrer,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store pageview (in production, send to analytics service)
        if 'pageviews' not in self.metrics_store:
            self.metrics_store['pageviews'] = []
        
        self.metrics_store['pageviews'].append(pageview_data)
        
        # Keep only last 1000 pageviews
        if len(self.metrics_store['pageviews']) > 1000:
            self.metrics_store['pageviews'] = self.metrics_store['pageviews'][-1000:]
        
        return {
            "success": True,
            "pageview_data": pageview_data,
            "message": f"Pageview for '{page_url}' tracked successfully"
        }
    
    def _process_analytics_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Process Google Analytics report data"""
        
        processed_data = {
            'column_headers': [],
            'rows': [],
            'totals': {}
        }
        
        # Extract column headers
        if 'columnHeader' in report:
            header = report['columnHeader']
            if 'dimensions' in header:
                processed_data['column_headers'].extend(header['dimensions'])
            if 'metricHeader' in header and 'metricHeaderEntries' in header['metricHeader']:
                for entry in header['metricHeader']['metricHeaderEntries']:
                    processed_data['column_headers'].append(entry['name'])
        
        # Extract rows
        if 'data' in report and 'rows' in report['data']:
            for row in report['data']['rows']:
                processed_row = {}
                
                # Add dimensions
                if 'dimensions' in row:
                    for i, dim in enumerate(row['dimensions']):
                        if i < len(processed_data['column_headers']):
                            processed_row[processed_data['column_headers'][i]] = dim
                
                # Add metrics
                if 'metrics' in row:
                    for metric_set in row['metrics']:
                        if 'values' in metric_set:
                            metric_start_idx = len(row.get('dimensions', []))
                            for i, value in enumerate(metric_set['values']):
                                header_idx = metric_start_idx + i
                                if header_idx < len(processed_data['column_headers']):
                                    processed_row[processed_data['column_headers'][header_idx]] = value
                
                processed_data['rows'].append(processed_row)
        
        # Extract totals
        if 'data' in report and 'totals' in report['data']:
            for total_set in report['data']['totals']:
                if 'values' in total_set:
                    metric_headers = [h for h in processed_data['column_headers'] if h.startswith('ga:')]
                    for i, value in enumerate(total_set['values']):
                        if i < len(metric_headers):
                            processed_data['totals'][metric_headers[i]] = value
        
        return processed_data
    
    def _get_access_token(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Optional[str]:
        """Get Google Analytics access token"""
        
        # Try parameters first
        if 'access_token' in parameters:
            return parameters['access_token']
        
        # Try context credentials
        if context and 'credentials' in context:
            credentials = context['credentials']
            if 'google_analytics' in credentials:
                return credentials['google_analytics'].get('access_token', '')
        
        # Try environment variables
        return os.getenv('GOOGLE_ANALYTICS_ACCESS_TOKEN', '')
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations"""
        return [
            'getReport', 'getRealtimeReport', 'getAudienceReport',
            'getTrafficReport', 'getConversionReport', 'track', 'get',
            'getAll', 'aggregate', 'batch', 'getPopularPages',
            'createDashboard', 'getDashboard', 'alert'
        ]
