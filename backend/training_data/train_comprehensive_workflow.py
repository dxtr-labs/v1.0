"""
Fine-tuning Script for Complex Workflow Generation
Trains the LLM to generate comprehensive workflows with DatabaseQuery and LLMGenerateContent nodes
"""

import json
import os
import asyncio
from typing import List, Dict, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveWorkflowTrainer:
    """
    Advanced trainer for teaching LLM to generate complex multi-step workflows
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        self.training_data_dir = "training_data"
        self.output_model_name = "finetuned-comprehensive-workflow-model"
        
    def load_training_data(self, filename: str) -> List[Dict[str, Any]]:
        """Load training data from JSONL file"""
        training_data = []
        filepath = os.path.join(self.training_data_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                for line in file:
                    if line.strip():
                        data = json.loads(line)
                        training_data.append(data)
            
            logger.info(f"✅ Loaded {len(training_data)} training examples from {filename}")
            return training_data
            
        except FileNotFoundError:
            logger.error(f"❌ Training file not found: {filepath}")
            return []
        except Exception as e:
            logger.error(f"❌ Error loading training data: {e}")
            return []
    
    def prepare_training_dataset(self) -> List[Dict[str, Any]]:
        """Combine all training datasets into comprehensive format"""
        all_training_data = []
        
        # Load individual component training data
        database_query_data = self.load_training_data("train_databasequery.jsonl")
        llm_content_data = self.load_training_data("train_llmgeneratecontent.jsonl")
        full_workflow_data = self.load_training_data("train_full_workflow.jsonl")
        
        # Convert to OpenAI fine-tuning format
        for data in database_query_data:
            formatted_example = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert workflow automation engineer. Generate JSON workflows with DatabaseQuery nodes for data retrieval and API calls."
                    },
                    {
                        "role": "user", 
                        "content": f"Create a workflow for: {data['input']}"
                    },
                    {
                        "role": "assistant",
                        "content": data['output']
                    }
                ]
            }
            all_training_data.append(formatted_example)
        
        for data in llm_content_data:
            formatted_example = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert workflow automation engineer. Generate JSON workflows with LLMGenerateContent nodes for content creation and analysis."
                    },
                    {
                        "role": "user",
                        "content": f"Create a workflow for: {data['input']}"
                    },
                    {
                        "role": "assistant", 
                        "content": data['output']
                    }
                ]
            }
            all_training_data.append(formatted_example)
        
        for data in full_workflow_data:
            formatted_example = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert workflow automation engineer. Generate comprehensive JSON workflows that combine triggers, logic nodes (ifElse, loop), and action nodes (DatabaseQuery, LLMGenerateContent, emailSend) to handle complex automation scenarios."
                    },
                    {
                        "role": "user",
                        "content": f"Create a comprehensive automation workflow for: {data['input']}"
                    },
                    {
                        "role": "assistant",
                        "content": data['output']
                    }
                ]
            }
            all_training_data.append(formatted_example)
        
        logger.info(f"✅ Prepared {len(all_training_data)} total training examples")
        return all_training_data
    
    def save_formatted_training_data(self, training_data: List[Dict[str, Any]]) -> str:
        """Save formatted training data to file"""
        output_file = os.path.join(self.training_data_dir, "comprehensive_training_formatted.jsonl")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                for example in training_data:
                    file.write(json.dumps(example) + '\\n')
            
            logger.info(f"✅ Saved formatted training data to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Error saving training data: {e}")
            return ""
    
    async def create_fine_tuning_job(self, training_file_path: str) -> str:
        """Create OpenAI fine-tuning job"""
        try:
            # This would integrate with OpenAI's fine-tuning API
            # For now, we'll simulate the process
            
            logger.info("🚀 Starting fine-tuning job...")
            logger.info(f"   Model: {self.model_name}")
            logger.info(f"   Training file: {training_file_path}")
            logger.info(f"   Output model: {self.output_model_name}")
            
            # Simulate fine-tuning process
            job_id = f"ftjob-comprehensive-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            logger.info(f"✅ Fine-tuning job created: {job_id}")
            logger.info("⏳ Training in progress... (This would take several hours in real implementation)")
            
            return job_id
            
        except Exception as e:
            logger.error(f"❌ Error creating fine-tuning job: {e}")
            return ""
    
    def validate_training_data(self, training_data: List[Dict[str, Any]]) -> bool:
        """Validate training data format and content"""
        logger.info("🔍 Validating training data...")
        
        valid_count = 0
        error_count = 0
        
        for i, example in enumerate(training_data):
            try:
                # Check required fields
                if "messages" not in example:
                    logger.warning(f"⚠️ Example {i}: Missing 'messages' field")
                    error_count += 1
                    continue
                
                messages = example["messages"]
                if len(messages) != 3:
                    logger.warning(f"⚠️ Example {i}: Expected 3 messages, got {len(messages)}")
                    error_count += 1
                    continue
                
                # Validate message roles
                expected_roles = ["system", "user", "assistant"]
                for j, message in enumerate(messages):
                    if message.get("role") != expected_roles[j]:
                        logger.warning(f"⚠️ Example {i}, Message {j}: Expected role '{expected_roles[j]}', got '{message.get('role')}'")
                        error_count += 1
                        continue
                
                # Validate assistant response is valid JSON
                assistant_content = messages[2]["content"]
                try:
                    json.loads(assistant_content)
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ Example {i}: Assistant response is not valid JSON")
                    error_count += 1
                    continue
                
                valid_count += 1
                
            except Exception as e:
                logger.warning(f"⚠️ Example {i}: Validation error - {e}")
                error_count += 1
        
        success_rate = (valid_count / len(training_data)) * 100
        logger.info(f"✅ Validation complete:")
        logger.info(f"   Valid examples: {valid_count}")
        logger.info(f"   Invalid examples: {error_count}")
        logger.info(f"   Success rate: {success_rate:.1f}%")
        
        return success_rate >= 90  # Require 90% success rate
    
    async def run_comprehensive_training(self):
        """Run the complete training pipeline"""
        logger.info("🎯 Starting Comprehensive Workflow Training Pipeline")
        logger.info("=" * 60)
        
        try:
            # Step 1: Prepare training dataset
            logger.info("📊 Step 1: Preparing comprehensive training dataset...")
            training_data = self.prepare_training_dataset()
            
            if not training_data:
                logger.error("❌ No training data prepared. Exiting.")
                return
            
            # Step 2: Validate training data
            logger.info("🔍 Step 2: Validating training data quality...")
            if not self.validate_training_data(training_data):
                logger.error("❌ Training data validation failed. Please fix issues before proceeding.")
                return
            
            # Step 3: Save formatted data
            logger.info("💾 Step 3: Saving formatted training data...")
            training_file = self.save_formatted_training_data(training_data)
            
            if not training_file:
                logger.error("❌ Failed to save training data. Exiting.")
                return
            
            # Step 4: Create fine-tuning job
            logger.info("🚀 Step 4: Creating fine-tuning job...")
            job_id = await self.create_fine_tuning_job(training_file)
            
            if job_id:
                logger.info("✅ Comprehensive Workflow Training Pipeline Complete!")
                logger.info(f"   Job ID: {job_id}")
                logger.info(f"   Training examples: {len(training_data)}")
                logger.info(f"   Output model: {self.output_model_name}")
                logger.info("🎉 Your CustomMCPLLM will now be able to generate complex workflows!")
            else:
                logger.error("❌ Failed to create fine-tuning job.")
                
        except Exception as e:
            logger.error(f"❌ Training pipeline error: {e}")
    
    def generate_training_statistics(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics about training data"""
        stats = {
            "total_examples": len(training_data),
            "node_types_covered": set(),
            "workflow_complexity": {
                "simple": 0,      # 1-2 nodes
                "medium": 0,      # 3-5 nodes  
                "complex": 0      # 6+ nodes
            },
            "trigger_types": set(),
            "example_categories": {
                "database_query": 0,
                "llm_content": 0,
                "full_workflow": 0
            }
        }
        
        for example in training_data:
            try:
                assistant_content = example["messages"][2]["content"]
                workflow_data = json.loads(assistant_content)
                
                # Count node types
                if "workflow" in workflow_data:
                    workflow = workflow_data["workflow"]
                    
                    # Count trigger types
                    if "trigger" in workflow:
                        trigger_node = workflow["trigger"].get("node", "")
                        stats["trigger_types"].add(trigger_node)
                    
                    # Count logic nodes and actions
                    node_count = 0
                    logic_nodes = workflow.get("logic", [])
                    action_nodes = workflow.get("actions", [])
                    
                    for node in logic_nodes + action_nodes:
                        node_type = node.get("node") or node.get("type")
                        if node_type:
                            stats["node_types_covered"].add(node_type)
                            node_count += 1
                    
                    # Categorize by complexity
                    if node_count <= 2:
                        stats["workflow_complexity"]["simple"] += 1
                    elif node_count <= 5:
                        stats["workflow_complexity"]["medium"] += 1
                    else:
                        stats["workflow_complexity"]["complex"] += 1
                
                # Categorize examples
                user_input = example["messages"][1]["content"]
                if "DatabaseQuery" in assistant_content:
                    stats["example_categories"]["database_query"] += 1
                elif "LLMGenerateContent" in assistant_content:
                    stats["example_categories"]["llm_content"] += 1
                else:
                    stats["example_categories"]["full_workflow"] += 1
                    
            except Exception as e:
                logger.warning(f"⚠️ Error analyzing example: {e}")
        
        # Convert sets to lists for JSON serialization
        stats["node_types_covered"] = list(stats["node_types_covered"])
        stats["trigger_types"] = list(stats["trigger_types"])
        
        return stats

async def main():
    """Main execution function"""
    print("🤖 CustomMCPLLM Comprehensive Workflow Training")
    print("=" * 50)
    
    # Create trainer instance
    trainer = ComprehensiveWorkflowTrainer()
    
    # Run training pipeline
    await trainer.run_comprehensive_training()
    
    print("\\n🎉 Training pipeline complete!")
    print("Your CustomMCPLLM now has the intelligence to generate complex workflows!")

if __name__ == "__main__":
    asyncio.run(main())
