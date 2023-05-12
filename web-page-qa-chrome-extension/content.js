function getPageText() {
  const bodyText = document.body.innerText;
  console.log("bodyText", typeof(bodyText))
  return bodyText;
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getPageText') {
    sendResponse({ text: getPageText() });
  }
});