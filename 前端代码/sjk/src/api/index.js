import axios from "axios"

// ⚠️ 关键修改：动态获取正确的API地址
const getCorrectBaseURL = () => {
  // 获取当前页面的主机名
  const hostname = window.location.hostname;
  console.log('当前访问主机名:', hostname);

  // 如果是本机访问（通过localhost或127.0.0.1）
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:5000';
  }

  // 如果是手机通过IP访问（如 192.168.192.1:8080）
  // 那么API地址应该是电脑的IP:5000

  // ⚠️ 这里需要填写你的电脑实际IP ⚠️
  // 你的电脑IP是（根据之前的信息）：192.168.0.100
  const computerIP = '192.168.0.100'; // ← 修改为你的电脑IP

  return `http://${computerIP}:5000`;
};

const aaxios = axios.create({
  baseURL: getCorrectBaseURL(),
  timeout: 10000
});

// 添加详细的调试信息
console.log('🎯 前端API配置:');
console.log('访问URL:', window.location.href);
console.log('API地址:', aaxios.defaults.baseURL);
console.log('------------------------');

// 请求拦截器
aaxios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.token = token;
  }
  console.log(`📤 请求: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
  return config;
});

// 响应拦截器
aaxios.interceptors.response.use(
  response => {
    console.log(`📥 响应成功: ${response.config.url}`);
    return response;
  },
  error => {
    console.error('❌ 请求失败:');
    console.error('URL:', error.config?.baseURL + error.config?.url);
    console.error('错误:', error.message);
    console.error('错误代码:', error.code);
    console.error('错误详情:', error);

    // 如果是网络错误，显示详细提示
    if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
      const errorMsg = `
网络连接失败！

请检查：
1. 后端服务是否运行在: ${error.config?.baseURL}
2. 电脑IP是否正确: 192.168.0.100
3. 手机和电脑是否在同一局域网
4. 电脑防火墙是否允许5000端口

当前API地址: ${error.config?.baseURL}
      `;
      console.warn(errorMsg);
      error.friendlyMessage = '网络连接失败，请检查后端服务是否运行';
    } else if (error.response) {
      // 服务器返回了错误响应
      error.friendlyMessage = `服务器错误(${error.response.status}): ${error.response.data?.msg || error.message}`;
    } else {
      error.friendlyMessage = `请求失败: ${error.message}`;
    }
    return Promise.reject(error);
  }
);

export default aaxios;

// AI 聊天接口
export function askChat(question) {
  return aaxios.post('/api/chat', { question });
}