import datetime
import openai
import os
from utils import create_chat_string_from_list
from tools import get_tools
from prompt import get_full_prompt, get_user_content, get_system_message, chat_history_to_messages

def extract_action_input(llm_output, ai_name):
    """
    This is designed to be a robust way to extract the action and input from the LLM output using string splitting
    """
    # extract the action and input
    if "Action:" in llm_output and "Input:" in llm_output:
        action_list = llm_output.split("Action:")
        # make sure that "Action:" only appears once and that "Input:" appears after "Action:"
        if len(action_list) == 2 and "Input:" in action_list[1]:
            action = action_list[1].split("Input:")[0].strip()
            input_list = action_list[1].split("Input:")
            # make sure that "Input:" only appears once
            if len(input_list) == 2:
                input = input_list[1].strip()
            else:
                raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        else:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")   
    else:
        raise ValueError(f"Could not parse LLM output: `{llm_output}`")

    return action, input

def use_a_tool(action, action_input, list_of_tools):
    # Construct a mapping of tool name to tool for easy lookup
    name_to_tool_map = {tool.name: tool for tool in list_of_tools} 
    
    # Look up the tool and if it exists, call it
    if action in name_to_tool_map:
        tool = name_to_tool_map[action]
        try:
            # We then call the tool on the tool input to get an observation
            tool_output = tool.func(action_input)
            success = True
        except Exception as e:
            tool_output = f"Error using tool: {e}"
            success = False
    else:
        tool_output = "Error, " + f"{action} is not a valid tool."
        success = False
    return tool_output, success

def make_llm_call(llm_provider: str, model_name: str, temperature: float, max_tokens: int, tool_use_allowed: bool, system_message_content: str, input_str: str, chat_history_str: str, relevant_knowledge: str, long_term_memory: str, tool_names: str = "", tool_descriptions: str = "", agent_action_log=[], ai_name="AI", verbose=False, openai_api_key=None, chat_history_list=[]):
    # fix types
    temperature = float(temperature)
    max_tokens = int(max_tokens)
    
    has_knowledge_base = len(relevant_knowledge) > 0
    has_short_term_memory = len(chat_history_str) > 0
    has_long_term_memory = len(long_term_memory) > 0

    if model_name == "gpt-3.5-turbo" or model_name == "gpt-4":
        template = get_user_content(tool_use_allowed, has_knowledge_base, has_long_term_memory, agent_action_log)
        chat_history_messages = chat_history_to_messages(chat_history_list, ai_name)
    else:
        template = get_full_prompt(tool_use_allowed, has_knowledge_base, has_short_term_memory, has_long_term_memory, agent_action_log)
    
    # format the prompt template in order to create the final prompt
    prompt = template.format(
        relevant_knowledge=relevant_knowledge,
        long_term_memory=long_term_memory,
        chat_history=chat_history_str,
        tool_descriptions=tool_descriptions,
        tool_names=tool_names,
        input=input_str,
        ai_name=ai_name,
    )

    if verbose:
        print("\n" + prompt)
    
    # make the LLM call
    if llm_provider == "openai":
        if model_name == "gpt-3.5-turbo" or model_name == "gpt-4":
            openai.api_key = os.getenv("OPENAI_API_KEY")
            user_input_message = {"role": "user", "content": prompt}
            messages = [get_system_message(system_message_content)] + chat_history_messages + [user_input_message]
            if verbose: print (f"{model_name}\n\n{messages}\n\n{max_tokens}\n\n{temperature}")
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
    else:
        raise ValueError(f"LLM provider {llm_provider} is not supported.")

    # strip ai_name from beginning of llm_output if it's there
    while llm_output.startswith(ai_name+":"):
        llm_output = llm_output[(len(ai_name)+1):]

    return llm_output.strip(), prompt


