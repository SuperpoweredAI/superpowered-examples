# Superpowered AI Examples

This repo contains a collection of examples for working with and building LLM applications with Superpowered AI.

To run these examples, you'll need a Superpowered AI account ([create a free account here](https://superpowered.ai)) and API keys. Some examples also require an OpenAI account and API key.

Most of these examples use the Superpowered Python SDK, which can be installed with pip using `pip install superpowered-sdk`

## Simple scripts/notebooks
#### [Domain-specific ChatGPT](domain-specific-ChatGPT)
This example shows how to build a domain-specific chatbot using the Superpowered AI API and the OpenAI (i.e. ChatGPT) API.

#### [Chatbot with long-term memory](chatbot_with_long_term_memory.py)
This example shows how to add long-term memory to a chatbot, using Superpowered AI as the long-term memory store.

#### [Copywriting assistant](copywriting_assistant.ipynb)
This example shows how to use a Superpowered Knowledge Base to add context to the prompt for a simple copywriting assistant that can write short blog posts.

#### [Webpage question answering](webpage_qa.ipynb)
This example shows how to use the Query Passages endpoint to do question answering over a webpage.

## Larger projects
#### [Knowledge base agent](knowledge-base-agent)
This project shows how to build a conversational agent that can use Superpowered Knowledge Bases as tools.

#### [Personal knowledge base Chrome extension](personal-kb-chrome-extension)
In this project we build a Chrome extension that runs in the background and uploads the text from every webpage you visit to a Superpowered Knowledge Base (that is private to you). You can then query that Knowledge Base through the Playground or a downstream application and it will have context around every webpage you've visited. This is basically a simple version of [Rewind](https://rewind.ai).

#### [Webpage question answering Chrome extension](web-page-qa-chrome-extension)
This project uses the same basic idea as the Webpage question answering example notebook, but packages it into a Chrome extension.
