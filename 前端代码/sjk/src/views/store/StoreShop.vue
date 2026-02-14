<template>
    <div class="store-management">
        <!-- 顶部操作栏 -->
        <div class="store-actions-header">
            <div class="header-left">
                <h2>店铺管理</h2>
                <p class="subtitle">管理您的店铺和菜单</p>
            </div>
            <div class="header-right">
                <el-button
                    type="primary"
                    icon="el-icon-plus"
                    @click="createStore"
                    size="medium">
                    创建新店铺
                </el-button>
            </div>
        </div>

        <!-- 店铺选择器 -->
        <div class="store-selector-section" v-if="stores.length > 0">
            <div class="section-title">
                <i class="el-icon-s-shop"></i>
                <span>我的店铺</span>
                <el-tag type="info" size="small">{{ stores.length }}个店铺</el-tag>
            </div>

            <div class="store-cards">
                <el-card
                    v-for="store in stores"
                    :key="store.shop_id"
                    class="store-card"
                    :class="{ 'active-store': currentStore && currentStore.shop_id === store.shop_id }"
                    @click.native="selectStore(store)">
                    <div class="store-card-content">
                        <div class="store-avatar">
                            <el-avatar
                                :size="60"
                                :src="store.image_url"
                                :icon="store.image_url ? '' : 'el-icon-s-shop'"
                                shape="square">
                            </el-avatar>
                        </div>
                        <div class="store-info">
                            <h4 class="store-name">{{ store.shop_name }}</h4>
                            <p class="store-desc" :title="store.description">
                                {{ store.description || '暂无描述' }}
                            </p>
                            <div class="store-meta">
                                <span class="create-time">
                                    <i class="el-icon-time"></i>
                                    {{ formatTime(store.created_time) }}
                                </span>
                                <el-tag
                                    :type="store.status ? 'success' : 'danger'"
                                    size="mini">
                                    {{ store.status ? '营业中' : '已打烊' }}
                                </el-tag>
                            </div>
                        </div>
                        <div class="store-actions">
                            <el-button
                                size="mini"
                                icon="el-icon-edit"
                                @click.stop="editStoreInfo(store)"
                                class="edit-btn">
                                编辑
                            </el-button>
                            <el-button
                                size="mini"
                                icon="el-icon-delete"
                                type="danger"
                                @click.stop="deleteStore(store)"
                                class="delete-btn">
                                删除
                            </el-button>
                        </div>
                    </div>
                </el-card>

                <!-- 添加新店铺卡片 -->
                <el-card class="store-card add-store-card" @click.native="createStore">
                    <div class="add-store-content">
                        <i class="el-icon-plus" style="font-size: 32px; color: #c0c4cc; margin-bottom: 8px;"></i>
                        <p>添加新店铺</p>
                    </div>
                </el-card>
            </div>
        </div>

        <!-- 没有店铺的提示 -->
        <el-card v-if="!hasShop && stores.length === 0" class="empty-store-card">
            <div class="empty-store">
                <i class="el-icon-s-shop" style="font-size: 64px; color: #c0c4cc; margin-bottom: 16px;"></i>
                <h3>您还没有创建店铺</h3>
                <p style="color: #909399; margin-bottom: 20px;">创建您的第一个店铺开始营业吧</p>
                <el-button type="primary" icon="el-icon-plus" size="medium" @click="createStore">
                    立即创建店铺
                </el-button>
            </div>
        </el-card>

        <!-- 菜单管理 -->
        <div class="menu-management" v-if="currentStore && currentStore.shop_id">
            <div class="section-header">
                <div class="section-title">
                    <i class="el-icon-menu"></i>
                    <span>菜单管理 - {{ currentStore.shop_name }}</span>
                </div>
                <el-button
                    type="primary"
                    icon="el-icon-plus"
                    @click="addMenuItem"
                    size="medium">
                    添加菜品
                </el-button>
            </div>

            <el-table
                :data="menuItems"
                style="width: 100%"
                v-loading="loading"
                class="menu-table"
                empty-text="暂无菜品，请添加菜品">
                <el-table-column label="菜品图片" width="100" align="center">
                    <template slot-scope="scope">
                        <el-avatar
                            :size="50"
                            :src="scope.row.image_url"
                            :icon="scope.row.image_url ? '' : 'el-icon-picture'"
                            shape="square"
                            @click.native="previewImage(scope.row.image_url)"
                            style="cursor: pointer;">
                        </el-avatar>
                    </template>
                </el-table-column>
                <el-table-column prop="dish_name" label="菜品名称" width="180"></el-table-column>
                <el-table-column prop="price" label="价格" width="100" align="center">
                    <template slot-scope="scope">
                        <span class="price-text">¥{{ scope.row.price }}</span>
                    </template>
                </el-table-column>
                <el-table-column prop="monthly_sales" label="月销量" width="100" align="center">
                    <template slot-scope="scope">
                        <span class="sales-text">{{ scope.row.monthly_sales }}</span>
                    </template>
                </el-table-column>
                <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip></el-table-column>
                <el-table-column prop="sort_order" label="排序" width="80" align="center">
                    <template slot-scope="scope">
                        <span class="sort-text">{{ scope.row.sort_order }}</span>
                    </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="100" align="center">
                    <template slot-scope="scope">
                        <el-tag :type="scope.row.status ? 'success' : 'danger'" size="small">
                            {{ scope.row.status ? '上架' : '下架' }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="200" align="center" fixed="right">
                    <template slot-scope="scope">
                        <el-button
                            size="mini"
                            icon="el-icon-edit"
                            @click="editMenuItem(scope.row)"
                            class="edit-btn">
                            编辑
                        </el-button>
                        <el-button
                            size="mini"
                            icon="el-icon-delete"
                            type="danger"
                            @click="deleteMenuItem(scope.row)"
                            class="delete-btn">
                            删除
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 空状态 -->
            <div v-if="menuItems.length === 0 && !loading" class="empty-menu">
                <i class="el-icon-dish" style="font-size: 48px; color: #c0c4cc; margin-bottom: 16px;"></i>
                <p>暂无菜品，请添加菜品开始营业</p>
                <el-button type="primary" icon="el-icon-plus" @click="addMenuItem">
                    添加第一个菜品
                </el-button>
            </div>
        </div>

        <!-- 店铺对话框 -->
        <store-dialog
            :visible="storeDialogVisible"
            :formData="storeFormData"
            :username="currentUser.username"
            @close="handleStoreDialogClose"
            @refresh="handleStoreRefresh"
        />
    </div>
</template>

<script>
import StoreDialog from './dialogs/StoreDialog.vue'

export default {
    name: 'StoreShop',
    components: {
        StoreDialog
    },
    props: {
        currentUser: {
            type: Object,
            required: true,
            default: () => ({ username: '' })
        }
    },
    data() {
        return {
            stores: [],
            currentStore: null,
            hasShop: false,
            menuItems: [],
            loading: false,
            // 店铺对话框相关
            storeDialogVisible: false,
            storeFormData: {
                shop_name: '',
                description: '',
                status: true,
                image_url: '/images/shop/default-shop.jpg'
            }
        }
    },
    mounted() {
        this.loadShopData();
    },
    methods: {
        async loadShopData() {
            try {
                this.loading = true;
                console.log('开始加载店铺数据，用户名:', this.currentUser.username);

                const shopRes = await this.$axios.get(`/api/shop/owner/${this.currentUser.username}`);
                console.log('店铺API响应:', shopRes.data);

                if (shopRes.data.status === 200) {
                    this.stores = shopRes.data.data;
                    if (Array.isArray(this.stores) && this.stores.length > 0) {
                        this.currentStore = this.stores[0];
                        this.hasShop = true;
                        this.loadDishes();
                        // 通知父组件当前选中的店铺
                        this.$emit('shop-selected', this.currentStore.shop_id);
                    } else {
                        this.currentStore = null;
                        this.hasShop = false;
                        this.menuItems = [];
                        this.$emit('shop-selected', null);
                    }
                } else if (shopRes.data.status === 404) {
                    this.stores = [];
                    this.currentStore = null;
                    this.hasShop = false;
                    this.menuItems = [];
                    this.$emit('shop-selected', null);
                }
            } catch (error) {
                console.error('加载店铺信息失败:', error);
                this.$message.error('加载店铺信息失败');
            } finally {
                this.loading = false;
            }
        },
        async loadDishes() {
            if (!this.currentStore || !this.currentStore.shop_id) {
                this.menuItems = [];
                return;
            }

            try {
                this.loading = true;
                const res = await this.$axios.get(`/api/dishes/shop/${this.currentStore.shop_id}`);
                if (res.data.status === 200) {
                    this.menuItems = res.data.data;
                } else if (res.data.status === 404) {
                    this.menuItems = [];
                }
            } catch (error) {
                console.error('加载菜品失败:', error);
                this.$message.error('加载菜品失败');
            } finally {
                this.loading = false;
            }
        },
        selectStore(store) {
            this.currentStore = store;
            this.loadDishes();
            this.$emit('shop-selected', store.shop_id);
        },

        formatTime(timeStr) {
            if (!timeStr) return '未知';
            return timeStr.split(' ')[0]; // 只显示日期部分
        },
        createStore() {
            this.storeFormData = {
                shop_name: '',
                description: '',
                status: true,
                image_url: '/images/shop/default-shop.jpg'
            };
            this.storeDialogVisible = true;
        },
        editStoreInfo(store) {
            this.storeFormData = {
                ...store,
                status: store.status === 1 || store.status === true
            };
            this.storeDialogVisible = true;
        },
        deleteStore(store) {
            this.$confirm(`确定要删除店铺 "${store.shop_name}" 吗？此操作将删除店铺所有菜品且不可恢复！`, '警告', {
                type: 'warning',
                confirmButtonText: '确定删除',
                cancelButtonText: '取消',
                confirmButtonClass: 'el-button--danger'
            }).then(async () => {
                try {
                    const res = await this.$axios.delete(`/api/shop/${store.shop_id}/owner/${this.currentUser.username}`);
                    if (res.data.status === 200) {
                        this.$message.success('店铺删除成功');
                        this.loadShopData();
                    } else {
                        this.$message.error(res.data.msg || '删除失败');
                    }
                } catch (error) {
                    console.error('删除店铺失败:', error);
                    this.$message.error('删除店铺失败');
                }
            });
        },
        addMenuItem() {
            if (!this.currentStore || !this.currentStore.shop_id) {
                this.$message.warning('请先选择店铺');
                return;
            }
            this.$emit('show-dish-dialog');
        },
        editMenuItem(item) {
            this.$emit('show-dish-dialog', {
                dish_id: item.dish_id,
                dish_name: item.dish_name,
                price: parseFloat(item.price),
                description: item.description || '',
                image_url: item.image_url || '/images/dish/default-dish.jpg',
                sort_order: item.sort_order || 0,
                status: Boolean(item.status)
            });
        },
        deleteMenuItem(item) {
            this.$confirm(`确定要删除菜品 "${item.dish_name}" 吗？此操作不可恢复！`, '警告', {
                type: 'warning',
                confirmButtonText: '确定删除',
                cancelButtonText: '取消',
                confirmButtonClass: 'el-button--danger'
            }).then(async () => {
                try {
                    const res = await this.$axios.delete(`/api/dishes/${item.dish_id}`);
                    if (res.data.status === 200) {
                        this.$message.success('菜品删除成功');
                        this.loadDishes();
                    } else {
                        this.$message.error(res.data.msg || '删除失败');
                    }
                } catch (error) {
                    console.error('删除菜品失败:', error);
                    this.$message.error('删除菜品失败');
                }
            });
        },
        previewImage(url) {
            if (url) {
                this.$emit('show-image-preview', url);
            }
        },
        // 店铺对话框相关方法
        handleStoreDialogClose() {
            this.storeDialogVisible = false;
        },
        handleStoreRefresh() {
            this.loadShopData();
        }
    }
}
</script>

<style scoped>
/* 样式保持不变 */
.store-management {
    padding: 20px;
    background: #f5f7fa;
    min-height: 100vh;
}

/* 顶部操作栏 */
.store-actions-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding: 24px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-left h2 {
    margin: 0 0 8px 0;
    font-size: 24px;
    color: #2c3e50;
}

.header-left .subtitle {
    margin: 0;
    color: #909399;
    font-size: 14px;
}

/* 店铺选择器区域 */
.store-selector-section {
    margin-bottom: 24px;
}

.section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    font-size: 16px;
    font-weight: 600;
    color: #2c3e50;
}

