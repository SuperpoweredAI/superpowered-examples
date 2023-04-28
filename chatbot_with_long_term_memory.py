from superpowered import create_knowledge_base, add_document_to_kb, query
import openai
import os

# set API keys
#os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
#os.environ["SUPERPOWERED_API_KEY_ID"] = "YOUR_API_KEY_ID"
#os.environ["SUPERPOWERED_API_KEY_SECRET"] = "YOUR_API_KEY_SECRET"

# create a knowledge base to store the messages
create_knowledge_base(title="Chatbot memory")

# create the prompt template for the LLM call
prompt_template = """
Here are some messages from your conversation history, in no particular order, that you may find relevant to the current conversation:
{long_term_memory}

Current message:
{user_input}
""".strip()

def get_long_term_memory(user_input: str, num_messages=5):
    results = query(kb_titles=["Chatbot memory"], query=user_input, reranker_top_k=num_messages)
    long_term_memory_str = "\n".join([f"{result['content']}" for result in results["ranked_results"]])
    return long_term_memory_str

chat_messages = []

# start the chat loop
while True:
    user_input = input("You: ")
    if user_input == "exit":
        break

    # get relevant messages from long term memory
    long_term_memory = get_long_term_memory(user_input, num_messages=5)

    # generate the response
    prompt = prompt_template.format(long_term_memory=long_term_memory, user_input=user_input)
    openai.api_key = os.getenv("OPENAI_API_KEY")
    user_input_message = {"role": "user", "content": prompt}
    messages = chat_messages + [user_input_message]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=500,
        temperature=0.9,
        request_timeout=120,
    )
    llm_output = response['choices'][0]['message']['content'].strip()

    # print the response
    print("Chatbot:", llm_output)

    # store the user input and response in a list of messages
    chat_messages.append({"role": "user", "content": user_input})
    chat_messages.append({"role": "assistant", "content": llm_output})

    # check if we need to move any messages from the chat_messages list to long term memory
    while len(chat_messages) > 20:
        # move the oldest message from chat_messages to long term memory
        oldest_message = chat_messages.pop(0)
        message_prefix = oldest_message["role"]
        add_document_to_kb(kb_title="Chatbot memory", content=message_prefix + " " + oldest_message["content"])