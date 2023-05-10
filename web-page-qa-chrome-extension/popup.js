const apiKeyId = 'INSERT_API_KEY_ID_HERE';
const apiKeySecret = 'INSERT_API_KEY_SECRET_HERE';
const superpoweredApiUrl = 'https://api.superpowered.ai/v1/realtime_query';

function getHeaders() {
  const token = btoa(`${apiKeyId}:${apiKeySecret}`);
  return { Authorization: `Bearer ${token}` };
}

function realTimeQuery(query, passages, callback) {
  const payload = {
    query,
    passages,
    top_k: 5,
    max_chunk_length: 500,
    summarize_results: true,
  };

  fetch(superpoweredApiUrl, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(payload),
  })
    .then((response) => response.json())
    .then((data) => callback(data))
    .catch((error) => console.error('Error:', error));
}

document.getElementById('searchButton').addEventListener('click', () => {
    const query = document.getElementById('queryInput').value;
  
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, { action: 'getPageText' }, (response) => {
        realTimeQuery(query, [response.text], (apiResponse) => {
          const resultsContainer = document.getElementById('resultsContainer');
          resultsContainer.textContent = apiResponse.summary;
        });
      });
    });
  });