.section-title i {
    font-size: 18px;
}

/* 店铺卡片布局 */
.store-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
}

.store-card {
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2px solid transparent;
}

.store-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.active-store {
    border-color: #409eff;
    background-color: #f0f9ff;
}

.store-card-content {
    display: flex;
    align-items: flex-start;
    gap: 16px;
}

.store-info {
    flex: 1;
    min-width: 0;
}

.store-name {
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 600;
    color: #2c3e50;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.store-desc {
    margin: 0 0 12px 0;
    color: #606266;
    font-size: 13px;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.store-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.create-time {
    font-size: 12px;
    color: #909399;
}

.store-actions {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

/* 添加新店铺卡片 */
.add-store-card {
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px dashed #dcdfe6;
    background-color: #fafafa;
}

.add-store-card:hover {
    border-color: #409eff;
    background-color: #f0f9ff;
}

.add-store-content {
    text-align: center;
    color: #909399;
    padding: 20px;
}

.add-store-content p {
    margin: 0;
    font-size: 14px;
}

/* 空状态 */
.empty-store-card {
    text-align: center;
    padding: 60px 40px;
    margin-bottom: 24px;
}

.empty-store h3 {
    margin: 0 0 8px 0;
    color: #303133;
}

/* 菜单管理 */
.menu-management {
    background: white;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.menu-table {
    border-radius: 4px;
    overflow: hidden;
}

.price-text {
    color: #ff6b35;
    font-weight: 600;
}

.sales-text {
    color: #67c23a;
    font-weight: 500;
}

.sort-text {
    color: #909399;
}

.empty-menu {
    text-align: center;
    padding: 40px;
    color: #909399;
}

/* 按钮样式 */
.edit-btn {
    color: #409eff;
    border-color: #409eff;
}

.edit-btn:hover {
    background-color: #ecf5ff;
}

.delete-btn {
    color: #f56c6c;
    border-color: #f56c6c;
}

.delete-btn:hover {
    background-color: #fef0f0;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .store-actions-header {
        flex-direction: column;
        gap: 16px;
        text-align: center;
    }

    .store-cards {
        grid-template-columns: 1fr;
    }

    .store-card-content {
        flex-direction: column;
        text-align: center;
    }

    .store-actions {
        flex-direction: row;
        justify-content: center;
    }

    .section-header {
        flex-direction: column;
        gap: 16px;
        align-items: stretch;
    }
}

/* 快速修复 - 添加到现有样式的最后 */
::v-deep .delete-btn.el-button--danger {
    background: white !important;
    border-color: #f56c6c !important;
    color: #f56c6c !important;
}

::v-deep .delete-btn.el-button--danger:hover {
    background: #f56c6c !important;
    color: white !important;
}
</style>