<template>
    <div class="manage-order-issues">
        <div class="page-header">
            <h2 class="page-title">订单异常处理</h2>
            <p class="page-subtitle">管理和处理所有用户的订单问题</p>
        </div>

        <!-- 筛选条件 -->
        <div class="filter-section">
            <el-row :gutter="20">
                <el-col :span="5">
                    <div class="filter-item">
                        <span class="filter-label">状态：</span>
                        <el-select v-model="filterStatus" placeholder="全部状态" clearable>
                            <el-option label="待处理" value="pending"></el-option>
                            <el-option label="处理中" value="processing"></el-option>
                            <el-option label="已处理" value="resolved"></el-option>
                            <el-option label="已关闭" value="closed"></el-option>
                        </el-select>
                    </div>
                </el-col>
                <el-col :span="5">
                    <div class="filter-item">
                        <span class="filter-label">问题类型：</span>
                        <el-select v-model="filterType" placeholder="全部类型" clearable>
                            <el-option label="配送问题" value="delivery"></el-option>
                            <el-option label="商品问题" value="product"></el-option>
                            <el-option label="订单问题" value="order"></el-option>
                            <el-option label="支付问题" value="payment"></el-option>
                            <el-option label="其他问题" value="other"></el-option>
                        </el-select>
                    </div>
                </el-col>
                <el-col :span="5">
                    <div class="filter-item">
                        <span class="filter-label">紧急程度：</span>
                        <el-select v-model="filterUrgency" placeholder="全部" clearable>
                            <el-option label="低" value="low"></el-option>
                            <el-option label="中" value="medium"></el-option>
                            <el-option label="高" value="high"></el-option>
                        </el-select>
                    </div>
                </el-col>
                <el-col :span="7">
                    <div class="filter-item">
                        <span class="filter-label">时间范围：</span>
                        <el-date-picker
                            v-model="dateRange"
                            type="daterange"
                            range-separator="至"
                            start-placeholder="开始日期"
                            end-placeholder="结束日期"
                            value-format="yyyy-MM-dd"
                            clearable>
                        </el-date-picker>
                    </div>
                </el-col>
                <el-col :span="2">
                    <div class="filter-item">
                        <el-button type="primary" @click="applyFilters">筛选</el-button>
                        <el-button @click="resetFilters">重置</el-button>
                    </div>
                </el-col>
            </el-row>
        </div>

        <!-- 统计卡片 -->
        <div class="stats-cards">
            <el-row :gutter="20">
                <el-col :span="4">
                    <div class="stat-card total">
                        <div class="stat-icon">
                            <i class="el-icon-warning-outline"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-number">{{ stats.total || 0 }}</div>
                            <div class="stat-label">全部问题</div>
                        </div>
                    </div>
                </el-col>
                <el-col :span="4">
                    <div class="stat-card pending">
                        <div class="stat-icon">
                            <i class="el-icon-time"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-number">{{ stats.pending || 0 }}</div>
                            <div class="stat-label">待处理</div>
                        </div>
                    </div>
                </el-col>
                <el-col :span="4">
                    <div class="stat-card processing">
                        <div class="stat-icon">
                            <i class="el-icon-loading"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-number">{{ stats.processing || 0 }}</div>
                            <div class="stat-label">处理中</div>
                        </div>
                    </div>
                </el-col>
                <el-col :span="4">
                    <div class="stat-card resolved">
                        <div class="stat-icon">
                            <i class="el-icon-circle-check"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-number">{{ stats.resolved || 0 }}</div>
                            <div class="stat-label">已处理</div>
                        </div>
                    </div>
                </el-col>
                <el-col :span="4">
                    <div class="stat-card closed">
                        <div class="stat-icon">
                            <i class="el-icon-circle-close"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-number">{{ stats.closed || 0 }}</div>
                            <div class="stat-label">已关闭</div>
                        </div>
                    </div>
                </el-col>
                <el-col :span="4">
                    <div class="stat-card urgent">
                        <div class="stat-icon">
                            <i class="el-icon-s-flag"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-number">{{ stats.high || 0 }}</div>
                            <div class="stat-label">紧急问题</div>
                        </div>
                    </div>
                </el-col>
            </el-row>
        </div>

        <!-- 订单异常列表 -->
        <div class="issues-table">
            <el-table
                :data="issuesList"
                v-loading="loading"
                style="width: 100%"
                class="issues-list-table">

                <el-table-column prop="issue_id" label="问题编号" width="90" align="center">
                    <template slot-scope="scope">
                        <el-tag size="small">#{{ scope.row.issue_id }}</el-tag>
                    </template>
                </el-table-column>

                <el-table-column prop="order_id" label="订单号" width="100" align="center">
                    <template slot-scope="scope">
                        <span class="order-id">#{{ scope.row.order_id }}</span>
                    </template>
                </el-table-column>

                <el-table-column prop="username" label="用户" width="120" align="center">
                    <template slot-scope="scope">
                        <div class="user-info">
                            <span>{{ scope.row.username || scope.row.user_phone }}</span>
                        </div>
                    </template>
                </el-table-column>

                <el-table-column prop="shop_name" label="店铺" width="150">
                    <template slot-scope="scope">
                        {{ scope.row.shop_name || '未知店铺' }}
                    </template>
                </el-table-column>

                <el-table-column prop="issue_type" label="问题类型" width="120" align="center">
                    <template slot-scope="scope">
                        <el-tag :type="getIssueTypeTag(scope.row.issue_type)" size="small">
                            {{ getIssueTypeText(scope.row.issue_type) }}
                        </el-tag>
                    </template>
                </el-table-column>

                <el-table-column prop="urgency" label="紧急程度" width="100" align="center">
                    <template slot-scope="scope">
                        <el-tag :type="getUrgencyTag(scope.row.urgency)" size="small">
                            {{ getUrgencyText(scope.row.urgency) }}
                        </el-tag>
                    </template>
                </el-table-column>

                <el-table-column prop="title" label="问题标题" min-width="180">
                    <template slot-scope="scope">
                        <div class="issue-title">
                            <span>{{ scope.row.title }}</span>
                        </div>
                    </template>
                </el-table-column>

                <el-table-column prop="status" label="状态" width="100" align="center">
                    <template slot-scope="scope">
                        <el-tag :type="getStatusTag(scope.row.status)" size="small">
                            {{ getStatusText(scope.row.status) }}
                        </el-tag>
                    </template>
                </el-table-column>

                <el-table-column prop="created_time" label="提交时间" width="160" align="center">
                    <template slot-scope="scope">
                        {{ formatDateTime(scope.row.created_time) }}
                    </template>
                </el-table-column>

                <el-table-column label="操作" width="250" fixed="right" align="center">
                    <template slot-scope="scope">
                        <div class="action-buttons">
                            <el-button
                                size="mini"
                                type="primary"
                                @click="viewIssueDetail(scope.row)"
                                icon="el-icon-view">
                                查看
                            </el-button>
                            <el-button
                                v-if="scope.row.status === 'pending'"
                                size="mini"
                                type="warning"
                                @click="handleProcessIssue(scope.row, 'processing')"
                                icon="el-icon-edit">
                                开始处理
                            </el-button>
                            <el-button
                                v-if="scope.row.status === 'processing'"
                                size="mini"
                                type="success"
                                @click="handleProcessIssue(scope.row, 'resolved')"
                                icon="el-icon-check">
                                标记解决
                            </el-button>
                            <el-button
                                v-if="scope.row.status === 'resolved'"
                                size="mini"
                                type="info"
                                @click="handleProcessIssue(scope.row, 'closed')"
                                icon="el-icon-circle-close">
                                关闭
                            </el-button>
                        </div>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-container">
                <el-pagination
                    @size-change="handleSizeChange"
                    @current-change="handleCurrentChange"
                    :current-page="pagination.currentPage"
                    :page-sizes="[10, 20, 50, 100]"
                    :page-size="pagination.pageSize"
                    layout="total, sizes, prev, pager, next, jumper"
                    :total="pagination.total">
                </el-pagination>
            </div>
        </div>

        <!-- 问题详情对话框 -->
        <el-dialog
            :title="`问题详情 #${currentIssue.issue_id}`"
            :visible.sync="detailDialogVisible"
            width="900px"
            class="issue-detail-dialog">

            <div v-loading="detailLoading">
                <div class="issue-detail-header">
                    <div class="header-left">
                        <h3 class="issue-title">{{ currentIssue.title }}</h3>
                        <div class="issue-meta">
                            <el-tag :type="getIssueTypeTag(currentIssue.issue_type)" size="small">
                                {{ getIssueTypeText(currentIssue.issue_type) }}
                            </el-tag>
                            <el-tag :type="getStatusTag(currentIssue.status)" size="small">
                                {{ getStatusText(currentIssue.status) }}
                            </el-tag>
                            <el-tag :type="getUrgencyTag(currentIssue.urgency)" size="small">
                                {{ getUrgencyText(currentIssue.urgency) }}
                            </el-tag>
                        </div>
                    </div>
                    <div class="header-right">
                        <div class="issue-id">问题编号: #{{ currentIssue.issue_id }}</div>
                        <div class="order-id">关联订单: #{{ currentIssue.order_id }}</div>
                        <div class="user-info">用户: {{ currentIssue.username || currentIssue.user_phone }}</div>
                        <div class="shop-info">店铺: {{ currentIssue.shop_name || '未知' }}</div>
                    </div>
                </div>

                <div class="issue-detail-content">
                    <div class="detail-section">
                        <h4 class="section-title">问题描述</h4>
                        <div class="section-content description">
                            {{ currentIssue.description }}
                        </div>
                    </div>

                    <div v-if="currentIssue.image_url" class="detail-section">
                        <h4 class="section-title">问题凭证</h4>
                        <div class="section-content images">
                            <div v-for="(image, index) in currentIssue.image_url.split(',')" :key="index" class="image-item">
                                <el-image
                                    :src="image"
                                    :preview-src-list="currentIssue.image_url.split(',')"
                                    fit="cover">
                                </el-image>
                            </div>
                        </div>
                    </div>

                    <div v-if="currentIssue.expected_solution" class="detail-section">
                        <h4 class="section-title">期望解决方案</h4>
                        <div class="section-content expected-solution">
                            {{ currentIssue.expected_solution }}
                        </div>
                    </div>

                    <!-- 跟进记录 -->
                    <div class="detail-section">
                        <h4 class="section-title">跟进记录</h4>
                        <div class="section-content followups">
                            <div v-if="followups.length === 0" class="no-followups">
                                暂无跟进记录
                            </div>
                            <el-timeline v-else>
                                <el-timeline-item
                                    v-for="(followup) in followups"
                                    :key="followup.followup_id"
                                    :timestamp="formatDateTime(followup.created_time)"
                                    :type="getFollowupType(followup.followup_type)"
                                    placement="top">

                                    <div class="followup-item">
                                        <div class="followup-header">
                                            <span class="followup-type">{{ getFollowupTypeText(followup.followup_type) }}</span>
                                            <span class="followup-author">{{ followup.created_by }}</span>
                                        </div>
                                        <div class="followup-content">{{ followup.content }}</div>
                                        <div v-if="followup.image_url" class="followup-images">
                                            <el-image
                                                v-for="(image, imgIndex) in followup.image_url.split(',')"
                                                :key="imgIndex"
                                                :src="image"
                                                :preview-src-list="followup.image_url.split(',')"
                                                fit="cover"
                                                class="followup-image">
                                            </el-image>
                                        </div>
                                    </div>
                                </el-timeline-item>
                            </el-timeline>
                        </div>
                    </div>

                    <!-- 管理员处理 -->
                    <div v-if="currentIssue.status !== 'closed'" class="detail-section">
                        <h4 class="section-title">处理问题</h4>
                        <div class="section-content process-form">
                            <el-form :model="processForm" :rules="processRules" ref="processFormRef">
                                <el-form-item label="处理操作" prop="action">
                                    <el-radio-group v-model="processForm.action">
                                        <el-radio label="processing" :disabled="currentIssue.status !== 'pending'">开始处理</el-radio>
                                        <el-radio label="resolved" :disabled="currentIssue.status !== 'processing'">标记为已解决</el-radio>
                                        <el-radio label="closed" :disabled="currentIssue.status !== 'resolved'">关闭问题</el-radio>
                                    </el-radio-group>
                                </el-form-item>

                                <el-form-item label="处理备注" prop="comment">
                                    <el-input
                                        type="textarea"
                                        :rows="3"
                                        v-model="processForm.comment"
                                        placeholder="请输入处理备注（例如：解决方案、跟进情况等）"
                                        maxlength="200"
                                        show-word-limit>
                                    </el-input>
                                </el-form-item>

                                <el-form-item>
                                    <el-button
                                        type="primary"
                                        @click="submitProcess"
                                        :loading="processing">
                                        提交处理
                                    </el-button>
                                </el-form-item>
                            </el-form>
                        </div>
                    </div>
                </div>
            </div>

            <span slot="footer" class="dialog-footer">
                <el-button @click="detailDialogVisible = false">关闭</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
