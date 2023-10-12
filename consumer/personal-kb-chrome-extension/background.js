// Replace these with your own API key ID and secret, and Knowledge Base ID
const apiKeyId = 'YOUR_API_KEY_ID';
const apiKeySecret = 'YOUR_API_KEY_SECRET';
const kbId = 'YOUR_KNOWLEDGE_BASE_ID';

const baseUrl = 'https://api.superpowered.ai/v1/';

function init() {
    const token = btoa(`${apiKeyId}:${apiKeySecret}`);
    return `Bearer ${token}`;
}

const headers = {
    'Authorization': init(),
    'Content-Type': 'application/json'
};

function extractTextFromPage(data) {
    const { title, url, content } = data;

    const payload = {
        title: title,
        link_to_source: url,
        content: content,
        auto_context: true,
    };

    fetch(`${baseUrl}knowledge_bases/${kbId}/documents/raw_text`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload)
    })
        .then(response => response.json())
        .then(data => console.log('Document uploaded:', data))
        .catch(error => console.error('Error uploading document:', error));
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extractText') {
        extractTextFromPage(request.data);
    }
});