let lastError = null;

async function sendUrl(url, fileName) {
    await fetch(`http://localhost:3000/?url=${encodeURIComponent(url)}&fileName=${encodeURIComponent(fileName)}`);
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "sendUrl") {
        sendUrl(request.url, request.fileName).catch((error) => {
            console.log(error);
            lastError = error.message;
        });
    } else if (request.action === "getLastError") {
        sendResponse({error: lastError});
        lastError = null;
    }
});
