<template>
    <div class="order-management">
        <div class="header">
            <h2>{{ orderTypeText }}</h2>
            <p class="subtitle">{{ orderSubtitle }}</p>
        </div>

        <div class="content-body">
            <!-- 订单统计 -->
            <div class="order-stats">
                <el-row :gutter="20">
                    <el-col :span="6">
                        <div class="stat-card">
                            <div class="stat-icon total">
                                <i class="el-icon-s-order"></i>
                            </div>
                            <div class="stat-info">
                                <div class="stat-value">{{ allOrders.length }}</div>
                                <div class="stat-label">总订单数</div>
                            </div>
                        </div>
                    </el-col>
                    <el-col :span="6">
                        <div class="stat-card">
                            <div class="stat-icon pending">
                                <i class="el-icon-time"></i>
                            </div>
                            <div class="stat-info">
                                <div class="stat-value">{{ pendingOrders.length }}</div>
                                <div class="stat-label">待发货</div>
                            </div>
                        </div>
                    </el-col>
                    <el-col :span="6">
                        <div class="stat-card">
                            <div class="stat-icon shipping">
                                <i class="el-icon-truck"></i>
                            </div>
                            <div class="stat-info">
                                <div class="stat-value">{{ shippingOrders.length }}</div>
                                <div class="stat-label">配送中</div>
                            </div>
                        </div>
                    </el-col>
                    <el-col :span="6">
                        <div class="stat-card">
                            <div class="stat-icon completed">
                                <i class="el-icon-circle-check"></i>
                            </div>
                            <div class="stat-info">
                                <div class="stat-value">{{ completedOrders.length }}</div>
                                <div class="stat-label">已完成</div>
                            </div>
                        </div>
                    </el-col>
                </el-row>
            </div>

            <div class="table-container">
                <el-table
                    :data="filteredOrders"
                    style="width: 100%"
                    class="order-table"
                    v-loading="loading"
                    empty-text="暂无订单数据">

                    <!-- 订单号 -->
                    <el-table-column label="订单号" width="100" align="center">
                        <template slot-scope="scope">
                            <span class="order-id">#{{ scope.row.order_id }}</span>
                        </template>
                    </el-table-column>

                    <!-- 店铺信息 -->
                    <el-table-column label="店铺" width="160" align="center">
                        <template slot-scope="scope">
                            <div class="shop-info">
                                <el-avatar
                                    :src="getShopImage(scope.row.shop_id)"
                                    :size="36"
                                    shape="square">
                                </el-avatar>
                                <span class="shop-name">{{ scope.row.shop_name }}</span>
                            </div>
                        </template>
                    </el-table-column>

                    <!-- 菜品详情 -->
                    <el-table-column label="菜品详情" min-width="200" align="center">
                        <template slot-scope="scope">
                            <div class="dish-details">
                                <div
                                    v-for="item in scope.row.orderDetails"
                                    :key="item.dish_id"
                                    class="dish-item">
                                    <span class="dish-name">{{ item.dish_name }}</span>
                                    <span class="dish-quantity">×{{ item.quantity }}</span>
                                    <span class="dish-price">¥{{ item.price }}</span>
                                </div>
                                <div v-if="!scope.row.orderDetails || scope.row.orderDetails.length === 0" class="no-dishes">
                                    无菜品信息
                                </div>
                            </div>
                        </template>
                    </el-table-column>

                    <!-- 订单金额 -->
                    <el-table-column label="订单价格" width="100" align="center">
                        <template slot-scope="scope">
                            <span class="price">¥{{ scope.row.order_money }}</span>
                        </template>
                    </el-table-column>

                    <!-- 下单时间 -->
                    <el-table-column
                        prop="create_time"
                        label="下单时间"
                        width="180"
                        align="center">
                    </el-table-column>

                    <!-- 订餐方式 -->
                    <el-table-column
                        prop="order_way"
                        label="订餐方式"
                        width="120"
                        align="center">
                        <template slot-scope="scope">
                            <el-tag
                                :type="scope.row.order_way === '网上订餐' ? 'success' : 'primary'"
                                size="small">
                                {{ scope.row.order_way }}
                            </el-tag>
                        </template>
                    </el-table-column>

                    <!-- 收货人信息 -->
                    <el-table-column label="收货人信息" width="150" align="center">
                        <template slot-scope="scope">
                            <div class="consignee-info">
                                <div class="cons-name">{{ scope.row.cons_name }}</div>
                                <div class="cons-phone">{{ scope.row.cons_phone }}</div>
                            </div>
                        </template>
                    </el-table-column>

                    <!-- 收货地址 -->
                    <el-table-column
                        prop="cons_addre"
                        label="收货地址"
                        width="180"
                        align="center"
                        show-overflow-tooltip>
                    </el-table-column>

                    <!-- 配送员信息（仅配送中和已完成订单显示） -->
                    <el-table-column
                        v-if="active === '4' || active === '3'"
                        label="配送员"
                        width="150"
                        align="center">
                        <template slot-scope="scope">
                            <div v-if="scope.row.deliveryInfo" class="dispatcher-info">
                                <div class="disp-name">{{ scope.row.deliveryInfo.dispatcher_name }}</div>
                                <div class="disp-id">ID: {{ scope.row.deliveryInfo.disp_id }}</div>
                            </div>
                            <div v-else class="no-dispatcher">未分配</div>
                        </template>
                    </el-table-column>

                    <!-- 配送员电话（仅配送中和已完成订单显示） -->
                    <el-table-column
                        v-if="active === '4' || active === '3'"
                        label="配送员电话"
                        width="150"
                        align="center">
                        <template slot-scope="scope">
                            <span v-if="scope.row.deliveryInfo">{{ scope.row.deliveryInfo.dispatcher_phone }}</span>
                            <span v-else>-</span>
                        </template>
                    </el-table-column>

                    <!-- 预计送达时间（仅配送中订单显示） -->
                    <el-table-column
                        v-if="active === '4'"
                        label="预计送达"
                        width="180"
                        align="center">
                        <template slot-scope="scope">
                            <span v-if="scope.row.deliveryInfo">{{ scope.row.deliveryInfo.deliver_time }}</span>
                            <span v-else>-</span>
                        </template>
                    </el-table-column>

                    <!-- 操作 -->
                    <el-table-column
                        label="操作"
                        width="200"
                        align="center"
                        fixed="right">
                        <template slot-scope="scope">
                            <el-button
                                type="text"
                                size="small"
                                @click="viewOrderDetail(scope.row)"
                                class="action-btn">
                                <i class="el-icon-view"></i> 订单详情
                            </el-button>

                            <!-- 待发货订单操作 -->
                            <template v-if="active === '5'">
                                <el-button
                                    type="text"
                                    size="small"
                                    @click="prepareOrder(scope.row)"
                                    class="action-btn"
                                    :disabled="scope.row.preparing">
                                    <i class="el-icon-knife-fork"></i> {{ scope.row.preparing ? '备餐中' : '开始备餐' }}
                                </el-button>
                                <el-button
                                    type="text"
                                    size="small"
                                    @click="showShipDialog(scope.row)"
                                    class="action-btn confirm-btn"
                                    :disabled="!scope.row.preparing">
                                    <i class="el-icon-ship"></i> 发货
                                </el-button>
                            </template>

                            <!-- 配送中订单操作 -->
                            <el-button
                                v-if="active === '4'"
                                type="text"
                                size="small"
                                @click="markAsDelivered(scope.row)"
                                class="action-btn confirm-btn"
                                :loading="scope.row.confirming">
                                <i class="el-icon-circle-check"></i> 确认送达
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <!-- 分页组件 -->
            <div class="pagination-container" v-if="filteredOrders.length > 0">
                <el-pagination
                    background
                    layout="prev, pager, next"
                    :total="filteredOrders.length"
                    :page-size="pageSize"
                    @current-change="handlePageChange">
                </el-pagination>
            </div>
        </div>

        <!-- 发货对话框 -->
        <el-dialog title="发货设置" :visible.sync="shipDialogVisible" width="400px">
            <el-form :model="shipForm" label-width="80px">
                <el-form-item label="配送员">
                    <el-select v-model="shipForm.disp_id" placeholder="请选择配送员" style="width: 100%">
                        <el-option
                            v-for="dispatcher in dispatchers"
                            :key="dispatcher.dispatcher_id"
                            :label="`${dispatcher.dispatcher_name} (${dispatcher.dispatcher_phone})`"
                            :value="dispatcher.dispatcher_id">
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="预计时间">
                    <el-input v-model="shipForm.deliver_time" placeholder="例如：30分钟"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer">
                <el-button @click="shipDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="shipOrder" :loading="shipping">确认发货</el-button>
            </div>
        </el-dialog>

        <!-- 订单详情对话框 -->
        <el-dialog
            title="订单详情"
            :visible.sync="detailDialogVisible"
            width="600px"
            class="detail-dialog">
            <div v-if="currentOrder" class="order-detail">
                <div class="order-header">
                    <h3>订单号: {{ currentOrder.order_id }}</h3>
                    <el-tag :type="currentOrder.order_way === '网上订餐' ? 'success' : 'primary'">
                        {{ currentOrder.order_way }}
                    </el-tag>
                </div>

                <div class="order-info">
                    <div class="info-section">
                        <h4>店铺信息</h4>
                        <div class="shop-info-detail">
                            <el-avatar
                                :src="getShopImage(currentOrder.shop_id)"
                                :size="50"
                                shape="square">
                            </el-avatar>
                            <span class="shop-name">{{ currentOrder.shop_name }}</span>
                        </div>
                    </div>

                    <div class="info-section">
                        <h4>收货信息</h4>
                        <p><strong>收货人:</strong> {{ currentOrder.cons_name }}</p>
                        <p><strong>联系电话:</strong> {{ currentOrder.cons_phone }}</p>
                        <p><strong>收货地址:</strong> {{ currentOrder.cons_addre }}</p>
                    </div>

                    <div v-if="currentOrder.deliveryInfo" class="info-section">
                        <h4>配送信息</h4>
                        <p><strong>配送员:</strong> {{ currentOrder.deliveryInfo.dispatcher_name }} (ID: {{ currentOrder.deliveryInfo.disp_id }})</p>
                        <p><strong>联系电话:</strong> {{ currentOrder.deliveryInfo.dispatcher_phone }}</p>
                        <p v-if="currentOrder.deliveryInfo.deliver_time"><strong>预计送达:</strong> {{ currentOrder.deliveryInfo.deliver_time }}</p>
                    </div>

                    <div class="info-section">
                        <h4>菜品详情</h4>
                        <div class="dish-list">
                            <div
                                v-for="item in currentOrder.orderDetails"
                                :key="item.dish_id"
                                class="dish-item-detail">
                                <div class="dish-info">
                                    <span class="dish-name">{{ item.dish_name }}</span>
                                    <span class="dish-quantity">×{{ item.quantity }}</span>
                                </div>
                                <div class="dish-price">
                                    ¥{{ item.price }} × {{ item.quantity }} = ¥{{ item.subtotal }}
                                </div>
                            </div>
                        </div>
                        <div class="order-total">
                            <strong>订单总额: ¥{{ currentOrder.order_money }}</strong>
                        </div>
                    </div>
                </div>
            </div>
            <div slot="footer" class="dialog-footer">
                <el-button type="primary" @click="detailDialogVisible = false">关闭</el-button>
            </div>
        </el-dialog>
    </div>
