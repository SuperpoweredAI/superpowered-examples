# Superpowered AI Examples

This repo contains a collection of examples for working with and building retrieval-augmented LLM applications with Superpowered AI.

To run these examples, you'll need a Superpowered AI account ([create a free account here](https://superpowered.ai)) and API keys.

Most of these examples use the Superpowered Python SDK, which can be installed with pip using `pip install superpowered-sdk`

#### [Personal knowledge base Chrome extension](consumer/personal-kb-chrome-extension)
In this project we build a Chrome extension that runs in the background and uploads the text from every webpage you visit to a Superpowered Knowledge Base (that is private to you). You can then query that Knowledge Base through the Playground or a downstream application and it will have context around every webpage you've visited. This is basically a simple version of [Rewind](https://rewind.ai).

#### [Company handbook assistant](employee-productivity/company_handbook_assistant)
In this project, we build a knowledge base with an entire company handbook and use it to answer questions employees may have. We use the Sourcegraph company handbook here, since it's publicly accessible and fairly large (1.4M tokens).