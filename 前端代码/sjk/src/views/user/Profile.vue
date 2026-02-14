<template>
    <div class="app-container">
        <!-- 顶部导航栏（保持原样） -->
        <div class="header">
            <div class="header-content">
                <div class="logo">
                    <i class="el-icon-food"></i>
                    <span class="logo-text">校园点餐平台</span>
                </div>
                <div class="user-info">
                    <el-dropdown @command="handleCommand">
                        <span class="el-dropdown-link">
                            <el-avatar
                                :size="32"
                                :src="userAvatar"
                                :key="avatarKey"
                                class="user-avatar"
                            >
                                <span class="avatar-text" v-if="!userAvatar || userAvatar.includes('default')">
                                    {{ userName ? userName.charAt(0).toUpperCase() : 'U' }}
                                </span>
                            </el-avatar>
                            <span class="username">{{ userName || '加载中...' }}</span>
                            <i class="el-icon-arrow-down el-icon--right"></i>
                        </span>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </div>
            </div>
        </div>

        <div class="main-body">
            <!-- 左侧导航栏 - 在个人中心下添加"地址管理" -->
            <div class="sidebar">
                <el-menu
                    ref="menu"
                    :default-active="active + ''"
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

                    <!-- 逛店铺 -->
                    <el-menu-item index="9">
                        <i class="el-icon-s-shop"></i>
                        <span slot="title">逛店铺</span>
                    </el-menu-item>

                    <!-- 购物车 -->
                    <el-menu-item index="10">
                        <i class="el-icon-shopping-cart-full"></i>
                        <span slot="title">购物车</span>
                        <el-badge v-if="cartItemCount > 0" :value="cartItemCount" class="cart-badge" />
                    </el-menu-item>

                    <!-- 推荐与评价模块 -->
                    <el-menu-item index="11">
                        <i class="el-icon-star-on"></i>
                        <span slot="title">推荐与评价</span>
                        <el-badge v-if="pendingReviewCount > 0" :value="pendingReviewCount"
                                 class="review-badge" type="danger" />
                    </el-menu-item>

                    <!-- 个人订单 -->
                    <el-submenu index="2">
                        <template slot="title">
                            <i class="el-icon-document"></i>
                            <span>个人订单</span>
                        </template>
                        <el-menu-item-group>
                            <el-menu-item index="3">
                                <i class="el-icon-circle-check"></i>
                                <span>历史订单</span>
                            </el-menu-item>
                            <el-menu-item index="4">
                                <i class="el-icon-truck"></i>
                                <span>已发货订单</span>
                            </el-menu-item>
                            <el-menu-item index="5">
                                <i class="el-icon-clock"></i>
                                <span>未发货订单</span>
                            </el-menu-item>
                            <!-- 订单异常 -->
                            <el-menu-item index="12">
                                <i class="el-icon-warning-outline"></i>
                                <span>订单异常</span>
                                <el-badge v-if="issueCount > 0" :value="issueCount"
                                         class="issue-badge" type="danger" />
                            </el-menu-item>
                        </el-menu-item-group>
                    </el-submenu>

                    <!-- 个人中心 - 新增地址管理 -->
                    <el-submenu index="6">
                        <template slot="title">
                            <i class="el-icon-user"></i>
                            <span>个人中心</span>
                        </template>
                        <el-menu-item-group>
                            <el-menu-item index="7">
                                <i class="el-icon-s-custom"></i>
                                <span>个人信息</span>
                            </el-menu-item>
                            <!-- 新增：地址管理菜单项 -->
                            <el-menu-item index="13">
                                <i class="el-icon-location-information"></i>
                                <span>地址管理</span>
                            </el-menu-item>
                            <el-menu-item index="8">
                                <i class="el-icon-lock"></i>
                                <span>修改密码</span>
                            </el-menu-item>
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
                    <!-- 各模块内容 -->
                    <div id="shoplist" v-show="active == 9">
                        <shoplist></shoplist>
                    </div>

                    <div id="cart" v-show="active == 10">
                        <cart></cart>
                    </div>

                    <div id="recommend" v-show="active == 11">
                        <recommend-component ref="recommendComponent"></recommend-component>
                    </div>

                    <div id="userfinished" v-show="active == 3">
                        <userfinished></userfinished>
                    </div>

                    <div id="usersending" v-show="active == 4">
                        <usersending></usersending>
                    </div>

                    <div id="userunsend" v-show="active == 5">
                        <userunsend></userunsend>
                    </div>

                    <!-- 订单异常模块 -->
                    <div id="orderissues" v-show="active == 12">
                        <order-issues ref="orderIssues"></order-issues>
                    </div>

                    <div id="indimsg" v-show="active == 7">
                        <indimsg ref="indimsg"></indimsg>
                    </div>

                    <!-- 新增：地址管理模块 -->
                    <div id="addressmanagement" v-show="active == 13">
                        <address-management ref="addressManagement"></address-management>
                    </div>

                    <div id="changepwd" v-show="active == 8">
                        <changepwd></changepwd>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import userfinished from '@/views/user/orders/UserFinished.vue'
