<template>
    <div class="app-container">
        <!-- 顶部导航栏保持不变 -->
        <div class="header">
            <div class="header-content">
                <div class="logo">
                    <i class="el-icon-s-shop"></i>
                    <span class="logo-text">校园点餐平台 - 商家管理</span>
                </div>
                <div class="user-info">
                    <el-dropdown @command="handleCommand">
                        <span class="el-dropdown-link">
                            <el-avatar icon="el-icon-user-solid" size="small"></el-avatar>
                            <span class="username">{{ currentUser.username || '商家' }}</span>
                            <i class="el-icon-arrow-down el-icon--right"></i>
                        </span>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item command="profile">商家信息</el-dropdown-item>
                            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </div>
            </div>
        </div>

        <div class="main-body">
            <!-- 左侧导航栏 - 关键修改 -->
            <div class="sidebar" :class="{ 'sidebar-collapsed': isCollapse }">
                <el-menu
                    default-active="1"
                    class="el-menu-vertical-demo"
                    background-color="#2c3e50"
                    text-color="#b7c4cc"
                    active-text-color="#409EFF"
                    @select="handleselect"
                    :collapse="isCollapse">

                    <!-- 菜单头部 - 优化收起状态 -->
                    <div class="menu-header" @click="toggleCollapse">
                        <i class="el-icon-s-fold" v-if="!isCollapse"></i>
                        <i class="el-icon-s-unfold" v-else></i>
                        <span v-if="!isCollapse" class="menu-header-text">收起菜单</span>
                    </div>

                    <!-- 菜单项保持不变 -->
                    <el-menu-item index="1">
                        <i class="el-icon-s-shop"></i>
                        <span slot="title">我的店铺</span>
                    </el-menu-item>

                    <el-submenu index="2">
                        <template slot="title">
                            <i class="el-icon-s-order"></i>
                            <span>订单管理</span>
                        </template>
                        <el-menu-item-group>
                            <el-menu-item index="3"><i class="el-icon-finished"></i> 已完成订单</el-menu-item>
                            <el-menu-item index="4"><i class="el-icon-truck"></i> 已发货订单</el-menu-item>
                            <el-menu-item index="5"><i class="el-icon-clock"></i> 未发货订单</el-menu-item>
                        </el-menu-item-group>
                    </el-submenu>

                    <el-menu-item index="6">
                        <i class="el-icon-s-data"></i>
                        <span slot="title">销售统计</span>
                    </el-menu-item>
                </el-menu>
            </div>

            <!-- 主内容区域 -->
            <div class="content-main" :class="{ 'content-expanded': isCollapse }">
                <!-- 内容区域保持不变 -->
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
                    <!-- 动态加载子组件 -->
                    <component
                        v-if="userInfoReady"
                        :is="currentComponent"
                        :currentUser="currentUser"
                        :active="active"
                        ref="currentComponentRef"
                        @show-profile-dialog="showProfileDialog"
                        @show-store-dialog="showStoreDialog"
                        @show-dish-dialog="showDishDialog"
                        @show-image-preview="showImagePreview"
                        @shop-selected="handleShopSelected">
                    </component>
                    <div v-else class="loading-user">
                        <el-skeleton :rows="5" animated />
                        <el-alert title="正在加载用户信息..." type="info" :closable="false" center show-icon style="margin-top: 20px;"></el-alert>
                    </div>
                </div>
            </div>
        </div>

        <!-- 添加回弹窗组件 -->
        <ProfileDialog
            :visible="profileDialogVisible"
            :form-data="storeAdminForm"
            @close="profileDialogVisible = false"
            @save="saveStoreAdminProfile" />

        <StoreDialog
            :visible="storeDialogVisible"
            :form-data="storeForm"
            :username="currentUser.username"
            @close="storeDialogVisible = false"
            @save="saveStoreInfo"
            @refresh="handleStoreRefresh"
            @preview-image="showImagePreview" />

        <DishDialog
            :visible="editDishDialogVisible"
            :form-data="editDishForm"
            :shopId="currentShopId"
            @close="editDishDialogVisible = false"
            @save="saveDishEdit"
            @refresh="handleDishRefresh"
            @preview-image="showImagePreview" />

        <ImagePreview
            :visible="imagePreviewVisible"
            :image-url="previewImageUrl"
            @close="imagePreviewVisible = false" />
    </div>
