// ==UserScript==
// @name         Google Arts & Culture Asset Link Collector
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Collect all asset links from Google Arts & Culture and save to a TXT file
// @author       Grok
// @match        https://artsandculture.google.com/
// @grant        none
// @require      https://code.jquery.com/jquery-3.6.0.min.js
// ==/UserScript==

(function() {
    'use strict';

    // Hàm scroll để tải toàn bộ nội dung
    function scrollToBottom(callback) {
        let lastHeight = document.body.scrollHeight;
        let scrollInterval = setInterval(() => {
            window.scrollTo(0, document.body.scrollHeight);
            let newHeight = document.body.scrollHeight;
            if (newHeight === lastHeight) {
                clearInterval(scrollInterval);
                callback();
            }
            lastHeight = newHeight;
        }, 2000); // Đợi 2 giây giữa mỗi lần scroll
    }

    // Hàm lấy tất cả URL asset
    function getAssetUrls() {
        const urls = new Set();
        $('a[href^="/asset/"]').each(function() {
            const fullUrl = 'https://artsandculture.google.com' + $(this).attr('href');
            urls.add(fullUrl);
        });
        return Array.from(urls);
    }

    // Hàm tạo và tải file TXT
    function downloadTxtFile(urls) {
        const textContent = urls.join('\n'); // Mỗi URL trên một dòng
        const blob = new Blob([textContent], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'asset_links.txt'; // Tên file tải về
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    // Hàm chính
    function main() {
        console.log('Starting scroll to load all assets...');
        scrollToBottom(() => {
            const assetUrls = getAssetUrls();
            console.log(`Found ${assetUrls.length} asset URLs.`);

            if (assetUrls.length > 0) {
                downloadTxtFile(assetUrls);
                console.log('Links saved to asset_links.txt');
            } else {
                console.log('No asset URLs found.');
            }
        });
    }

    // Thêm nút để kích hoạt script
    $(document).ready(() => {
        const button = $('<button>Collect Asset Links</button>')
            .css({
                position: 'fixed',
                top: '10px',
                right: '10px',
                zIndex: 9999,
                padding: '10px',
                background: '#4CAF50',
                color: 'white',
                border: 'none',
                cursor: 'pointer'
            })
            .click(main);

        $('body').append(button);
    });
})();