</template>

<script>
export default {
    name: 'StoreOrder',
    props: {
        currentUser: Object,
        active: String
    },
    data() {
        return {
            orders: [],
            allOrders: [],
            loading: false,
            shipping: false,
            shipDialogVisible: false,
            detailDialogVisible: false,
            currentOrder: null,
            orderDetails: [],
            dispatchers: [],
            shipForm: {
                order_id: null,
                disp_id: '',
                deliver_time: '30分钟'
            },
            pageSize: 10,
            currentPage: 1,
            // 新增：存储店铺信息
            shops: [],
            shopImageMap: {}
        }
    },
    computed: {
        orderTypeText() {
            const texts = {
                '3': '已完成订单',
                '4': '配送中订单',
                '5': '待发货订单'
            };
            return texts[this.active] || '订单管理';
        },
        orderSubtitle() {
            const subtitles = {
                '3': '查看已完成的订单记录',
                '4': '查看正在配送中的订单',
                '5': '处理待发货的订单'
            };
            return subtitles[this.active] || '管理您的店铺订单';
        },
        filteredOrders() {
            let filtered = [];
            if (this.active === '3') {
                filtered = this.completedOrders;
            } else if (this.active === '4') {
                filtered = this.shippingOrders;
            } else if (this.active === '5') {
                filtered = this.pendingOrders;
            }

            // 分页处理
            const start = (this.currentPage - 1) * this.pageSize;
            const end = start + this.pageSize;
            return filtered.slice(start, end);
        },
        pendingOrders() {
            return this.allOrders.filter(order => order.checked === 0);
        },
        shippingOrders() {
            return this.allOrders.filter(order => order.checked === 1);
        },
        completedOrders() {
            return this.allOrders.filter(order => order.checked === 2);
        }
    },
    mounted() {
        this.loadShops();
        this.loadOrders();
        this.loadDispatchers();
    },
    methods: {
        // 新增：加载店铺信息
        async loadShops() {
            try {
                const res = await this.$axios.get(`/api/shop/owner/${this.currentUser.username}`);
                if (res.data.status === 200) {
                    this.shops = res.data.data;
                    // 构建店铺图片映射
                    this.buildShopImageMap();
                }
            } catch (error) {
                console.error('加载店铺信息失败:', error);
            }
        },
        // 新增：构建店铺图片映射
        buildShopImageMap() {
            const map = {};
            this.shops.forEach(shop => {
                map[shop.shop_id] = shop.image_url || '/images/shop/default-shop.jpg';
            });
            this.shopImageMap = map;
        },
        async loadOrders() {
            try {
                this.loading = true;
                const res = await this.$axios.get(`/api/orders/shop/owner/${this.currentUser.username}`);
                if (res.data.status === 200) {
                    // 为每个订单添加确认状态和配送信息
                    this.allOrders = await Promise.all(
                        res.data.data.map(async order => ({
                            ...order,
                            preparing: false,
                            confirming: false,
                            deliveryInfo: await this.loadDeliveryInfo(order.order_id),
                            orderDetails: await this.loadOrderDetails(order.order_id)
                        }))
                    );
                } else if (res.data.status === 404) {
                    this.allOrders = [];
                }
            } catch (error) {
                console.error('加载订单失败:', error);
                this.$message.error('加载订单失败');
            } finally {
                this.loading = false;
            }
        },
        async loadDeliveryInfo(orderId) {
            try {
                const res = await this.$axios.get(`/api/orders/${orderId}/delivery`);
                if (res.data.status === 200) {
                    return res.data.data;
                }
                return null;
            } catch (error) {
                console.error('加载配送信息失败:', error);
                return null;
            }
        },
        async loadOrderDetails(orderId) {
            try {
                const res = await this.$axios.get(`/api/orders/${orderId}/details`);
                if (res.data.status === 200) {
                    return res.data.data;
                }
                return [];
            } catch (error) {
                console.error('加载订单详情失败:', error);
                return [];
            }
        },
        async loadDispatchers() {
            try {
                const res = await this.$axios.get('/api/dispatchers');
                if (res.data.status === 200) {
                    this.dispatchers = res.data.data;
                }
            } catch (error) {
                console.error('加载配送员失败:', error);
            }
        },
        // 修改：动态获取店铺图片
        getShopImage(shopId) {
            // 优先从店铺映射中获取，如果没有则使用默认图片
            return this.shopImageMap[shopId] || '/images/shop/default-shop.jpg';
        },
        async viewOrderDetail(order) {
            try {
                this.currentOrder = order;
                this.detailDialogVisible = true;
            } catch (error) {
                console.error('查看订单详情失败:', error);
                this.$message.error('查看订单详情失败');
            }
        },
        prepareOrder(order) {
            this.$set(order, 'preparing', true);
            this.$message.success(`订单 #${order.order_id} 开始备餐`);
        },
        showShipDialog(order) {
            this.shipForm.order_id = order.order_id;
            this.shipDialogVisible = true;
        },
        async shipOrder() {
            if (!this.shipForm.disp_id) {
                this.$message.warning('请选择配送员');
                return;
            }

            try {
                this.shipping = true;
                await this.$axios.post(`/api/orders/${this.shipForm.order_id}/delivery`, this.shipForm);
                this.$message.success('发货成功');
                this.shipDialogVisible = false;
                this.loadOrders(); // 重新加载订单
            } catch (error) {
                console.error('发货失败:', error);
                if (error.response && error.response.data.msg) {
                    this.$message.error(error.response.data.msg);
                } else {
                    this.$message.error('发货失败');
                }
            } finally {
                this.shipping = false;
            }
        },
        async markAsDelivered(order) {
            try {
                this.$set(order, 'confirming', true);
                await this.$confirm('确认订单已送达？', '提示', { type: 'warning' });
                await this.$axios.put(`/api/orders/${order.order_id}/status`, { checked: 2 });
                this.$message.success(`订单 #${order.order_id} 已标记为送达`);
                this.loadOrders(); // 重新加载订单
            } catch (error) {
                if (error !== 'cancel') {
                    console.error('确认送达失败:', error);
                    this.$message.error('确认送达失败');
                }
            } finally {
                this.$set(order, 'confirming', false);
            }
        },
        handlePageChange(page) {
            this.currentPage = page;
        }
    }
}
</script>

