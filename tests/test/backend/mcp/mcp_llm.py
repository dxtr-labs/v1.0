import json
import os
import asyncio
import asyncpg
import uuid
from core.simple_agent_manager import AgentManager # Import the AgentManager

# Optional imports for ML capabilities
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from peft import PeftModel # For loading LoRA adapters
    PEFT_AVAILABLE = True
except ImportError:
    PEFT_AVAILABLE = False

class MCP_LLM_Orchestrator:
    def __init__(self, db_config: dict = None, fine_tuned_model_path: str = None):
        """
        Initializes the MCP_LLM_Orchestrator.

        Args:
            db_config (dict): Database connection configuration (host, port, user, password, dbname).
            fine_tuned_model_path (str): Path to your fine-tuned LLM model (e.g., "finetuned-full-workflow-model").
        """
        # Set defaults if not provided
        if db_config is None:
            db_config = {
                "host": os.getenv("PGHOST", "localhost"),
                "port": int(os.getenv("PGPORT", 5432)),
                "user": os.getenv("PGUSER", "postgres"),
                "password": os.getenv("PGPASSWORD", "your_password"),
                "database": os.getenv("PGDATABASE", "automation")
            }
        
        if fine_tuned_model_path is None:
            fine_tuned_model_path = os.getenv("FINE_TUNED_MODEL_PATH", "mock-model")
            
        self.db_config = db_config
        self.fine_tuned_model_path = fine_tuned_model_path
        self.db_pool = None # Connection pool for async DB operations
        self.agent_manager = None # AgentManager instance
        self.tokenizer = None
        self.model = None
        self.system_prompt_template = self._get_base_system_prompt()
        self.chat_history = [] # Stores conversation turns for the current session
        self.current_workflow_draft = {} # Stores the partially or fully built workflow JSON

        # Define the schemas for your action, logic, and trigger nodes.
        # These schemas guide the LLM's output and are used for validation.
        self.node_schemas = self._define_automation_node_schemas()

    async def _init_db_pool(self):
        """Initializes the PostgreSQL connection pool and AgentManager."""
        if self.db_pool is None:
            self.db_pool = await asyncpg.create_pool(**self.db_config)
            self.agent_manager = AgentManager(self.db_pool) # Initialize AgentManager
            print("Database connection pool and AgentManager initialized.")

    async def _load_fine_tuned_llm(self):
        """Loads the fine-tuned LLM and tokenizer."""
        if not TRANSFORMERS_AVAILABLE:
            print("⚠️ Transformers library not available. Running in mock mode.")
            self.mock_llm_mode = True
            self.model = None
            self.tokenizer = None
            return
            
        if self.tokenizer is None or self.model is None:
            try:
                print(f"Loading tokenizer from {self.fine_tuned_model_path}...")
                self.tokenizer = AutoTokenizer.from_pretrained(self.fine_tuned_model_path)
                if self.tokenizer.pad_token is None:
                    self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})

                print(f"Loading base model and LoRA adapters from {self.fine_tuned_model_path}...")
                base_model_id = "deepseek-ai/deepseek-llm-7b-chat" # Or deepseek-coder-1.3b-base
                
                from transformers import BitsAndBytesConfig
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=False,
                    bnb_4bit_compute_dtype=torch.float16,
                )

                self.model = AutoModelForCausalLM.from_pretrained(
                    base_model_id,
                    quantization_config=bnb_config,
                    device_map="auto",
                    torch_dtype=torch.float16,
                    attn_implementation="eager",
                )
                
                if PEFT_AVAILABLE and os.path.exists(self.fine_tuned_model_path):
                    self.model = PeftModel.from_pretrained(self.model, self.fine_tuned_model_path)
                    self.model = self.model.merge_and_unload()
                else:
                    print("⚠️ PEFT not available or model path doesn't exist. Using base model only.")
                    
                self.model.eval()
                print("Fine-tuned LLM loaded successfully.")

                if self.tokenizer.pad_token_id is not None and len(self.tokenizer) > self.model.config.vocab_size:
                    self.model.resize_token_embeddings(len(self.tokenizer))
                    
            except Exception as e:
                print(f"❌ Failed to load model: {e}")
                print("🔄 Falling back to mock mode...")
                self.mock_llm_mode = True
                self.model = None
                self.tokenizer = None


    def _get_base_system_prompt(self) -> str:
        """Defines the base instructions for the LLM."""
        return """
        You are an intelligent automation agent designed to help users build workflows.
        Your goal is to understand the user's request, gather all necessary information,
        and generate a complete, valid JSON workflow definition.
        You can communicate with the user to ask for missing parameters.
        Once the workflow is complete, you will present it for user confirmation.

        ---
        Available Workflow Structure (JSON Schema):
        The top-level output should be a JSON object with a 'workflow' key.
        The 'workflow' object can contain 'trigger', 'logic' (optional, an array), and 'actions' (an array).

        Example Workflow Structure:
        {
          "workflow": {
            "trigger": { ... },
            "logic": [ { ... } ],
            "actions": [ { ... } ]
          }
        }

        ---
        Available Nodes (Tools) and their parameters:

        - emailSend: Send an email.
            Parameters:
                - toEmail (string, required): Recipient's email address.
                - subject (string, required): Subject of the email.
                - text (string, required): Body of the email in plain text.
                - fromEmail (string, optional): Sender's email address. (Default: 'automations@yourdomain.com')
                - html (string, optional): HTML body of the email.

        - httpRequest: Make an HTTP request.
            Parameters:
                - url (string, required): The URL to send the request to.
                - method (string, required): HTTP method (GET, POST, PUT, DELETE, PATCH).
                - body (object, optional): Request body (e.g., {"type": "json", "data": {...}}).
                - headers (array, optional): Array of header objects (e.g., [{"name": "Content-Type", "value": "application/json"}]).

        - cron: Schedule a workflow to run at specific times.
            Parameters:
                - triggerTimes (array of objects, required): Array of schedule objects. Each object needs:
                    - hour (integer, required): Hour (0-23).
                    - minute (integer, required): Minute (0-59).
                    - weekday (string, optional): Day of week (0-6, or '*', '1-5').
                    - dayOfMonth (integer, optional): Day of month (1-31, or '*').
                    - month (string, optional): Month (1-12, or '*').

        - webhook: Listen for incoming HTTP requests to trigger a workflow.
            Parameters:
                - path (string, required): The URL path for the webhook (e.g., '/new-user-signup').
                - method (string, optional): HTTP method to listen for (GET, POST, PUT, DELETE, PATCH). (Default: 'POST')

        - emailReadImap: Read emails from an IMAP server.
            Parameters:
                - mailbox (string, required): Mailbox to read from (e.g., 'INBOX').
                - postProcessAction (string, required): Action after reading ('read' or 'delete').
                - format (string, required): Output format ('simple' or 'resolved').
                - downloadAttachments (boolean, optional): Whether to download attachments.
                - options (object, optional): Custom IMAP search options (e.g., {"customEmailConfig": "[\\"UNSEEN\\", [\\"SUBJECT\\", \\"invoice\\"]]"} )

        - twilio: Send SMS or WhatsApp messages.
            Parameters:
                - to (string, required): Recipient's phone number.
                - message (string, required): The message content.
                - toWhatsapp (boolean, optional): True for WhatsApp, False for SMS.
                - from (string, optional): Your Twilio sender number. (Default: '+14151234567')

        - ifElse: Create conditional branches in the workflow.
            Parameters:
                - condition (string, required): The condition to evaluate (e.g., "{{$json.status == 'completed'}}").
                - truePath (array of objects, required): Array of nodes to execute if the condition is true.
                - falsePath (array of objects, required): Array of nodes to execute if the condition is false.

        - loopItems: Iterate over a list of items.
            Parameters:
                - items (string, required): The expression for the list to iterate over (e.g., "{{$node['Get Data'].json['users']}}").
                - loopBody (array of objects, required): Array of nodes to execute for each item within the loop.

        ---
        Your output for a completed workflow must be a single JSON object matching the 'workflow' schema.
        If you need more information from the user to complete the workflow, respond with a natural language question.
        If the user asks a general question not related to workflow building, respond conversationally.
        """

    def _define_automation_node_schemas(self) -> dict:
        """
        Defines the JSON schemas for all available nodes (actions, logic, and triggers).
        These are used both in the system prompt and for validation.
        """
        # Define schemas for each node type.
        # This is crucial for guiding the LLM's output and for validation.
        email_send_schema = {
            "type": "object",
            "properties": {
                "node": {"type": "string", "enum": ["emailSend"]},
                "parameters": {
                    "type": "object",
                    "properties": {
                        "toEmail": {"type": "string"},
                        "subject": {"type": "string"},
                        "text": {"type": "string"},
                        "fromEmail": {"type": "string"},
                        "html": {"type": "string"}
                    },
                    "required": ["toEmail", "subject", "text"]
                }
            },
            "required": ["node", "parameters"]
        }
        http_request_schema = {
            "type": "object",
            "properties": {
                "node": {"type": "string", "enum": ["httpRequest"]},
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]},
                        "body": {"type": "object"},
                        "headers": {"type": "array", "items": {"type": "object"}}
                    },
                    "required": ["url", "method"]
                }
            },
            "required": ["node", "parameters"]
        }
        cron_schema = {
            "type": "object",
            "properties": {
                "node": {"type": "string", "enum": ["cron"]},
                "parameters": {
                    "type": "object",
                    "properties": {
                        "triggerTimes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "hour": {"type": "integer", "minimum": 0, "maximum": 23},
                                    "minute": {"type": "integer", "minimum": 0, "maximum": 59},
                                    "weekday": {"type": "string"},
                                    "dayOfMonth": {"type": "integer", "minimum": 1, "maximum": 31},
                                    "month": {"type": "string"}
                                },
                                "required": ["hour", "minute"] # Weekday, dayOfMonth, month can be wildcards
                            }
                        }
                    },
                    "required": ["triggerTimes"]
                }
            },
            "required": ["node", "parameters"]
        }
        webhook_schema = {
            "type": "object",
            "properties": {
                "node": {"type": "string", "enum": ["webhook"]},
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]}
                    },
                    "required": ["path"]
                }
            },
            "required": ["node", "parameters"]
        }
        email_read_imap_schema = {
            "type": "object",
            "properties": {
                "node": {"type": "string", "enum": ["emailReadImap"]},
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mailbox": {"type": "string"},
                        "postProcessAction": {"type": "string", "enum": ["read", "delete"]},
                        "format": {"type": "string", "enum": ["simple", "resolved"]},
                        "downloadAttachments": {"type": "boolean"},
                        "options": {"type": "object"}
                    },
                    "required": ["mailbox", "postProcessAction", "format"]
                }
            },
            "required": ["node", "parameters"]
        }
        twilio_schema = {
            "type": "object",
            "properties": {
                "node": {"type": "string", "enum": ["twilio"]},
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "message": {"type": "string"},
                        "toWhatsapp": {"type": "boolean"},
                        "from": {"type": "string"}
                    },
                    "required": ["to", "message"]
                }
            },
            "required": ["node", "parameters"]
        }
        if_else_schema = {
            "type": "object",
            "properties": {
                "node": {"type": "string", "enum": ["ifElse"]},
                "parameters": {
                    "type": "object",
                    "properties": {
                        "condition": {"type": "string"},
                        "truePath": {"type": "array", "items": {"type": "object"}}, # Can contain nested nodes
                        "falsePath": {"type": "array", "items": {"type": "object"}} # Can contain nested nodes
                    },
                    "required": ["condition", "truePath", "falsePath"]
                }
            },
            "required": ["node", "parameters"]
        }
        loop_items_schema = {
            "type": "object",
            "properties": {
                "node": {"type": "string", "enum": ["loopItems"]},
                "parameters": {
                    "type": "object",
                    "properties": {
                        "items": {"type": "string"},
                        "loopBody": {"type": "array", "items": {"type": "object"}} # Can contain nested nodes
                    },
                    "required": ["items", "loopBody"]
                }
            },
            "required": ["node", "parameters"]
        }


        # Define the overall workflow schema that the LLM should output
        workflow_definition_schema = {
            "type": "object",
            "properties": {
                "workflow": {
                    "type": "object",
                    "properties": {
                        "trigger": {"type": "object", "description": "The trigger node for the workflow."},
                        "logic": {
                            "type": "array",
                            "items": {"type": "object"}, # Each item is a logic node
                            "description": "An array of logic nodes (e.g., ifElse, loopItems)."
                        },
                        "actions": {
                            "type": "array",
                            "items": {"type": "object"}, # Each item is an action node
                            "description": "An array of action nodes to be executed sequentially."
                        }
                    },
                    "required": ["trigger", "actions"] # Workflows must have at least a trigger and actions
                }
            },
            "required": ["workflow"]
        }

        return {
            "emailSend": email_send_schema,
            "httpRequest": http_request_schema,
            "cron": cron_schema,
            "webhook": webhook_schema,
            "emailReadImap": email_read_imap_schema,
            "twilio": twilio_schema,
            "ifElse": if_else_schema,
            "loopItems": loop_items_schema,
            "workflow_definition": workflow_definition_schema
        }

    async def _fetch_user_and_agent_context(self, user_id: str, agent_id: str) -> dict:
        """
        Fetches user-specific and agent-specific context from the database using AgentManager.
        """
        await self._init_db_pool() # Ensure pool and AgentManager are initialized

        user_context = {}
        agent_context = {}

        try:
            # Fetch user memory context
            async with self.db_pool.acquire() as conn:
                # Set RLS context for fetching user's own memory_context
                await conn.execute(f"SET app.current_user_id = '{user_id}';")
                await conn.execute("SET ROLE app_user;") # Assume app_user for fetching self context
                user_row = await conn.fetchrow(
                    "SELECT memory_context FROM users WHERE user_id = $1",
                    user_id
                )
                if user_row and user_row['memory_context']:
                    user_context['memory_context'] = user_row['memory_context']
                await conn.execute("RESET ROLE;")
                await conn.execute("RESET app.current_user_id;")

            # Fetch agent details and memory context using AgentManager
            # AgentManager handles RLS internally based on the user_id passed
            agent_data = await self.agent_manager.get_agent_details(agent_id, user_id=user_id, is_admin=False)
            if agent_data:
                agent_context = {
                    'agent_name': agent_data.get('agent_name'),
                    'agent_role': agent_data.get('agent_role'),
                    'agent_personality': agent_data.get('agent_personality'),
                    'agent_expectations': agent_data.get('agent_expectations'),
                    'agent_memory_context': agent_data.get('agent_memory_context')
                }
        except Exception as e:
            print(f"Error fetching context from DB: {e}")
            # Log error, but don't re-raise if context is not critical for basic operation
        
        return {"user": user_context, "agent": agent_context}

    async def _build_llm_prompt(self, user_id: str, agent_id: str, user_message: str) -> list:
        """
        Constructs the full prompt for the LLM, including system instructions,
        user/agent context, and chat history.
        """
        context_data = await self._fetch_user_and_agent_context(user_id, agent_id)

        # Build dynamic system prompt based on agent personality/role
        dynamic_system_prompt_parts = []
        if context_data['agent']:
            dynamic_system_prompt_parts.append(f"You are {context_data['agent']['agent_name']}, an AI assistant with the role of a {context_data['agent']['agent_role']}.")
            dynamic_system_prompt_parts.append(f"Your personality is: {context_data['agent']['agent_personality']}")
            dynamic_system_prompt_parts.append(f"Your key expectations are: {context_data['agent']['agent_expectations']}")
            dynamic_system_prompt_parts.append("---")

        dynamic_system_prompt_parts.append(self.system_prompt_template) # Add base prompt

        if context_data['user'].get('memory_context'):
            dynamic_system_prompt_parts.append(f"\n---User Context---\n{context_data['user']['memory_context']}")
        if context_data['agent'].get('agent_memory_context'):
            dynamic_system_prompt_parts.append(f"\n---Agent Specific Memory---\n{context_data['agent']['agent_memory_context']}")

        full_system_prompt = "\n".join(dynamic_system_prompt_parts)

        # Prepare chat history for LLM API call
        # The first message is always the system prompt
        messages = [{"role": "system", "parts": [{"text": full_system_prompt}]}]
        messages.extend(self.chat_history) # Add previous turns

        # Add the current user message
        messages.append({"role": "user", "parts": [{"text": user_message}]})

        # If there's a current workflow draft, include it to guide the LLM
        if self.current_workflow_draft:
            messages.append({"role": "assistant", "parts": [{"text": f"### Current Workflow Draft:\n{json.dumps(self.current_workflow_draft, indent=2)}\n### Continue:"}]})

        return messages

    async def process_user_input(self, user_id: str, agent_id: str, user_message: str) -> dict:
        """
        Processes user input, interacts with the LLM, and manages the workflow building process.

        Returns a dictionary with status, message, and potentially the workflow JSON.
        Status can be: "info_needed", "review_needed", "conversational", "error", "completed".
        """
        await self._init_db_pool() # Ensure DB pool and AgentManager are initialized
        await self._load_fine_tuned_llm() # Ensure LLM is loaded

        # Append current user message to chat history for this session
        self.chat_history.append({"role": "user", "parts": [{"text": user_message}]})

        # Build the full prompt including dynamic context
        full_llm_prompt_messages = await self._build_llm_prompt(user_id, agent_id, user_message)

        try:
            # --- LLM API Call ---
            # Convert messages to a format suitable for your local model's generation
            # This part is crucial and depends on your specific model's chat template.
            # DeepSeek-LLM-7b-chat typically uses: <|user|>\n{query}\n<|assistant|>
            # For multi-turn, it concatenates.
            # For system messages, it's often prepended to the first user message or handled implicitly.
            
            # Using tokenizer.apply_chat_template is the most robust way if available.
            # If not, the manual concatenation below is a starting point.
            
            # Example for DeepSeek-LLM-7b-chat's expected format for inference:
            # This is a common pattern for models fine-tuned with instruction-response pairs
            # and might need adjustment based on your exact fine-tuning prompt format.
            formatted_prompt_text = ""
            for msg in full_llm_prompt_messages:
                if msg["role"] == "system":
                    # System instruction often goes at the very beginning or with the first user turn
                    formatted_prompt_text = f"### System Instruction:\n{msg['parts'][0]['text']}\n\n" + formatted_prompt_text
                elif msg["role"] == "user":
                    formatted_prompt_text += f"### Instruction:\n{msg['parts'][0]['text']}\n\n"
                elif msg["role"] == "assistant":
                    formatted_prompt_text += f"### Response:\n{msg['parts'][0]['text']}\n\n"
            formatted_prompt_text += "### Response:\n" # Model should generate the response here

            inputs = self.tokenizer(formatted_prompt_text, return_tensors="pt").to(self.model.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=512, # Max tokens for the LLM's response
                    num_return_sequences=1,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    do_sample=True, # Enable sampling for more varied responses
                    top_p=0.9, # Nucleus sampling
                    temperature=0.7 # Controls randomness
                )
            
            # Decode the generated text, excluding the input prompt
            llm_response_text = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()

            # --- End LLM API Call ---

            try:
                # Attempt to parse as JSON (full workflow)
                parsed_llm_output = json.loads(llm_response_text)
                if "workflow" in parsed_llm_output:
                    # Step A.5: Check if parameters are completed and validate
                    validation_result = self._validate_workflow_json(parsed_llm_output["workflow"])

                    if validation_result["is_valid"]:
                        self.current_workflow_draft = parsed_llm_output["workflow"]
                        # Step A.7: Convert JSON back to natural format for user review
                        human_readable_summary = self._convert_json_to_natural_language(self.current_workflow_draft)
                        # Append LLM's full JSON response to history for context
                        self.chat_history.append({"role": "assistant", "parts": [{"text": llm_response_text}]})
                        return {"status": "review_needed", "message": human_readable_summary, "workflow_json": self.current_workflow_draft}
                    else:
                        # Step A.4: Parameters missing or invalid - ask back to user
                        question = self._formulate_clarifying_question(validation_result["missing_params"], parsed_llm_output["workflow"])
                        self.chat_history.append({"role": "assistant", "parts": [{"text": question}]})
                        return {"status": "info_needed", "message": question, "workflow_json": parsed_llm_output["workflow"]}
                else:
                    # LLM responded with valid JSON but not a workflow (e.g., just an action node)
                    # This case might need refinement in your LLM's training to always output 'workflow'
                    self.chat_history.append({"role": "assistant", "parts": [{"text": llm_response_text}]})
                    return {"status": "conversational", "message": "I received a structured response, but it's not a complete workflow. Let's refine it."}

            except json.JSONDecodeError:
                # LLM responded with natural language (e.g., a greeting or clarification)
                self.chat_history.append({"role": "assistant", "parts": [{"text": llm_response_text}]})
                return {"status": "conversational", "message": llm_response_text}

        except Exception as e:
            print(f"Error during LLM interaction: {e}")
            self.chat_history.append({"role": "assistant", "parts": [{"text": "I encountered an error. Please try again."}]})
            return {"status": "error", "message": "I encountered an error. Please try again."}

    async def update_memory_context(self, user_id: str, agent_id: str, conversation_segment: str):
        """
        Analyzes a conversation segment and updates user/agent memory context in the database.
        This would typically be a separate, background LLM call.
        """
        print(f"Simulating memory update for user {user_id}, agent {agent_id} based on: {conversation_segment[:50]}...")
        
        # This is a conceptual implementation. You'd use a specific prompt
        # to ask the LLM to extract facts from `conversation_segment`.
        # Example prompt: "Extract key facts about the user's company or preferences from this text: {conversation_segment}"
        
        # For now, let's just simulate an update.
        # In a real scenario, you'd call the LLM to extract structured facts
        # and then update the database using self.agent_manager or a UserManager.
        
        # Example:
        # extracted_facts_prompt = f"Extract key facts about the user's company or preferences from this text: {conversation_segment}\nOutput as JSON: {{'fact1': 'value1', 'fact2': 'value2'}}"
        # facts_inputs = self.tokenizer(extracted_facts_prompt, return_tensors="pt").to(self.model.device)
        # with torch.no_grad():
        #     facts_outputs = self.model.generate(**facts_inputs, max_new_tokens=100, num_return_sequences=1)
        # extracted_facts_text = self.tokenizer.decode(facts_outputs[0][facts_inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
        
        # try:
        #     new_facts = json.loads(extracted_facts_text)
        #     # Fetch current memory, merge, and update
        #     current_agent_data = await self.agent_manager.get_agent_details(agent_id, user_id=user_id, is_admin=False)
        #     current_memory = current_agent_data.get('agent_memory_context', {})
        #     if isinstance(current_memory, str): # Handle case where it's still a string
        #         try: current_memory = json.loads(current_memory)
        #         except: current_memory = {}
        #     
        #     merged_memory = {**current_memory, **new_facts} # Simple merge
        #     await self.agent_manager.update_agent_memory(agent_id, merged_memory, user_id=user_id, is_admin=False)
        #     print(f"Memory updated for agent {agent_id}.")
        # except json.JSONDecodeError:
        #     print(f"Could not parse extracted facts for memory update: {extracted_facts_text}")
        # except Exception as e:
        #     print(f"Failed to update agent memory: {e}")


    def _validate_workflow_json(self, workflow_json: dict) -> dict:
        """
        Validates the generated workflow JSON against predefined schemas.
        This is a critical step to ensure the LLM's output is executable.
        """
        # This is a simplified placeholder. Real validation would be complex.
        # You'd use a JSON schema validator library (e.g., `jsonschema`).
        # Check if 'trigger' and 'actions' are present and are dict/list respectively
        if not isinstance(workflow_json, dict) or "trigger" not in workflow_json or "actions" not in workflow_json:
            return {"is_valid": False, "missing_params": ["workflow structure (trigger/actions)"]}

        # Basic check for trigger node
        if not isinstance(workflow_json["trigger"], dict) or "node" not in workflow_json["trigger"]:
             return {"is_valid": False, "missing_params": ["trigger node definition"]}

        # Basic check for action nodes
        if not isinstance(workflow_json["actions"], list) or not workflow_json["actions"]:
            return {"is_valid": False, "missing_params": ["action nodes list"]}

        # You'd loop through actions and logic nodes, validating each against its specific schema
        # For example:
        # for action in workflow_json["actions"]:
        #     if action["node"] == "emailSend":
        #         # Validate action['parameters'] against self.node_schemas['emailSend']
        #         # Check for required fields like 'toEmail', 'subject', 'text'
        #         if "toEmail" not in action["parameters"]:
        #             return {"is_valid": False, "missing_params": ["emailSend.toEmail"]}
        # etc.

        return {"is_valid": True, "missing_params": []}

    def _formulate_clarifying_question(self, missing_params: list, current_draft: dict) -> str:
        """
        Formulates a natural language question to the user for missing parameters.
        Can be rule-based or use the LLM itself.
        """
        if "workflow structure" in missing_params:
            return "I need more details to build the workflow. Could you tell me what you want to automate?"
        
        if missing_params:
            return f"I need more information to complete the workflow. Specifically, I'm missing: {', '.join(missing_params)}. Can you provide these details?"
        return "I need a bit more information. Could you elaborate?"


    def _convert_json_to_natural_language(self, workflow_json: dict) -> str:
        """
        Converts the complete workflow JSON into a human-readable summary for user review.
        This can be rule-based or LLM-assisted (recommended for complex workflows).
        """
        summary_parts = ["I've drafted the following automation workflow for your review:"]

        # Summarize Trigger
        trigger = workflow_json.get("trigger", {})
        if trigger.get("node") == "cron":
            summary_parts.append(f"- It will run on a schedule: {trigger['parameters'].get('triggerTimes')}")
        elif trigger.get("node") == "webhook":
            summary_parts.append(f"- It will be triggered by a webhook at path: {trigger['parameters'].get('path')}")
        # Add other trigger types

        # Summarize Logic (simplified)
        logic_nodes = workflow_json.get("logic", [])
        if logic_nodes:
            summary_parts.append("- It includes conditional logic or loops.")
            # You could iterate and describe each logic node in more detail

        # Summarize Actions (detailed, especially for email content)
        actions = workflow_json.get("actions", [])
        for action in actions:
            if action.get("node") == "emailSend":
                params = action.get("parameters", {})
                summary_parts.append(f"\n- **Email Action:**")
                summary_parts.append(f"  To: {params.get('toEmail', 'N/A')}")
                summary_parts.append(f"  Subject: {params.get('subject', 'N/A')}")
                summary_parts.append(f"  Body:\n    {params.get('text', 'N/A')}")
            elif action.get("node") == "httpRequest":
                params = action.get("parameters", {})
                summary_parts.append(f"\n- **HTTP Request Action:**")
                summary_parts.append(f"  Method: {params.get('method', 'N/A')}")
                summary_parts.append(f"  URL: {params.get('url', 'N/A')}")
                if params.get('body'):
                    summary_parts.append(f"  Body: {json.dumps(params['body'])}")
            # Add summaries for other action nodes (Twilio, etc.)

        summary_parts.append("\nDo you confirm this workflow? (Yes/No)")
        return "\n".join(summary_parts)

