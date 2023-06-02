from superpowered import query_knowledge_bases
import openai
import os

"""
# set API keys here (and uncomment this block), or export them in your shell
os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
os.environ["SUPERPOWERED_API_KEY_ID"] = "YOUR_API_KEY_ID"
os.environ["SUPERPOWERED_API_KEY_SECRET"] = "YOUR_API_KEY_SECRET"
"""

# set the knowledge base id here
knowledge_base_id = "YOUR_KNOWLEDGE_BASE_ID"

# create the prompt template for the LLM call
prompt_template = """
{relevant_knowledge}

{chat_history}

user: {user_input}

assistant:
""".strip()

# set the system message to tell the chatbot how to behave -  you should customize this to your domain
SYSTEM_MESSAGE = "You are a highly intelligent chatbot that can answer questions about Superpowered AI. You MUST only answer questions about Superpowered AI and should refuse to answer questions about other topics."

# This function calls the Superpowered API to get relevant knowledge from the knowledge base
def get_relevant_knowledge(user_input: str):
    results = query_knowledge_bases(knowledge_base_ids=[knowledge_base_id], query=user_input, top_k=10, summarize_results=False)
    relevant_knowledge_str = "Here are some text chunks that you may find relevant to the current conversation:\n\n" + "\n\n".join([f"{result['content']}" for result in results["ranked_results"]])
    return relevant_knowledge_str

# This function converts the chat messages to a string for the LLM prompt
def chat_messages_to_str(chat_messages):
    chat_history = ""
    for message in chat_messages:
        chat_history += f"{message['role']}: {message['content']}\n"
    if chat_history != "":
        chat_history = "Here is your conversation history:\n\n" + chat_history
    return chat_history

# start the chat loop - type "exit" to end the chat
chat_messages = []
while True:
    user_input = input("User: ")
    if user_input == "exit":
        break

    # get relevant knowledge from the knowledge base
    relevant_knowledge = get_relevant_knowledge(user_input)

    # generate the response
    prompt = prompt_template.format(relevant_knowledge=relevant_knowledge, chat_history=chat_messages_to_str(chat_messages), user_input=user_input)

    openai.api_key = os.getenv("OPENAI_API_KEY")
    system_message = {"role": "system", "content": SYSTEM_MESSAGE}
    user_input_message = {"role": "user", "content": prompt}
    messages = [system_message, user_input_message]

    # call the LLM - using the "gpt-3.5-turbo" model here, but you could swap this to "gpt-4" for higher quality (but much slower and more expensive) responses
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=500,
        temperature=0.3,
        request_timeout=120,
    )
    llm_output = response['choices'][0]['message']['content'].strip()

    # print the response
    print("Chatbot:", llm_output)

    # store the user input and response in a list of messages
    chat_messages.append({"role": "user", "content": user_input})
    chat_messages.append({"role": "assistant", "content": llm_output})