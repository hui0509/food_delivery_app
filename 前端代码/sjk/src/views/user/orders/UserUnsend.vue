<template>
    <div class="completed-orders-container">
        <div class="header">
            <h2>未发货订单</h2>
            <p class="subtitle">管理您待处理的订单</p>
        </div>

        <div class="content-body">
            <div class="table-container">
                <el-table
                    :data="tabledata"
                    style="width: 100%"
                    class="order-table"
                    :row-class-name="tableRowClassName"
                    v-loading="loading"
                    empty-text="暂无未发货订单数据">

                    <!-- 店铺信息 -->
                    <el-table-column
                        label="店铺"
                        width="180"
                        align="center">
                        <template slot-scope="scope">
                            <div class="shop-info">
                                <el-avatar
                                    v-if="scope.row.shop_image"
                                    :src="scope.row.shop_image"
                                    :size="40"
                                    shape="square">
                                </el-avatar>
                                <span class="shop-name">{{ scope.row.shop_name }}</span>
                            </div>
                        </template>
                    </el-table-column>

                    <!-- 菜品详情 -->
                    <el-table-column
                        label="菜品详情"
                        min-width="200"
                        align="center">
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

                    <!-- 订单价格 -->
                    <el-table-column
                        label="订单价格"
                        width="120"
                        align="center">
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
                                :type="scope.row.order_way === '线上订餐' ? 'success' : 'primary'"
                                size="small">
                                {{ scope.row.order_way }}
                            </el-tag>
                        </template>
                    </el-table-column>

                    <!-- 订餐人姓名 -->
                    <el-table-column
                        prop="cons_name"
                        label="订餐人姓名"
                        width="120"
                        align="center">
                    </el-table-column>

                    <!-- 收货地址 -->
                    <el-table-column
                        prop="cons_addre"
                        label="收货地址"
                        width="200"
                        align="center"
                        show-overflow-tooltip>
                    </el-table-column>

                    <!-- 操作 -->
                    <el-table-column
                        label="操作"
                        width="220"
                        align="center">
                        <template slot-scope="scope">
                            <el-button
                                size="small"
                                type="primary"
                                @click="showdia_ch(scope.row)"
                                class="action-btn edit-btn">
                                <i class="el-icon-edit"></i>修改订单
                            </el-button>
                            <el-button
                                size="small"
                                type="danger"
                                @click="showdia_dl(scope.row)"
                                class="action-btn delete-btn">
                                <i class="el-icon-delete"></i>取消订单
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>

            <!-- 分页组件 -->
            <div class="pagination-container" v-if="tabledata.length > 0">
                <el-pagination
                    background
                    layout="prev, pager, next"
                    :total="total"
                    :page-size="pageSize"
                    @current-change="handlePageChange">
                </el-pagination>
            </div>
        </div>

        <!-- 修改订单对话框 -->
        <el-dialog
            title="修改订单"
            :visible.sync="dialog_chnage"
            width="500px"
            class="custom-dialog"
            :before-close="handleDialogClose">
            <el-form
                ref="form"
                :model="form_change"
                label-width="100px"
                :rules="formRules">
                <el-form-item label="订餐人姓名：" prop="cons_name">
                    <el-input
                        v-model="form_change.cons_name"
                        placeholder="请输入订餐人姓名"
                        maxlength="10"
                        show-word-limit>
                    </el-input>
                </el-form-item>
                <el-form-item label="收货地址：" prop="cons_addre">
                    <el-input
                        v-model="form_change.cons_addre"
                        type="textarea"
                        :rows="3"
                        placeholder="请输入详细收货地址"
                        maxlength="50"
                        show-word-limit>
                    </el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click="dialog_chnage = false">取消</el-button>
                <el-button
                    type="primary"
                    @click="change"
                    :loading="submitting">
                    {{ submitting ? '提交中...' : '确认修改' }}
                </el-button>
            </div>
        </el-dialog>

        <!-- 取消订单对话框 -->
        <el-dialog
            title="取消订单"
            :visible.sync="dialog_delete"
            width="400px"
            class="custom-dialog">
            <div style="text-align: center; padding: 20px 0;">
                <i class="el-icon-warning" style="color: #e6a23c; font-size: 48px; margin-bottom: 16px;"></i>
                <p style="font-size: 16px; color: #606266; margin-bottom: 8px;">确定取消此订单吗？</p>
                <p style="font-size: 14px; color: #909399;">此操作不可撤销</p>
            </div>
            <div slot="footer" class="dialog-footer">
                <el-button @click="dialog_delete = false">取消</el-button>
                <el-button
                    type="danger"
                    @click="order_delete"
                    :loading="deleting">
                    {{ deleting ? '取消中...' : '确定取消' }}
                </el-button>
            </div>
        </el-dialog>
    </div>
