from config import ai_name

# MaDPCA - Modular and Dynamic Prompt Construction Architecture

ACTIONS = """OPTIONAL ACTIONS
In addition to directly responding to questions and prompts, you can also choose to perform any of the following actions:

{tool_descriptions}

If you want to take an action, you MUST use the following (Action, Input) format. You MUST include both parts of the format, and you MUST use the exact words and formatting shown below. Do not include any additional text in your response:

Action: [your action, which must be one of these: {tool_names}]
Input: [your input to the action, which must be formatted correctly]

For example, if you wanted to use the Search tool to look up 2022 Super Bowl results, you would respond with:
```
Action: Search
Input: 2022 Super Bowl game score
```

That's it! You just need to give the Action and Input. DO NOT try to answer the question after writing your Action and Input. The answer will be automatically added to the response later.

If you don't want to take an action, you can just respond to the prompt directly, without using the (Action, Input) format. Only take an action if you feel it is necessary."""

FULL_PROMPT_LAYOUT = """

{relevant_knowledge}

{long_term_memory}

{chat_history}

{actions}

{prompt}

{agent_actions}

{response}"""

def get_relevant_knowledge(has_knowledge_base) -> str:
    if has_knowledge_base:
        return "RELEVANT KNOWLEDGE\n{relevant_knowledge}"
    else:
        return ""

def get_long_term_memory(has_long_term_memory) -> str:
    if has_long_term_memory:
        ltm_string = f"LONG TERM MEMORY\nHere are some messages from past conversations with the same user that you may or may not find relevant to the present conversation. The '{ai_name}' prefix indicates a message you sent. Note that the '{ai_name}' prefix was added after the fact, and you don't actually include it in your messages."
        return ltm_string + "\n\n{long_term_memory}"
    else:
        return ""

def get_chat_history(has_short_term_memory) -> str:
    if has_short_term_memory:
        return "CONVERSATION HISTORY - remember, you are {ai_name}\n{chat_history}"
    else:
        return ""

def get_actions(tool_use_allowed) -> str:
    if tool_use_allowed:
        return ACTIONS
    else:
        return ""

def get_prompt() -> str:
    return "PROMPT\n{input}"

def agent_action_log_to_str(agent_action_log, tool_use_allowed):
    """
    Convert agent action log to a string so we can put it into the prompt
    """
    # if there are no actions, return an empty string
    if len(agent_action_log) == 0:
        return ""
    
    # the beginning and ending of the string depends on whether the agent is allowed to use tools this time around
    if tool_use_allowed:
        first_part = "Here are the actions you've taken so far, along with their outputs:\n"
        last_part = "You can take another action if you need to, but before doing so you should look very closely to see if the answer to the user's prompt is in the output of any of these actions you've already taken. If so, you should respond to the user with the answer. You should not repeat the same Action and Input more than once."
    else:
        first_part = "You were previously given access to a variety of tools and actions:\n"
        last_part = "Now it's time to respond to the user. First, consider the output from the action(s) you took, and decide if that output is useful or not. If the output is useful, then use it to inform your response to the user. If the output is an error message, if it's empty, or if it is otherwise not useful, then ignore it when constructing your response."
    
    # loop through the actions and add them to a string
    action_output = ""
    is_first_action = True
    for action, action_input, output in agent_action_log:
        if is_first_action:
            intro_word = "First"
            is_first_action = False
        else:
            intro_word = "Then"
        action_output += f"{intro_word}, you chose to use: {action}. Your input to {action} was {action_input}, which resulted in an output of {output}.\n\n"

    return f"ACTION OUTPUT\n{first_part}{action_output}{last_part}"

def get_response_str() -> str:
    return "RESPONSE"

def get_full_prompt(tool_use_allowed, has_knowledge_base, has_short_term_memory, has_long_term_memory, agent_action_log) -> str:
    FULL_PROMPT = FULL_PROMPT_LAYOUT.format(
        relevant_knowledge=get_relevant_knowledge(has_knowledge_base),
        long_term_memory=get_long_term_memory(has_long_term_memory),
        chat_history=get_chat_history(has_short_term_memory),
        actions=get_actions(tool_use_allowed),
        prompt=get_prompt(),
        agent_actions=agent_action_log_to_str(agent_action_log, tool_use_allowed),
        response=get_response_str(),
    )

    # remove extra new lines
    while FULL_PROMPT.find('\n\n\n') != -1:
        FULL_PROMPT = FULL_PROMPT.replace('\n\n\n', '\n\n')

    return FULL_PROMPT

# for use with GPT-3.5-Turbo - this is what goes into the system message
def get_system_message(system_message_content: str) -> dict:
    system_message = {"role": "system", "content": system_message_content}
    return system_message

# for use with GPT-3.5-Turbo - this is what goes into the most recent user message
def get_user_content(tool_use_allowed, has_knowledge_base, has_long_term_memory, agent_action_log) -> str:
    USER_CONTENT = FULL_PROMPT_LAYOUT.format(
        relevant_knowledge=get_relevant_knowledge(has_knowledge_base),
        long_term_memory=get_long_term_memory(has_long_term_memory),
        chat_history="",
        actions=get_actions(tool_use_allowed),
        prompt=get_prompt(),
        agent_actions=agent_action_log_to_str(agent_action_log, tool_use_allowed),
        response="",
    )

    # remove extra new lines
    USER_CONTENT = USER_CONTENT.strip()
    while USER_CONTENT.find('\n\n\n') != -1:
        USER_CONTENT = USER_CONTENT.replace('\n\n\n', '\n\n')

    return USER_CONTENT

def chat_history_to_messages(chat_history: list[dict], ai_name: str):
    """
    Convert chat history to a list of messages in the format that GPT-3.5-Turbo expects
    """
    messages = []
    for chat_message in chat_history:
        message = {}
        if chat_message["prefix"] == ai_name:
            message["role"] = "assistant"
        else:
            message["role"] = "user"
        message["content"] = chat_message["content"]
        messages.append(message)
    return messages