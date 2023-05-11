import os
import pickle
import copy
from superpowered import query

from utils import make_query_self_contained, update_chat_history, create_chat_string_from_list, set_abilities
from agent import KnowledgeBaseAgent
from long_term_memory import retrieve_from_long_term_memory, save_to_long_term_memory
from config import knowledge_base_names, has_long_term_memory, human_prefix, ai_name, mqsc, initialize_long_term_memory

"""
You'll need to set the following environment variables:
- OPENAI_API_KEY
- SUPERPOWERED_API_KEY_ID
- SUPERPOWERED_API_KEY_SECRET
"""

model_spec = {
    "ai_name": ai_name,
    "llm_provider": "openai",
    "llm_model_name": "gpt-3.5-turbo",
    "system_message": "You are a good chatbot.",
    "temperature": "dynamic",
    "max_tokens": 1000,
    "tool_names": ["Knowledge Bases"], # "Knowledge Bases"
}

pickle_chat_history = False
verbose = True

if len(knowledge_base_names) > 0:
    has_knowledge_base = True
else:
    has_knowledge_base = False

initialize_long_term_memory()

# Load data from Pickle files
if pickle_chat_history:
    chat_history_list = pickle.load(open("chat_history.pkl", "rb"))    
    if verbose: 
        print ("\n\n" + "CHAT HISTORY\n\n" + create_chat_string_from_list(chat_history_list) + "\n")
else:
    chat_history_list = []

# start the chat loop
while True:
    # get input from the user
    human_input_content = input(human_prefix + ": ")
    if human_input_content == "exit":
        # save the chat history to long term memory, but only if we haven't been pickling the chat history
        if not pickle_chat_history:
            for message in chat_history_list:
                message_prefix = message["prefix"]
                formatted_message = message_prefix + ": " + message["content"]
                save_to_long_term_memory(formatted_message)
        break

    human_input = [{"prefix": human_prefix, "content": human_input_content}] # list of messages, where a message is a dict with keys "prefix" and "content"

    # add context to the human input
    if mqsc:
        expanded_input = make_query_self_contained(chat_history_list, human_input)
        if verbose: print(f"\nExpanded input: {expanded_input}\n")
    else:
        expanded_input = human_input_content

    # dynamic prompt construction - ask the model what abilities it needs to best answer the question
    try:
        dpc_params = set_abilities(input=expanded_input)
        print (f"set_abilities: {dpc_params}")
    except Exception as e:
        dpc_params = {
            'need_relevant_knowledge': True,
            'need_long_term_memory': True,
            'temperature': 0.0,
            'tool_list': 'all',
        }
        print(f"Error in set_abilities: {e}")

    # create a copy of model_spec to modify - this will reset each iteration
    modified_model_spec = copy.deepcopy(model_spec)

    # check for dynamic temperature and set it accordingly
    if modified_model_spec['temperature'] == 'dynamic':
        modified_model_spec['temperature'] = dpc_params['temperature']
        print (f"Setting temperature to {dpc_params['temperature']}")

    # check for tools needed and set them accordingly
    if dpc_params['tool_list'] != 'all':
        if "Knowledge Bases" in modified_model_spec['tool_names'] and "Knowledge Bases" not in dpc_params['tool_list']:
            modified_model_spec['tool_names'].remove("Knowledge Bases")
    
    if has_knowledge_base and dpc_params['need_relevant_knowledge']:
        results = query(query=expanded_input, kb_titles=knowledge_base_names, extract_and_summarize=False)
        relevant_knowledge = "\n\n".join([result["content"] for result in results["ranked_results"]])
    else:
        relevant_knowledge = ""

    if has_long_term_memory and dpc_params['need_long_term_memory']:
        long_term_memory = retrieve_from_long_term_memory(expanded_input)
    else:
        long_term_memory = ""

    # get agent response  
    agent = KnowledgeBaseAgent(modified_model_spec, ai_name, api_key=os.environ['OPENAI_API_KEY'])
    ai_output, agent_action_log = agent.run(
        input=human_input, 
        chat_history_list=chat_history_list, 
        relevant_knowledge=relevant_knowledge, 
        long_term_memory=long_term_memory, 
        verbose=verbose,
    )

    print(f"\n{ai_name}: {ai_output}\n")

    # update chat history with agent response
    ai_output_dict = {"prefix": ai_name, "content": ai_output}
    chat_history_list = update_chat_history(chat_history_list, human_input, ai_output_dict)

    # save chat history to a Pickle file so we can pick up where we left off next time
    if pickle_chat_history:
        pickle.dump(chat_history_list, open("chat_history.pkl", "wb"))