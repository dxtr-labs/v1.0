"""
Stripe Driver - Handles Stripe payment processing operations
Supports: customers, payments, subscriptions, invoices, products
"""

import logging
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Union
import json
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

class StripeDriver(BaseUniversalDriver):
    """Universal driver for Stripe payment processing operations"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "stripe_driver"
        self.supported_node_types = [
            'n8n-nodes-base.stripe',
            'stripe.customer',
            'stripe.payment',
            'stripe.subscription',
            'stripe.invoice',
            'stripe.product',
            'stripe.charge'
        ]
        self.base_url = "https://api.stripe.com/v1"
    
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
            # Get API key
            api_key = self._get_api_key(parameters, context)
            if not api_key:
                return {
                    "success": False,
                    "error": "Stripe API key is required"
                }
            
            resource = node_type.split('.')[-1] if '.' in node_type else 'customer'
            operation = parameters.get('operation', 'get')
            
            if resource == 'customer':
                return await self._handle_customer_operations(operation, parameters, api_key, context)
            elif resource == 'payment':
                return await self._handle_payment_operations(operation, parameters, api_key, context)
            elif resource == 'subscription':
                return await self._handle_subscription_operations(operation, parameters, api_key, context)
            elif resource == 'invoice':
                return await self._handle_invoice_operations(operation, parameters, api_key, context)
            elif resource == 'product':
                return await self._handle_product_operations(operation, parameters, api_key, context)
            elif resource == 'charge':
                return await self._handle_charge_operations(operation, parameters, api_key, context)
            else:
                return await self._handle_customer_operations(operation, parameters, api_key, context)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "node_type": node_type
            }
    
    async def _handle_customer_operations(self, operation: str, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle customer operations"""
        self.logger.info(f"Handling Stripe customer operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_customer(parameters, api_key, context)
            elif operation == 'getAll':
                return await self._get_all_customers(parameters, api_key, context)
            elif operation == 'create':
                return await self._create_customer(parameters, api_key, context)
            elif operation == 'update':
                return await self._update_customer(parameters, api_key, context)
            elif operation == 'delete':
                return await self._delete_customer(parameters, api_key, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown customer operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Customer operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_payment_operations(self, operation: str, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle payment operations"""
        self.logger.info(f"Handling Stripe payment operation: {operation}")
        
        try:
            if operation == 'create':
                return await self._create_payment_intent(parameters, api_key, context)
            elif operation == 'get':
                return await self._get_payment_intent(parameters, api_key, context)
            elif operation == 'confirm':
                return await self._confirm_payment_intent(parameters, api_key, context)
            elif operation == 'cancel':
                return await self._cancel_payment_intent(parameters, api_key, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown payment operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Payment operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_subscription_operations(self, operation: str, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle subscription operations"""
        self.logger.info(f"Handling Stripe subscription operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_subscription(parameters, api_key, context)
            elif operation == 'getAll':
                return await self._get_all_subscriptions(parameters, api_key, context)
            elif operation == 'create':
                return await self._create_subscription(parameters, api_key, context)
            elif operation == 'update':
                return await self._update_subscription(parameters, api_key, context)
            elif operation == 'cancel':
                return await self._cancel_subscription(parameters, api_key, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown subscription operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Subscription operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_invoice_operations(self, operation: str, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle invoice operations"""
        self.logger.info(f"Handling Stripe invoice operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_invoice(parameters, api_key, context)
            elif operation == 'getAll':
                return await self._get_all_invoices(parameters, api_key, context)
            elif operation == 'create':
                return await self._create_invoice(parameters, api_key, context)
            elif operation == 'pay':
                return await self._pay_invoice(parameters, api_key, context)
            elif operation == 'void':
                return await self._void_invoice(parameters, api_key, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown invoice operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Invoice operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_product_operations(self, operation: str, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle product operations"""
        self.logger.info(f"Handling Stripe product operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_product(parameters, api_key, context)
            elif operation == 'getAll':
                return await self._get_all_products(parameters, api_key, context)
            elif operation == 'create':
                return await self._create_product(parameters, api_key, context)
            elif operation == 'update':
                return await self._update_product(parameters, api_key, context)
            elif operation == 'delete':
                return await self._delete_product(parameters, api_key, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown product operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Product operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_charge_operations(self, operation: str, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle charge operations"""
        self.logger.info(f"Handling Stripe charge operation: {operation}")
        
        try:
            if operation == 'get':
                return await self._get_charge(parameters, api_key, context)
            elif operation == 'getAll':
                return await self._get_all_charges(parameters, api_key, context)
            elif operation == 'create':
                return await self._create_charge(parameters, api_key, context)
            elif operation == 'capture':
                return await self._capture_charge(parameters, api_key, context)
            elif operation == 'refund':
                return await self._refund_charge(parameters, api_key, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown charge operation: {operation}"
                }
        except Exception as e:
            self.logger.error(f"Charge operation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_customer(self, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new customer"""
        email = parameters.get('email', '')
        name = parameters.get('name', '')
        description = parameters.get('description', '')
        metadata = parameters.get('metadata', {})
        
        if not email:
            return {
                "success": False,
                "error": "Email is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'email': email,
            'name': name,
            'description': description
        }
        
        # Add metadata
        for key, value in metadata.items():
            data[f'metadata[{key}]'] = value
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/customers", headers=headers, data=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return {
                        "success": True,
                        "data": response_data,
                        "message": "Customer created successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('error', {}).get('message', 'Unknown error')
                    }
    
    async def _get_customer(self, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a specific customer"""
        customer_id = parameters.get('customer_id', '')
        
        if not customer_id:
            return {
                "success": False,
                "error": "Customer ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/customers/{customer_id}", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "Customer retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('error', {}).get('message', 'Unknown error')
                    }
    
    async def _get_all_customers(self, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get all customers"""
        limit = parameters.get('limit', 10)
        starting_after = parameters.get('starting_after', '')
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'limit': min(limit, 100)
        }
        
        if starting_after:
            params['starting_after'] = starting_after
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/customers", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "count": len(data.get('data', [])),
                        "message": "Customers retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('error', {}).get('message', 'Unknown error')
                    }
    
    async def _create_payment_intent(self, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a payment intent"""
        amount = parameters.get('amount', 0)
        currency = parameters.get('currency', 'usd')
        customer_id = parameters.get('customer_id', '')
        payment_method = parameters.get('payment_method', '')
        description = parameters.get('description', '')
        
        if not amount or amount <= 0:
            return {
                "success": False,
                "error": "Amount must be greater than 0"
            }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'amount': int(amount * 100),  # Convert to cents
            'currency': currency,
            'description': description
        }
        
        if customer_id:
            data['customer'] = customer_id
        if payment_method:
            data['payment_method'] = payment_method
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/payment_intents", headers=headers, data=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return {
                        "success": True,
                        "data": response_data,
                        "message": "Payment intent created successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('error', {}).get('message', 'Unknown error')
                    }
    
    async def _get_payment_intent(self, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a payment intent"""
        payment_intent_id = parameters.get('payment_intent_id', '')
        
        if not payment_intent_id:
            return {
                "success": False,
                "error": "Payment intent ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/payment_intents/{payment_intent_id}", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "Payment intent retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('error', {}).get('message', 'Unknown error')
                    }
    
    async def _confirm_payment_intent(self, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Confirm a payment intent"""
        payment_intent_id = parameters.get('payment_intent_id', '')
        payment_method = parameters.get('payment_method', '')
        
        if not payment_intent_id:
            return {
                "success": False,
                "error": "Payment intent ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {}
        if payment_method:
            data['payment_method'] = payment_method
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/payment_intents/{payment_intent_id}/confirm", headers=headers, data=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return {
                        "success": True,
                        "data": response_data,
                        "message": "Payment intent confirmed successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('error', {}).get('message', 'Unknown error')
                    }
    
    async def _create_subscription(self, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a subscription"""
        customer_id = parameters.get('customer_id', '')
        price_id = parameters.get('price_id', '')
        trial_period_days = parameters.get('trial_period_days', None)
        
        if not customer_id:
            return {
                "success": False,
                "error": "Customer ID is required"
            }
        
        if not price_id:
            return {
                "success": False,
                "error": "Price ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'customer': customer_id,
            'items[0][price]': price_id
        }
        
        if trial_period_days:
            data['trial_period_days'] = trial_period_days
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/subscriptions", headers=headers, data=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return {
                        "success": True,
                        "data": response_data,
                        "message": "Subscription created successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('error', {}).get('message', 'Unknown error')
                    }
    
    async def _get_subscription(self, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a subscription"""
        subscription_id = parameters.get('subscription_id', '')
        
        if not subscription_id:
            return {
                "success": False,
                "error": "Subscription ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/subscriptions/{subscription_id}", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "Subscription retrieved successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('error', {}).get('message', 'Unknown error')
                    }
    
    async def _cancel_subscription(self, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Cancel a subscription"""
        subscription_id = parameters.get('subscription_id', '')
        
        if not subscription_id:
            return {
                "success": False,
                "error": "Subscription ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/subscriptions/{subscription_id}", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "message": "Subscription cancelled successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('error', {}).get('message', 'Unknown error')
                    }
    
    async def _create_charge(self, parameters: Dict[str, Any], api_key: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a charge"""
        amount = parameters.get('amount', 0)
        currency = parameters.get('currency', 'usd')
        source = parameters.get('source', '')
        customer_id = parameters.get('customer_id', '')
        description = parameters.get('description', '')
        
        if not amount or amount <= 0:
            return {
                "success": False,
                "error": "Amount must be greater than 0"
            }
        
        if not source and not customer_id:
            return {
                "success": False,
                "error": "Source or customer ID is required"
            }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'amount': int(amount * 100),  # Convert to cents
            'currency': currency,
            'description': description
        }
        
        if source:
            data['source'] = source
        if customer_id:
            data['customer'] = customer_id
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/charges", headers=headers, data=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return {
                        "success": True,
                        "data": response_data,
                        "message": "Charge created successfully"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('error', {}).get('message', 'Unknown error')
                    }
    
    def _get_api_key(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Optional[str]:
        """Get Stripe API key"""
        
        # Try parameters first
        if 'api_key' in parameters:
            return parameters['api_key']
        
        # Try context credentials
        if context and 'credentials' in context:
            credentials = context['credentials']
            if 'stripe' in credentials:
                return credentials['stripe'].get('api_key', '')
        
        # Try environment variables
        return os.getenv('STRIPE_API_KEY', '')
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations"""
        return [
            'get', 'getAll', 'create', 'update', 'delete',
            'confirm', 'cancel', 'pay', 'void', 'capture', 'refund'
        ]