class KnowledgeBaseAgent():
    def __init__(self, model_spec: dict, api_key: str):
        self.api_key = api_key
        self.ai_name = model_spec['ai_name'] # this is the prefix that the AI uses to identify itself in the chat
        self.system_message = model_spec['system_message']
        self.llm_provider = model_spec['llm_provider']
        self.model_name = model_spec['llm_model_name']
        self.temperature = model_spec['temperature']
        self.max_tokens = model_spec['max_tokens']
        self.max_iterations = model_spec['max_iterations'] # this is the maximum number of times the agent can take an action in a single turn

        # check if this model uses tools
        if model_spec.get('tool_names'):
            self.tool_names = model_spec['tool_names']
            self.is_agent = True
            self.list_of_tools = get_tools(self.tool_names) # call a function to get the Tool objects from the list of tool names
        else:   
            self.tool_names = []
            self.is_agent = False

        # add information about the current date and time
        self.system_message += f'\n\nYou were trained with data up to September 29, 2021 but it is currently {datetime.datetime.utcnow().isoformat()} UTC.'

    def run(self, input: list[dict], chat_history_list=[], relevant_knowledge="", long_term_memory="", verbose=False):       
        chat_history_str = create_chat_string_from_list(chat_history_list)
        input_str = create_chat_string_from_list(input).strip()

        # If this is not an agent, then we just call the LLM and return the output
        if self.is_agent == False:
            tool_use_allowed = False           
            ai_output, prompt = make_llm_call(self.llm_provider, self.model_name, self.temperature, self.max_tokens, tool_use_allowed, self.system_message, input_str, chat_history_str, relevant_knowledge, long_term_memory, ai_name=self.ai_name, verbose=verbose, openai_api_key=self.api_key, chat_history_list=chat_history_list)
            return ai_output, None

        # We now enter the agent loop - the agent can use multiple tools in a row before returning to the user
        agent_action_log = []
        iterations = 0
        have_response_to_user = False
        while iterations < self.max_iterations:
            # Call the agent LLM to see what to do
            tool_use_allowed = True
            tool_names = ", ".join([tool.name for tool in self.list_of_tools])
            tool_descriptions = "\n\n".join([tool.name + ": " + tool.description for tool in self.list_of_tools])
            agent_llm_output, prompt = make_llm_call(self.llm_provider, self.model_name, self.temperature, self.max_tokens, tool_use_allowed, self.system_message, input_str, chat_history_str, relevant_knowledge, long_term_memory, tool_names=tool_names, tool_descriptions=tool_descriptions, agent_action_log=agent_action_log, ai_name=self.ai_name, verbose=verbose, openai_api_key=self.api_key, chat_history_list=chat_history_list)
            if verbose: 
                print ("\n" + "RAW LLM OUTPUT:\n" + agent_llm_output + "\nEND OF RAW LLM OUTPUT" + "\n")

            # See if the agent chose an action, by trying to extract an action and input from the LLM output
            try:
                action, action_input = extract_action_input(agent_llm_output, ai_name=self.ai_name)
                if verbose:
                    print("\nExtracted action and input:")
                    print ("Action:", action)
                    print ("Input:", action_input)
            except:
                # If the agent did not choose an action, then its response is the complete LLM output, so we break from the agent loop
                ai_output = agent_llm_output
                have_response_to_user = True            
                break

            # If we get to this point then the agent chose an action, so we call the appropriate tool function
            tool_output, success = use_a_tool(action, action_input, self.list_of_tools)
            agent_action_log.append((action, action_input, tool_output))
            if verbose: 
                print(f"\nOutput: {tool_output}")
            if not success:
                break # no more tool use following a tool use failure
            
            iterations += 1

        # generate response to user if we have not already done so - do not allow the use of tools
        if not have_response_to_user:
            tool_use_allowed = False
            ai_output, prompt = make_llm_call(self.llm_provider, self.model_name, self.temperature, self.max_tokens, tool_use_allowed, self.system_message, input_str, chat_history_str, relevant_knowledge, long_term_memory, tool_names=[], tool_descriptions=[], agent_action_log=agent_action_log, ai_name=self.ai_name, verbose=verbose, openai_api_key=self.api_key, chat_history_list=chat_history_list)

        return ai_output, agent_action_log