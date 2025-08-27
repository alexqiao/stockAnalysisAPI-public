// 简单的cookie调试脚本
function debugCookies() {
    console.log('当前所有cookies:', document.cookie);
    
    const token = getCookie('access_token');
    console.log('access_token cookie值:', token);
    
    if (token) {
        console.log('Token解析结果:');
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            console.log('Payload:', payload);
            console.log('用户名:', payload.sub);
            console.log('过期时间:', new Date(payload.exp * 1000));
        } catch (e) {
            console.log('Token解析失败:', e);
        }
    } else {
        console.log('未找到access_token cookie');
    }
}

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

// 运行调试
debugCookies();
