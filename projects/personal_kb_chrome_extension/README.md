# Personal knowledge base Chrome extension

In this project we build a Chrome extension that runs in the background and uploads the text from every webpage you visit to a Superpowered Knowledge Base (that is private to you). You can then query that Knowledge Base through the Playground or a downstream application and it will have context around every webpage you've visited. This is basically a simple version of [Rewind](https://rewind.ai).

To run the Chrome extension, you'll need to edit the `background.js` file in this directory to add your Superpowered API key ID and Secret, as well as a knowledge base ID. For the knowledge base ID, you can just create an empty KB in the UI and copy and paste the ID.