export default {
    name: 'ManageOrderIssues',

    data() {
        return {
            // 数据相关
            issuesList: [],
            stats: {},
            loading: false,

            // 分页相关
            pagination: {
                currentPage: 1,
                pageSize: 10,
                total: 0
            },

            // 筛选相关
            filterStatus: '',
            filterType: '',
            filterUrgency: '',
            dateRange: [],

            // 问题详情相关
            detailDialogVisible: false,
            currentIssue: {},
            detailLoading: false,
            followups: [],

            // 处理表单相关
            processForm: {
                action: '',
                comment: ''
            },
            processRules: {
                action: [
                    { required: true, message: '请选择处理操作', trigger: 'change' }
                ]
            },
            processing: false
        };
    },

    mounted() {
        this.loadData();
    },

    methods: {
        // 加载数据
        async loadData() {
            try {
                this.loading = true;
                const token = localStorage.getItem('token');

                if (!token) {
                    this.$message.error('请先登录');
                    return;
                }

                // 构建查询参数
                const params = {
                    page: this.pagination.currentPage,
                    size: this.pagination.pageSize
                };

                if (this.filterStatus) params.status = this.filterStatus;
                if (this.filterType) params.issue_type = this.filterType;
                if (this.filterUrgency) params.urgency = this.filterUrgency;
                if (this.dateRange && this.dateRange.length === 2) {
                    params.start_date = this.dateRange[0];
                    params.end_date = this.dateRange[1];
                }

                const response = await this.$axios.get('/api/manager/issues', {
                    headers: { 'token': token },
                    params: params
                });

                if (response.data.status === 200) {
                    this.issuesList = response.data.data.issues || [];
                    this.pagination.total = response.data.data.total || 0;

                    // 计算统计数据
                    this.calculateStats();
                } else {
                    this.$message.error(response.data.msg || '加载失败');
                }
            } catch (error) {
                console.error('加载订单异常数据失败:', error);
                this.$message.error('加载失败，请稍后重试');
            } finally {
                this.loading = false;
            }
        },

        // 计算统计数据
        calculateStats() {
            const stats = {
                total: this.issuesList.length,
                pending: 0,
                processing: 0,
                resolved: 0,
                closed: 0,
                high: 0
            };

            this.issuesList.forEach(issue => {
                if (issue.status === 'pending') stats.pending++;
                if (issue.status === 'processing') stats.processing++;
                if (issue.status === 'resolved') stats.resolved++;
                if (issue.status === 'closed') stats.closed++;
                if (issue.urgency === 'high') stats.high++;
            });

            this.stats = stats;
        },

        // 应用筛选
        applyFilters() {
            this.pagination.currentPage = 1;
            this.loadData();
        },

        // 重置筛选
        resetFilters() {
            this.filterStatus = '';
            this.filterType = '';
            this.filterUrgency = '';
            this.dateRange = [];
            this.pagination.currentPage = 1;
            this.loadData();
        },

        // 分页相关
        handleSizeChange(size) {
            this.pagination.pageSize = size;
            this.loadData();
        },

        handleCurrentChange(page) {
            this.pagination.currentPage = page;
            this.loadData();
        },

        // 查看问题详情
        async viewIssueDetail(issue) {
            this.currentIssue = { ...issue };
            this.detailDialogVisible = true;
            this.processForm.action = '';
            this.processForm.comment = '';

            await this.loadIssueFollowups(issue.issue_id);
        },

        // 加载问题跟进记录
        async loadIssueFollowups(issueId) {
            try {
                this.detailLoading = true;
                const token = localStorage.getItem('token');

                const response = await this.$axios.get(`/api/user/issues/${issueId}/followups`, {
                    headers: { 'token': token }
                });

                if (response.data.status === 200) {
                    this.followups = response.data.data || [];
                } else {
                    this.followups = [];
                }
            } catch (error) {
                console.error('加载跟进记录失败:', error);
                this.followups = [];
            } finally {
                this.detailLoading = false;
            }
        },

        // 处理问题
        handleProcessIssue(issue, action) {
            this.currentIssue = { ...issue };
            this.processForm.action = action;
            this.processForm.comment = '';
            this.detailDialogVisible = true;
            this.loadIssueFollowups(issue.issue_id);
        },

        // 提交处理
        submitProcess() {
            this.$refs.processFormRef.validate(async (valid) => {
                if (!valid) return;

                try {
                    this.processing = true;
                    const token = localStorage.getItem('token');

                    const response = await this.$axios.put(
                        `/api/manager/issues/${this.currentIssue.issue_id}/process`,
                        this.processForm,
                        {
                            headers: { 'token': token }
                        }
                    );

                    if (response.data.status === 200) {
                        this.$message.success(response.data.msg || '处理成功');
                        this.detailDialogVisible = false;
                        this.loadData();
                    } else {
                        this.$message.error(response.data.msg || '处理失败');
                    }
                } catch (error) {
                    console.error('处理问题失败:', error);
                    this.$message.error('处理失败，请稍后重试');
                } finally {
                    this.processing = false;
                }
            });
        },

        // 辅助方法
        getIssueTypeTag(type) {
            const map = {
                delivery: 'primary',
                product: 'warning',
                order: 'danger',
                payment: 'success',
                other: 'info'
            };
            return map[type] || 'info';
        },

        getIssueTypeText(type) {
            const map = {
                delivery: '配送问题',
                product: '商品问题',
                order: '订单问题',
                payment: '支付问题',
                other: '其他问题'
            };
            return map[type] || '未知类型';
        },

        getUrgencyTag(urgency) {
            const map = {
                low: 'info',
                medium: 'warning',
                high: 'danger'
            };
            return map[urgency] || 'info';
        },

        getUrgencyText(urgency) {
            const map = {
                low: '低',
                medium: '中',
                high: '高'
            };
            return map[urgency] || '未知';
        },

        getStatusTag(status) {
            const map = {
                pending: 'warning',
                processing: 'primary',
                resolved: 'success',
                closed: 'info'
            };
            return map[status] || 'info';
        },

        getStatusText(status) {
            const map = {
                pending: '待处理',
                processing: '处理中',
                resolved: '已处理',
                closed: '已关闭'
            };
            return map[status] || '未知状态';
        },

        formatDateTime(dateTime) {
            if (!dateTime) return '';

            try {
                const date = new Date(dateTime);
                if (isNaN(date.getTime())) {
                    return dateTime;
                }

                return date.toLocaleString('zh-CN', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                }).replace(/\//g, '-');
            } catch (error) {
                return dateTime;
            }
        },

        getFollowupType(type) {
            const map = {
                user: 'primary',
                admin: 'success',
                system: 'info'
            };
            return map[type] || 'info';
        },

        getFollowupTypeText(type) {
            const map = {
                user: '用户',
                admin: '客服',
                system: '系统'
            };
            return map[type] || '未知';
        }
    }
};
</script>

