<template>
  <div class="unsend-orders-container">
    <!-- 页面标题卡片 -->
    <div class="page-header">
      <h1><i class="el-icon-s-clock"></i> 未发货订单</h1>
      <p>以下是顾客已支付但尚未派单的订单，请尽快分配送餐员</p>
    </div>

    <!-- 主表格卡片 -->
    <div class="table-card">
      <div class="card-header">
        <span class="title">待派单订单列表</span>
        <el-button type="primary" size="medium" @click="getdata" :loading="loading">
          <i class="el-icon-refresh"></i> 刷新列表
        </el-button>
      </div>

      <el-table
        :data="tableData"
        v-loading="loading"
        element-loading-text="加载中..."
        class="custom-table"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="order_id" label="订单编号" width="100" align="center" fixed="left">
          <template slot-scope="scope">
            <el-tag type="warning" size="small">{{ scope.row.order_id }}</el-tag>
          </template>
        </el-table-column>

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
        <el-table-column label="菜品详情" min-width="220" align="center">
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
        <el-table-column label="金额" width="100" align="center">
          <template slot-scope="scope">
            <span style="color:#F56C6C; font-weight:600;">¥{{ scope.row.order_money }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="create_time" label="下单时间" width="180" align="center"></el-table-column>

        <!-- 订餐方式 -->
        <el-table-column prop="order_way" label="订餐方式" width="120" align="center">
          <template slot-scope="scope">
            <el-tag size="small" :type="scope.row.order_way === '线上订餐' ? 'success' : 'primary'">
              {{ scope.row.order_way }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="cons_phone" label="联系电话" width="140" align="center"></el-table-column>
        <el-table-column prop="cons_name" label="订餐人" width="120" align="center"></el-table-column>
        <el-table-column prop="cons_addre" label="配送地址" min-width="220" show-overflow-tooltip></el-table-column>

        <el-table-column label="操作" width="140" align="center" fixed="right">
          <template slot-scope="scope">
            <el-button size="small" type="success" plain @click="show_dialog(scope.row)">
              立即派单
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空数据提示 -->
      <div v-if="!loading && tableData.length === 0" class="empty-data">
        <img src="https://img.alicdn.com/imgextra/i4/O1CN01rAJv3Z1D0b2r0p2jH_!!6000000000200-2-tps-400-400.png" alt="空" style="width:120px; opacity:0.6;">
        <p>当前没有待派单的订单，顾客们都好乖～</p>
      </div>
    </div>

    <!-- 派单对话框 -->
    <el-dialog title="派发订单" :visible.sync="dialog" width="500px" center :close-on-click-modal="false">
      <el-form ref="form" :model="form" :rules="rules" label-width="120px" size="medium">
        <el-form-item label="订单编号" prop="order_id">
          <el-input v-model="form.order_id" disabled></el-input>
        </el-form-item>

        <el-form-item label="选择送餐员" prop="dispatcher_id">
          <el-select v-model="form.dispatcher_id" placeholder="请选择送餐员" style="width: 100%;">
            <el-option
              v-for="item in disp_range"
              :key="item.disp_id"
              :label="`${item.disp_name} (${item.disp_id}) - ${item.disp_phone}`"
              :value="item.disp_id"
            ></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="预计送达时间" prop="deliver_time">
          <el-date-picker
            v-model="form.deliver_time"
            type="datetime"
            placeholder="选择预计送达时间"
            value-format="yyyy-MM-dd HH:mm:ss"
            style="width: 100%;"
          ></el-date-picker>
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="dialog = false">取 消</el-button>
        <el-button type="primary" @click="add" :loading="submitting">确定派发</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tableData: [],
      disp_range: [],
      loading: false,
      submitting: false,
      dialog: false,
      form: {
        order_id: '',
        dispatcher_id: '',
        deliver_time: ''
      },
      rules: {
        dispatcher_id: [
          { required: true, message: '请选择送餐员', trigger: 'change' }
        ],
        deliver_time: [
          { required: true, message: '请选择预计送达时间', trigger: 'change' }
        ]
      }
    }
  },
  created() {
    this.getdata()
  },
  methods: {
    getdata() {
      this.loading = true
      this.$axios.get("/api/manager/unsend")
        .then(res => {
          if (res.data.status === 200) {
            this.tableData = res.data.tabledata || []
            this.disp_range = res.data.disp_range || []
            console.log("管理端订单数据:", this.tableData)
            console.log("送餐员数据:", this.disp_range)
          } else {
            this.$message.error("获取订单失败")
          }
        })
        .catch(error => {
          console.error("获取数据失败:", error)
          this.$message.error("网络错误")
        })
        .finally(() => {
          this.loading = false
        })
    },

    show_dialog(row) {
      this.form = {
        order_id: row.order_id,
        dispatcher_id: '',
        deliver_time: ''
      }
      this.dialog = true
      this.$nextTick(() => {
        this.$refs.form && this.$refs.form.clearValidate()
      })
    },

    add() {
      this.$refs.form.validate(valid => {
        if (!valid) return
        this.submitting = true
        this.$axios.post("/api/manager/unsend", this.form)
          .then(res => {
            if (res.data.status === 200) {
              this.$message.success(res.data.msg || "派单成功！")
              this.dialog = false
              this.getdata()
            } else {
              this.$message.error(res.data.msg || "派单失败")
            }
          })
          .catch(error => {
            console.error("派单失败:", error)
            this.$message.error("网络错误")
          })
          .finally(() => {
            this.submitting = false
          })
      })
    }
  }
}
</script>

<style scoped>
.unsend-orders-container {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: calc(100vh - 140px);
}

/* 标题卡片 - 统一紫蓝渐变 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px 40px;
  border-radius: 16px;
  text-align: center;
  margin-bottom: 30px;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 700;
}

.page-header p {
  margin: 0;
  opacity: 0.9;
  font-size: 16px;
}

/* 主卡片 + 表格样式完全统一 */
.table-card {
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

.card-header {
  padding: 20px 24px;
  background: #f8f9fc;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
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

.custom-table :deep(.el-table__header th) {
  background-color: #f2f6fc !important;
  color: #303133;
  font-weight: 600;
}

.custom-table :deep(.el-table__row:hover) {
  background-color: #f5f7fa !important;
}

.empty-data {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-data p {
  margin-top: 20px;
  font-size: 16px;
}

.dialog-footer {
  text-align: center;
}

/* 响应式 */
@media (max-width: 768px) {
  .unsend-orders-container { padding: 10px; }
  .page-header { padding: 20px; }
  .card-header { flex-direction: column; gap: 15px; align-items: stretch; }
}
</style>