</template>

<script>
export default {
    created() {
        this.getUnsendOrders()
    },
    data() {
        return {
            tabledata: [],
            loading: false,
            dialog_chnage: false,
            dialog_delete: false,
            submitting: false,
            deleting: false,
            total: 0,
            pageSize: 10,
            currentPage: 1,
            form_change: {
                order_id: '',
                cons_addre: '',
                cons_name: '',
            },
            delete_id: '',
            formRules: {
                cons_name: [
                    { required: true, message: '请输入订餐人姓名', trigger: 'blur' },
                    { min: 2, max: 10, message: '姓名长度在 2 到 10 个字符', trigger: 'blur' }
                ],
                cons_addre: [
                    { required: true, message: '请输入收货地址', trigger: 'blur' },
                    { min: 5, max: 50, message: '地址长度在 5 到 50 个字符', trigger: 'blur' }
                ]
            }
        }
    },
    methods: {
        // 获取未发送订单
        async getUnsendOrders() {
            this.loading = true
            try {
                const res = await this.$axios.get("/api/user/unsend")
                if (res.data.status === 200) {
                    this.tabledata = res.data.tabledata
                    console.log("订单数据:", this.tabledata)
                    // 更新总数用于分页
                    this.total = this.tabledata.length
                } else {
                    this.$message.error('获取订单失败')
                }
            } catch (error) {
                console.error('获取订单失败:', error)
                this.$message.error('网络错误')
            } finally {
                this.loading = false
            }
        },
        tableRowClassName({rowIndex}) {
            if (rowIndex % 2 === 1) {
                return 'stripe-row';
            }
            return '';
        },
        showdia_ch(row) {
            this.form_change.order_id = row.order_id;
            this.form_change.cons_name = row.cons_name;
            this.form_change.cons_addre = row.cons_addre;
            this.dialog_chnage = true;
        },
        async change() {
            this.$refs.form.validate(async (valid) => {
                if (!valid) return;

                this.submitting = true;
                try {
                    const res = await this.$axios.post("/api/user/unsend", this.form_change)
                    console.log(res.data);
                    if (res.data.status == 200) {
                        this.$message({
                            message: res.data.msg,
                            type: "success"
                        })
                        await this.getUnsendOrders()
                        this.dialog_chnage = false;
                    } else {
                        this.$message.error(res.data.msg || '修改失败');
                    }
                } catch (error) {
                    this.$message.error('网络错误，请稍后重试');
                } finally {
                    this.submitting = false;
                }
            })
        },
        showdia_dl(row) {
            this.delete_id = row.order_id;
            this.dialog_delete = true;
        },
        async order_delete() {
            this.deleting = true;
            try {
                const res = await this.$axios.delete("/api/user/unsend", { data: { delete_id: this.delete_id } })
                console.log(res.data);
                if (res.data.status == 200) {
                    this.$message({
                        message: res.data.msg,
                        type: "success"
                    })
                    await this.getUnsendOrders()
                    this.dialog_delete = false;
                } else {
                    this.$message.error(res.data.msg || '取消订单失败');
                }
            } catch (error) {
                this.$message.error('网络错误，请稍后重试');
            } finally {
                this.deleting = false;
            }
        },
        handlePageChange(page) {
            this.currentPage = page;
            // 这里可以实现分页逻辑，如果需要的话
        },
        handleDialogClose() {
            this.dialog_chnage = false;
            if (this.$refs.form) {
                this.$refs.form.clearValidate();
            }
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
    gap: 10px;
}

.shop-name {
    font-weight: 500;
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
    transition: all 0.2s;
}

.action-btn:hover {
    transform: translateY(-1px);
}

.edit-btn {
    background: linear-gradient(135deg, #409eff, #66b1ff);
    border: none;
    border-radius: 4px;
}

.delete-btn {
    background: linear-gradient(135deg, #f56c6c, #f78989);
    border: none;
    border-radius: 4px;
}

.pagination-container {
    padding: 20px;
    display: flex;
    justify-content: center;
    border-top: 1px solid #f0f0f0;
    background-color: #fafafa;
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

/* 对话框样式优化 */
::v-deep .custom-dialog .el-dialog {
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

::v-deep .custom-dialog .el-dialog__header {
    background: linear-gradient(135deg, #f8f9fc 0%, #eaecf4 100%);
    border-radius: 12px 12px 0 0;
    padding: 20px;
    border-bottom: 1px solid #eaeaea;
}

::v-deep .custom-dialog .el-dialog__title {
    color: #333;
    font-weight: 600;
    font-size: 18px;
}

.dialog-footer {
    text-align: center;
    padding-top: 20px;
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

    ::v-deep .custom-dialog .el-dialog {
        width: 90% !important;
    }
}
</style>