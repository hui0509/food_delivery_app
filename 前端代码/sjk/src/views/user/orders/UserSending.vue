<template>
    <div class="delivering-orders-container">
        <div class="header">
            <h2>配送中订单</h2>
            <p class="subtitle">查看正在配送中的订单</p>
        </div>

        <div class="content-body">
            <div class="table-container">
                <el-table
                    :data="tableData"
                    style="width: 100%"
                    class="order-table"
                    :row-class-name="tableRowClassName"
                    v-loading="loading"
                    empty-text="暂无配送中订单数据">

                    <!-- 订单号 -->
                    <el-table-column
                        prop="order_id"
                        label="订单号"
                        width="150"
                        align="center">
                    </el-table-column>

                    <!-- 店铺信息 -->
                    <el-table-column label="店铺" width="180" align="center">
                        <template slot-scope="scope">
                            <div class="shop-info">
                                <el-avatar
                                    v-if="scope.row.shop_image"
                                    :src="scope.row.shop_image"
                                    :size="36"
                                    shape="square"
                                    class="shop-avatar">
                                </el-avatar>
                                <div class="shop-text">
                                    <div class="shop-name">{{ scope.row.shop_name }}</div>
                                    <div class="order-time" v-if="scope.row.create_time">
                                        下单：{{ formatTime(scope.row.create_time) }}
                                    </div>
                                </div>
                            </div>
                        </template>
                    </el-table-column>

                    <!-- 菜品详情 -->
                    <el-table-column label="订单详情" min-width="250" align="center">
                        <template slot-scope="scope">
                            <div class="dish-details">
                                <div class="dishes-summary">
                                    <span class="dish-count">
                                        共 {{ getDishCount(scope.row.orderDetails) }} 件商品
                                    </span>
                                    <span class="total-price">¥{{ scope.row.order_money }}</span>
                                </div>
                                <div class="dishes-preview">
                                    <template v-if="scope.row.orderDetails && scope.row.orderDetails.length > 0">
                                        <span
                                            v-for="(item, index) in getPreviewDishes(scope.row.orderDetails)"
                                            :key="item.dish_id"
                                            class="dish-preview-item">
                                            {{ item.dish_name }}×{{ item.quantity }}
                                            <span v-if="index < scope.row.orderDetails.length - 1">、</span>
                                        </span>
                                        <span v-if="scope.row.orderDetails.length > 2" class="more-dishes">
                                            等{{ scope.row.orderDetails.length }}件
                                        </span>
                                    </template>
                                    <div v-else class="no-dishes">
                                        无菜品信息
                                    </div>
                                </div>
                            </div>
                        </template>
                    </el-table-column>

                    <!-- 收货信息 -->
                    <el-table-column label="收货信息" width="200" align="center">
                        <template slot-scope="scope">
                            <div class="consignee-info">
                                <div class="consignee-name">
                                    <i class="el-icon-user"></i>
                                    {{ scope.row.cons_name }}
                                </div>
                                <div class="consignee-address" :title="scope.row.cons_addre">
                                    <i class="el-icon-location"></i>
                                    {{ truncateAddress(scope.row.cons_addre) }}
                                </div>
                                <div v-if="scope.row.cons_phone" class="consignee-phone">
                                    <i class="el-icon-phone"></i>
                                    {{ scope.row.cons_phone }}
                                </div>
                            </div>
                        </template>
                    </el-table-column>

                    <!-- 配送信息 -->
                    <el-table-column label="配送信息" width="220" align="center">
                        <template slot-scope="scope">
                            <div class="delivery-info">
                                <!-- 预计送达时间 -->
                                <div class="delivery-time" v-if="scope.row.deliver_time">
                                    <i class="el-icon-time"></i>
                                    预计：{{ formatTime(scope.row.deliver_time) }}
                                </div>
                                <div v-else class="no-time">
                                    <i class="el-icon-time"></i>
                                    未设定送达时间
                                </div>

                                <!-- 配送员信息 -->
                                <div v-if="scope.row.disp_name" class="dispatcher-info">
                                    <i class="el-icon-user-solid"></i>
                                    {{ scope.row.disp_name }}
                                    <el-tag v-if="scope.row.disp_phone" size="mini" class="phone-tag">
                                        <i class="el-icon-phone"></i>
                                        {{ scope.row.disp_phone }}
                                    </el-tag>
                                </div>
                                <div v-else class="no-dispatcher">
                                    <i class="el-icon-user-solid"></i>
                                    未分配配送员
                                </div>
                            </div>
                        </template>
                    </el-table-column>

                    <!-- 订单状态 -->
                    <el-table-column
                        label="状态"
                        width="120"
                        align="center"
                        fixed="right">
                        <template slot-scope="scope">
                            <el-tag
                                :type="getOrderStatusType(scope.row)"
                                effect="dark"
                                size="small"
                                class="status-tag">
                                <i class="el-icon-truck"></i>
                                配送中
                            </el-tag>
                        </template>
                    </el-table-column>

                    <!-- 操作 -->
                    <el-table-column
                        label="操作"
                        width="150"
                        align="center"
                        fixed="right">
                        <template slot-scope="scope">
                            <div class="action-buttons">
                                <el-button
                                    type="primary"
                                    size="small"
                                    @click="viewOrderDetail(scope.row)"
                                    class="detail-btn"
                                    icon="el-icon-view">
                                    详情
                                </el-button>
                                <el-button
                                    type="success"
                                    size="small"
                                    @click="confirmReceipt(scope.row)"
                                    class="confirm-btn"
                                    icon="el-icon-circle-check"
                                    :loading="scope.row.confirming"
                                    :disabled="!scope.row.disp_name">
                                    收货
                                </el-button>
                            </div>
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <!-- 分页组件 -->
            <div class="pagination-container" v-if="tableData.length > 0">
                <el-pagination
                    background
                    layout="prev, pager, next"
                    :total="total"
                    :page-size="pageSize"
                    @current-change="handlePageChange">
                </el-pagination>
            </div>
        </div>

        <!-- 订单详情对话框 -->
        <el-dialog
            title="订单详情"
            :visible.sync="detailDialogVisible"
            width="700px"
            class="detail-dialog">
            <div v-if="currentOrder" class="order-detail">
                <div class="order-header">
                    <div class="order-title">
                        <h3>订单号：{{ currentOrder.order_id }}</h3>
                        <div class="order-status">
                            <el-tag type="warning" effect="dark">配送中</el-tag>
                            <el-tag :type="currentOrder.order_way === '线上订餐' ? 'success' : 'primary'" style="margin-left: 8px;">
                                {{ currentOrder.order_way }}
                            </el-tag>
                        </div>
                    </div>
                </div>

                <div class="order-body">
                    <!-- 基本信息 -->
                    <div class="basic-info">
                        <div class="info-card">
                            <h4><i class="el-icon-shop"></i> 店铺信息</h4>
                            <div class="shop-info-detail">
                                <el-avatar
                                    v-if="currentOrder.shop_image"
                                    :src="currentOrder.shop_image"
                                    :size="60"
                                    shape="square">
                                </el-avatar>
                                <div class="shop-info-text">
                                    <div class="shop-name">{{ currentOrder.shop_name }}</div>
                                    <div class="order-time">下单时间：{{ currentOrder.create_time }}</div>
                                </div>
                            </div>
                        </div>

                        <div class="info-card">
                            <h4><i class="el-icon-user"></i> 收货信息</h4>
                            <div class="consignee-details">
                                <p><strong>收货人：</strong>{{ currentOrder.cons_name }}</p>
                                <p><strong>联系电话：</strong>{{ currentOrder.cons_phone }}</p>
                                <p><strong>收货地址：</strong>{{ currentOrder.cons_addre }}</p>
                            </div>
                        </div>

                        <div class="info-card">
                            <h4><i class="el-icon-truck"></i> 配送信息</h4>
                            <div class="delivery-details">
                                <div v-if="currentOrder.disp_name">
                                    <p><strong>配送员：</strong>{{ currentOrder.disp_name }} (ID: {{ currentOrder.disp_id }})</p>
                                    <p><strong>联系电话：</strong>{{ currentOrder.disp_phone }}</p>
                                </div>
                                <div v-else>
                                    <p><strong>配送状态：</strong>等待分配配送员</p>
                                </div>
                                <p><strong>预计送达：</strong>{{ currentOrder.deliver_time || '未设定' }}</p>
                            </div>
                        </div>
                    </div>

                    <!-- 菜品详情 -->
                    <div class="dishes-detail">
                        <h4><i class="el-icon-fork-spoon"></i> 菜品详情</h4>
                        <div class="dishes-list">
                            <div
                                v-for="item in currentOrder.orderDetails"
                                :key="item.dish_id"
                                class="dish-detail-item">
                                <div class="dish-info">
                                    <span class="dish-name">{{ item.dish_name }}</span>
                                    <span class="dish-quantity">×{{ item.quantity }}</span>
                                </div>
                                <div class="dish-price-info">
                                    <span class="unit-price">¥{{ item.price }}</span>
                                    <span class="subtotal">小计：¥{{ item.price * item.quantity }}</span>
                                </div>
                            </div>
                        </div>
                        <div class="order-summary">
                            <div class="summary-item">
                                <span>商品总数：</span>
                                <span>{{ getDishCount(currentOrder.orderDetails) }} 件</span>
                            </div>
                            <div class="summary-item total">
                                <span>订单总额：</span>
                                <span class="total-amount">¥{{ currentOrder.order_money }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div slot="footer" class="dialog-footer">
                <el-button type="primary" @click="detailDialogVisible = false">关闭</el-button>
                <el-button
                    type="success"
                    @click="confirmReceipt(currentOrder)"
                    icon="el-icon-circle-check"
                    :loading="currentOrder && currentOrder.confirming"
                    :disabled="!currentOrder || !currentOrder.disp_name">
                    确认收货
                </el-button>
            </div>
        </el-dialog>
    </div>
</template>

<script>
export default {
    created() {
        this.getdata()
    },
    data() {
        return {
            tableData: [],
            loading: false,
            total: 0,
            pageSize: 10,
            currentPage: 1,
            detailDialogVisible: false,
            currentOrder: null,
            confirmingOrderId: null // 正在确认的订单ID
        }
    },
    methods: {
        async getdata() {
            this.loading = true;
            try {
                const res = await this.$axios.get("/api/user/sending")
                console.log("配送中订单数据:", res.data);
                if (res.data.status == 200) {
                    // 为每个订单添加确认状态
                    this.tableData = res.data.tabledata.map(order => ({
                        ...order,
                        confirming: false
                    }));
                    this.total = this.tableData.length;
                } else {
                    this.$message.error('获取订单失败')
                }
            } catch (error) {
                console.error('获取配送中订单失败:', error)
                this.$message.error('网络错误')
            } finally {
                this.loading = false;
            }
        },

        tableRowClassName({rowIndex}) {
            if (rowIndex % 2 === 1) {
                return 'stripe-row';
            }
            return '';
        },

        formatTime(time) {
            if (!time) return '';
            // 简化时间显示，只保留日期和时间部分
            return time.replace('T', ' ').substring(0, 16);
        },

        getDishCount(orderDetails) {
            if (!orderDetails || !Array.isArray(orderDetails)) return 0;
            return orderDetails.reduce((total, item) => total + item.quantity, 0);
        },

        getPreviewDishes(orderDetails) {
            if (!orderDetails || !Array.isArray(orderDetails)) return [];
            // 只显示前2个菜品作为预览
            return orderDetails.slice(0, 2);
        },

        truncateAddress(address) {
            if (!address) return '';
            if (address.length > 15) {
                return address.substring(0, 15) + '...';
            }
            return address;
        },

        getOrderStatusType(order) {
            // 根据配送状态返回不同的标签类型
            if (!order.disp_name) {
                return 'info'; // 未分配配送员
            }
            return 'warning'; // 配送中
        },

        viewOrderDetail(row) {
            this.currentOrder = row;
            this.detailDialogVisible = true;
        },

        async confirmReceipt(row) {
            if (!row || !row.disp_name) {
                this.$message.warning('订单尚未分配配送员，无法确认收货');
                return;
            }

            try {
                // 设置确认状态
                row.confirming = true;
                this.confirmingOrderId = row.order_id;

                const result = await this.$confirm('确认收到订单了吗？', '提示', {
                    confirmButtonText: '确认收货',
                    cancelButtonText: '取消',
                    type: 'warning',
                    confirmButtonClass: 'confirm-button',
                    cancelButtonClass: 'cancel-button'
                });

                if (result) {
                    // 调用确认收货的API
                    const res = await this.$axios.post("/api/user/confirm-receipt", {
                        order_id: row.order_id
                    })

                    if (res.data.status === 200) {
                        this.$message.success({
                            message: `订单 ${row.order_id} 已确认收货`,
                            duration: 2000
                        });

                        // 刷新列表
                        await this.getdata();

                        // 提示用户可以在已完成订单中查看
                        this.$message.info({
                            message: '您可以在"已完成订单"中查看此订单',
                            duration: 3000
                        });
                    } else {
                        this.$message.error(res.data.msg || '确认收货失败');
                    }
                }
            } catch (error) {
                if (error !== 'cancel') {
                    console.error('确认收货失败:', error)
                    this.$message.error('网络错误');
                }
            } finally {
                // 重置确认状态
                if (row) {
                    row.confirming = false;
                }
                this.confirmingOrderId = null;
            }
        },

        handlePageChange(page) {
            this.currentPage = page;
        }
    }
}
</script>

<style scoped>
.delivering-orders-container {
    min-height: 100vh;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 20px;
}

.header {
    background: linear-gradient(135deg,#667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    text-align: center;
    border-radius: 12px;
    margin-bottom: 25px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.header h2 {
    margin: 0;
    font-size: 28px;
    font-weight: 700;
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

.table-container {
    padding: 20px;
}

.order-table {
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #eaeaea;
}

/* 店铺信息样式 */
.shop-info {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
}

.shop-avatar {
    flex-shrink: 0;
    border-radius: 6px;
}

.shop-text {
    flex: 1;
    text-align: left;
    overflow: hidden;
}

.shop-name {
    font-weight: 600;
    font-size: 14px;
    color: #333;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.order-time {
    font-size: 12px;
    color: #666;
}

/* 菜品详情样式 */
.dish-details {
    text-align: left;
    padding: 8px 0;
}

.dishes-summary {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
    font-size: 13px;
}

.dish-count {
    color: #666;
}

.total-price {
    color: #ff6b35;
    font-weight: 600;
    font-size: 14px;
}

.dishes-preview {
    font-size: 12px;
    color: #666;
    line-height: 1.4;
}

.dish-preview-item {
    display: inline-block;
    margin-right: 2px;
}

.more-dishes {
    color: #999;
    font-style: italic;
}

.no-dishes {
    color: #999;
    font-style: italic;
    text-align: center;
    font-size: 13px;
}

/* 收货信息样式 */
.consignee-info {
    text-align: left;
    padding: 8px 0;
    font-size: 13px;
}

.consignee-name {
    font-weight: 500;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.consignee-address {
    color: #666;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
    line-height: 1.3;
}

.consignee-phone {
    color: #666;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* 配送信息样式 */
.delivery-info {
    text-align: left;
    padding: 8px 0;
    font-size: 13px;
}

.delivery-time {
    color: #ff7e5f;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 500;
}

.dispatcher-info {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 4px;
    color: #409eff;
}

.phone-tag {
    margin-left: 8px;
    height: 20px;
    line-height: 18px;
    padding: 0 4px;
    font-size: 11px;
}

.no-dispatcher {
    color: #999;
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
}

.no-time {
    color: #999;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 8px;
}

/* 状态标签样式 */
.status-tag {
    font-weight: 500;
    padding: 4px 8px;
}

/* 操作按钮样式 */
.action-buttons {
    display: flex;
    gap: 8px;
    justify-content: center;
}

.detail-btn {
    background-color: #ecf5ff;
    border-color: #d9ecff;
    color: #409eff;
}

.confirm-btn {
    background-color: #f0f9eb;
    border-color: #e1f3d8;
    color: #67c23a;
}

.confirm-btn:disabled {
    background-color: #f5f7fa;
    border-color: #e4e7ed;
    color: #c0c4cc;
    cursor: not-allowed;
}

/* 表头样式 */
::v-deep .el-table th {
    background: #f8f9fa;
    color: #333;
    font-weight: 600;
    height: 50px;
    border-bottom: 2px solid #eaeaea;
    font-size: 14px;
}

::v-deep .el-table td {
    padding: 16px 0;
    border-bottom: 1px solid #f0f0f0;
    color: #666;
    vertical-align: top;
}

::v-deep .stripe-row td {
    background-color: #fafafa;
}

::v-deep .el-table--enable-row-hover .el-table__body tr:hover>td {
    background-color: #f5f7fa;
}

.pagination-container {
    padding: 20px;
    display: flex;
    justify-content: center;
    border-top: 1px solid #f0f0f0;
    background-color: #fafafa;
}

/* 订单详情对话框样式 */
.order-detail {
    padding: 0 10px;
}

.order-header {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eaeaea;
}

.order-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.order-title h3 {
    margin: 0;
    color: #333;
}

.order-status {
    display: flex;
    gap: 8px;
}

.order-body {
    max-height: 500px;
    overflow-y: auto;
    padding-right: 10px;
}

.basic-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.info-card {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 16px;
    border: 1px solid #eaeaea;
}

.info-card h4 {
    margin: 0 0 12px 0;
    color: #333;
    font-size: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.shop-info-detail {
    display: flex;
    align-items: center;
    gap: 12px;
}

.shop-info-text {
    flex: 1;
}

.shop-info-text .shop-name {
    font-size: 16px;
    margin-bottom: 6px;
}

.consignee-details p,
.delivery-details p {
    margin: 8px 0;
    font-size: 13px;
    color: #666;
}

.delivery-details .el-tag {
    margin-left: 8px;
    height: 22px;
    line-height: 20px;
}

.dishes-detail {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 16px;
    border: 1px solid #eaeaea;
}

.dishes-detail h4 {
    margin: 0 0 16px 0;
    color: #333;
    font-size: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.dishes-list {
    border: 1px solid #eaeaea;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 16px;
}

.dish-detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background: white;
    border-bottom: 1px solid #f0f0f0;
}

.dish-detail-item:last-child {
    border-bottom: none;
}

.dish-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

.dish-name {
    font-size: 14px;
    color: #333;
}

.dish-quantity {
    color: #666;
    font-size: 13px;
}

.dish-price-info {
    text-align: right;
}

.unit-price {
    display: block;
    color: #ff6b35;
    font-size: 13px;
    margin-bottom: 4px;
}

.subtotal {
    display: block;
    color: #666;
    font-size: 12px;
}

.order-summary {
    text-align: right;
    padding-top: 16px;
    border-top: 1px solid #eaeaea;
}

.summary-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 14px;
    color: #666;
}

.summary-item.total {
    font-size: 16px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px dashed #eaeaea;
}

.total-amount {
    color: #ff6b35;
    font-weight: 600;
    font-size: 18px;
}

.dialog-footer {
    padding: 16px 0 0;
    border-top: 1px solid #eaeaea;
}

/* 响应式调整 */
@media (max-width: 1200px) {
    .content-body {
        overflow-x: auto;
    }

    .table-container {
        min-width: 1000px;
    }
}

@media (max-width: 768px) {
    .delivering-orders-container {
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

    ::v-deep .detail-dialog .el-dialog {
        width: 95% !important;
        margin: 20px auto !important;
    }

    .basic-info {
        grid-template-columns: 1fr;
    }

    .action-buttons {
        flex-direction: column;
        gap: 6px;
    }

    .action-buttons .el-button {
        width: 100%;
    }
}

/* 自定义对话框按钮样式 */
::v-deep .confirm-button {
    background-color: #67c23a !important;
    border-color: #67c23a !important;
}

::v-deep .cancel-button {
    background-color: #f5f7fa !important;
    border-color: #e4e7ed !important;
    color: #606266 !important;
}
</style>