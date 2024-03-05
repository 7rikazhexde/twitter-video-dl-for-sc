const languageSelect = document.getElementById('languageSelect');
const sendCurrentUrlButton = document.getElementById('sendCurrentUrl');
const sendInputUrlButton = document.getElementById('sendInputUrl');
const fileNameInput = document.getElementById('fileNameInput');
const urlInput = document.getElementById('urlInput');
const title = document.getElementById('title');

const text = {
    en: {
        title: 'twitter-video-dl-send',
        fileNamePlaceholder: 'Enter file name',
        sendCurrentUrl: 'Send current URL',
        sendInputUrl: 'Send the URL you entered',
        urlPlaceholder: 'Enter URL',
        sent: 'Sent',
    },
    ja: {
        title: 'twitter-video-dl-send',
        fileNamePlaceholder: 'ファイル名を入力',
        sendCurrentUrl: '現在のURLを送信',
        sendInputUrl: '入力したURLを送信',
        urlPlaceholder: 'URLを入力',
        sent: '送信済み',
    },
};

function updateLanguage() {
    const lang = languageSelect.value;
    localStorage.setItem('language', lang);
    title.innerText = text[lang].title;
    fileNameInput.placeholder = text[lang].fileNamePlaceholder;
    sendCurrentUrlButton.innerText = text[lang].sendCurrentUrl;
    sendInputUrlButton.innerText = text[lang].sendInputUrl;
    urlInput.placeholder = text[lang].urlPlaceholder;
}

languageSelect.addEventListener('change', updateLanguage);

window.addEventListener('DOMContentLoaded', () => {
    const savedLanguage = localStorage.getItem('language') || 'en';
    languageSelect.value = savedLanguage;
    updateLanguage();
});

document.getElementById('sendCurrentUrl').addEventListener('click', function() {
    const fileName = document.getElementById('fileNameInput').value;
    chrome.tabs.query({active: true, currentWindow: true}, tabs => {
        chrome.runtime.sendMessage({action: "sendUrl", url: tabs[0].url, fileName: fileName}).catch((error) => {
            console.log(error);
            chrome.runtime.sendMessage({action: "getLastError"}, response => {
                if (response.error) {
                    alert(response.error);
                }
            });
        });
    });
    this.style.backgroundColor = '#888888';
    this.innerText = text[languageSelect.value].sent;
    setTimeout(() => {
        this.style.backgroundColor = '#2a4fc9';
        this.innerText = text[languageSelect.value].sendCurrentUrl;
    }, 2000);
});

document.getElementById('sendInputUrl').addEventListener('click', function() {
    const url = document.getElementById('urlInput').value;
    const fileName = document.getElementById('fileNameInput').value;
    if (url) {
        chrome.runtime.sendMessage({action: "sendUrl", url: url, fileName: fileName}).catch((error) => {
            console.log(error);
            chrome.runtime.sendMessage({action: "getLastError"}, response => {
                if (response.error) {
                    alert(response.error);
                }
            });
        });
        this.style.backgroundColor = '#888888';
        this.innerText = text[languageSelect.value].sent;
        setTimeout(() => {
            this.style.backgroundColor = '#2a4fc9';
            this.innerText = text[languageSelect.value].sendInputUrl;
        }, 2000);
    } else {
        alert('URLを入力してください');
    }
});
