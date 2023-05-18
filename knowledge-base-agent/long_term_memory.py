from superpowered import query_knowledge_bases, create_document_via_text
from config import long_term_memory_store_id

def save_to_long_term_memory(formatted_message):
    try:
        create_document_via_text(knowledge_base_id=long_term_memory_store_id, content=formatted_message)
    except:
        pass

def retrieve_from_long_term_memory(user_input):
    results = query_knowledge_bases(query=user_input, knowledge_base_ids=[long_term_memory_store_id], summarize_results=False)
    return "\n\n".join([result["content"] for result in results["ranked_results"]])