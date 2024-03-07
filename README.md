# Superpowered AI Examples

This repo contains a collection of examples for working with and building retrieval-augmented LLM applications with Superpowered AI.

To run these examples, you'll need a Superpowered AI account ([create a free account here](https://superpowered.ai)) and API keys.

Some of these examples use the Superpowered Python SDK, which can be installed with pip using `pip install superpowered-sdk`

If you're using the SDK, please make sure you have `SUPERPOWERED_API_KEY_ID` and `SUPERPOWERED_API_KEY_SECRET` set as environment variables or the variables directly via `superpowered.set_api_key()`.

## Projects

#### [Personal knowledge base Chrome extension](projects/personal_kb_chrome_extension)
In this project we build a Chrome extension that runs in the background and uploads the text from every webpage you visit to a Superpowered Knowledge Base (that is private to you). You can then query that Knowledge Base through the Playground or a downstream application and it will have context around every webpage you've visited. This is basically a simple version of [Rewind](https://rewind.ai).

#### [Company handbook assistant](projects/company_handbook_assistant)
In this project, we build a knowledge base with an entire company handbook and use it to answer questions employees may have. We use the Sourcegraph company handbook here, since it's publicly accessible and fairly large (1.4M tokens).

## Notebooks

There are lots of different workflows demonstrated in the notebooks and most of these notebooks are covered during our weekly webinars.

[Webinar Recordings](https://www.youtube.com/playlist?list=PLePKvgYhNOFxg3O7gXfmxaKp0EWXEhvNC)

Some fun fun worksflows:

- [Writing a book using "document review" and "long form" endpoints](notebooks/book_generation_pt_2.ipynb)
- [AI debate on the "theory of everything"](notebooks/ai_debate.ipynb)
- [Knowledge base augmentation with web search](notebooks/augment_kb_with_web_search.ipynb)