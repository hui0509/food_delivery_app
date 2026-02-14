const express = require('express');
const app = express();

// 简单的测试路由
app.get('/api/test', (req, res) => {
  res.json({
    message: '后端API正常工作',
    timestamp: new Date().toISOString(),
    clientIP: req.ip
  });
});

// 必须绑定到 0.0.0.0
const PORT = 5000;
const HOST = '0.0.0.0';

app.listen(PORT, HOST, () => {
  console.log(`✅ 后端服务启动成功`);
  console.log(`📍 本机访问: http://localhost:${PORT}/api/test`);
  console.log(`🌐 局域网访问: http://你的IP:${PORT}/api/test`);
  console.log(`🔗 绑定地址: ${HOST}:${PORT}`);
});