<style scoped>
.manage-order-issues {
    padding: 20px;
}

.page-header {
    margin-bottom: 30px;
}

.page-title {
    font-size: 24px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 10px 0;
}

.page-subtitle {
    font-size: 14px;
    color: #909399;
    margin: 0;
}

.filter-section {
    background: #f5f7fa;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.filter-item {
    display: flex;
    align-items: center;
}

.filter-label {
    margin-right: 10px;
    font-size: 14px;
    color: #606266;
    min-width: 70px;
}

.stats-cards {
    margin-bottom: 30px;
}

.stat-card {
    background: white;
    border-radius: 8px;
    padding: 15px;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    height: 80px;
}

.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 20px 0 rgba(0, 0, 0, 0.15);
}

.stat-card.total {
    border-left: 4px solid #909399;
}

.stat-card.pending {
    border-left: 4px solid #e6a23c;
}

.stat-card.processing {
    border-left: 4px solid #409eff;
}

.stat-card.resolved {
    border-left: 4px solid #67c23a;
}

.stat-card.closed {
    border-left: 4px solid #909399;
}

.stat-card.urgent {
    border-left: 4px solid #f56c6c;
}

.stat-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;
    font-size: 24px;
}

.stat-card.total .stat-icon {
    background: rgba(144, 147, 153, 0.1);
    color: #909399;
}