# --- Example Usage (Conceptual - how you'd use this class in your application) ---
# This part would typically be in your web server's endpoint for handling chat messages.
async def main():
    # Replace with your actual DB connection details from .env.local
    db_config = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": os.getenv("PGPORT", 5432),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", "your_db_password"),
        "database": os.getenv("PGDATABASE", "automation")
    }
    # Path where your fine-tuned model (LoRA adapters) is saved
    fine_tuned_model_path = "finetuned-full-workflow-model" # Ensure this matches your training output

    orchestrator = MCP_LLM_Orchestrator(db_config, fine_tuned_model_path)
    
    # --- Agent Creation Example (for initial setup or UI interaction) ---
    # This would typically happen via a web UI where a user defines a new agent.
    # For demonstration, let's create a dummy user and agent.
    # In a real app, user_id comes from authentication.
    dummy_user_id = "a1b2c3d4-e5f6-7890-1234-567890abcdef" # Use a real UUID for testing
    
    # Initialize DB pool and agent manager outside the orchestrator for this setup step
    temp_db_pool = await asyncpg.create_pool(**db_config)
    temp_agent_manager = AgentManager(temp_db_pool)

    try:
        # Create a dummy user if not exists (for testing RLS)
        async with temp_db_pool.acquire() as conn:
            await conn.execute("SET app.current_user_id = '00000000-0000-0000-0000-000000000000';") # Admin or temp user for initial user creation
            await conn.execute("SET ROLE app_admin;") # Or a role with INSERT on users
            await conn.execute("""
                INSERT INTO users (user_id, email, password)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO NOTHING;
            """, uuid.UUID(dummy_user_id), f"testuser_{dummy_user_id[:8]}@example.com", "hashed_password")
            await conn.execute("RESET ROLE;")
            await conn.execute("RESET app.current_user_id;")


        # Try to create a new agent
        print("\nAttempting to create a new agent...")
        new_agent_data = await temp_agent_manager.create_agent(
            user_id=dummy_user_id,
            agent_name="Marketing Maestro",
            agent_role="Email Marketing Automation Specialist",
            agent_personality="Creative, persuasive, and data-driven.",
            agent_expectations="Always suggest A/B testing. Optimize for conversion rates."
        )
        if new_agent_data:
            test_agent_id = str(new_agent_data['agent_id'])
            print(f"Agent '{new_agent_data['agent_name']}' created with ID: {test_agent_id}")
        else:
            # If agent already exists, fetch it
            user_agents = await temp_agent_manager.get_user_agents(dummy_user_id)
            if user_agents:
                test_agent_id = str(user_agents[0]['agent_id'])
                print(f"Agent already exists for user. Using existing agent ID: {test_agent_id}")
            else:
                print("Failed to create agent and no existing agents found. Exiting.")
                return # Cannot proceed without an agent

    except Exception as e:
        print(f"Error during agent creation setup: {e}")
        return
    finally:
        await temp_db_pool.close() # Close temporary pool

    # --- Agent Interaction Loop ---
    print("\n--- Agent Interaction ---")
    print("MCP_LLM Orchestrator ready. Type your automation request for the agent.")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break

        response = await orchestrator.process_user_input(dummy_user_id, test_agent_id, user_input)
        
        print(f"AI ({response['status']}): {response['message']}")

        if response["status"] == "review_needed":
            confirm = input("Confirm? (yes/no): ")
            if confirm.lower() == "yes":
                print("Workflow confirmed! Sending to Automation Engine...")
                # Here, you would pass response["workflow_json"] to your Automation_Engine
                orchestrator.current_workflow_draft = {}
                orchestrator.chat_history = [] # Start fresh for next workflow
                print("Automation Engine would now execute this workflow.")
            else:
                print("Workflow not confirmed. Let's try again from scratch for this workflow.")
                orchestrator.current_workflow_draft = {}
                orchestrator.chat_history = [] # Start fresh for next workflow

        elif response["status"] == "info_needed":
            pass # Wait for next user input

        elif response["status"] == "conversational":
            pass

        # Trigger memory updates in the background after each significant turn
        # This should be more sophisticated, perhaps only on certain types of user input
        # or after a workflow is successfully drafted.
        await orchestrator.update_memory_context(dummy_user_id, test_agent_id, user_input)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv() # Load .env.local variables

    asyncio.run(main())