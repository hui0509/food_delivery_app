<template>
  <div class="dispatcher-management-container">
    <!-- 页面标题卡片 -->
    <div class="page-header">
      <h1><i class="el-icon-bicycle"></i> 送餐员管理</h1>
      <p>管理所有送餐员信息，支持添加新送餐员与解雇操作</p>
    </div>

    <!-- 主表格卡片 -->
    <div class="table-card">
      <div class="card-header">
        <span class="title">送餐员列表</span>
        <div class="header-actions">
          <el-button type="success" size="medium" @click="showdia_add">
            <i class="el-icon-plus"></i> 添加送餐员
          </el-button>
          <el-button type="primary" size="medium" @click="getdata" :loading="loading" style="margin-left: 12px;">
            <i class="el-icon-refresh"></i> 刷新
          </el-button>
        </div>
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
        <el-table-column prop="dispatcher_id" label="送餐员编号" width="180" align="center" fixed="left">
          <template slot-scope="scope">
            <el-tag size="small" type="primary">{{ scope.row.dispatcher_id }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="dispatcher_name" label="姓名" width="160" align="center">
          <template slot-scope="scope">
            <strong>{{ scope.row.dispatcher_name }}</strong>
          </template>
        </el-table-column>

        <el-table-column prop="dispatcher_phone" label="联系电话" min-width="180" align="center">
          <template slot-scope="scope">
            <i class="el-icon-phone-outline"></i> {{ scope.row.dispatcher_phone }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="140" align="center" fixed="right">
          <template slot-scope="scope">
            <el-popconfirm
              title="确定要解雇该送餐员吗？此操作不可恢复！"
              confirm-button-text="确定解雇"
              cancel-button-text="取消"
              icon="el-icon-warning"
              icon-color="#F56C6C"
              @confirm="deletedispatcher(scope.row)"
            >
              <el-button slot="reference" size="small" type="danger" plain>解雇</el-button>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空数据提示 -->
      <div v-if="!loading && tableData.length === 0" class="empty-data">
        <img src="https://img.alicdn.com/imgextra/i4/O1CN01rAJv3Z1D0b2r0p2jH_!!6000000000200-2-tps-400-400.png" alt="空" style="width:120px; opacity:0.6;">
        <p>暂无送餐员记录，点击右上角“添加送餐员”开始吧～</p>
      </div>
    </div>

    <!-- 添加送餐员对话框 -->
    <el-dialog title="添加送餐员" :visible.sync="dia_add" width="420px" center>
      <el-form ref="add_form" :model="add_form" :rules="add_form_rules" label-width="110px" size="medium">
        <el-form-item label="送餐员编号" prop="dispatcher_id">
          <el-input v-model.trim="add_form.dispatcher_id" placeholder="例如：D001"></el-input>
        </el-form-item>
        <el-form-item label="姓名" prop="dispatcher_name">
          <el-input v-model.trim="add_form.dispatcher_name" placeholder="请输入真实姓名"></el-input>
        </el-form-item>
        <el-form-item label="联系电话" prop="dispatcher_phone">
          <el-input v-model.trim="add_form.dispatcher_phone" placeholder="11位手机号"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dia_add = false">取 消</el-button>
        <el-button type="primary" @click="adddispatcher">确 定添 加</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tableData: [],
      loading: false,
      dia_add: false,
      add_form: {
        dispatcher_id: '',
        dispatcher_name: '',
        dispatcher_phone: '',
      },
      add_form_rules: {
        dispatcher_id: [
          { required: true, message: '请输入送餐员编号', trigger: 'blur' }
        ],
        dispatcher_name: [
          { required: true, message: '请输入姓名', trigger: 'blur' }
        ],
        dispatcher_phone: [
          { required: true, message: '请输入联系电话', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' }
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
      this.$axios.get("/api/manager/dispatcher")
        .then(res => {
          if (res.data.status === 200) {
            this.tableData = res.data.tabledata || []
          } else {
            this.$message.error("获取送餐员列表失败")
          }
        })
        .finally(() => {
          this.loading = false
        })
    },

    showdia_add() {
      this.dia_add = true
      this.$nextTick(() => {
        this.$refs.add_form && this.$refs.add_form.resetFields()
      })
    },

    adddispatcher() {
      this.$refs.add_form.validate(valid => {
        if (!valid) return
        this.$axios.post("/api/manager/dispatcher", this.add_form)
          .then(res => {
            if (res.data.status === 200) {
              this.$message.success("添加成功！")
              this.dia_add = false
              this.getdata()
            } else {
              this.$message.error(res.data.msg || "添加失败")
            }
          })
      })
    },

    deletedispatcher(row) {
      this.$axios.delete("/api/manager/dispatcher", {
        data: { want_delete: row.dispatcher_id }
      }).then(res => {
        if (res.data.status === 200) {
          this.$message.success("解雇成功")
          this.getdata()
        } else {
          this.$message.error(res.data.msg || "解雇失败")
        }
      })
    }
  }
}
</script>

<style scoped>
.dispatcher-management-container {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: calc(100vh - 140px);
}

/* 标题卡片 - 紫蓝渐变统一风格 */
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

/* 主卡片 */
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

.header-actions {
  display: flex;
  align-items: center;
}

/* 表格样式统一 */
.custom-table :deep(.el-table__header th) {
  background-color: #f2f6fc !important;
  color: #303133;
  font-weight: 600;
}

.custom-table :deep(.el-table__row:hover) {
  background-color: #f5f7fa !important;
}

/* 空数据 */
.empty-data {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-data p {
  margin-top: 20px;
  font-size: 16px;
}

/* 对话框底部按钮 */
.dialog-footer {
  text-align: center;
}

/* 响应式 */
@media (max-width: 768px) {
  .dispatcher-management-container { padding: 10px; }
  .page-header { padding: 20px; }
  .card-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  .header-actions {
    justify-content: center;
  }
}
</style>