.stat-card.pending .stat-icon {
    background: rgba(230, 162, 60, 0.1);
    color: #e6a23c;
}

.stat-card.processing .stat-icon {
    background: rgba(64, 158, 255, 0.1);
    color: #409eff;
}

.stat-card.resolved .stat-icon {
    background: rgba(103, 194, 58, 0.1);
    color: #67c23a;
}

.stat-card.closed .stat-icon {
    background: rgba(144, 147, 153, 0.1);
    color: #909399;
}

.stat-card.urgent .stat-icon {
    background: rgba(245, 108, 108, 0.1);
    color: #f56c6c;
}

.stat-number {
    font-size: 24px;
    font-weight: bold;
    color: #303133;
    margin-bottom: 5px;
}

.stat-label {
    font-size: 14px;
    color: #909399;
}

.issues-table {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.order-id {
    font-family: 'Courier New', monospace;
    font-weight: bold;
    color: #409eff;
}

.issue-title {
    font-size: 14px;
    line-height: 1.4;
}

.user-info {
    font-size: 14px;
    color: #606266;
}

.action-buttons {
    display: flex;
    gap: 5px;
    flex-wrap: wrap;
    justify-content: center;
}

.pagination-container {
    margin-top: 20px;
    text-align: center;
}

.issue-detail-dialog >>> .el-dialog__body {
    padding: 20px;
    max-height: 70vh;
    overflow-y: auto;
}

.issue-detail-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #ebeef5;
}

