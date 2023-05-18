import openai
import os
from utils_prompts import MQSC_PROMPT, REQUIRED_ABILITIES_PROMPT
from long_term_memory import save_to_long_term_memory

def openai_api_call(prompt: str, model_name: str, temperature: float, max_tokens: int) -> str:
    if model_name == "gpt-3.5-turbo" or model_name == "gpt-4":
        openai.api_key = os.getenv("OPENAI_API_KEY")
        user_input_message = {"role": "user", "content": prompt}
        messages = [user_input_message]
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        llm_output = response['choices'][0]['message']['content'].strip()
    else:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.Completion.create(
            model=model_name,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        llm_output = response['choices'][0]['text'].strip()
    return llm_output

def possible_abilities():
    # NOTE: do not change the numbers of these abilities, as the handling of them is hardcoded in set_abilities()
    possible_abilities = {
        1: "Knowledge bases - the ability to retrieve information from domain-specific or company-specific knowledge bases",
        2: "Memory - the ability to remember previous conversations with the user; this is the ONLY way to remember anything the user has previously said, so you most likely need this ability",
        3: "Creative writing ability - the ability to write creatively, such as for essays, poetry, comedy, screenwriting, etc.",
        4: "Casual conversation ability - the ability to have a casual conversation",
    }
    possible_abilities_str = "\n".join([f"{k}: {v}" for k, v in possible_abilities.items()])
    return possible_abilities_str


def get_required_abilities(input: str, verbose: bool = False):
    """
    - ideally input is an expanded human input, but the non-expanded version will work too
    """
    prompt = REQUIRED_ABILITIES_PROMPT.format(input=input, possible_abilities=possible_abilities())
    llm_output = openai_api_call(prompt, model_name="gpt-3.5-turbo", temperature=0.0, max_tokens=50)

    # if verbose, print the raw llm output
    if verbose:
        print (f"PROMPT: {prompt}\n")
        print(f"LLM OUTPUT: {llm_output}")

    return llm_output

def set_abilities(input: str, verbose: bool = False):
    """
    - ideally input is an expanded human input, but the non-expanded version will work too
    """

    abilities_str = get_required_abilities(input, verbose=verbose)

    if verbose:
        print(f"LLM OUTPUT: {abilities_str}")

    # TODO: validate that the abilities are valid

    # extract the abilities from the llm output
    abilities = [int(a) for a in abilities_str.split(",")]

    # information retrieval
    if 1 in abilities:
        need_relevant_knowledge = True
    else:
        need_relevant_knowledge = False

    # long-term memory
    if 2 in abilities:
        need_long_term_memory = True
    else:
        need_long_term_memory = False

    # creative writing ability
    if 3 in abilities:
        need_creative_writing_ability = True
    else:
        need_creative_writing_ability = False

    # casual conversation ability
    if 4 in abilities:
        need_casual_conversation_ability = True
    else:
        need_casual_conversation_ability = False

    # set temperature based on the abilities needed
    temperature = 0.2 # default
    if need_creative_writing_ability:
        temperature = 0.9
    elif need_casual_conversation_ability:
        temperature = 0.8

    # set the tool list based on the abilities needed - will still need to check what tools are available based on the model spec
    tool_list = [] # default
    if need_relevant_knowledge:
        tool_list.append("Knowledge Bases")

    # if there are tools required, but the temperature is too high to reliably use them, set the temperature to 0.4
    if tool_list != [] and temperature > 0.4:
        temperature = 0.4

    abilities_dict = {
        "need_relevant_knowledge": need_relevant_knowledge,
        "need_long_term_memory": need_long_term_memory,
        "temperature": temperature,
        "tool_list": tool_list,
    }

    return abilities_dict

def create_chat_string_from_list(chat_list: list) -> str:
    if chat_list == []:
        chat_str = ""
    elif chat_list[0]["prefix"] == "":
        chat_str = '\n\n'.join([f'{m["content"]}' for m in chat_list]) # if there is no prefix, don't include it
    else:
        chat_str = '\n\n'.join([f'{m["prefix"]}: {m["content"]}' for m in chat_list])
    return chat_str

def update_chat_history(chat_history: list, input: list, model_response: dict, max_characters: int = 6000) -> list:
    """
    Update the chat history list based on the most recent user input and model response
    """
    # add the user input to the chat history
    chat_history.extend(input)

    # add the model response to the chat history
    assert type(model_response) == dict and set(model_response.keys()) == set(["prefix", "content"])
    chat_history.append(model_response)

    # Limit the chat history to the last max_characters characters
    # To do this, we remove the oldest messages until the chat history is less than max_characters characters
    chat_history_str = create_chat_string_from_list(chat_history)
    while len(chat_history_str) > max_characters:
        # move the oldest message to long term memory
        oldest_message = chat_history.pop(0)
        message_prefix = oldest_message["prefix"]
        formatted_message = message_prefix + ": " + oldest_message["content"]
        save_to_long_term_memory(formatted_message)
        
        chat_history_str = create_chat_string_from_list(chat_history)

    return chat_history

def make_query_self_contained(chat_history_list: list, input_list: list, verbose: bool = False):
    """
    Function to restate the user input in a way that is self-contained - will be used for embeddings search among other things
    - chat_history_list is the most recent chat history
    - input_list is the user input
    """
    input = create_chat_string_from_list(input_list)

    # If the user input is empty, None, etc., return the human input (as a string)
    if not chat_history_list:
        return input

    chat_history = create_chat_string_from_list(chat_history_list)

    # If the user input is too long, don't restate it, because it'll be expensive and probably unnecessary
    if len(input) > 600:
        return input

    # Limit the chat history to the last 1000 characters (~250 tokens)
    if len(chat_history) > 1000:
        chat_history = chat_history[-1000:]

    # call the LLM
    prompt = MQSC_PROMPT.format(chat_history=chat_history, input=input)
    if verbose:
        print(prompt)
    llm_output = openai_api_call(prompt, model_name="gpt-3.5-turbo", temperature=0.0, max_tokens=300)
    
    # handle the possibility that the LLM returns an empty string
    if not llm_output:
        return input
    else:
        return llm_output