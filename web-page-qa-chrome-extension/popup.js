const apiKeyId = '';
const apiKeySecret = '';
const superpoweredApiUrl = 'https://api.superpowered.ai/v1/realtime_query';

function getHeaders() {
  const token = btoa(`${apiKeyId}:${apiKeySecret}`);
  return { Authorization: `Bearer ${token}` };
}

async function realTimeQuery(query, passages, callback) {
  const payload = {
    query,
    passages,
    top_k: 5,
    max_chunk_length: 500,
    summarize_results: true,
  };

  const response = await fetch (superpoweredApiUrl, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(payload)
  })

  const resData = await response.json();
  callback(resData, response.status);
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
      realTimeQuery(query, [response.text], (apiResponse, status) => {

        // Check specifically for a 500 error, which typically means the api key and/or secret are invalid
        if (status === 500) {
          alert('Error: Please make sure your API key and secret are valid')
          document.getElementById('loading').style.display = 'none';
          return;
        } else if (status !== 200) {
          // If the status is not 200 or 500, then we just show a generic error message
          alert("Error: We couldn't process your request at this time. Please try again later.")
          document.getElementById('loading').style.display = 'none';
          return;
        }
        
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