.header-left {
    flex: 1;
}

.issue-title {
    margin: 0 0 10px 0;
    font-size: 18px;
    color: #303133;
}

.issue-meta {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.header-right {
    text-align: right;
    min-width: 200px;
}

.issue-id, .order-id, .user-info, .shop-info {
    font-size: 14px;
    color: #909399;
    margin-bottom: 5px;
}

.detail-section {
    margin-bottom: 25px;
}

.section-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 10px 0;
    padding-left: 10px;
    border-left: 4px solid #409eff;
}

.section-content {
    background: #f5f7fa;
    padding: 15px;
    border-radius: 6px;
    font-size: 14px;
    line-height: 1.6;
    color: #606266;
}

.images {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.image-item {
    width: 120px;
    height: 120px;
    border-radius: 6px;
    overflow: hidden;
}

.followups {
    max-height: 300px;
    overflow-y: auto;
}

.no-followups {
    text-align: center;
    color: #909399;
    padding: 40px 0;
    font-size: 14px;
}

.followup-item {
    background: white;
    border-radius: 6px;
    padding: 15px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.followup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.followup-type {
    font-weight: bold;
    color: #409eff;
}

.followup-author {
    font-size: 12px;
    color: #909399;
}

.followup-content {
    font-size: 14px;
    line-height: 1.5;
    color: #606266;
    margin-bottom: 10px;
}

.followup-images {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.followup-image {
    width: 80px;
    height: 80px;
    border-radius: 4px;
    overflow: hidden;
}

.process-form {
    background: white;
    border: 1px solid #ebeef5;
    padding: 15px;
}

@media (max-width: 768px) {
    .filter-section .el-col {
        margin-bottom: 15px;
    }

    .stat-card {
        margin-bottom: 15px;
    }

    .issue-detail-header {
        flex-direction: column;
    }

    .header-right {
        margin-top: 15px;
        text-align: left;
    }

    .action-buttons {
        flex-direction: column;
    }

    .action-buttons .el-button {
        margin: 2px 0;
    }
}
</style>