#!/usr/bin/env python3
"""
Universal Driver Registry Report
Lists all 48 loaded node drivers with comprehensive details
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(backend_dir)

from mcp.universal_driver_manager import UniversalDriverManager

class DriverRegistryReport:
    def __init__(self):
        self.manager = None
        self.driver_details = {}
        self.categories = {
            'email': [],
            'ai_llm': [],
            'http_api': [],
            'database': [],
            'data_processing': [],
            'google_services': [],
            'messaging': [],
            'productivity': [],
            'social_media': [],
            'file_processing': [],
            'conditional_logic': [],
            'automation_core': [],
            'other': []
        }
    
    async def initialize_manager(self):
        """Initialize the driver manager"""
        print("🔧 Initializing Universal Driver Manager...")
        
        self.manager = UniversalDriverManager()
        await self.manager.load_all_drivers()
        
        driver_count = len(self.manager.loaded_drivers)
        print(f"✅ Loaded {driver_count} drivers successfully")
        return driver_count
    
    def categorize_driver(self, driver_name: str, node_types: list) -> str:
        """Categorize driver based on name and node types"""
        
        name_lower = driver_name.lower()
        node_types_str = ' '.join(node_types).lower()
        
        # Email drivers
        if any(word in name_lower for word in ['email', 'gmail', 'smtp', 'imap']):
            return 'email'
        if any(word in node_types_str for word in ['email', 'gmail']):
            return 'email'
        
        # AI/LLM drivers
        if any(word in name_lower for word in ['openai', 'ai', 'llm', 'chat', 'langchain']):
            return 'ai_llm'
        if any(word in node_types_str for word in ['openai', 'langchain', 'chat']):
            return 'ai_llm'
        
        # HTTP/API drivers
        if any(word in name_lower for word in ['http', 'api', 'webhook', 'request']):
            return 'http_api'
        if any(word in node_types_str for word in ['http', 'webhook']):
            return 'http_api'
        
        # Database drivers
        if any(word in name_lower for word in ['mysql', 'postgres', 'mongodb', 'database', 'sql']):
            return 'database'
        if any(word in node_types_str for word in ['mysql', 'postgres', 'mongodb']):
            return 'database'
        
        # Google Services
        if any(word in name_lower for word in ['google', 'gmail', 'drive', 'sheets', 'docs']):
            return 'google_services'
        if any(word in node_types_str for word in ['google', 'gmail']):
            return 'google_services'
        
        # Messaging
        if any(word in name_lower for word in ['slack', 'telegram', 'discord', 'message']):
            return 'messaging'
        if any(word in node_types_str for word in ['slack', 'telegram']):
            return 'messaging'
        
        # Social Media
        if any(word in name_lower for word in ['twitter', 'facebook', 'linkedin', 'social']):
            return 'social_media'
        if any(word in node_types_str for word in ['twitter']):
            return 'social_media'
        
        # File Processing
        if any(word in name_lower for word in ['file', 'csv', 'json', 'pdf', 'xml']):
            return 'file_processing'
        if any(word in node_types_str for word in ['file', 'csv', 'json', 'pdf']):
            return 'file_processing'
        
        # Data Processing
        if any(word in name_lower for word in ['data', 'processor', 'transform', 'filter', 'set']):
            return 'data_processing'
        if any(word in node_types_str for word in ['set', 'filter', 'transform']):
            return 'data_processing'
        
        # Conditional Logic
        if any(word in name_lower for word in ['if', 'condition', 'switch', 'merge']):
            return 'conditional_logic'
        if any(word in node_types_str for word in ['if', 'switch', 'merge']):
            return 'conditional_logic'
        
        # Productivity
        if any(word in name_lower for word in ['asana', 'trello', 'notion', 'calendar']):
            return 'productivity'
        if any(word in node_types_str for word in ['asana', 'trello']):
            return 'productivity'
        
        # Automation Core
        if any(word in name_lower for word in ['trigger', 'schedule', 'cron', 'wait']):
            return 'automation_core'
        if any(word in node_types_str for word in ['trigger', 'schedule', 'cron']):
            return 'automation_core'
        
        return 'other'
    
    def analyze_all_drivers(self):
        """Analyze all loaded drivers"""
        print("\n🔍 Analyzing Driver Registry...")
        
        for driver_name, driver_instance in self.manager.loaded_drivers.items():
            try:
                # Get supported node types
                node_types = driver_instance.get_supported_node_types()
                
                # Get driver category
                category = self.categorize_driver(driver_name, node_types)
                
                # Create driver info
                driver_info = {
                    'name': driver_name,
                    'class_name': driver_instance.__class__.__name__,
                    'node_types': node_types,
                    'node_count': len(node_types),
                    'category': category,
                    'module': driver_instance.__module__ if hasattr(driver_instance, '__module__') else 'unknown'
                }
                
                # Try to get additional info if available
                if hasattr(driver_instance, 'get_driver_info'):
                    try:
                        extra_info = driver_instance.get_driver_info()
                        driver_info.update(extra_info)
                    except:
                        pass
                
                self.driver_details[driver_name] = driver_info
                self.categories[category].append(driver_info)
                
            except Exception as e:
                print(f"   ⚠️ Error analyzing {driver_name}: {e}")
    
    def generate_comprehensive_report(self):
        """Generate detailed driver report"""
        print("\n" + "=" * 80)
        print("📋 UNIVERSAL DRIVER REGISTRY REPORT")
        print("=" * 80)
        
        total_drivers = len(self.driver_details)
        total_node_types = sum(info['node_count'] for info in self.driver_details.values())
        
        print(f"📊 REGISTRY OVERVIEW:")
        print(f"   • Total Drivers: {total_drivers}")
        print(f"   • Total Node Types: {total_node_types}")
        print(f"   • Categories: {len([cat for cat in self.categories.values() if cat])}")
        print()
        
        # Category breakdown
        print(f"📂 DRIVER CATEGORIES:")
        for category_name, drivers in self.categories.items():
            if drivers:
                node_count = sum(d['node_count'] for d in drivers)
                print(f"   • {category_name.replace('_', ' ').title()}: {len(drivers)} drivers, {node_count} node types")
        print()
        
        # Detailed driver listing by category
        for category_name, drivers in self.categories.items():
            if drivers:
                print(f"🔧 {category_name.replace('_', ' ').upper()} DRIVERS:")
                
                for i, driver in enumerate(sorted(drivers, key=lambda x: x['name']), 1):
                    print(f"   {i:2d}. {driver['name']}")
                    print(f"       Class: {driver['class_name']}")
                    print(f"       Node Types: {driver['node_count']}")
                    
                    # Show first few node types
                    if driver['node_types']:
                        if len(driver['node_types']) <= 3:
                            print(f"       Supports: {', '.join(driver['node_types'])}")
                        else:
                            print(f"       Supports: {', '.join(driver['node_types'][:3])}, ... (+{len(driver['node_types'])-3} more)")
                    
                    print()
                
                print()
        
        # Top drivers by node type coverage
        print(f"🏆 TOP DRIVERS BY NODE TYPE COVERAGE:")
        top_drivers = sorted(self.driver_details.values(), key=lambda x: x['node_count'], reverse=True)[:10]
        
        for i, driver in enumerate(top_drivers, 1):
            print(f"   {i:2d}. {driver['name']}: {driver['node_count']} node types")
        print()
        
        # Complete alphabetical listing
        print(f"📜 COMPLETE DRIVER LISTING (Alphabetical):")
        print(f"{'#':>3} {'Driver Name':<35} {'Category':<20} {'Node Types':<12} {'Class Name'}")
        print(f"{'-'*3} {'-'*35} {'-'*20} {'-'*12} {'-'*30}")
        
        sorted_drivers = sorted(self.driver_details.values(), key=lambda x: x['name'])
        for i, driver in enumerate(sorted_drivers, 1):
            category_display = driver['category'].replace('_', ' ').title()[:19]
            class_name = driver['class_name'][:29]
            print(f"{i:>3} {driver['name']:<35} {category_display:<20} {driver['node_count']:<12} {class_name}")
        
        print()
        
        # Node type registry overview
        print(f"🎯 NODE TYPE REGISTRY OVERVIEW:")
        
        # Count node types by category
        category_node_counts = {}
        for category_name, drivers in self.categories.items():
            if drivers:
                node_count = sum(d['node_count'] for d in drivers)
                category_node_counts[category_name] = node_count
        
        sorted_categories = sorted(category_node_counts.items(), key=lambda x: x[1], reverse=True)
        
        for category, count in sorted_categories:
            percentage = (count / total_node_types) * 100
            print(f"   • {category.replace('_', ' ').title()}: {count} node types ({percentage:.1f}%)")
        
        print()
        
        # Summary statistics
        print(f"📈 DRIVER STATISTICS:")
        avg_nodes_per_driver = total_node_types / total_drivers if total_drivers > 0 else 0
        max_nodes = max(info['node_count'] for info in self.driver_details.values()) if self.driver_details else 0
        min_nodes = min(info['node_count'] for info in self.driver_details.values()) if self.driver_details else 0
        
        print(f"   • Average Node Types per Driver: {avg_nodes_per_driver:.1f}")
        print(f"   • Maximum Node Types (single driver): {max_nodes}")
        print(f"   • Minimum Node Types (single driver): {min_nodes}")
        print()
        
        print(f"🎉 DRIVER REGISTRY ANALYSIS COMPLETE!")
        print(f"   Total Coverage: {total_drivers} drivers supporting {total_node_types} node types")

async def main():
    """Main function to generate driver report"""
    
    reporter = DriverRegistryReport()
    
    # Initialize and load drivers
    driver_count = await reporter.initialize_manager()
    
    if driver_count == 0:
        print("❌ No drivers loaded - cannot generate report")
        return
    
    # Analyze all drivers
    reporter.analyze_all_drivers()
    
    # Generate comprehensive report
    reporter.generate_comprehensive_report()

if __name__ == "__main__":
    asyncio.run(main())
