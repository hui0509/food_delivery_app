<template>
  <div class="user-management-container">
    <!-- 页面标题卡片 -->
    <div class="page-header">
      <h1><i class="el-icon-user"></i> 用户管理</h1>
      <p>管理系统所有注册用户，可设置用户权限或删除用户</p>
    </div>

    <!-- 搜索 + 操作栏卡片 -->
    <div class="table-card">
      <div class="card-header">
        <div class="left-actions">
          <el-input
            v-model="search"
            placeholder="搜索用户名或手机号"
            clearable
            style="width: 300px;"
            @input="debounceLoad"
            size="medium"
          >
            <i slot="prefix" class="el-icon-search"></i>
          </el-input>
        </div>
        <div class="right-actions">
          <el-button type="primary" size="medium" @click="loadData" :loading="loading">
            <i class="el-icon-refresh"></i> 刷新列表
          </el-button>
        </div>
      </div>

      <!-- 表格 -->
      <el-table
        :data="tableData"
        v-loading="loading"
        element-loading-text="加载中..."
        class="custom-table"
        stripe
        border
        style="width: 100%"
      >
        <!-- 序号 -->
        <el-table-column label="序号" width="80" align="center" fixed="left">
          <template slot-scope="scope">
            <span class="serial-number">{{ (page - 1) * pageSize + scope.$index + 1 }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="username" label="用户名" width="180" show-overflow-tooltip>
          <template slot-scope="scope">
            <strong>{{ scope.row.username }}</strong>
            <el-tag v-if="scope.row.username === 'admin'" size="mini" type="danger" style="margin-left:8px;">系统管理员</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="telephone" label="手机号" width="180" align="center"></el-table-column>
        <el-table-column prop="created_time" label="注册时间" width="180" align="center"></el-table-column>

        <el-table-column label="角色" width="140" align="center">
          <template slot-scope="scope">
            <el-tag
              :type="getRoleTagType(scope.row)"
              effect="dark"
            >
              {{ getRoleDisplayText(scope.row) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" min-width="200" align="center">
          <template slot-scope="scope">
            <!-- 系统管理员显示管理按钮 -->
            <el-button
              v-if="scope.row.username === 'admin'"
              size="small"
              type="primary"
              @click="handleManage(scope.row)"
            >
              管理
            </el-button>

            <!-- 非系统管理员显示配套商家/业务连接按钮 -->
            <template v-else>
              <el-button
                size="small"
                :type="scope.row.role === 1 ? 'info' : 'danger'"
                @click="setAdmin(scope.row)"
              >
                {{ scope.row.role === 1 ? '配套商家' : '业务连接' }}
              </el-button>

              <el-popconfirm
                title="确定要永久删除这个用户吗？此操作不可恢复！"
                confirm-button-text="删除"
                cancel-button-text="取消"
                icon="el-icon-info"
                icon-color="red"
                @confirm="deleteUser(scope.row)"
              >
                <el-button
                  slot="reference"
                  size="small"
                  type="danger"
                  style="margin-left: 10px;"
                >删除</el-button>
              </el-popconfirm>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空数据提示 -->
      <div v-if="!loading && tableData.length === 0" class="empty-data">
        <img src="https://img.alicdn.com/imgextra/i4/O1CN01rAJv3Z1D0b2r0p2jH_!!6000000000200-2-tps-400-400.png" alt="空" style="width:120px; opacity:0.6;">
        <p>暂无用户数据</p>
      </div>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          :page-size.sync="pageSize"
          :current-page.sync="page"
          :page-sizes="[10, 20, 50, 100]"
          @size-change="loadData"
          @current-change="loadData"
        ></el-pagination>
      </div>
    </div>
  </div>
</template>

<script>
import { debounce } from 'lodash'

export default {
  data() {
    return {
      search: '',
      tableData: [],
      loading: false,
      total: 0,
      page: 1,
      pageSize: 10
    }
  },

  computed: {
    // 计算属性：判断是否为超级管理员
    isSuperAdmin() {
      return (
        this.$store?.state?.user?.is_super === 1 ||
        Number(localStorage.getItem('isSuper')) === 1
      );
    }
  },

  created() {
    // 非超级管理员直接禁止进入
    if (!this.isSuperAdmin) {
      this.$message.error('权限不足：只有超级管理员可以访问用户管理页面');
      this.$router.replace('/');
      return;
    }

    this.loadData();
  },

  methods: {
    // 获取角色显示文本
    getRoleDisplayText(user) {
      if (user.username === 'admin') {
        return '系统管理员';
      }
      return user.role === 1 ? '商家' : '普通用户';
    },

    // 获取角色标签类型
    getRoleTagType(user) {
      if (user.username === 'admin') {
        return 'danger';
      }
      return user.role === 1 ? 'warning' : 'success';
    },

    // 管理按钮点击事件
    handleManage(user) {
      this.$message.info(`管理系统管理员 ${user.username}`);
      // 这里可以添加管理逻辑
    },

    loadData() {
      this.loading = true;
      this.$axios
        .get('/api/manager/users', {
          params: {
            search: this.search,
            page: this.page,
            size: this.pageSize
          }
        })
        .then(res => {
          if (res.data.status === 200) {
            this.tableData = res.data.data || [];
            this.total = res.data.total || 0;
          } else {
            this.$message.error('获取用户列表失败');
          }
        })
        .catch(() => {
          this.$message.error('网络异常');
        })
        .finally(() => {
          this.loading = false;
        });
    },

    debounceLoad: debounce(function () {
      this.page = 1;
      this.loadData();
    }, 500),

    setAdmin(row) {
      const newRole = row.role === 1 ? 0 : 1;
      const action = newRole === 1 ? '设为商家' : '取消商家权限';

      this.$confirm(
        `确定要将用户 <strong>${row.username}</strong> ${action} 吗？`,
        '权限修改确认',
        {
          dangerouslyUseHTMLString: true,
          type: 'warning'
        }
      ).then(() => {
        this.$axios
          .put('/api/manager/users', { id: row.id, role: newRole })
          .then(res => {
            if (res.data.status === 200) {
              this.$message.success('操作成功');
              // 更新本地数据
              row.role = newRole;
            } else {
              this.$message.error(res.data.msg || '操作失败');
            }
          })
          .catch(() => {
            this.$message.error('网络异常，操作失败');
          });
      });
    },

    deleteUser(row) {
      this.$axios
        .delete('/api/manager/users', { data: { id: row.id } })
        .then(res => {
          if (res.data.status === 200) {
            this.$message.success('用户已删除');
            this.loadData();
          } else {
            this.$message.error(res.data.msg || '删除失败');
          }
        })
        .catch(() => {
          this.$message.error('网络异常，删除失败');
        });
    }
  }
};
</script>

<style scoped>
.user-management-container {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: calc(100vh - 140px);
}

/* 标题卡片 - 和物流页面完全一致 */
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

.left-actions, .right-actions {
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

.serial-number {
  font-weight: bold;
  color: #409EFF;
}

/* 分页区域 */
.pagination-wrapper {
  padding: 20px;
  text-align: center;
  background: #fafafa;
  border-top: 1px solid #ebeef5;
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

/* 响应式 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  .left-actions, .right-actions {
    justify-content: center;
  }
}
</style>