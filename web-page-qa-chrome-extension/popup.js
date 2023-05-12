const apiKeyId = '';
const apiKeySecret = '';
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

const textArea = document.getElementById('queryInput');
textArea.addEventListener('input', autoResize);

function autoResize() {
  // We need to reset the height momentarily to get the correct scrollHeight for the textarea
  this.style.height = '0px';
  const scrollHeight = this.scrollHeight;

  // We then set the height directly, outside of the render loop
  this.style.height = scrollHeight + 'px';
}

function removeCitations(resultText) {
  // We don't need the citations here since we can't click on them or tie them to the relevant text
  // The format can either be [1], [1, 2, 3], or [1-4]
  const citationRegex = /\[\d+(?:-\d+|,\s*\d+)*\]/g;
  const citationMatches = resultText.match(citationRegex);
  if (citationMatches) {
    citationMatches.forEach((citation) => {
      resultText = resultText.replace(citation, '');
    });
  }
  // Remove the space that is leftover before the period
  const regex = / \./g;
  resultText = resultText.replace(regex, '.');
  return resultText;
}

document.getElementById('searchButton').addEventListener('click', () => {
  const query = document.getElementById('queryInput').value;

  document.getElementById('loading').style.display = 'block';

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, { action: 'getPageText' }, (response) => {
      realTimeQuery(query, [response.text], (apiResponse) => {
        
        // Add the resultTextShown class to the result text element in order to add the correct padding (kind of a crude way of doing this)
        const resultTextElement = document.getElementById('resultText');
        resultTextElement.classList.add("resultTextShown");

        let resultText = apiResponse.summary;
        resultText = removeCitations(resultText);
        resultTextElement.innerHTML = resultText;

        document.getElementById('loading').style.display = 'none';
      });
    });
  });
});