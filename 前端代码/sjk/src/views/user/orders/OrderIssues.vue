<template>
    <div class="order-issues-container">
        <div class="page-header">
            <h2 class="page-title">订单异常处理</h2>
            <p class="page-subtitle">报告和处理您的订单问题</p>
        </div>

        <div class="action-buttons">
            <el-button type="primary" icon="el-icon-plus" @click="showReportDialog">
                报告新问题
            </el-button>
            <el-button type="info" icon="el-icon-refresh" @click="loadData">
                刷新列表
            </el-button>
        </div>

        <!-- 筛选条件 -->
        <div class="filter-section">
            <el-row :gutter="20">
                <el-col :span="6">
                    <div class="filter-item">
                        <span class="filter-label">状态筛选：</span>
                        <el-select v-model="filterStatus" placeholder="全部状态" clearable>
                            <el-option label="待处理" value="pending"></el-option>
                            <el-option label="处理中" value="processing"></el-option>
                            <el-option label="已处理" value="resolved"></el-option>
                            <el-option label="已关闭" value="closed"></el-option>
                        </el-select>
                    </div>
                </el-col>
                <el-col :span="6">
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
                <el-col :span="6">
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
                <el-col :span="6">
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
                <el-col :span="6">
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
                <el-col :span="6">
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
                <el-col :span="6">
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
                <el-col :span="6">
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
            </el-row>
        </div>

        <!-- 订单异常列表 -->
        <div class="issues-table">
            <el-table
                :data="issuesList"
                v-loading="loading"
                style="width: 100%"
                @row-click="viewIssueDetail"
                class="issues-list-table">

                <el-table-column prop="issue_id" label="问题编号" width="100" align="center">
                    <template slot-scope="scope">
                        <el-tag size="small">#{{ scope.row.issue_id }}</el-tag>
                    </template>
                </el-table-column>

                <el-table-column prop="order_id" label="订单号" width="120" align="center">
                    <template slot-scope="scope">
                        <span class="order-id">#{{ scope.row.order_id }}</span>
                    </template>
                </el-table-column>

                <el-table-column prop="issue_type" label="问题类型" width="120" align="center">
                    <template slot-scope="scope">
                        <el-tag :type="getIssueTypeTag(scope.row.issue_type)">
                            {{ getIssueTypeText(scope.row.issue_type) }}
                        </el-tag>
                    </template>
                </el-table-column>

                <el-table-column prop="title" label="问题标题" min-width="180">
                    <template slot-scope="scope">
                        <div class="issue-title">
                            <span>{{ scope.row.title }}</span>
                            <span v-if="scope.row.urgency === 'high'" class="urgent-tag">紧急</span>
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

                <el-table-column prop="updated_time" label="最后更新" width="160" align="center">
                    <template slot-scope="scope">
                        {{ formatDateTime(scope.row.updated_time) }}
                    </template>
                </el-table-column>

                 <el-table-column label="操作" width="180" fixed="right" align="center">
                    <template slot-scope="scope">
                        <div class="action-buttons-container">
                            <el-button
                                size="mini"
                                type="primary"
                                @click.stop="viewIssueDetail(scope.row)"
                                icon="el-icon-view"
                                class="action-btn">
                                查看
                            </el-button>
                            <el-button
                                v-if="scope.row.status === 'pending' || scope.row.status === 'processing'"
                                size="mini"
                                type="warning"
                                @click.stop="addFollowUp(scope.row)"
                                icon="el-icon-chat-dot-round"
                                class="action-btn">
                                跟进
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

        <!-- 报告问题对话框 -->
        <el-dialog
            title="报告订单问题"
            :visible.sync="reportDialogVisible"
            width="700px"
            @close="resetReportForm">

            <el-form
                :model="reportForm"
                :rules="reportRules"
                ref="reportFormRef"
                label-width="100px"
                class="report-form">

                <el-form-item label="关联订单" prop="order_id">
                    <el-select
                        v-model="reportForm.order_id"
                        placeholder="请选择订单"
                        @change="handleOrderSelect"
                        filterable>
                        <el-option
                            v-for="order in availableOrders"
                            :key="order.order_id"
                            :label="`#${order.order_id} - ${order.shop_name} - ¥${order.order_money}`"
                            :value="order.order_id">
                        </el-option>
                    </el-select>
                </el-form-item>

                <el-form-item label="问题类型" prop="issue_type">
                    <el-select v-model="reportForm.issue_type" placeholder="请选择问题类型">
                        <el-option label="配送问题" value="delivery">
                            <span>配送问题</span>
                            <span class="option-desc">(超时、送错地址、配送员态度等)</span>
                        </el-option>
                        <el-option label="商品问题" value="product">
                            <span>商品问题</span>
                            <span class="option-desc">(商品损坏、质量问题、漏发错发等)</span>
                        </el-option>
                        <el-option label="订单问题" value="order">
                            <span>订单问题</span>
                            <span class="option-desc">(价格错误、订单状态异常、重复扣款等)</span>
                        </el-option>
                        <el-option label="支付问题" value="payment">
                            <span>支付问题</span>
                            <span class="option-desc">(支付失败、重复支付、退款问题等)</span>
                        </el-option>
                        <el-option label="其他问题" value="other">
                            <span>其他问题</span>
                            <span class="option-desc">(其他未分类的问题)</span>
                        </el-option>
                    </el-select>
                </el-form-item>

                <el-form-item label="紧急程度" prop="urgency">
                    <el-radio-group v-model="reportForm.urgency">
                        <el-radio label="low">低</el-radio>
                        <el-radio label="medium">中</el-radio>
                        <el-radio label="high">高</el-radio>
                    </el-radio-group>
                </el-form-item>

                <el-form-item label="问题标题" prop="title">
                    <el-input
                        v-model="reportForm.title"
                        placeholder="请简要描述问题，例如：配送超时1小时"
                        maxlength="100"
                        show-word-limit>
                    </el-input>
                </el-form-item>

                <el-form-item label="详细描述" prop="description">
                    <el-input
                        type="textarea"
                        :rows="4"
                        v-model="reportForm.description"
                        placeholder="请详细描述您遇到的问题，包括时间、具体情况等"
                        maxlength="500"
                        show-word-limit>
                    </el-input>
                </el-form-item>

                <el-form-item label="上传凭证" prop="image_url">
                    <el-upload
                        class="upload-demo"
                        action="/api/upload"
                        :on-success="handleUploadSuccess"
                        :on-error="handleUploadError"
                        :on-remove="handleUploadRemove"
                        :before-upload="beforeUpload"
                        :file-list="fileList"
                        list-type="picture"
                        :limit="3"
                        :on-exceed="handleExceed">
                        <el-button size="small" type="primary">点击上传</el-button>
                        <div slot="tip" class="el-upload__tip">支持jpg/png格式，最多3张，每张不超过2MB</div>
                    </el-upload>
                </el-form-item>

                <el-form-item label="期望解决方案" prop="expected_solution">
                    <el-input
                        type="textarea"
                        :rows="2"
                        v-model="reportForm.expected_solution"
                        placeholder="请描述您期望的解决方案（可选）"
                        maxlength="200"
                        show-word-limit>
                    </el-input>
                </el-form-item>
            </el-form>

            <span slot="footer" class="dialog-footer">
                <el-button @click="reportDialogVisible = false">取消</el-button>
                <el-button
                    type="primary"
                    @click="submitReport"
                    :loading="submitting">
                    {{ submitting ? '提交中...' : '提交报告' }}
                </el-button>
            </span>
        </el-dialog>

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
                            <el-tag v-if="currentIssue.urgency === 'high'" type="danger" size="small">
                                紧急
                            </el-tag>
                        </div>
                    </div>
                    <div class="header-right">
                        <div class="issue-id">问题编号: #{{ currentIssue.issue_id }}</div>
                        <div class="order-id">关联订单: #{{ currentIssue.order_id }}</div>
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

                    <!-- 添加跟进 -->
                    <div v-if="currentIssue.status !== 'closed' && currentIssue.status !== 'resolved'"
                         class="detail-section">
                        <h4 class="section-title">添加跟进</h4>
                        <div class="section-content add-followup">
                            <el-form :model="followupForm" :rules="followupRules" ref="followupFormRef">
                                <el-form-item prop="content">
                                    <el-input
                                        type="textarea"
                                        :rows="3"
                                        v-model="followupForm.content"
                                        placeholder="请输入跟进内容（例如：补充信息、询问进度等）"
                                        maxlength="500"
                                        show-word-limit>
                                    </el-input>
                                </el-form-item>

                                <el-form-item>
                                    <el-upload
                                        class="followup-upload"
                                        action="/api/upload"
                                        :on-success="handleFollowupUploadSuccess"
                                        :before-upload="beforeUpload"
                                        :file-list="followupFileList"
                                        list-type="picture"
                                        :limit="2">
                                        <el-button size="small" type="primary">上传图片</el-button>
                                        <div slot="tip" class="el-upload__tip">支持jpg/png格式，最多2张，每张不超过2MB</div>
                                    </el-upload>
                                </el-form-item>

                                <el-form-item>
                                    <el-button
                                        type="primary"
                                        @click="submitFollowup"
                                        :loading="submittingFollowup">
                                        提交跟进
                                    </el-button>
                                </el-form-item>
                            </el-form>
                        </div>
                    </div>
                </div>
            </div>

            <span slot="footer" class="dialog-footer">
                <el-button @click="detailDialogVisible = false">关闭</el-button>
                <el-button
                    v-if="currentIssue.status === 'pending' || currentIssue.status === 'processing'"
                    type="warning"
                    @click="markAsResolved">
                    标记为已解决
                </el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
