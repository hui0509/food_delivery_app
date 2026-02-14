<template>
    <div class="sales-analysis">
        <!-- 头部区域 -->
        <div class="analysis-header">
            <div class="header-content">
                <h2>销售统计</h2>
                <p class="subtitle">实时掌握店铺经营数据</p>
            </div>
            <div class="time-filter">
                <el-select v-model="timeRange" placeholder="选择时间范围" @change="loadSalesData" size="medium">
                    <el-option label="最近7天" value="7"></el-option>
                    <el-option label="最近30天" value="30"></el-option>
                    <el-option label="最近90天" value="90"></el-option>
                </el-select>
            </div>
        </div>

        <!-- 核心指标卡片 -->
        <div class="metrics-grid">
            <el-card class="metric-card total-revenue">
                <div class="metric-content">
                    <div class="metric-icon">
                        <i class="el-icon-money"></i>
                    </div>
                    <div class="metric-info">
                        <h3>总销售额</h3>
                        <p class="metric-value">¥{{ formatNumber(salesData.summary?.total_revenue || 0) }}</p>
                        <p class="metric-period">{{ timeRange }}天内</p>
                    </div>
                </div>
            </el-card>

            <el-card class="metric-card total-orders">
                <div class="metric-content">
                    <div class="metric-icon">
                        <i class="el-icon-s-order"></i>
                    </div>
                    <div class="metric-info">
                        <h3>总订单数</h3>
                        <p class="metric-value">{{ formatNumber(salesData.summary?.total_orders || 0) }}</p>
                        <p class="metric-period">{{ timeRange }}天内</p>
                    </div>
                </div>
            </el-card>

            <el-card class="metric-card avg-order">
                <div class="metric-content">
                    <div class="metric-icon">
                        <i class="el-icon-shopping-cart-2"></i>
                    </div>
                    <div class="metric-info">
                        <h3>客单价</h3>
                        <p class="metric-value">¥{{ formatNumber(salesData.summary?.avg_order_value || 0) }}</p>
                        <p class="metric-period">平均每单金额</p>
                    </div>
                </div>
            </el-card>

            <el-card class="metric-card today-stats">
                <div class="metric-content">
                    <div class="metric-icon">
                        <i class="el-icon-date"></i>
                    </div>
                    <div class="metric-info">
                        <h3>今日数据</h3>
                        <p class="metric-value">{{ salesData.summary?.today_orders || 0 }} 单</p>
                        <p class="metric-period">¥{{ formatNumber(salesData.summary?.today_revenue || 0) }}</p>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- 图表区域 -->
        <div class="charts-section">
            <el-row :gutter="20">
                <!-- 销售趋势图 -->
                <el-col :span="16">
                    <el-card class="chart-card">
                        <div slot="header" class="chart-header">
                            <span>销售趋势</span>
                            <div class="chart-legend">
                                <span class="legend-item revenue">
                                    <i class="el-icon-trend-chart"></i>
                                    销售额
                                </span>
                                <span class="legend-item orders">
                                    <i class="el-icon-s-data"></i>
                                    订单数
                                </span>
                            </div>
                        </div>
                        <div class="chart-container">
                            <div ref="trendChart" style="height: 300px;"></div>
                        </div>
                    </el-card>
                </el-col>

                <!-- 订单状态分布 -->
                <el-col :span="8">
                    <el-card class="chart-card">
                        <div slot="header">
                            <span>订单状态分布</span>
                        </div>
                        <div class="chart-container">
                            <div ref="statusChart" style="height: 300px;"></div>
                        </div>
                    </el-card>
                </el-col>
            </el-row>
        </div>

        <!-- 数据表格区域 -->
        <div class="data-section">
            <el-row :gutter="20">
                <!-- 热销商品 -->
                <el-col :span="12">
                    <el-card class="data-card">
                        <div slot="header" class="data-header">
                            <span>热销商品TOP5</span>
                        </div>
                        <el-table
                            :data="salesData.popular_dishes"
                            style="width: 100%"
                            empty-text="暂无销售数据">
                            <el-table-column label="菜品名称" prop="dish_name" min-width="150"></el-table-column>
                            <el-table-column label="销量" prop="total_sold" width="100" align="center">
                                <template slot-scope="scope">
                                    <span class="sales-count">{{ scope.row.total_sold }}</span>
                                </template>
                            </el-table-column>
                            <el-table-column label="销售额" width="120" align="center">
                                <template slot-scope="scope">
                                    <span class="revenue-amount">¥{{ formatNumber(scope.row.total_revenue) }}</span>
                                </template>
                            </el-table-column>
                        </el-table>
                        <div v-if="salesData.popular_dishes?.length === 0" class="empty-data">
                            <i class="el-icon-dish"></i>
                            <p>暂无热销商品数据</p>
                        </div>
                    </el-card>
                </el-col>

                <!-- 店铺销售排行 -->
                <el-col :span="12">
                    <el-card class="data-card">
                        <div slot="header" class="data-header">
                            <span>店铺销售排行</span>
                        </div>
                        <el-table
                            :data="salesData.shop_stats"
                            style="width: 100%"
                            empty-text="暂无店铺数据">
                            <el-table-column label="店铺名称" prop="shop_name" min-width="150"></el-table-column>
                            <el-table-column label="订单数" prop="order_count" width="100" align="center">
                                <template slot-scope="scope">
                                    <span class="order-count">{{ scope.row.order_count }}</span>
                                </template>
                            </el-table-column>
                            <el-table-column label="销售额" width="120" align="center">
                                <template slot-scope="scope">
                                    <span class="revenue-amount">¥{{ formatNumber(scope.row.total_revenue) }}</span>
                                </template>
                            </el-table-column>
                            <el-table-column label="排名" width="80" align="center">
                                <template slot-scope="scope">
                                    <el-tag
                                        :type="getRankType(scope.$index)"
                                        size="small">
                                        {{ scope.$index + 1 }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                        </el-table>
                        <div v-if="salesData.shop_stats?.length === 0" class="empty-data">
                            <i class="el-icon-s-shop"></i>
                            <p>暂无店铺销售数据</p>
                        </div>
                    </el-card>
                </el-col>
            </el-row>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-overlay">
            <el-card class="loading-card">
                <div class="loading-content">
                    <i class="el-icon-loading"></i>
                    <p>正在加载销售数据...</p>
                </div>
            </el-card>
        </div>
    </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
    name: 'StoreAnalysis',
    props: {
        currentUser: Object
    },
    data() {
        return {
            loading: false,
            timeRange: '7',
            salesData: {
                summary: {},
                popular_dishes: [],
                sales_trend: [],
                shop_stats: [],
                order_status: []
            },
            trendChart: null,
            statusChart: null
        }
    },
    mounted() {
        this.loadAllData();
    },
    beforeDestroy() {
        this.disposeCharts();
    },
    watch: {
        timeRange() {
            this.loadAllData();
        }
    },
    methods: {
        async loadAllData() {
            this.loading = true;
            try {
                await Promise.all([
                    this.loadSalesData(),
                    this.loadOrderStatus()
                ]);
            } catch (error) {
                console.error('加载数据失败:', error);
                this.$message.error('加载数据失败');
            } finally {
                this.loading = false;
            }
        },
        async loadSalesData() {
            try {
                const res = await this.$axios.get(`/api/sales/statistics/owner/${this.currentUser.username}`, {
                    params: {
                        days: this.timeRange,
                        _t: new Date().getTime() // 防止缓存
                    }
                });

                if (res.data.status === 200) {
                    this.salesData = {
                        ...this.salesData,
                        ...res.data.data
                    };
                    this.$nextTick(() => {
                        this.initCharts();
                    });
                } else {
                    this.$message.error(res.data.msg || '加载销售数据失败');
                }
            } catch (error) {
                console.error('加载销售数据失败:', error);
                this.$message.error('加载销售数据失败');
            }
        },
        async loadOrderStatus() {
            try {
                const res = await this.$axios.get(`/api/sales/order-status/owner/${this.currentUser.username}`, {
                    params: {
                        days: this.timeRange,
                        _t: new Date().getTime() // 防止缓存
                    }
                });

                if (res.data.status === 200) {
                    this.salesData.order_status = res.data.data;
                    this.$nextTick(() => {
                        this.initStatusChart();
                    });
                }
            } catch (error) {
                console.error('加载订单状态数据失败:', error);
            }
        },
        initCharts() {
            // 先销毁已有图表
            if (this.trendChart) {
                this.trendChart.dispose();
            }

            // 检查是否有数据
            if (!this.$refs.trendChart || !this.salesData.sales_trend?.length) {
                return;
            }

            this.trendChart = echarts.init(this.$refs.trendChart);

            const trendData = this.salesData.sales_trend || [];
            const dates = trendData.map(item => {
                // 格式化日期，显示为"月-日"
                const date = new Date(item.date);
                return `${date.getMonth() + 1}-${date.getDate()}`;
            });

            const revenues = trendData.map(item => item.daily_revenue);
            const orders = trendData.map(item => item.order_count);

            const option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'cross'
                    },
                    formatter: function(params) {
                        let result = params[0].axisValue + '<br/>';
                        params.forEach(item => {
                            if (item.seriesName === '销售额') {
                                result += `${item.marker} ${item.seriesName}: ¥${item.value.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}<br/>`;
                            } else {
                                result += `${item.marker} ${item.seriesName}: ${item.value} 单<br/>`;
                            }
                        });
                        return result;
                    }
                },
                legend: {
                    data: ['销售额', '订单数'],
                    right: 10,
                    top: 10
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    data: dates,
                    axisLine: {
                        lineStyle: {
                            color: '#dcdfe6'
                        }
                    }
                },
                yAxis: [
                    {
                        type: 'value',
                        name: '销售额(元)',
                        axisLine: {
                            lineStyle: {
                                color: '#dcdfe6'
                            }
                        },
                        splitLine: {
                            lineStyle: {
                                color: '#f0f0f0'
                            }
                        },
                        axisLabel: {
                            formatter: '¥{value}'
                        }
                    },
                    {
                        type: 'value',
                        name: '订单数',
                        axisLine: {
                            lineStyle: {
                                color: '#dcdfe6'
                            }
                        },
                        splitLine: {
                            show: false
                        }
                    }
                ],
                series: [
                    {
                        name: '销售额',
                        type: 'line',
                        smooth: true,
                        lineStyle: {
                            width: 3
                        },
                        itemStyle: {
                            color: '#36a3f7'
                        },
                        areaStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: 'rgba(54, 163, 247, 0.5)' },
                                { offset: 1, color: 'rgba(54, 163, 247, 0.1)' }
                            ])
                        },
                        data: revenues
                    },
                    {
                        name: '订单数',
                        type: 'bar',
                        yAxisIndex: 1,
                        itemStyle: {
                            color: '#67c23a'
                        },
                        data: orders
                    }
                ]
            };

            this.trendChart.setOption(option);

            // 窗口大小变化时重绘图表
            window.addEventListener('resize', this.handleResize);
        },
        initStatusChart() {
            // 先销毁已有图表
            if (this.statusChart) {
                this.statusChart.dispose();
            }

            // 检查是否有数据
            if (!this.$refs.statusChart || !this.salesData.order_status?.length) {
                return;
            }

            this.statusChart = echarts.init(this.$refs.statusChart);

            const statusData = this.salesData.order_status || [];
            const pieData = statusData.map(item => ({
                value: item.count,
                name: item.label
            }));

            const option = {
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}: {c}单 ({d}%)'
                },
                legend: {
                    orient: 'vertical',
                    right: 10,
                    top: 'center',
                    data: statusData.map(item => item.label)
                },
                series: [
                    {
                        name: '订单状态',
                        type: 'pie',
                        radius: ['50%', '70%'],
                        avoidLabelOverlap: false,
                        itemStyle: {
                            borderRadius: 10,
                            borderColor: '#fff',
                            borderWidth: 2
                        },
                        label: {
                            show: false,
                            position: 'center',
                            formatter: '{b}\n{c}单\n{d}%'
                        },
                        emphasis: {
                            label: {
                                show: true,
                                fontSize: '14',
                                fontWeight: 'bold'
                            }
                        },
                        labelLine: {
                            show: false
                        },
                        data: pieData,
                        color: ['#e6a23c', '#409eff', '#67c23a'] // 对应待发货、配送中、已完成
                    }
                ]
            };

            this.statusChart.setOption(option);

            // 窗口大小变化时重绘图表
            window.addEventListener('resize', this.handleResize);
        },
        handleResize() {
            if (this.trendChart) {
                this.trendChart.resize();
            }
            if (this.statusChart) {
                this.statusChart.resize();
            }
        },
        disposeCharts() {
            if (this.trendChart) {
                this.trendChart.dispose();
                this.trendChart = null;
            }
            if (this.statusChart) {
                this.statusChart.dispose();
                this.statusChart = null;
            }
            window.removeEventListener('resize', this.handleResize);
        },
        formatNumber(num) {
            return Number(num).toLocaleString('zh-CN', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        },
        getRankType(index) {
            const types = ['', 'success', 'info', 'warning', ''];
            return types[index] || '';
        }
    }
}
</script>