</template>

<script>
import StoreShop from './StoreShop.vue'
import StoreOrder from './StoreOrder.vue'
import StoreAnalysis from './StoreAnalysis.vue'
import ProfileDialog from './dialogs/ProfileDialog.vue'
import StoreDialog from './dialogs/StoreDialog.vue'
import DishDialog from './dialogs/DishDialog.vue'
import ImagePreview from './dialogs/ImagePreview.vue'

export default {
    name: 'StoreManage',
    components: {
        StoreShop,
        StoreOrder,
        StoreAnalysis,
        ProfileDialog,
        StoreDialog,
        DishDialog,
        ImagePreview
    },
    data() {
        return {
            userInfoReady: false,
            active: '1',
            isCollapse: false,
            currentTime: '',
            timer: null,
            currentUser: {
                username: '',
                role: 0,
                id: null
            },
            currentShopId: null, // 当前选中的店铺ID
            // 弹窗控制
            profileDialogVisible: false,
            storeDialogVisible: false,
            editDishDialogVisible: false,
            imagePreviewVisible: false,
            // 表单数据
            storeAdminForm: {
                real_name: '',
                sex: '',
                age: null,
                mail: '',
                phone: '',
                user_name: ''
            },
            storeForm: {
                shop_name: '',
                description: '',
                status: true,
                image_url: ''
            },
            editDishForm: {
                dish_id: null,
                dish_name: '',
                price: 0,
                description: '',
                image_url: '',
                sort_order: 0,
                status: true
            },
            previewImageUrl: ''
        }
    },
    computed: {
        currentPageTitle() {
            const titles = {
                '1': '我的店铺',
                '3': '订单管理 - 已完成订单',
                '4': '订单管理 - 已发货订单',
                '5': '订单管理 - 未发货订单',
                '6': '销售统计'
            };
            return titles[this.active] || '商家管理系统';
        },
        welcomeMessage() {
            const hour = new Date().getHours();
            if (hour < 6) return '夜深了，商家辛苦了';
            if (hour < 12) return '早上好！开始今天的营业吧';
            if (hour < 18) return '下午好！生意兴隆';
            return '晚上好！感谢您今天的辛勤工作';
        },
        currentComponent() {
            const componentMap = {
                '1': 'StoreShop',
                '3': 'StoreOrder',
                '4': 'StoreOrder',
                '5': 'StoreOrder',
                '6': 'StoreAnalysis'
            };
            return componentMap[this.active] || 'StoreShop';
        }
    },
    mounted() {
        this.updateTime()
        this.timer = setInterval(this.updateTime, 1000)
        this.loadUserInfo()
    },
    beforeDestroy() {
        if (this.timer) clearInterval(this.timer);
    },
    methods: {
        loadUserInfo() {
            const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
            const token = localStorage.getItem('token')

            if (!userInfo.username && token) {
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]))
                    if (payload.data && payload.data.username) {
                        userInfo.username = payload.data.username
                        userInfo.id = payload.data.id
                        userInfo.role = payload.data.role
                        userInfo.is_super = payload.data.is_super
                        localStorage.setItem('userInfo', JSON.stringify(userInfo))
                    }
                } catch (error) {
                    console.error('解析JWT token失败:', error)
                }
            }

            this.currentUser = {
                username: userInfo.username || '商家',
                role: userInfo.role || 0,
                is_super: userInfo.is_super || 0,
                id: userInfo.id || null
            }

            // 设置用户信息就绪标志
            this.userInfoReady = !!this.currentUser.username;

            console.log('用户信息加载完成:', this.currentUser);
        },
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
                this.loadStoreAdminProfile();
            }
        },
        updateTime() {
            const now = new Date();
            this.currentTime = now.toLocaleString('zh-CN', {
                year: 'numeric', month: 'long', day: 'numeric', weekday: 'long',
                hour: '2-digit', minute: '2-digit', second: '2-digit'
            });
        },
        // 店铺选择事件处理
        handleShopSelected(shopId) {
            this.currentShopId = shopId;
            console.log('当前选中店铺ID:', this.currentShopId);
        },
        // 弹窗显示方法
        showProfileDialog() {
            this.profileDialogVisible = true;
        },
        showStoreDialog(storeData) {
            this.storeForm = storeData || {
                shop_name: '',
                description: '',
                status: true,
                image_url: '/images/shop/default-shop.jpg'
            };
            this.storeDialogVisible = true;
        },
        showDishDialog(dishData) {
            this.editDishForm = dishData || {
                dish_id: null,
                dish_name: '',
                price: 0,
                description: '',
                image_url: '/images/dish/default-dish.jpg',
                sort_order: 0,
                status: true
            };
            this.editDishDialogVisible = true;
        },
        showImagePreview(url) {
            this.previewImageUrl = url;
            this.imagePreviewVisible = true;
        },
        // 数据保存方法
        async saveStoreAdminProfile(formData) {
            try {
                await this.$axios.post('/api/manage/admininfo', formData)
                this.$message.success('商家信息保存成功！');
                this.profileDialogVisible = false;
            } catch (error) {
                this.$message.error('保存失败');
            }
        },
        async saveStoreInfo(storeData) {
            try {
                if (storeData.shop_id) {
                    await this.$axios.put(`/api/shop/${storeData.shop_id}/owner/${this.currentUser.username}`, storeData)
                    this.$message.success('店铺信息更新成功！');
                } else {
                    await this.$axios.post(`/api/shop/owner/${this.currentUser.username}`, storeData)
                    this.$message.success('店铺创建成功！');
                }
                this.storeDialogVisible = false;
                // 通知店铺管理组件刷新数据
                if (this.$refs.currentComponentRef && this.$refs.currentComponentRef.loadShopData) {
                    this.$refs.currentComponentRef.loadShopData();
                }
            } catch (error) {
                console.error('保存店铺失败:', error);
                this.$message.error('操作失败');
            }
        },
        async saveDishEdit(dishData) {
            try {
                if (dishData.dish_id) {
                    // 编辑菜品 - 使用 FormData 格式提交
                    const formData = new FormData();
                    for (const key in dishData) {
                        if (dishData[key] !== null && dishData[key] !== undefined) {
                            formData.append(key, dishData[key]);
                        }
                    }
                    await this.$axios.put(`/api/dishes/${dishData.dish_id}`, formData, {
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        }
                    });
                    this.$message.success('菜品更新成功');
                } else {
                    // 添加菜品 - 使用 FormData 格式提交
                    const formData = new FormData();
                    formData.append('shop_id', this.currentShopId);
                    formData.append('dish_name', dishData.dish_name);
                    formData.append('price', dishData.price);
                    formData.append('description', dishData.description || '');
                    formData.append('sort_order', dishData.sort_order || 0);
                    formData.append('status', dishData.status ? 1 : 0);

                    await this.$axios.post('/api/dishes', formData, {
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        }
                    });
                    this.$message.success('菜品添加成功');
                }
                this.editDishDialogVisible = false;
                // 通知店铺管理组件刷新菜品数据
                if (this.$refs.currentComponentRef && this.$refs.currentComponentRef.loadDishes) {
                    this.$refs.currentComponentRef.loadDishes();
                }
            } catch (error) {
                console.error('保存菜品失败:', error);
                this.$message.error('操作失败');
            }
        },
        // 刷新处理方法
        handleStoreRefresh() {
            if (this.$refs.currentComponentRef && this.$refs.currentComponentRef.loadShopData) {
                this.$refs.currentComponentRef.loadShopData();
            }
        },
        handleDishRefresh() {
            if (this.$refs.currentComponentRef && this.$refs.currentComponentRef.loadDishes) {
                this.$refs.currentComponentRef.loadDishes();
            }
        },
        loadStoreAdminProfile() {
            this.$axios.get('/api/manage/admininfo').then(res => {
                if (res.data.status === 200) {
                    this.storeAdminForm = {
                        ...res.data.data,
                        user_name: this.currentUser.username
                    };
                }
            });
        }
    }
}
</script>