export default {
    name: 'OrderIssues',

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
            dateRange: [],

            // 报告问题相关
            reportDialogVisible: false,
            reportForm: {
                order_id: '',
                issue_type: '',
                urgency: 'medium',
                title: '',
                description: '',
                image_url: '',
                expected_solution: ''
            },
            reportRules: {
                order_id: [
                    { required: true, message: '请选择关联订单', trigger: 'change' }
                ],
                issue_type: [
                    { required: true, message: '请选择问题类型', trigger: 'change' }
                ],
                title: [
                    { required: true, message: '请输入问题标题', trigger: 'blur' },
                    { min: 5, max: 100, message: '长度在 5 到 100 个字符', trigger: 'blur' }
                ],
                description: [
                    { required: true, message: '请输入问题描述', trigger: 'blur' },
                    { min: 10, max: 500, message: '长度在 10 到 500 个字符', trigger: 'blur' }
                ]
            },
            availableOrders: [],
            fileList: [],
            submitting: false,

            // 问题详情相关
            detailDialogVisible: false,
            currentIssue: {},
            detailLoading: false,
            followups: [],
            followupForm: {
                content: '',
                image_url: ''
            },
            followupRules: {
                content: [
                    { required: true, message: '请输入跟进内容', trigger: 'blur' },
                    { min: 5, max: 500, message: '长度在 5 到 500 个字符', trigger: 'blur' }
                ]
            },
            followupFileList: [],
            submittingFollowup: false
        };
    },

    mounted() {
        this.loadData();
        this.loadAvailableOrders();
    },

    methods: {

        async loadAvailableOrders() {
            try {
                console.log('开始加载可用订单...');
                const token = localStorage.getItem('token');
                if (!token) {
                    console.error('未找到token');
                    return;
                }

                const response = await this.$axios.get('/api/user/issues/available-orders', {
                    headers: { 'token': token }
                });

                console.log('可用订单接口响应:', response.data);

                if (response.data.status === 200) {
                    this.availableOrders = response.data.data || [];
                    console.log('设置可用订单:', this.availableOrders);

                    if (this.availableOrders.length === 0) {
                        this.$message.warning('暂无可用订单，请确认您有已完成的订单');
                    }
                } else {
                    console.error('获取可用订单失败:', response.data.msg);
                    this.$message.warning('无法加载可用订单');
                }
            } catch (error) {
                console.error('加载可用订单失败:', error);
                this.$message.error('加载可用订单失败，请稍后重试');
            }
        },
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
                if (this.dateRange && this.dateRange.length === 2) {
                    params.start_date = this.dateRange[0];
                    params.end_date = this.dateRange[1];
                }

                const response = await this.$axios.get('/api/user/issues', {
                    headers: { 'token': token },
                    params: params
                });

                if (response.data.status === 200) {
                    this.issuesList = response.data.data.issues || [];
                    this.pagination.total = response.data.data.total || 0;
                    this.stats = response.data.data.stats || {};

                    // 触发事件更新徽章数量
                    this.$bus.$emit('issue-updated');
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


        // 应用筛选
        applyFilters() {
            this.pagination.currentPage = 1;
            this.loadData();
        },

        // 重置筛选
        resetFilters() {
            this.filterStatus = '';
            this.filterType = '';
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

        // 显示报告对话框
        showReportDialog() {
            this.reportDialogVisible = true;
        },

        // 处理订单选择
        handleOrderSelect(orderId) {
            const selectedOrder = this.availableOrders.find(order => order.order_id === orderId);
            if (selectedOrder) {
                // 可以自动填充一些信息
                this.reportForm.title = `${selectedOrder.shop_name}订单问题`;
            }
        },

        // 文件上传相关
        beforeUpload(file) {
            const isImage = file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/gif';
            const isLt2M = file.size / 1024 / 1024 < 2;

            if (!isImage) {
                this.$message.error('只能上传图片文件!');
                return false;
            }
            if (!isLt2M) {
                this.$message.error('图片大小不能超过 2MB!');
                return false;
            }
            return true;
        },

        handleUploadSuccess(response, file, fileList) {
            if (response.status === 200) {
                const urls = fileList.map(item => item.response?.data?.url || item.url).filter(Boolean);
                this.reportForm.image_url = urls.join(',');
            }
        },

        handleUploadError(err) {
            console.error('上传失败:', err);
            this.$message.error('上传失败，请重试');
        },

        handleUploadRemove(file, fileList) {
            const urls = fileList.map(item => item.response?.data?.url || item.url).filter(Boolean);
            this.reportForm.image_url = urls.join(',');
        },

        handleExceed(files, fileList) {
            this.$message.warning(`最多只能上传 ${fileList.length} 张图片`);
        },

        // 提交报告
        submitReport() {
            this.$refs.reportFormRef.validate(async (valid) => {
                if (!valid) return;

                try {
                    this.submitting = true;
                    const token = localStorage.getItem('token');

                    const response = await this.$axios.post('/api/user/issues', this.reportForm, {
                        headers: { 'token': token }
                    });

                    if (response.data.status === 200) {
                        this.$message.success('问题报告提交成功！');
                        this.reportDialogVisible = false;
                        this.loadData();
                        this.resetReportForm();
                    } else {
                        this.$message.error(response.data.msg || '提交失败');
                    }
                } catch (error) {
                    console.error('提交报告失败:', error);
                    this.$message.error('提交失败，请稍后重试');
                } finally {
                    this.submitting = false;
                }
            });
        },

        // 重置报告表单
        resetReportForm() {
            this.$refs.reportFormRef.resetFields();
            this.fileList = [];
            this.reportForm = {
                order_id: '',
                issue_type: '',
                urgency: 'medium',
                title: '',
                description: '',
                image_url: '',
                expected_solution: ''
            };
        },

        // 查看问题详情
        async viewIssueDetail(issue) {
            this.currentIssue = { ...issue };
            this.detailDialogVisible = true;
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
                }
            } catch (error) {
                console.error('加载跟进记录失败:', error);
                this.followups = [];
            } finally {
                this.detailLoading = false;
            }
        },

        // 添加跟进
        addFollowUp(issue) {
            this.currentIssue = { ...issue };
            this.detailDialogVisible = true;
            this.loadIssueFollowups(issue.issue_id);
        },

        // 跟进上传成功
              handleFollowupUploadSuccess(response, file, fileList) {
            if (response.status === 200) {
                const urls = fileList.map(item => item.response?.data?.url || item.url).filter(Boolean);
                this.followupForm.image_url = urls.join(',');
            }
        },

        // 提交跟进
        submitFollowup() {
            this.$refs.followupFormRef.validate(async (valid) => {
                if (!valid) return;

                try {
                    this.submittingFollowup = true;
                    const token = localStorage.getItem('token');

                    const data = {
                        content: this.followupForm.content,
                        image_url: this.followupForm.image_url
                    };

                    const response = await this.$axios.post(`/api/user/issues/${this.currentIssue.issue_id}/followups`, data, {
                        headers: { 'token': token }
                    });

                    if (response.data.status === 200) {
                        this.$message.success('跟进提交成功！');
                        this.followupForm.content = '';
                        this.followupForm.image_url = '';
                        this.followupFileList = [];
                        this.$refs.followupFormRef.resetFields();
                        await this.loadIssueFollowups(this.currentIssue.issue_id);
                        this.loadData(); // 刷新列表
                    } else {
                        this.$message.error(response.data.msg || '提交失败');
                    }
                } catch (error) {
                    console.error('提交跟进失败:', error);
                    this.$message.error('提交失败，请稍后重试');
                } finally {
                    this.submittingFollowup = false;
                }
            });
        },

        // 标记为已解决
        async markAsResolved() {
            try {
                this.$confirm('确认将此问题标记为已解决吗？', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(async () => {
                    const token = localStorage.getItem('token');

                    const response = await this.$axios.put(`/api/user/issues/${this.currentIssue.issue_id}/resolve`, {}, {
                        headers: { 'token': token }
                    });

                    if (response.data.status === 200) {
                        this.$message.success('问题已标记为已解决');
                        this.detailDialogVisible = false;
                        this.loadData();
                    } else {
                        this.$message.error(response.data.msg || '操作失败');
                    }
                });
            } catch (error) {
                console.error('标记为已解决失败:', error);
                this.$message.error('操作失败，请稍后重试');
            }
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
            const date = new Date(dateTime);
            return date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            }).replace(/\//g, '-');
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
.order-issues-container {
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

.action-buttons {
    margin-bottom: 20px;
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
    padding: 20px;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
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

.stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20px;
    font-size: 28px;
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

.stat-number {
    font-size: 28px;
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

.issues-list-table {
    cursor: pointer;
}

.issues-list-table >>> .el-table__row:hover {
    background-color: #f5f7fa;
}

.action-buttons-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    min-height: 32px; /* 保持操作栏高度一致 */
}
.action-btn {
    flex: 0 0 auto;
    margin: 0 !important;
}

/* 当只有一个按钮时，确保居中显示 */
.action-buttons-container:only-child {
    justify-content: center;
}

.order-id {
    font-family: 'Courier New', monospace;
    font-weight: bold;
    color: #409eff;
}

.issue-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.urgent-tag {
    background: #f56c6c;
    color: white;
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 10px;
    margin-left: 10px;
}

.pagination-container {
    margin-top: 20px;
    text-align: center;
}

.report-form >>> .option-desc {
    font-size: 12px;
    color: #909399;
    margin-left: 10px;
}

.upload-demo, .followup-upload {
    width: 100%;
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
}

.issue-id, .order-id {
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

.add-followup {
    background: white;
    border: 1px solid #ebeef5;
}

@media (max-width: 768px) {
    .filter-section .el-col {
        margin-bottom: 15px;
    }

    .stat-card {
        margin-bottom: 15px;
    }
    .action-buttons-container {
        flex-direction: column;
        gap: 5px;
    }

    .action-btn {
        width: 100%;
    }
    .issue-detail-header {
        flex-direction: column;
    }

    .header-right {
        margin-top: 15px;
        text-align: left;
    }
}
</style>