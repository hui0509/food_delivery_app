<template>
    <div class="app-container">
        <!-- 顶部导航栏 -->
        <div class="header">
            <div class="header-content">
                <div class="logo">
                    <i class="el-icon-s-platform"></i>
                    <span class="logo-text">校园点餐平台 - 后台管理</span>
                </div>
                <div class="user-info">
                    <el-dropdown @command="handleCommand">
                        <span class="el-dropdown-link">
                            <el-avatar icon="el-icon-user-solid" size="small"></el-avatar>
                            <span class="username">{{ currentUser.username || '管理员' }}</span>
                            <i class="el-icon-arrow-down el-icon--right"></i>
                        </span>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item command="profile">管理员信息</el-dropdown-item>
                            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </div>
            </div>
        </div>

        <div class="main-body">
            <!-- 左侧导航栏 -->
            <div class="sidebar">
                <el-menu
                    default-active="1"
                    class="el-menu-vertical-demo"
                    background-color="#2c3e50"
                    text-color="#b7c4cc"
                    active-text-color="#409EFF"
                    @select="handleselect"
                    :collapse="isCollapse">

                    <div class="menu-header" @click="toggleCollapse">
                        <i class="el-icon-s-fold" v-if="!isCollapse"></i>
                        <i class="el-icon-s-unfold" v-else></i>
                        <span v-if="!isCollapse">收起菜单</span>
                    </div>

                    <el-menu-item index="1">
                        <i class="el-icon-s-shop"></i>
                        <span slot="title">店铺管理</span>
                    </el-menu-item>

                    <el-menu-item index="2" v-if="currentUser.is_super == 1">
                        <i class="el-icon-user-solid"></i>
                        <span slot="title">用户管理</span>
                    </el-menu-item>

                    <el-menu-item index="3">
                        <i class="el-icon-s-check"></i>
                        <span slot="title">送餐员管理</span>
                    </el-menu-item>

                    <el-submenu index="4">
                        <template slot="title">
                            <i class="el-icon-s-promotion"></i>
                            <span>物流管理</span>
                        </template>
                        <el-menu-item-group>
                            <el-menu-item index="5"><i class="el-icon-circle-check"></i> 已完成</el-menu-item>
                            <el-menu-item index="6"><i class="el-icon-refresh"></i> 进行中</el-menu-item>
                        </el-menu-item-group>
                    </el-submenu>

                    <el-submenu index="7">
                        <template slot="title">
                            <i class="el-icon-s-order"></i>
                            <span>订单管理</span>
                        </template>
                        <el-menu-item-group>
                            <el-menu-item index="8"><i class="el-icon-finished"></i> 已完成订单</el-menu-item>
                            <el-menu-item index="9"><i class="el-icon-truck"></i> 已发货订单</el-menu-item>
                            <el-menu-item index="10"><i class="el-icon-clock"></i> 未发货订单</el-menu-item>
                             <el-menu-item index="11"><i class="el-icon-warning"></i> 订单异常处理</el-menu-item>
                        </el-menu-item-group>
                    </el-submenu>
                </el-menu>
            </div>

            <!-- 主内容区域 -->
            <div class="content-main" :class="{ 'collapsed': isCollapse }">
                <div class="content-header">
                    <el-breadcrumb separator="/">
                        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
                        <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
                    </el-breadcrumb>
                    <div class="welcome-text">
                        <h2>{{ welcomeMessage }}</h2>
                        <p>{{ currentTime }}</p>
                    </div>
                </div>

                <div class="content-body">
                    <div id="manageshop" v-show="active == 1"><manageshop></manageshop></div>
                    <div id="manageusers" v-show="active == 2"><manageusers></manageusers></div>
                    <div id="managedispatcher" v-show="active == 3"><managedispatcher></managedispatcher></div>
                    <div id="deliveryended" v-show="active == 5"><deliveryended></deliveryended></div>
                    <div id="deliveryunended" v-show="active == 6"><deliveryunended></deliveryunended></div>
                    <div id="ordersended" v-show="active == 8"><ordersended></ordersended></div>
                    <div id="ordersending" v-show="active == 9"><ordersending></ordersending></div>
                    <div id="orderunsend" v-show="active == 10"><orderunsend></orderunsend></div>
                    <div id="orderissues" v-show="active == 11"><manage-order-issues></manage-order-issues></div>
                </div>
            </div>
        </div>

        <!-- 管理员信息弹窗 -->
        <el-dialog
            title="管理员个人信息"
            :visible.sync="profileDialogVisible"
            width="500px"
            center
            :close-on-click-modal="false">
            <el-form :model="adminForm" :rules="adminRules" ref="adminForm" label-width="100px">
                <el-form-item label="用户名" prop="user_name">
                    <el-input v-model="adminForm.user_name" disabled></el-input>
                </el-form-item>
                <el-form-item label="真实姓名" prop="real_name">
                    <el-input v-model="adminForm.real_name"></el-input>
                </el-form-item>
                <el-form-item label="性别" prop="sex">
                    <el-radio-group v-model="adminForm.sex">
                        <el-radio label="男">男</el-radio>
                        <el-radio label="女">女</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="年龄" prop="age">
                    <el-input-number v-model="adminForm.age" :min="1" :max="120" style="width: 100%"></el-input-number>
                </el-form-item>
                <el-form-item label="邮箱" prop="mail">
                    <el-input v-model="adminForm.mail"></el-input>
                </el-form-item>
                <el-form-item label="手机号">
                    <el-input v-model="adminForm.phone" disabled></el-input>
                </el-form-item>
            </el-form>
            <span slot="footer" class="dialog-footer">
                <el-button @click="profileDialogVisible = false">取 消</el-button>
                <el-button type="primary" @click="saveAdminProfile">保 存</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
