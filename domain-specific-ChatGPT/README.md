# Domain-specific ChatGPT

This example shows how to build a domain-specific chatbot using the Superpowered AI API and the OpenAI (i.e. ChatGPT) API. You'll need a Superpowered AI API key and secret, and an OpenAI API key to run this example.

There are only two files:
1. create_knowledge_base.py: This script creates a Superpowered AI Knowledge Base and uploads domain-specific text to it. For this example, we use the Superpowered documentation, but you should change this to whatever you need for your application. You could also create your Knowledge Base and upload documents to it with our UI instead.
2. chat.py: This script runs a simple chat loop using the ChatGPT API. Relevant knowledge from your Knowledge Base is automatically inserted into the prompt with each message. Make sure you set your Knowledge Base ID in this script before running it.
