import os
import pickle
import copy
from superpowered import query_knowledge_bases

from utils import make_query_self_contained, update_chat_history, create_chat_string_from_list, set_abilities
from agent import KnowledgeBaseAgent
from long_term_memory import retrieve_from_long_term_memory, save_to_long_term_memory
from config import model_spec, knowledge_base_ids, has_long_term_memory, human_prefix, ai_name, pickle_chat_history, verbose

# see if we're using a knowledge base
if len(knowledge_base_ids) > 0:
    has_knowledge_base = True
else:
    has_knowledge_base = False

# Load data from Pickle files if needed
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

    # add context from recent chat history to the human input - helps with retrieval
    expanded_input = make_query_self_contained(chat_history_list, human_input)
    if verbose: print(f"\nExpanded input: {expanded_input}\n")

    # dynamic prompt construction - ask the model what abilities it needs to best respond to the user
    try:
        dpc_params = set_abilities(input=expanded_input)
        if verbose: print (f"set_abilities: {dpc_params}")
    except Exception as e:
        dpc_params = {
            'need_relevant_knowledge': True,
            'need_long_term_memory': True,
            'temperature': 0.0,
            'tool_list': 'all',
        }
        if verbose: print(f"Error in set_abilities: {e}")

    # create a copy of model_spec to modify - this will reset each iteration
    modified_model_spec = copy.deepcopy(model_spec)

    # check for dynamic temperature and set it accordingly
    if modified_model_spec['temperature'] == 'dynamic':
        modified_model_spec['temperature'] = dpc_params['temperature']
        if verbose: print (f"Setting temperature to {dpc_params['temperature']}")

    # check for tools needed and set them accordingly
    if dpc_params['tool_list'] != 'all':
        if "Knowledge Bases" in modified_model_spec['tool_names'] and "Knowledge Bases" not in dpc_params['tool_list']:
            modified_model_spec['tool_names'].remove("Knowledge Bases")
    
    # get relevant knowledge from Superpowered AI Knowledge Bases
    if has_knowledge_base and dpc_params['need_relevant_knowledge']:
        results = query_knowledge_bases(query=expanded_input, knowledge_base_ids=knowledge_base_ids, summarize_results=False)
        relevant_knowledge = "\n\n".join([result["content"] for result in results["ranked_results"]])
    else:
        relevant_knowledge = ""

    if has_long_term_memory and dpc_params['need_long_term_memory']:
        long_term_memory = retrieve_from_long_term_memory(expanded_input)
    else:
        long_term_memory = ""

    # get agent response  
    agent = KnowledgeBaseAgent(modified_model_spec, api_key=os.environ['OPENAI_API_KEY'])
    ai_output, agent_action_log = agent.run(
        input=human_input, 
        chat_history_list=chat_history_list, 
        relevant_knowledge=relevant_knowledge, 
        long_term_memory=long_term_memory, 
        verbose=verbose,
    )

    # print agent response
    print(f"\n{ai_name}: {ai_output}\n")

    # update chat history with agent response
    ai_output_dict = {"prefix": ai_name, "content": ai_output}
    chat_history_list = update_chat_history(chat_history_list, human_input, ai_output_dict)

    # save chat history to a Pickle file so we can pick up where we left off next time
    if pickle_chat_history:
        pickle.dump(chat_history_list, open("chat_history.pkl", "wb"))