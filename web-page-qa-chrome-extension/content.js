function getPageText() {
    const bodyText = document.body.innerText;
    return bodyText;
  }
  
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getPageText') {
      sendResponse({ text: getPageText() });
    }
  });