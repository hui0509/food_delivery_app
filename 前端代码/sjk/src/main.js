import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import router from '@/router'

// 引入axios配置
import axios from '@/api/index'

Vue.use(ElementUI);
Vue.config.productionTip = false

// 修改vue的原型链
Vue.prototype.$axios = axios
Vue.prototype.$bus = new Vue();
// ==================== 关键修改：管理员接口使用独立 token ====================
axios.interceptors.request.use(config => {
  // 判断是否是管理员后台接口（路径包含 /api/manage/ 或 /api/manager/）
  const isAdminApi = config.url.includes('/api/manage/') || config.url.includes('/api/manager/');

  if (isAdminApi) {
    // 优先使用独立的 admin_token（管理员登录时保存的）
    const adminToken = localStorage.getItem('admin_token');
    if (adminToken) {
      config.headers.token = adminToken;  // 强制覆盖为管理员 token
    }
  }
  // 普通接口保持默认行为（使用 localStorage.getItem('token')）

  return config;
}, error => {
  return Promise.reject(error);
});
// =============================================================================

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')