import manageshop from '@/views/admin/ShopManagement.vue'
import manageusers from '@/views/admin/UserManagement.vue'
import managedispatcher from '@/views/admin/DispatcherManagement.vue'
import deliveryended from '@/views/admin/delivery/DeliveryEnded.vue'
import deliveryunended from '@/views/admin/delivery/DeliveryUnended.vue'
import ordersended from '@/views/admin/orders/BeSended.vue'
import ordersending from '@/views/admin/orders/BeSending.vue'
import orderunsend from '@/views/admin/orders/UnSend.vue'
import manageOrderIssues from '@/views/admin/orders/ManageOrderIssues.vue'

export default {
    name: 'AdminDashboard',
    components: {
        manageshop,
        managedispatcher,
        deliveryended,
        deliveryunended,
        ordersended,
        ordersending,
        orderunsend,
        manageusers,
        'manage-order-issues': manageOrderIssues
    },
    data() {
        return {
            active: '1',
            isCollapse: false,
            currentTime: '',
            timer: null,
            currentUser: {
                username: '',
                role: 0
            },
            // 管理员信息弹窗相关
            profileDialogVisible: false,
            adminForm: {
                real_name: '',
                sex: '',
                age: null,
                mail: '',
                phone: '',
                user_name: ''
            },
            adminRules: {
                real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
                mail: [{ type: 'email', message: '请输入正确的邮箱格式', trigger: ['blur', 'change'] }]
            }
        }
    },
    computed: {
        currentPageTitle() {
            const titles = {
                '1': '店铺管理', '2': '用户管理', '3': '送餐员管理',
                '5': '物流管理 - 已完成', '6': '物流管理 - 进行中',
                '8': '订单管理 - 已完成订单', '9': '订单管理 - 已发货订单', '10': '订单管理 - 未发货订单'
            };
            return titles[this.active] || '后台管理系统';
        },
        welcomeMessage() {
            const hour = new Date().getHours();
            if (hour < 6) return '夜深了，管理员辛苦了';
            if (hour < 12) return '早上好！开始今天的管理工作吧';
            if (hour < 18) return '下午好！系统运行一切正常';
            return '晚上好！感谢您今天的辛勤工作';
        }
    },
    mounted() {
        this.updateTime()
        this.timer = setInterval(this.updateTime, 1000)

        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
        this.currentUser = {
            username: userInfo.username || '管理员',
            role: userInfo.role || 0,
            is_super: userInfo.is_super || 0
        }
        if (this.currentUser.is_super == 0 && this.active == 2) {
            this.active = "1";   // 普通管理员强制回到店铺管理
        }
    },
    beforeDestroy() {
        if (this.timer) clearInterval(this.timer);
    },
    methods: {
        handleselect(index) {
            this.active = index;
        },
        toggleCollapse() {
            this.isCollapse = !this.isCollapse;
        },
        handleCommand(command) {
            if (command === 'logout') {
                this.$confirm('确定要退出登录吗？', '提示', { type: 'warning' }).then(() => {
                    localStorage.removeItem('token');
                    localStorage.removeItem('userInfo');
                    this.$router.push('/login');
                    this.$message.success('退出成功！');
                });
            } else if (command === 'profile') {
                this.profileDialogVisible = true;
                this.loadAdminProfile();
            }
        },
        updateTime() {
            const now = new Date();
            this.currentTime = now.toLocaleString('zh-CN', {
                year: 'numeric', month: 'long', day: 'numeric', weekday: 'long',
                hour: '2-digit', minute: '2-digit', second: '2-digit'
            });
        },
        // 加载管理员个人信息（复用用户接口）
        loadAdminProfile() {
            this.$axios.get('/api/manage/admininfo').then(res => {
                if (res.data.status === 200) {
                    const d = res.data.data;
                    this.adminForm = {
                        real_name: d.real_name || '',
                        sex: d.sex || '男',
                        age: d.age ? Number(d.age) : null,
                        mail: d.mail || '',
                        phone: d.phone,
                        user_name: d.user_name || '管理员'
                    };
                }
            }).catch(() => {
                this.$message.error('加载管理员信息失败');
            });
        },
        // 保存管理员信息
        saveAdminProfile() {
              this.$refs.adminForm.validate(valid => {
                if (!valid) return;

                this.$axios.post('/api/manage/admininfo', this.adminForm).then(res => {
                  if (res.data.status === 200) {
                    this.$message.success('保存成功！');
                    this.profileDialogVisible = false;
                    this.currentUser.username = this.adminForm.user_name;
                    // 更新 localStorage
                    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
                    userInfo.username = this.adminForm.user_name;
                    localStorage.setItem('userInfo', JSON.stringify(userInfo));
                  } else if (res.data.status === 403) {
                    // 关键：捕获 403，提示用户当前不是管理员身份
                    this.$confirm(
                      '检测到您当前登录身份已变为普通用户，无法保存管理员信息。<br><br>是否重新登录管理员账号？',
                      '权限不足',
                      {
                        dangerouslyUseHTMLString: true,
                        type: 'warning',
                        distinguishCancelAndClose: true,
                        confirmButtonText: '重新登录管理员',
                        cancelButtonText: '暂不处理'
                      }
                    ).then(() => {
                      // 清除污染的 token，强制回到登录页
                      localStorage.removeItem('token');
                      localStorage.removeItem('userInfo');
                      this.$router.push('/login');
                      this.$message.info('请使用管理员账号重新登录');
                    });
                  } else {
                    this.$message.error(res.data.msg || '保存失败');
                  }
                }).catch(() => {
                  this.$message.error('网络错误');
                });
              });
            }
    }
}
</script>

