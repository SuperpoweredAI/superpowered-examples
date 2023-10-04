# Knowledge Base Agent
A conversational agent that can use knowledge bases as tools

### How to use
1. Set environmental variables for `SUPERPOWERED_API_KEY_ID`, `SUPERPOWERED_API_KEY_SECRET`, and `OPENAI_API_KEY`
2. Add your Knowledge Base IDs to config.py. You'll need at least one KB for the agent to query, but you can include multiple ones if you want. These IDs go in `knowledge_base_ids`. You'll also need a KB to use as the long-term memory store, which will go in `long_term_memory_store_id`. You can just create an empty KB called "Chatbot memory" or something along those lines. There are also some other parameters you can play around with here.
3. Run main.py. This will start the main chat loop.