<style scoped>
/* 样式保持不变 */
.order-management {
    min-height: 100vh;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 20px;
}

.header {
    background: white;
    color: #333;
    padding: 30px;
    text-align: center;
    border-radius: 12px;
    margin-bottom: 25px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    border: 1px solid #eaeaea;
}

.header h2 {
    margin: 0;
    font-size: 28px;
    font-weight: 700;
    color: #2c3e50;
}

.header .subtitle {
    margin: 10px 0 0 0;
    opacity: 0.9;
    font-size: 16px;
}

.content-body {
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    width: 95%;
    margin: 0 auto;
}

.order-stats {
    padding: 25px;
    border-bottom: 1px solid #f0f0f0;
}

.stat-card {
    display: flex;
    align-items: center;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
    width: 50px;
    height: 50px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;
    font-size: 24px;
    color: white;
}

.stat-icon.total { background: #667eea; }
.stat-icon.pending { background: #f093fb; }
.stat-icon.shipping { background: #4facfe; }
.stat-icon.completed { background: #43e97b; }

.stat-value {
    font-size: 24px;
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 14px;
    color: #7f8c8d;
}

.table-container {
    padding: 20px;
}

.order-table {
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #eaeaea;
}

.order-id {
    font-weight: 600;
    color: #2c3e50;
    font-family: 'Courier New', monospace;
}

.shop-info {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.shop-name {
    font-weight: 500;
    font-size: 14px;
}

.dish-details {
    text-align: left;
}

.dish-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0;
    border-bottom: 1px solid #f0f0f0;
}

.dish-item:last-child {
    border-bottom: none;
}

.dish-name {
    flex: 1;
    font-size: 13px;
}

.dish-quantity {
    color: #666;
    font-size: 12px;
    margin: 0 8px;
}

.dish-price {
    color: #ff6b35;
    font-size: 12px;
    font-weight: 500;
}

.no-dishes {
    color: #999;
    font-style: italic;
    text-align: center;
    font-size: 13px;
}

.consignee-info {
    text-align: center;
}

.cons-name {
    font-weight: 500;
    margin-bottom: 4px;
}

.cons-phone {
    font-size: 12px;
    color: #666;
}

.dispatcher-info {
    text-align: center;
}

.disp-name {
    font-weight: 500;
    margin-bottom: 4px;
}

.disp-id {
    font-size: 12px;
    color: #666;
}

.no-dispatcher {
    color: #999;
    font-style: italic;
}

::v-deep .el-table th {
    background: white;
    color: #333;
    font-weight: 600;
    height: 50px;
    border-bottom: 2px solid #f0f0f0;
    font-size: 14px;
}

::v-deep .el-table td {
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
    color: #666;
}

::v-deep .el-table--enable-row-hover .el-table__body tr:hover>td {
    background-color: #f5f7fa;
}

.price {
    color: #ff6b35;
    font-weight: 600;
    font-size: 14px;
}

.action-btn {
    color: #409eff !important;
    font-weight: 500;
    transition: all 0.2s;
    margin: 0 4px;
}

.action-btn:hover {
    color: #3375b9 !important;
}

.confirm-btn {
    color: #67c23a !important;
}

.confirm-btn:hover {
    color: #529b2e !important;
}

.pagination-container {
    padding: 20px;
    display: flex;
    justify-content: center;
    border-top: 1px solid #f0f0f0;
    background-color: #fafafa;
}

.order-detail {
    padding: 10px 0;
}

.order-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eaeaea;
}

.info-section {
    margin-bottom: 20px;
}

.info-section h4 {
    margin: 0 0 10px 0;
    color: #333;
    font-size: 16px;
}

.shop-info-detail {
    display: flex;
    align-items: center;
    gap: 12px;
}

.dish-list {
    border: 1px solid #eaeaea;
    border-radius: 6px;
    overflow: hidden;
}

.dish-item-detail {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 15px;
    border-bottom: 1px solid #f0f0f0;
    background: #fafafa;
}

.dish-item-detail:last-child {
    border-bottom: none;
}

.dish-info {
    display: flex;
    align-items: center;
    gap: 15px;
}

.dish-price {
    color: #ff6b35;
    font-weight: 500;
}

.order-total {
    text-align: right;
    margin-top: 15px;
    padding-top: 15px;
    border-top: 2px solid #eaeaea;
    font-size: 16px;
}

@media (max-width: 1200px) {
    .content-body {
        overflow-x: auto;
    }

    .table-container {
        min-width: 1200px;
    }
}

@media (max-width: 768px) {
    .order-management {
        padding: 10px;
    }

    .header {
        padding: 20px 15px;
    }

    .header h2 {
        font-size: 22px;
    }

    .content-body {
        margin: 0 10px;
        width: 95%;
    }

    .order-stats .el-col {
        margin-bottom: 15px;
    }

    ::v-deep .detail-dialog .el-dialog {
        width: 95% !important;
    }
}
</style>