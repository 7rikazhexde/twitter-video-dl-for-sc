function sendUrl(url, fileName) {
    fetch(`http://localhost:3000/?url=${encodeURIComponent(url)}&fileName=${encodeURIComponent(fileName)}`);
}
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "sendUrl") {
        sendUrl(request.url, request.fileName);
    }
});
