from superpowered import create_knowledge_base, get_knowledge_base

knowledge_base_names = ["Investment Advisers Act of 1940"]
long_term_memory_store_name = "Chatbot memory"
has_long_term_memory = True
human_prefix = "Zach"
ai_name = "Samantha"
mqsc = True # make query self contained

# create a knowledge base to store the messages if it doesn't already exist
def initialize_long_term_memory():
    try:
        get_knowledge_base(long_term_memory_store_name)
    except:
        create_knowledge_base(title=long_term_memory_store_name)