<style scoped>
.app-container {
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* 头部样式 */
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    z-index: 1000;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 30px;
    height: 70px;
}

.logo {
    display: flex;
    align-items: center;
    color: white;
    font-size: 24px;
    font-weight: bold;
}

.logo i {
    font-size: 32px;
    margin-right: 12px;
    color: #ffd04b;
}

.logo-text {
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-info {
    color: white;
}

.el-dropdown-link {
    display: flex;
    align-items: center;
    color: white;
    cursor: pointer;
}

.username {
    margin: 0 8px;
    font-size: 14px;
}

/* 主体布局 */
.main-body {
    display: flex;
    flex: 1;
    overflow: hidden;
}

/* 侧边栏样式 */
.sidebar {
    background: linear-gradient(to bottom, #1e2a3a, #2c3e50);  /* 更深邃的渐变蓝黑 */
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.2);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 999;
}

/* 菜单整体样式升级 */
.el-menu-vertical-demo {
    border-right: none !important;
    height: 100%;
    background: transparent !important;
}

/* 收起/展开按钮美化 */
.menu-header {
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #a8b5c8;
    background: rgba(0, 0, 0, 0.25);
    cursor: pointer;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    transition: all 0.3s ease;
    font-size: 15px;
    font-weight: 500;
}

.menu-header:hover {
    background: rgba(64, 158, 255, 0.25) !important;
    color: #ffffff !important;
}

.menu-header i {
    font-size: 20px;
    margin-right: 10px;
    transition: transform 0.3s ease;
}


.el-menu-item,
.el-submenu__title {
    height: 56px !important;
    line-height: 56px !important;
    font-size: 15px;
    font-weight: 500;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.el-menu-item i,
.el-submenu__title i {
    margin-right: 14px;
    font-size: 19px;
    width: 24px;
    text-align: center;
}

/* Hover 效果 - 光条滑动 */
.el-menu-item:hover,
.el-submenu__title:hover {
    background-color: rgba(64, 158, 255, 0.15) !important;
    color: #ffffff !important;
}


.el-menu-item:hover::before,
.el-submenu__title:hover::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: #409EFF;
    transform: scaleY(0);
    transition: transform 0.3s ease;
    transform-origin: center;
}

.el-menu-item:hover::before,
.el-submenu__title:hover::before {
    transform: scaleY(1);
}

/* 选中状态 - 更明显的蓝色高亮条 */
.el-menu-item.is-active {
    background: linear-gradient(to right, rgba(64, 158, 255, 0.25), transparent) !important;
    color: #409EFF !important;
    font-weight: 600;
    border-left: 4px solid #409EFF !important;
    position: relative;
}
.el-menu-item.is-active::after {
    content: '';
    position: absolute;
    right: 0;
    top: 50%;
    width: 8px;
    height: 8px;
    background: #409EFF;
    border-radius: 50%;
    transform: translateY(-50%);
    box-shadow: 0 0 10px #409EFF;
}

/* 子菜单缩进美化 */
.el-menu-item-group__title {
    padding-top: 12px !important;
    color: #8492a6 !important;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.el-menu--inline .el-menu-item {
    padding-left: 60px !important;
    font-size: 14px;
    background: rgba(0, 0, 0, 0.15) !important;
}

/* 图标颜色统一 */
.el-menu-item i,
.el-submenu__title i {
    color: #a8b5c8;
    transition: color 0.3s;
}

.el-menu-item:hover i,
.el-submenu__title:hover i,
.el-menu-item.is-active i {
    color: #409EFF;
}

/* 折叠状态下的 tooltip（可选增强） */
.el-menu--collapse .el-menu-item span,
.el-menu--collapse .el-submenu__title span {
    display: none;
}

/* 折叠时图标居中 */
.el-menu--collapse .el-menu-item,
.el-menu--collapse .el-submenu__title {
    text-align: center;
}

.el-menu--collapse .el-menu-item i,
.el-menu--collapse .el-submenu__title i {
    margin-right: 0 !important;
    font-size: 22px;
}

/* 主内容区域 */
.content-main {
    flex: 1;
    padding: 20px;
    transition: all 0.3s ease;
    overflow-y: auto;
}

.content-main.collapsed {
    margin-left: 0;
}

.content-header {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.welcome-text h2 {
    margin: 0 0 8px 0;
    color: #333;
    font-size: 24px;
    font-weight: 600;
}

.welcome-text p {
    margin: 0;
    color: #666;
    font-size: 14px;
}

.content-body {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    min-height: calc(100vh - 200px);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .header-content {
        padding: 0 15px;
    }

    .logo-text {
        font-size: 18px;
    }

    .content-main {
        padding: 10px;
    }

    .content-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }
}

/* 滚动条样式 */
.content-main::-webkit-scrollbar {
    width: 6px;
}

.content-main::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
}

.content-main::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
}

.content-main::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
}

/* 管理界面特定样式 */
.management-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
}

.stat-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-card h3 {
    margin: 0 0 10px 0;
    font-size: 16px;
    opacity: 0.9;
}

.stat-card .number {
    font-size: 32px;
    font-weight: bold;
    margin: 0;
}
</style>
