# Building a web page QA Chrome extension with Superpowered AI
This Chrome extension is an example of what can be built using Superpowered AI's real-time query endpoint. Unlike the normal query endpoint, real-time query doesn't run the query over an existing Knowledge Base. Instead, it runs the query over a passage or list of passages provided in the real-time query API call. This is useful for applications where you only need to query from a specific bit of text once or twice, and therefore don’t want to store it in a Knowledge Base. This makes it perfect for use as a web page question answering Chrome extension.

All of the code for the Chrome extension is provided in this folder. To run it, follow these steps:
1. Clone this repo
2. In the popup.js file, insert your Superpowered AI API Key ID and Secret
3. Open Chrome, click on Manage Extensions, and toggle Developer Mode on
4. Click "Load unpacked" and then choose the web-page-qa-chrome-extension directory

If you want to turn this into an actual product, then go for it! We really hope somebody does. All of this code is MIT-licensed, and we'd be happy to assist.