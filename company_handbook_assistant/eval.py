from superpowered import create_chat_thread, get_chat_response
import json

queries = [
    "What is Sourcegraph's mission?",
    "What is Cody?",
    "I'm a new employee. What should I do on my first day?",
    "How does the batch changes feature work?",
    "What are the legal team's FY'23 goals?",
    "How do product management and product marketing work together for new product launches?",
    "What are some cybersecurity best practices Sourcegraph follows?",
    "Are blog posts an important part of Sourcegraph's marketing strategy?",
    "What are some of the most important things to know about Sourcegraph's culture?",
]

sourcegraph_kb_id = "cc08403e-183d-4e8f-b196-16480e94890c"

responses = []
for query in queries:
    print (f"Query: {query}\n")

    chat_thread_id = create_chat_thread(use_rse=True, segment_length="medium")
    
    chat_response = get_chat_response(thread_id=chat_thread_id, input=query, knowledge_base_ids=[sourcegraph_kb_id], include_topic_summaries=False)

    responses.append({
        'query': query,
        'chat_response': chat_response
    })

# dump to json
with open('sourcegraph_eval.json', 'w') as f:
    json.dump(responses, f, indent=4)