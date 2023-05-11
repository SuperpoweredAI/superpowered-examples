from superpowered import query, add_document_to_kb
from config import long_term_memory_store_name

def save_to_long_term_memory(formatted_message):
    add_document_to_kb(kb_title=long_term_memory_store_name, content=formatted_message)

def retrieve_from_long_term_memory(user_input):
    results = query(query=user_input, kb_titles=[long_term_memory_store_name], extract_and_summarize=False)
    return "\n\n".join([result["content"] for result in results["ranked_results"]])