<style scoped>
/* 基础样式保持不变 */
.app-container {
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.header {
    background: #2c3e50;
    color: white;
    padding: 0 20px;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 60px;
}

.logo {
    display: flex;
    align-items: center;
    font-size: 18px;
    font-weight: bold;
}

.logo i {
    font-size: 24px;
    margin-right: 10px;
}

.user-info .el-dropdown-link {
    display: flex;
    align-items: center;
    color: white;
    cursor: pointer;
}

.username {
    margin: 0 8px;
}

.main-body {
    display: flex;
    flex: 1;
    overflow: hidden;
}

/* 关键修改：侧边栏样式 */
.sidebar {
    width: 200px;
    background: linear-gradient(to bottom, #1e2a3a, #2c3e50);
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.2);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 999;
    flex-shrink: 0;
    overflow: hidden;
}

/* 收起状态 - 只显示很窄的图标栏 */
.sidebar.sidebar-collapsed {
    width: 64px;
}

/* 菜单头部样式优化 */
.menu-header {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    color: #b7c4cc;
    cursor: pointer;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
    padding: 0 20px;
    background: rgba(0, 0, 0, 0.2);
}

.menu-header:hover {
    background: rgba(64, 158, 255, 0.2);
    color: #409EFF;
}

.menu-header i {
    font-size: 18px;
    margin-right: 10px;
    transition: all 0.3s ease;
}

.menu-header-text {
    font-size: 14px;
    transition: opacity 0.3s ease;
}

/* 收起状态下菜单头部样式 */
.sidebar.sidebar-collapsed .menu-header {
    justify-content: center;
    padding: 0;
}

.sidebar.sidebar-collapsed .menu-header-text {
    display: none;
}

.sidebar.sidebar-collapsed .menu-header i {
    margin-right: 0;
    font-size: 20px;
}

/* 菜单项样式优化 */
.el-menu-vertical-demo {
    border-right: none !important;
    background: transparent !important;
}

.el-menu-item,
.el-submenu__title {
    height: 50px !important;
    line-height: 50px !important;
    transition: all 0.3s ease;
}

.el-menu-item i,
.el-submenu__title i {
    margin-right: 12px;
    font-size: 18px;
}

/* 收起状态下菜单项样式 */
.sidebar.sidebar-collapsed .el-menu-item,
.sidebar.sidebar-collapsed .el-submenu__title {
    text-align: center;
    padding: 0 !important;
}

.sidebar.sidebar-collapsed .el-menu-item i,
.sidebar.sidebar-collapsed .el-submenu__title i {
    margin-right: 0;
    font-size: 20px;
}

.sidebar.sidebar-collapsed .el-submenu__icon-arrow {
    display: none;
}

/* 主内容区域调整 */
.content-main {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    transition: all 0.3s ease;
    margin-left: 0;
}

/* 侧边栏收起时，主内容区域可以更宽 */
.content-main.content-expanded {
    margin-left: 0;
}

.content-header {
    background: white;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.welcome-text h2 {
    margin: 0 0 8px 0;
    color: #2c3e50;
    font-size: 22px;
    font-weight: 600;
}

.welcome-text p {
    color: #7f8c8d;
    margin: 0;
    font-size: 14px;
}

.content-body {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    min-height: calc(100vh - 200px);
}

.loading-user {
    padding: 20px;
    text-align: center;
}

/* 确保菜单项在收起状态下的tooltip正常显示 */
.el-menu--collapse .el-menu-item span,
.el-menu--collapse .el-submenu__title span {
    display: none;
}

/* 滚动条美化 */
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
</style>