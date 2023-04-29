from superpowered import get_knowledge_base, create_knowledge_base, add_document_to_kb, query
import openai
import os

# set API keys
os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
os.environ["SUPERPOWERED_API_KEY_ID"] = "YOUR_API_KEY_ID"
os.environ["SUPERPOWERED_API_KEY_SECRET"] = "YOUR_API_KEY_SECRET"

# create a knowledge base to store the messages if it doesn't already exist
try:
    get_knowledge_base("Chatbot memory")
except:
    create_knowledge_base(title="Chatbot memory")

# create the prompt template for the LLM call
prompt_template = """
{long_term_memory}

{chat_history}

user: {user_input}

assistant:
""".strip()

def get_long_term_memory(user_input: str, num_messages=5):
    results = query(kb_titles=["Chatbot memory"], query=user_input, reranker_top_k=num_messages)
    long_term_memory_str = "Here are some messages from your conversation history, in no particular order, that you may find relevant to the current conversation:\n\n" + "\n\n".join([f"{result['content']}" for result in results["ranked_results"]])
    return long_term_memory_str

def chat_messages_to_str(chat_messages):
    chat_history = ""
    for message in chat_messages:
        chat_history += f"{message['role']}: {message['content']}\n"
    if chat_history != "":
        chat_history = "Here is your conversation history:\n\n" + chat_history
    return chat_history

chat_messages = []
messages_in_long_term_memory = 0

# start the chat loop
while True:
    user_input = input("You: ")
    if user_input == "exit":
        break

    # get relevant messages from long term memory
    if messages_in_long_term_memory > 0:
        long_term_memory = get_long_term_memory(user_input, num_messages=5)
    else:
        long_term_memory = ""

    # generate the response
    prompt = prompt_template.format(long_term_memory=long_term_memory, chat_history=chat_messages_to_str(chat_messages), user_input=user_input)

    openai.api_key = os.getenv("OPENAI_API_KEY")
    system_message = {"role": "system", "content": "You are a friendly chatbot"}
    user_input_message = {"role": "user", "content": prompt}
    messages = [system_message, user_input_message]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=500,
        temperature=0.7,
        request_timeout=120,
    )
    llm_output = response['choices'][0]['message']['content'].strip()

    # print the response
    print("Chatbot:", llm_output)

    # store the user input and response in a list of messages
    chat_messages.append({"role": "user", "content": user_input})
    chat_messages.append({"role": "assistant", "content": llm_output})

    # check if we need to move any messages from the chat_messages list to long term memory
    while len(chat_messages) > 0:
        # move the oldest message from chat_messages to long term memory
        oldest_message = chat_messages.pop(0)
        message_prefix = oldest_message["role"]
        formatted_message = message_prefix + ": " + oldest_message["content"]
        add_document_to_kb(kb_title="Chatbot memory", content=formatted_message, title=f"chat_{messages_in_long_term_memory}")
        messages_in_long_term_memory += 1