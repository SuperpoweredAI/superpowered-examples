# Company Handbook Assistant

In this project, we build a knowledge base with an entire company handbook and use it to answer questions employees may have. We use the Sourcegraph company [handbook](https://handbook.sourcegraph.com) here, since it's publicly accessible and fairly large (1.4M tokens).

The Sourcegraph company handbook is publicly available through a Github [repo](https://github.com/sourcegraph/handbook) as Markdown files, which makes it very convenient to work with. We've gone ahead and included these files as part of this example, in the `content` folder.

To run this example, all you need to do is run the `create_kb.py` script to create the knowledge base and upload all of the files. Then you can run `eval.py` to do a GPT-4 powered evaluation of the responses on a set of test queries.

Requirements
- Superpowered API key ID and Secret
- Superpowered Python SDK (`pip install superpowered-sdk`)
- OpenAI API key and SDK (just for the eval script)
