from superpowered import create_chat_thread, get_chat_response

"""
This example shows how to create a chat thread and get a response from the AI, using the Chat endpoint in the Superpowered API.

Be sure you install the Superpowered AI Python package first: pip install superpowered-sdk

To run this example, you need to already have a knowledge base created, which you can do in the Superpowered AI UI (https://superpowered.ai) or via API/SDK.
"""

# set parameters
kb_id = 'YOUR_KB_ID'
use_rse = True
segment_length = "medium"
system_message = "You are a friendly chatbot." # The more detailed the system message, the better. This is just a placeholder.

# create chat thread
chat_thread = create_chat_thread(knowledge_base_ids=[kb_id], use_rse=use_rse, segment_length=segment_length, system_message=system_message)
chat_thread_id = chat_thread['id']
print (f"Chat thread created with ID: {chat_thread_id}")

# start chat loop - type 'exit' to quit
while True:
    # get user message
    user_message = input("\nUser: ")
    if user_message == "exit":
        break

    # get AI response
    chat_response = get_chat_response(chat_thread_id, user_message)
    chat_response = chat_response["interaction"]["model_response"]["content"]
    print (f"\nAssistant: {chat_response}")