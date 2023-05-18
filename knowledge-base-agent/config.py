"""
You'll need to set the following environment variables:
- OPENAI_API_KEY
- SUPERPOWERED_API_KEY_ID
- SUPERPOWERED_API_KEY_SECRET
"""

# add at least one KB ID here - this is what the agent will have access to
knowledge_base_ids = []

# long-term memory
has_long_term_memory = True
long_term_memory_store_id = "" # ID of the knowledge base to store the chat messages

# parameters
human_prefix = "Zach" # name of the human user
ai_name = "Samantha" # name of the AI agent - can be whatever you want
pickle_chat_history = False # if True, chat history will be saved to a pickle file and loaded from the pickle file on subsequent runs
verbose = False

model_spec = {
    "ai_name": ai_name,
    "llm_provider": "openai",
    "llm_model_name": "gpt-3.5-turbo", # "gpt-3.5-turbo" and "gpt-4" are the only supported models right now
    "system_message": "You are a good chatbot.", # message to send to the AI agent at the beginning of each conversation
    "temperature": "dynamic",
    "max_tokens": 1000, # max tokens per response
    "tool_names": ["Knowledge Bases"], # "Knowledge Bases"
    "max_iterations": 1, # max number of times the agent can take an action (search a Knowledge Base) in a single turn
}