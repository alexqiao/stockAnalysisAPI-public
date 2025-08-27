// 测试修复后的getCookie函数
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        let cookieValue = parts.pop().split(';').shift();
        
        // 处理可能的引号包围
        if (cookieValue && cookieValue.startsWith('"') && cookieValue.endsWith('"')) {
            cookieValue = cookieValue.substring(1, cookieValue.length - 1);
        }
        
        // 如果cookie值包含"Bearer "前缀，去掉它
        if (cookieValue && cookieValue.startsWith('Bearer ')) {
            return cookieValue.substring(7); // 去掉"Bearer "前缀
        }
        return cookieValue;
    }
    return null;
}

// 测试用例
console.log("测试getCookie函数:");

// 测试1: 正常cookie（无引号）
document.cookie = "access_token=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjY3BwYWFwIiwiZXhwIjoxNzU2MzAxODY4fQ.***REMOVED***";
console.log("测试1 - 正常cookie:", getCookie('access_token'));

// 测试2: 带引号的cookie
document.cookie = "access_token=\"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjY3BwYWFwIiwiZXhwIjoxNzU2MzAxODY4fQ.***REMOVED***\"";
console.log("测试2 - 带引号cookie:", getCookie('access_token'));

// 测试3: 不存在的cookie
console.log("测试3 - 不存在的cookie:", getCookie('nonexistent'));

// 测试4: 空cookie
document.cookie = "access_token=";
console.log("测试4 - 空cookie:", getCookie('access_token'));
