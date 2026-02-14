<template>
    <div class="completed-orders-container">
        <div class="header">
            <h2>配送中订单</h2>
            <p class="subtitle">查看所有正在配送中的订单</p>
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

                    <!-- 店铺信息 -->
                    <el-table-column label="店铺" width="160" align="center">
                        <template slot-scope="scope">
                            <div class="shop-info">
                                <el-avatar
                                    v-if="scope.row.shop_image"
                                    :src="scope.row.shop_image"
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
                    <el-table-column
                        prop="cons_name"
                        label="收货人"
                        width="120"
                        align="center">
                    </el-table-column>

                    <!-- 收货人电话 -->
                    <el-table-column
                        prop="cons_phone"
                        label="收货人电话"
                        width="150"
                        align="center">
                    </el-table-column>

                    <!-- 收货地址 -->
                    <el-table-column
                        prop="cons_addre"
                        label="收货地址"
                        width="180"
                        align="center"
                        show-overflow-tooltip>
                    </el-table-column>

                    <!-- 配送员信息 -->
                    <el-table-column label="配送员" width="150" align="center">
                        <template slot-scope="scope">
                            <div v-if="scope.row.disp_name" class="dispatcher-info">
                                <div class="disp-name">{{ scope.row.disp_name }}</div>
                                <div class="disp-id">ID: {{ scope.row.disp_id }}</div>
                            </div>
                            <div v-else class="no-dispatcher">未分配</div>
                        </template>
                    </el-table-column>

                    <!-- 配送员电话 -->
                    <el-table-column
                        prop="disp_phone"
                        label="配送员电话"
                        width="150"
                        align="center">
                    </el-table-column>

                    <!-- 预计送达时间 -->
                    <el-table-column
                        prop="deliver_time"
                        label="预计送达时间"
                        width="180"
                        align="center">
                    </el-table-column>

                    <!-- 操作 -->
                    <el-table-column
                        label="操作"
                        width="120"
                        align="center">
                        <template slot-scope="scope">
                            <el-button
                                type="text"
                                size="small"
                                @click="viewOrderDetail(scope.row)"
                                class="action-btn">
                                <i class="el-icon-view"></i> 详情
                            </el-button>
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
                                v-if="currentOrder.shop_image"
                                :src="currentOrder.shop_image"
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

                    <div v-if="currentOrder.disp_name" class="info-section">
                        <h4>配送信息</h4>
                        <p><strong>配送员:</strong> {{ currentOrder.disp_name }} (ID: {{ currentOrder.disp_id }})</p>
                        <p><strong>联系电话:</strong> {{ currentOrder.disp_phone }}</p>
                        <p><strong>预计送达:</strong> {{ currentOrder.deliver_time }}</p>
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
            currentOrder: null
        }
    },
    methods: {
        async getdata() {
            this.loading = true;
            try {
                const res = await this.$axios.get("/api/manager/sending")
                console.log("配送中订单数据:", res.data);
                if (res.data.status == 200) {
                    this.tableData = res.data.tabledata;
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
        viewOrderDetail(row) {
            this.currentOrder = row;
            this.detailDialogVisible = true;
        },
        handlePageChange(page) {
            this.currentPage = page;
        }
    }
}
</script>

<style scoped>
.completed-orders-container {
    min-height: 100vh;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 20px;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
    justify-content: center;
    gap: 8px;
}

.shop-name {
    font-weight: 500;
    font-size: 14px;
}

/* 菜品详情样式 */
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

/* 配送员信息样式 */
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

/* 表头样式 */
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

::v-deep .stripe-row td {
    background-color: #fafafa;
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

.pagination-container {
    padding: 20px;
    display: flex;
    justify-content: center;
    border-top: 1px solid #f0f0f0;
    background-color: #fafafa;
}

/* 订单详情对话框样式 */
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

/* 分页组件样式调整 */
::v-deep .el-pagination.is-background .btn-next,
::v-deep .el-pagination.is-background .btn-prev,
::v-deep .el-pagination.is-background .el-pager li {
    background-color: white;
    border: 1px solid #eaeaea;
    color: #666;
    font-weight: 500;
}

::v-deep .el-pagination.is-background .el-pager li:not(.disabled).active {
    background: #409eff;
    color: white;
    border-color: #409eff;
}

::v-deep .el-pagination.is-background .el-pager li:not(.disabled):hover {
    color: #409eff;
    border-color: #409eff;
}

/* 加载动画颜色调整 */
::v-deep .el-loading-mask {
    background-color: rgba(255, 255, 255, 0.8);
}

::v-deep .el-loading-spinner .path {
    stroke: #409eff;
}

/* 标签样式调整 */
::v-deep .el-tag--primary {
    background-color: #ecf5ff;
    border-color: #d9ecff;
    color: #409eff;
}

::v-deep .el-tag--success {
    background-color: #f0f9eb;
    border-color: #e1f3d8;
    color: #67c23a;
}

/* 响应式调整 */
@media (max-width: 1200px) {
    .content-body {
        overflow-x: auto;
    }

    .table-container {
        min-width: 1200px;
    }
}

@media (max-width: 768px) {
    .completed-orders-container {
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
    }
}
</style>