<style scoped>

/* 响应式设计 */
@media (max-width: 768px) {
    .analysis-header {
        flex-direction: column;
        gap: 16px;
        text-align: center;
    }

    .time-filter {
        width: 100%;
    }

    .time-filter .el-select {
        width: 100%;
    }

    .metrics-grid {
        grid-template-columns: 1fr;
    }

    .charts-section .el-col {
        width: 100%;
        margin-bottom: 16px;
    }

    .data-section .el-col {
        width: 100%;
        margin-bottom: 16px;
    }
}

/* 添加图表容器的固定高度 */
.chart-container {
    height: 300px;
    width: 100%;
}

/* 确保图表正确渲染 */
#trendChart, #statusChart {
    width: 100% !important;
    height: 100% !important;
}


.sales-analysis {
    padding: 20px;
    background: #f5f7fa;
    min-height: 100vh;
}

.analysis-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding: 24px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-content h2 {
    margin: 0 0 8px 0;
    font-size: 24px;
    color: #2c3e50;
}

.header-content .subtitle {
    margin: 0;
    color: #909399;
    font-size: 14px;
}

/* 指标卡片 */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
    margin-bottom: 24px;
}

.metric-card {
    border-radius: 12px;
    border: none;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-4px);
}

.metric-content {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 8px;
}