import usersending from '@/views/user/orders/UserSending.vue'
import userunsend from '@/views/user/orders/UserUnsend.vue'
import indimsg from '@/views/user/profile/PersonalInfo.vue'
import changepwd from '@/views/user/profile/ChangePassword.vue'
import shoplist from '@/views/public/ShopList.vue'
import cart from '@/views/public/Cart.vue'
import RecommendComponent from '@/views/public/Recommend.vue'
import OrderIssues from '@/views/user/orders/OrderIssues.vue'

import AddressManagement from '@/views/user/profile/AddressManagement.vue'

export default {
    name: 'UserProfile',
    components: {
        userfinished,
        usersending,
        userunsend,
        indimsg,
        changepwd,
        shoplist,
        cart,
        RecommendComponent,
        OrderIssues,
        AddressManagement // 注册地址管理组件
    },
    data() {
        return {
            active: 9,
            isCollapse: false,
            currentTime: '',
            timer: null,
            cartItemCount: 0,
            pendingReviewCount: 0,
            issueCount: 0,
            refreshTimer: null,
            userAvatar: '',
            userName: '',
            avatarKey: 0,
            userInfoTimer: null,
        };
    },
    computed: {
        currentPageTitle() {
            const titles = {
                3: '已完成订单',
                4: '已发货订单',
                5: '未发货订单',
                7: '个人信息',
                8: '修改密码',
                9: '逛店铺',
                10: '购物车',
                11: '推荐与评价',
                12: '订单异常',
                13: '地址管理' // 新增
            };
            return titles[this.active] || '校园点餐平台';
        },
        welcomeMessage() {
            const hour = new Date().getHours();
            if (hour < 6) return '夜深了，注意休息';
            if (hour < 12) return '早上好！今天想吃点什么？';
            if (hour < 18) return '下午好！来份下午茶吗？';
            return '晚上好！晚餐时间到！';
        }
    },
    mounted() {
        this.updateTime();
        this.timer = setInterval(this.updateTime, 1000);
        this.loadCartCount();
        this.loadPendingReviewCount();
        this.loadIssueCount();

        this.loadUserInfo();

        this.$bus.$on('avatar-updated', this.handleAvatarUpdated);
        this.$bus.$on('user-info-updated', this.handleUserInfoUpdated);
        this.$bus.$on('issue-updated', this.loadIssueCount);

        this.refreshTimer = setInterval(() => {
            if (this.active === 11) {
                this.loadPendingReviewCount();
            }
            if (this.active === 12) {
                this.loadIssueCount();
            }
        }, 5 * 60 * 1000);

        this.userInfoTimer = setInterval(() => {
            this.loadUserInfo();
        }, 2 * 60 * 1000);
    },
    beforeDestroy() {
        if (this.timer) clearInterval(this.timer);
        if (this.refreshTimer) clearInterval(this.refreshTimer);
        if (this.userInfoTimer) clearInterval(this.userInfoTimer);

        this.$bus.$off('avatar-updated', this.handleAvatarUpdated);
        this.$bus.$off('user-info-updated', this.handleUserInfoUpdated);
        this.$bus.$off('issue-updated', this.loadIssueCount);
    },
    watch: {
        active(newVal) {
            if (newVal === 11 && this.$refs.recommendComponent) {
                setTimeout(() => {
                    this.$refs.recommendComponent.loadData();
                }, 100);
            }
            if (newVal === 12 && this.$refs.orderIssues) {
                setTimeout(() => {
                    this.$refs.orderIssues.loadData && this.$refs.orderIssues.loadData();
                }, 100);
            }

            if (newVal === 7 && this.$refs.indimsg) {
                setTimeout(() => {
                    this.$refs.indimsg.getdata && this.$refs.indimsg.getdata();
                }, 100);
            }

            // 新增：地址管理模块激活时加载数据
            if (newVal === 13 && this.$refs.addressManagement) {
                setTimeout(() => {
                    this.$refs.addressManagement.loadAddresses && this.$refs.addressManagement.loadAddresses();
                }, 100);
            }
        }
    },
    methods: {
        handleselect(index) {
            this.active = parseInt(index);
        },
        toggleCollapse() {
            this.isCollapse = !this.isCollapse;
        },
        handleCommand(command) {
            if (command === 'logout') {
                this.$confirm('确定要退出登录吗?', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    localStorage.removeItem('token');
                    localStorage.removeItem('user_avatar');
                    localStorage.removeItem('user_name');

                    this.userAvatar = '';
                    this.userName = '';
                    this.avatarKey++;

                    this.$router.push('/login');
                    this.$message({
                        type: 'success',
                        message: '退出成功!'
                    });
                });
            } else if (command === 'profile') {
                this.active = 7;
            }
        },
        updateTime() {
            const now = new Date();
            this.currentTime = now.toLocaleString('zh-CN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                weekday: 'long',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        },
        loadCartCount() {
            const cartData = localStorage.getItem('cart');
            if (cartData) {
                const cartItems = JSON.parse(cartData);
                this.cartItemCount = cartItems.reduce((total, item) => total + item.quantity, 0);
            }
        },
        async loadPendingReviewCount() {
            try {
                const token = localStorage.getItem('token');
                if (!token) {
                    this.pendingReviewCount = 0;
                    return;
                }

                const response = await this.$axios.get('/api/review/pending', {
                    headers: { 'token': token }
                });

                if (response.data.status === 200) {
                    this.pendingReviewCount = response.data.data.length;
                }
            } catch (error) {
                console.error('加载待评价数量失败:', error);
                this.pendingReviewCount = 0;
            }
        },
        async loadIssueCount() {
            try {
                const token = localStorage.getItem('token');
                if (!token) {
                    this.issueCount = 0;
                    return;
                }

                const response = await this.$axios.get('/api/user/issues/count', {
                    headers: { 'token': token }
                });

                if (response.data.status === 200) {
                    this.issueCount = response.data.data.pending_count || 0;
                }
            } catch (error) {
                console.error('加载订单异常数量失败:', error);
                this.issueCount = 0;
            }
        },
        async loadUserInfo() {
            try {
                const token = localStorage.getItem('token');
                if (!token) {
                    console.log('未找到token，使用默认头像');
                    this.setDefaultAvatar();
                    return;
                }

                console.log('正在加载用户信息...');

                const response = await this.$axios.get('/api/user/usermsg', {
                    headers: { 'token': token }
                });

                console.log('用户信息响应:', response.data);

                if (response.data.status === 200) {
                    const userData = response.data.data;

                    this.userName = userData.user_name || userData.real_name || '用户';

                    let avatarUrl = userData.avatar_url || '/images/user/default-avatar.jpg';

                    if (avatarUrl) {
                        if (!avatarUrl.startsWith('http://') && !avatarUrl.startsWith('https://')) {
                            if (!avatarUrl.startsWith('/')) {
                                avatarUrl = '/' + avatarUrl;
                            }
                            avatarUrl = avatarUrl + (avatarUrl.includes('?') ? '&' : '?') + 't=' + Date.now();
                        }
                    }

                    this.userAvatar = avatarUrl;
                    this.avatarKey++;

                    console.log('用户信息加载成功:', {
                        name: this.userName,
                        avatar: this.userAvatar
                    });

                    localStorage.setItem('user_avatar', this.userAvatar);
                    localStorage.setItem('user_name', this.userName);

                } else {
                    console.warn('加载用户信息失败:', response.data.msg);
                    this.setDefaultAvatar();
                }
            } catch (error) {
                console.error('加载用户信息错误:', error);
                this.setDefaultAvatar();
            }
        },
        setDefaultAvatar() {
            this.userAvatar = '/images/user/default-avatar.jpg';
            this.userName = '用户';
            this.avatarKey++;
        },
        handleAvatarUpdated(avatarUrl) {
            console.log('收到头像更新事件:', avatarUrl);
            if (avatarUrl) {
                let newAvatarUrl = avatarUrl;

                if (!newAvatarUrl.startsWith('http://') && !newAvatarUrl.startsWith('https://')) {
                    if (!newAvatarUrl.startsWith('/')) {
                        newAvatarUrl = '/' + newAvatarUrl;
                    }
                    newAvatarUrl = newAvatarUrl + (newAvatarUrl.includes('?') ? '&' : '?') + 't=' + Date.now();
                }

                this.userAvatar = newAvatarUrl;
                this.avatarKey++;

                localStorage.setItem('user_avatar', newAvatarUrl);

                setTimeout(() => {
                    this.loadUserInfo();
                }, 300);
            }
        },
        handleUserInfoUpdated() {
            console.log('收到用户信息更新事件，重新加载用户信息');
            this.loadUserInfo();
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

.el-icon-location-information {
    font-size: 19px;
    margin-right: 14px;
    width: 24px;
    text-align: center;
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
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* 用户头像样式 */
.user-avatar {
    border: 2px solid rgba(255, 255, 255, 0.8);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
}

.user-avatar:hover {
    border-color: #ffd04b;
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* 头像文字样式 */
.avatar-text {
    font-weight: bold;
    font-size: 16px;
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

/* 购物车徽标样式 */
.cart-badge {
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
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

    .username {
        max-width: 80px;
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

.review-badge {
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
}

.el-menu-item .review-badge {
    margin-left: 5px;
}

/* 原有样式保持不变，只添加新的徽章样式 */
.issue-badge {
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
}

.el-menu-item .issue-badge {
    margin-left: 5px;
}

/* 其他样式保持不变 */
.app-container {
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

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
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.user-avatar {
    border: 2px solid rgba(255, 255, 255, 0.8);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
}

.user-avatar:hover {
    border-color: #ffd04b;
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.avatar-text {
    font-weight: bold;
    font-size: 16px;
}

.main-body {
    display: flex;
    flex: 1;
    overflow: hidden;
}

.sidebar {
    background: linear-gradient(to bottom, #1e2a3a, #2c3e50);
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.2);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 999;
}

.el-menu-vertical-demo {
    border-right: none !important;
    height: 100%;
    background: transparent !important;
}

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

.cart-badge {
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
}

.el-menu--collapse .el-menu-item span,
.el-menu--collapse .el-submenu__title span {
    display: none;
}

.el-menu--collapse .el-menu-item,
.el-menu--collapse .el-submenu__title {
    text-align: center;
}

.el-menu--collapse .el-menu-item i,
.el-menu--collapse .el-submenu__title i {
    margin-right: 0 !important;
    font-size: 22px;
}

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

    .username {
        max-width: 80px;
    }
}

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

.review-badge {
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
}

.el-menu-item .review-badge {
    margin-left: 5px;
}
</style>