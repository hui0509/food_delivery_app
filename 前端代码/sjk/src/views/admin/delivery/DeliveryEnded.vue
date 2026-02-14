<template>
  <div class="finished-delivery-container">
    <!-- 页面标题卡片 -->
    <div class="page-header">
      <h1><i class="el-icon-truck"></i> 已完成物流</h1>
      <p>以下是所有已成功送达的订单信息</p>
    </div>

    <!-- 表格卡片 -->
    <div class="table-card">
      <div class="card-header">
        <span class="title">物流完成列表</span>
        <el-button type="primary" size="small" @click="getdata" :loading="loading">
          <i class="el-icon-refresh"></i> 刷新数据
        </el-button>
      </div>

      <el-table
        :data="tableData"
        style="width: 100%"
        v-loading="loading"
        element-loading-text="加载中..."
        element-loading-spinner="el-icon-loading"
        class="custom-table"
        stripe
        border>

        <el-table-column prop="order_id" label="订单编号" width="180" align="center" fixed="left">
          <template slot-scope="scope">
            <el-tag type="success" size="small">{{ scope.row.order_id }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="cons_phone" label="顾客电话" width="180" align="center">
          <template slot-scope="scope">
            <i class="el-icon-phone-outline"></i> {{ scope.row.cons_phone }}
          </template>
        </el-table-column>

        <el-table-column prop="disp_id" label="送餐员编号" width="160" align="center">
          <template slot-scope="scope">
            <el-tag size="small">{{ scope.row.disp_id }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="deliver_time" label="送达时间" min-width="200" align="center">
          <template slot-scope="scope">
            <i class="el-icon-time"></i>
            <span style="margin-left: 6px;">{{ scope.row.deliver_time }}</span>
          </template>
        </el-table-column>

        <!-- 如有额外字段可以继续加列 -->
      </el-table>

      <!-- 空数据提示美化 -->
      <div v-if="!loading && tableData.length === 0" class="empty-data">
        <img src="https://img.alicdn.com/imgextra/i4/O1CN01rAJv3Z1D0b2r0p2jH_!!6000000000200-2-tps-400-400.png" alt="空" style="width:120px; opacity:0.6;">
        <p>暂无已完成物流记录</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tableData: [],
      loading: false   // 加入 loading 状态，更友好
    }
  },
  created() {
    this.getdata()
  },
  methods: {
    getdata() {
      this.loading = true
      this.$axios.get("/api/manager/delivery?id=1")
        .then(res => {
          console.log(res.data)
          if (res.data.status === 200) {
            this.tableData = res.data.tabledata || []
          } else {
            this.$message.error("获取数据失败")
          }
        })
        .catch(() => {
          this.$message.error("网络错误，请重试")
        })
        .finally(() => {
          this.loading = false
        })
    }
  }
}
</script>

<style scoped>
.finished-delivery-container {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: calc(100vh - 140px);   /* 适配你原来的布局高度 */
}

/* 标题区域 */
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

/* 卡片容器 */
.table-card {
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

/* 卡片头部 */
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

/* 表格美化 */
.custom-table {
  font-size: 14px;
}

.custom-table :deep(.el-table__header th) {
  background-color: #f2f6fc !important;
  color: #303133;
  font-weight: 600;
}

.custom-table :deep(.el-table__row:hover) {
  background-color: #f5f7fa !important;
}

/* 空数据样式 */
.empty-data {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
  font-size: 16px;
}

.empty-data p {
  margin-top: 20px;
}

/* 响应式 */
@media (max-width: 768px) {
  .finished-delivery-container {
    padding: 10px;
  }
  .page-header {
    padding: 20px;
  }
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
}
</style>