.metric-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    color: white;
}

.total-revenue .metric-icon { background: linear-gradient(135deg, #36a3f7 0%, #1e88e5 100%); }
.total-orders .metric-icon { background: linear-gradient(135deg, #34bfa3 0%, #00c292 100%); }
.avg-order .metric-icon { background: linear-gradient(135deg, #f4516c 0%, #e91e63 100%); }
.today-stats .metric-icon { background: linear-gradient(135deg, #ffb822 0%, #ff9f00 100%); }

.metric-info h3 {
    margin: 0 0 8px 0;
    color: #666;
    font-size: 14px;
    font-weight: normal;
}

.metric-value {
    margin: 0 0 4px 0;
    font-size: 24px;
    font-weight: bold;
    color: #2c3e50;
}

.metric-period {
    margin: 0;
    font-size: 12px;
    color: #909399;
}

/* 图表区域 */
.charts-section {
    margin-bottom: 24px;
}

.chart-card {
    border-radius: 8px;
    border: none;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.chart-legend {
    display: flex;
    gap: 16px;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #666;
}

.legend-item.revenue i { color: #36a3f7; }
.legend-item.orders i { color: #67c23a; }

.chart-container {
    padding: 10px 0;
}

/* 数据表格区域 */
.data-section {
    margin-bottom: 24px;
}

.data-card {
    border-radius: 8px;
    border: none;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.data-header {
    font-weight: 600;
    color: #2c3e50;
}

.sales-count, .order-count {
    font-weight: 600;
    color: #36a3f7;
}

.revenue-amount {
    font-weight: 600;
    color: #67c23a;
}

.empty-data {
    text-align: center;
    padding: 40px;
    color: #909399;
}

.empty-data i {
    font-size: 48px;
    margin-bottom: 16px;
    display: block;
}

/* 加载状态 */
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

.loading-card {
    text-align: center;
    padding: 40px;
}

.loading-content i {
    font-size: 32px;
    color: #409eff;
    margin-bottom: 16px;
    display: block;
}

/* 响应式设计 */
@media (max-width: 1200px) {
    .metrics-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 768px) {
    .analysis-header {
        flex-direction: column;
        gap: 16px;
        text-align: center;
    }

    .metrics-grid {
        grid-template-columns: 1fr;
    }

    .charts-section .el-col {
        margin-bottom: 16px;
    }

    .data-section .el-col {
        margin-bottom: 16px;
    }
}
</style>