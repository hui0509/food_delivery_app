<template>
    <div class="shop-management">
        <!-- 统计卡片 -->
        <div class="management-stats">
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="el-icon-s-shop"></i>
                </div>
                <div class="stat-content">
                    <h3>总店铺数</h3>
                    <p class="number">{{ tableData.length }}</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="el-icon-s-data"></i>
                </div>
                <div class="stat-content">
                    <h3>平均月销量</h3>
                    <p class="number">{{ averageSales }}</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="el-icon-star-on"></i>
                </div>
                <div class="stat-content">
                    <h3>热门店铺</h3>
                    <p class="number">{{ hotShopCount }}</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="el-icon-check"></i>
                </div>
                <div class="stat-content">
                    <h3>营业中</h3>
                    <p class="number">{{ activeShopCount }}</p>
                </div>
            </div>
        </div>

        <!-- 操作栏 -->
        <div class="operation-bar">
            <div class="search-section">
                <el-input
                    v-model="searchKeyword"
                    placeholder="搜索店铺名称或描述..."
                    prefix-icon="el-icon-search"
                    clearable
                    style="width: 300px;"
                    @input="handleSearch"
                ></el-input>
                <el-select v-model="filterSales" placeholder="销量筛选" clearable @change="handleFilter">
                    <el-option label="高销量(100+)" value="high"></el-option>
                    <el-option label="中等销量(50-99)" value="medium"></el-option>
                    <el-option label="低销量(<50)" value="low"></el-option>
                </el-select>
                <el-select v-model="filterStatus" placeholder="状态筛选" clearable @change="handleFilter">
                    <el-option label="营业中" :value="1"></el-option>
                    <el-option label="已停业" :value="0"></el-option>
                </el-select>
            </div>
            <div class="action-section">
                <el-button type="success" icon="el-icon-plus" @click="showdia_add()">
                    添加店铺
                </el-button>
                <el-button icon="el-icon-refresh" @click="getdata">
                    刷新数据
                </el-button>
            </div>
        </div>

        <!-- 店铺表格 -->
        <div class="shop-table-container">
            <el-table :data="filteredShops" style="width: 100%" class="table" v-loading="loading">
                <el-table-column type="index" label="序号" width="80" align="center"></el-table-column>

                <!-- 店铺信息列（合并图片和文字） -->
                <el-table-column label="店铺信息" width="280" align="left">
                    <template slot-scope="scope">
                        <div class="shop-info">
                            <div class="shop-avatar">
                                <img
                                    :src="scope.row.image_url"
                                    :alt="scope.row.shop_name"
                                    class="shop-image"
                                    @error="handleImageError"
                                />
                            </div>
                            <div class="shop-details">
                                <div class="shop-name">{{ scope.row.shop_name }}</div>
                                <el-tooltip
                                    effect="dark"
                                    :content="scope.row.description"
                                    placement="top"
                                    v-if="scope.row.description && scope.row.description.length > 20"
                                >
                                    <div class="shop-description">
                                        {{ scope.row.description && scope.row.description.length > 20 ?
                                           scope.row.description.substring(0, 20) + '...' : scope.row.description }}
                                    </div>
                                </el-tooltip>
                                <div class="shop-description" v-else>
                                    {{ scope.row.description }}
                                </div>
                            </div>
                        </div>
                    </template>
                </el-table-column>

                <el-table-column prop="price" label="平均价格" width="120" align="center">
                    <template slot-scope="scope">
                        <span class="price">¥{{ scope.row.price.toFixed(2) }}</span>
                    </template>
                </el-table-column>

                <el-table-column prop="sale" label="月销量" width="120" align="center">
                    <template slot-scope="scope">
                        <div class="sales-info">
                            <span class="sales-number">{{ scope.row.sale }}</span>
                            <el-progress
                                :percentage="getSalesPercentage(scope.row.sale)"
                                :show-text="false"
                                :stroke-width="6"
                                :color="getSalesColor(scope.row.sale)"
                            ></el-progress>
                        </div>
                    </template>
                </el-table-column>

                <!-- 状态列 -->
                <el-table-column label="状态" width="100" align="center">
                    <template slot-scope="scope">
                        <el-tag :type="formatStatusType(scope.row.status)" effect="light" size="small">
                            {{ formatStatus(scope.row.status) }}
                        </el-tag>
                    </template>
                </el-table-column>

                <el-table-column label="操作" width="280" align="center">
                    <template slot-scope="scope">
                        <el-button size="mini" type="primary" @click="manageDishes(scope.row)">
                            <i class="el-icon-dish"></i>菜品
                        </el-button>
                        <el-button size="mini" type="warning" @click="showdia_chg(scope.row)">
                            <i class="el-icon-edit"></i>修改
                        </el-button>
                        <el-button
                            size="mini"
                            :type="scope.row.status === 1 ? 'info' : 'success'"
                            @click="toggleShopStatus(scope.row)"
                            :loading="scope.row.loading"
                        >
                            <i :class="scope.row.status === 1 ? 'el-icon-close' : 'el-icon-check'"></i>
                            {{ scope.row.status === 1 ? '停用' : '启用' }}
                        </el-button>
                        <el-button size="mini" type="danger" @click="showdia_dlt(scope.row)">
                            <i class="el-icon-delete"></i>删除
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-container" v-if="filteredShops.length > pageSize">
                <el-pagination
                    @size-change="handleSizeChange"
                    @current-change="handleCurrentChange"
                    :current-page="currentPage"
                    :page-sizes="[10, 20, 50, 100]"
                    :page-size="pageSize"
                    layout="total, sizes, prev, pager, next, jumper"
                    :total="filteredShops.length"
                >
                </el-pagination>
            </div>
        </div>

        <!-- 添加店铺对话框 -->
        <el-dialog title="添加店铺" :visible.sync="dia_add" width="500px" :before-close="handleDialogClose">
            <el-form ref="add_form" :model="add_form" label-width="100px" :rules="add_form_rules">
                <el-form-item label="店铺名称：" prop="shop_name">
                    <el-input v-model="add_form.shop_name" placeholder="请输入店铺名称"></el-input>
                </el-form-item>
                <el-form-item label="店铺描述：" prop="description">
                    <el-input
                        type="textarea"
                        v-model="add_form.description"
                        placeholder="请输入店铺描述"
                        :rows="3"
                    ></el-input>
                </el-form-item>
                <!-- 图片URL输入 -->
                <el-form-item label="图片URL：" prop="image_url">
                    <el-input v-model="add_form.image_url" placeholder="请输入图片URL路径">
                        <template slot="append">
                            <el-button @click="previewImage(add_form.image_url)">预览</el-button>
                        </template>
                    </el-input>
                </el-form-item>
                <!-- 图片预览 -->
                <el-form-item label="图片预览：" v-if="add_form.image_url">
                    <div class="image-preview">
                        <img :src="add_form.image_url" :alt="add_form.shop_name" class="preview-image" />
                    </div>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click="dia_add = false">取消</el-button>
                <el-button type="primary" @click="addshop()" :loading="submitLoading">
                    {{ submitLoading ? '提交中...' : '添加' }}
                </el-button>
            </div>
        </el-dialog>

        <!-- 修改店铺对话框 -->
        <el-dialog title="修改店铺" :visible.sync="dia_chg" width="500px" :before-close="handleDialogClose">
            <el-form ref="chg_form_ref" :model="chg_form" label-width="100px">
                <el-form-item label="店铺名称：">
                    <span style="font-weight: bold; color: #333;">{{ chg_form.shop_name }}</span>
                </el-form-item>
                <el-form-item label="店铺描述：">
                    <el-input
                        type="textarea"
                        v-model="chg_form.description"
                        placeholder="请输入店铺描述"
                        :rows="3"
                    ></el-input>
                </el-form-item>
                <el-form-item label="店铺状态：">
                    <el-switch
                        v-model="chg_form.status"
                        :active-value="1"
                        :inactive-value="0"
                        active-text="营业中"
                        inactive-text="已停业"
                    ></el-switch>
                </el-form-item>
                <!-- 图片URL输入 -->
                <el-form-item label="图片URL：">
                    <el-input v-model="chg_form.image_url" placeholder="请输入图片URL路径">
                        <template slot="append">
                            <el-button @click="previewImage(chg_form.image_url)">预览</el-button>
                        </template>
                    </el-input>
                </el-form-item>
                <!-- 图片预览 -->
                <el-form-item label="图片预览：" v-if="chg_form.image_url">
                    <div class="image-preview">
                        <img :src="chg_form.image_url" :alt="chg_form.shop_name" class="preview-image" />
                    </div>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click="dia_chg = false">取消</el-button>
                <el-button type="primary" @click="changeshop()" :loading="submitLoading">
                    {{ submitLoading ? '提交中...' : '修改' }}
                </el-button>
            </div>
        </el-dialog>

        <!-- 删除确认对话框 -->
        <el-dialog title="删除店铺" :visible.sync="dia_dlt" width="400px">
            <div style="text-align: center; padding: 20px 0;">
                <i class="el-icon-warning" style="color: #e6a23c; font-size: 48px; margin-bottom: 16px;"></i>
                <p style="font-size: 16px; color: #606266;">确定删除店铺 "{{ want_delete }}" 吗？</p>
                <p style="font-size: 14px; color: #909399; margin-top: 8px;">此操作不可撤销，且会删除该店铺下的所有菜品</p>
            </div>
            <div slot="footer" class="dialog-footer">
                <el-button @click="dia_dlt = false">取消</el-button>
                <el-button type="danger" @click="deleteshop()" :loading="deleteLoading">
                    {{ deleteLoading ? '删除中...' : '确定删除' }}
                </el-button>
            </div>
        </el-dialog>

        <!-- 菜品管理对话框 -->
        <el-dialog
            :title="`管理菜品 - ${currentShop?.shop_name || ''}`"
            :visible.sync="dia_dishes"
            width="90%"
            top="5vh"
            class="dish-management-dialog"
        >
            <div class="dish-management-content">
                <!-- 操作栏 -->
                <div class="dish-operation-bar">
                    <el-button type="primary" icon="el-icon-plus" @click="showAddDishDialog">
                        添加菜品
                    </el-button>
                    <el-button icon="el-icon-refresh" @click="loadDishes">
                        刷新
                    </el-button>
                    <div class="dish-stats">
                        <span>共 {{ dishes.length }} 个菜品</span>
                        <span class="stat-divider">|</span>
                        <span>在售: {{ activeDishCount }}</span>
                        <span class="stat-divider">|</span>
                        <span>停售: {{ inactiveDishCount }}</span>
                    </div>
                </div>

                <!-- 菜品表格 -->
                <el-table :data="dishes" v-loading="dishLoading" style="width: 100%">
                    <el-table-column type="index" label="序号" width="80" align="center"></el-table-column>

                    <el-table-column label="菜品图片" width="120" align="center">
                        <template slot-scope="scope">
                            <div class="dish-image-container">
                                <img
                                    :src="scope.row.image_url"
                                    :alt="scope.row.dish_name"
                                    class="dish-image"
                                    @error="handleDishImageError"
                                />
                            </div>
                        </template>
                    </el-table-column>

                    <el-table-column prop="dish_name" label="菜品名称" min-width="150">
                        <template slot-scope="scope">
                            <div class="dish-info">
                                <div class="dish-name">{{ scope.row.dish_name }}</div>
                                <div class="dish-description">{{ scope.row.description }}</div>
                            </div>
                        </template>
                    </el-table-column>

                    <el-table-column prop="price" label="价格" width="120" align="center">
                        <template slot-scope="scope">
                            <span class="price">¥{{ scope.row.price.toFixed(2) }}</span>
                        </template>
                    </el-table-column>

                    <el-table-column prop="monthly_sales" label="月销量" width="120" align="center">
                        <template slot-scope="scope">
                            <span class="sales">{{ scope.row.monthly_sales }}</span>
                        </template>
                    </el-table-column>

                    <el-table-column prop="sort_order" label="排序" width="100" align="center">
                        <template slot-scope="scope">
                            <el-input-number
                                v-model="scope.row.sort_order"
                                :min="0"
                                :max="999"
                                size="mini"
                                @change="updateDishSort(scope.row)"
                            ></el-input-number>
                        </template>
                    </el-table-column>

                    <el-table-column label="状态" width="100" align="center">
                        <template slot-scope="scope">
                            <el-tag :type="scope.row.status === 1 ? 'success' : 'info'" effect="light" size="small">
                                {{ scope.row.status === 1 ? '在售' : '停售' }}
                            </el-tag>
                        </template>
                    </el-table-column>

                    <el-table-column label="操作" width="200" align="center">
                        <template slot-scope="scope">
                            <el-button size="mini" type="warning" @click="editDish(scope.row)">
                                <i class="el-icon-edit"></i>编辑
                            </el-button>
                            <el-button size="mini" type="danger" @click="deleteDish(scope.row)">
                                <i class="el-icon-delete"></i>删除
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>
        </el-dialog>

        <!-- 添加/编辑菜品对话框 -->
        <el-dialog
            :title="(editingDish ? '编辑' : '添加') + '菜品'"
            :visible.sync="dia_dish_edit"
            width="500px"
        >
            <el-form :model="dishForm" :rules="dishRules" ref="dishFormRef" label-width="100px">
                <el-form-item label="菜品名称：" prop="dish_name">
                    <el-input v-model="dishForm.dish_name" placeholder="请输入菜品名称"></el-input>
                </el-form-item>

                <el-form-item label="价格：" prop="price">
                    <el-input-number
                        v-model="dishForm.price"
                        :min="0.01"
                        :max="1000"
                        :precision="2"
                        controls-position="right"
                        style="width: 100%"
                    ></el-input-number>
                </el-form-item>

                <el-form-item label="描述：">
                    <el-input
                        type="textarea"
                        v-model="dishForm.description"
                        placeholder="请输入菜品描述"
                        :rows="3"
                    ></el-input>
                </el-form-item>

                <el-form-item label="状态：">
                    <el-radio-group v-model="dishForm.status">
                        <el-radio :label="1">在售</el-radio>
                        <el-radio :label="0">停售</el-radio>
                    </el-radio-group>
                </el-form-item>

                <el-form-item label="排序：">
                    <el-input-number
                        v-model="dishForm.sort_order"
                        :min="0"
                        :max="999"
                        controls-position="right"
                    ></el-input-number>
                </el-form-item>

                <el-form-item label="图片URL：">
                    <el-input v-model="dishForm.image_url" placeholder="请输入图片URL">
                        <template slot="append">
                            <el-button @click="previewDishImage(dishForm.image_url)">预览</el-button>
                        </template>
                    </el-input>
                </el-form-item>

                <el-form-item label="图片预览：" v-if="dishForm.image_url">
                    <div class="image-preview">
                        <img :src="dishForm.image_url" :alt="dishForm.dish_name" class="preview-image" />
                    </div>
                </el-form-item>
            </el-form>

            <div slot="footer" class="dialog-footer">
                <el-button @click="dia_dish_edit = false">取消</el-button>
                <el-button type="primary" @click="saveDish" :loading="dishSubmitLoading">
                    {{ dishSubmitLoading ? '提交中...' : '保存' }}
                </el-button>
            </div>
        </el-dialog>
    </div>
</template>

<script>
export default {
    name: 'ManageShop',
    created() {
        this.getdata()
    },
    data() {
        return {
            tableData: [],
            loading: false,
            submitLoading: false,
            deleteLoading: false,
            dia_add: false,
            dia_chg: false,
            dia_dlt: false,
            searchKeyword: '',
            filterSales: '',
            filterStatus: '',
            currentPage: 1,
            pageSize: 10,
            defaultImage: '/images/shop/default-shop.jpg',
            add_form: {
                shop_name: '',
                description: '',
                image_url: '',
                status: 1,
                action: "add",
            },
            chg_form: {
                shop_id: '',
                shop_name: '',
                description: '',
                image_url: '',
                status: 1,
                action: "change",
            },
            want_delete: '',
            want_delete_id: '',
            add_form_rules: {
                shop_name: [{ required: true, message: '请输入店铺名称', trigger: 'blur' }],
                description: [{ required: true, message: '请输入店铺描述', trigger: 'blur' }]
            },

            // 菜品管理相关
            dia_dishes: false,
            dia_dish_edit: false,
            currentShop: null,
            dishes: [],
            dishLoading: false,
            dishSubmitLoading: false,
            editingDish: null,
            dishForm: {
                dish_name: '',
                price: 0,
                description: '',
                image_url: '/images/dish/default-dish.jpg',
                sort_order: 0,
                status: 1  // 默认在售
            },
            dishRules: {
                dish_name: [
                    { required: true, message: '请输入菜品名称', trigger: 'blur' }
                ],
                price: [
                    { required: true, message: '请输入价格', trigger: 'blur' }
                ]
            }
        }
    },
    computed: {
        filteredShops() {
            let result = [...this.tableData];

            // 搜索过滤
            if (this.searchKeyword) {
                result = result.filter(shop =>
                    shop.shop_name.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
                    (shop.description && shop.description.toLowerCase().includes(this.searchKeyword.toLowerCase()))
                );
            }

            // 销量过滤
            if (this.filterSales) {
                switch (this.filterSales) {
                    case 'high':
                        result = result.filter(shop => shop.sale >= 100);
                        break;
                    case 'medium':
                        result = result.filter(shop => shop.sale >= 50 && shop.sale < 100);
                        break;
                    case 'low':
                        result = result.filter(shop => shop.sale < 50);
                        break;
                }
            }

            // 状态过滤
            if (this.filterStatus !== '') {
                result = result.filter(shop => shop.status == this.filterStatus);
            }

            // 分页
            const start = (this.currentPage - 1) * this.pageSize;
            const end = start + this.pageSize;
            return result.slice(start, end);
        },
         averageSales() {
            if (this.tableData.length === 0) return 0;
            // 改成用总销量算平均（这是大家习惯的算法）
            const totalSales = this.tableData.reduce((sum, shop) => sum + shop.sale, 0);
            return Math.round(totalSales / this.tableData.length);
        },
        hotShopCount() {
            return this.tableData.filter(shop => shop.sale >= 100).length;
        },
        activeShopCount() {
            return this.tableData.filter(shop => shop.status === 1).length;
        },

        // 菜品统计
        activeDishCount() {
            return this.dishes.filter(dish => dish.status === 1).length;
        },
        inactiveDishCount() {
            return this.dishes.filter(dish => dish.status === 0).length;
        }
    },
    methods: {
        getdata() {
            this.loading = true;
            this.$axios.get("/api/manager/shop").then((res) => {
                console.log(res.data);
                if (res.data.status == 200) {
                    // 为每个店铺添加loading状态
                    this.tableData = res.data.tabledata.map(shop => ({
                        ...shop,
                        loading: false
                    }));
                }
            }).catch(error => {
                console.error('获取数据失败:', error);
                this.$message.error('获取数据失败');
            }).finally(() => {
                this.loading = false;
            });
        },
        showdia_add() {
            this.dia_add = true;
            this.add_form = {
                shop_name: '',
                description: '',
                image_url: '',
                status: 1,
                action: "add",
            };
        },
        addshop() {
            this.$refs.add_form.validate(valid => {
                if (!valid) return;

                this.submitLoading = true;
                this.$axios.post("/api/manager/shop", this.add_form).then((res) => {
                    console.log(res.data);
                    if (res.data.status == 200) {
                        this.$message({
                            message: "添加成功",
                            type: "success"
                        })
                        this.dia_add = false;
                        this.getdata();
                    } else {
                        this.$message({
                            message: res.data.msg,
                            type: "error"
                        })
                    }
                }).catch(error => {
                    console.error('添加失败:', error);
                    this.$message.error('添加失败');
                }).finally(() => {
                    this.submitLoading = false;
                });
            })
        },
        showdia_chg(row) {
            this.chg_form = {
                shop_id: row.shop_id,
                shop_name: row.shop_name,
                description: row.description || '',
                image_url: row.image_url || '',
                status: row.status,
                action: "change",
            };
            this.dia_chg = true;
        },
        changeshop() {
            this.submitLoading = true;
            this.$axios.post("/api/manager/shop", this.chg_form).then((res) => {
                console.log(res.data);
                if (res.data.status == 200) {
                    this.$message({
                        message: "修改成功",
                        type: "success"
                    })
                    this.dia_chg = false;
                    this.getdata();
                } else {
                    this.$message({
                        message: res.data.msg || '修改失败',
                        type: "error"
                    })
                }
            }).catch(error => {
                console.error('修改失败:', error);
                this.$message.error('修改失败');
            }).finally(() => {
                this.submitLoading = false;
            });
        },
        showdia_dlt(row) {
            this.want_delete = row.shop_name;
            this.want_delete_id = row.shop_id;
            this.dia_dlt = true;
        },
        deleteshop() {
            this.deleteLoading = true;
            this.$axios.delete("/api/manager/shop", {
                data: { shop_id: this.want_delete_id }
            }).then((res) => {
                if (res.data.status == 200) {
                    this.$message({
                        message: res.data.msg,
                        type: "success"
                    })
                    this.getdata()
                    this.dia_dlt = false;
                } else {
                    this.$message({
                        message: res.data.msg || '删除失败',
                        type: "error"
                    })
                }
            }).catch(error => {
                console.error('删除失败:', error);
                this.$message.error('删除失败');
            }).finally(() => {
                this.deleteLoading = false;
            });
        },
        // 切换店铺状态
        toggleShopStatus(row) {
            const newStatus = row.status === 1 ? 0 : 1;
            const action = newStatus === 1 ? '启用' : '停用';

            this.$confirm(`确定要${action}店铺"${row.shop_name}"吗？`, '提示', {
                type: 'warning'
            }).then(() => {
                // 使用新的专用接口
                this.$axios.post("/api/manager/shop/status", {
                    shop_id: row.shop_id,
                    status: newStatus
                }).then((res) => {
                    if (res.data.status == 200) {
                        this.$message.success(`${action}成功`);
                        // 直接更新当前行的状态，避免重新加载所有数据
                        row.status = newStatus;
                    } else {
                        this.$message.error(res.data.msg || `${action}失败`);
                    }
                }).catch(error => {
                    console.error(`${action}失败:`, error);
                    this.$message.error(`${action}失败`);
                });
            }).catch(() => {
                // 用户取消操作
                this.$message.info('已取消操作');
            });
        },
        // 格式化状态显示
        formatStatus(status) {
            return status === 1 ? '营业中' : '已停业';
        },
        formatStatusType(status) {
            return status === 1 ? 'success' : 'danger';
        },
        handleSearch() {
            this.currentPage = 1;
        },
        handleFilter() {
            this.currentPage = 1;
        },
        handleSizeChange(val) {
            this.pageSize = val;
            this.currentPage = 1;
        },
        handleCurrentChange(val) {
            this.currentPage = val;
        },
        handleDialogClose() {
            this.dia_add = false;
            this.dia_chg = false;
            if (this.$refs.add_form) {
                this.$refs.add_form.clearValidate();
            }
        },
        getSalesPercentage(sales) {
            if (this.tableData.length === 0) return 0;
            const maxSales = Math.max(...this.tableData.map(shop => shop.sale));
            return maxSales > 0 ? Math.round((sales / maxSales) * 100) : 0;
        },
        getSalesColor(sales) {
            if (sales >= 100) return '#f56c6c';
            if (sales >= 50) return '#e6a23c';
            return '#67c23a';
        },
        // 图片加载失败处理
        handleImageError(event) {
            event.target.src = this.defaultImage;
        },
        // 图片预览
        previewImage(url) {
            if (url) {
                window.open(url, '_blank');
            } else {
                this.$message.warning('请输入图片URL');
            }
        },

        // 菜品管理相关方法
        // 管理菜品
        manageDishes(shop) {
            this.currentShop = shop;
            this.dia_dishes = true;
            this.loadDishes();
        },

        // 加载菜品列表
        loadDishes() {
            if (!this.currentShop) return;

            this.dishLoading = true;
            this.$axios.get(`/api/manager/shop/${this.currentShop.shop_id}/dishes`)
                .then(res => {
                    if (res.data.status === 200) {
                        this.dishes = res.data.data;
                    }
                })
                .catch(error => {
                    console.error('加载菜品失败:', error);
                    this.$message.error('加载菜品失败');
                })
                .finally(() => {
                    this.dishLoading = false;
                });
        },

        // 显示添加菜品对话框
        showAddDishDialog() {
            this.editingDish = null;
            this.dishForm = {
                dish_name: '',
                price: 0,
                description: '',
                image_url: '/images/dish/default-dish.jpg',
                sort_order: 0,
                status: 1  // 默认在售
            };
            this.dia_dish_edit = true;
        },

        // 编辑菜品
        editDish(dish) {
            this.editingDish = dish;
            this.dishForm = { ...dish };
            this.dia_dish_edit = true;
        },

        // 保存菜品
        saveDish() {
            this.$refs.dishFormRef.validate(valid => {
                if (!valid) return;

                this.dishSubmitLoading = true;
                const url = `/api/manager/shop/${this.currentShop.shop_id}/dishes`;
                const method = this.editingDish ? 'put' : 'post';
                const data = { ...this.dishForm };

                if (this.editingDish) {
                    data.dish_id = this.editingDish.dish_id;
                }

                this.$axios({ method, url, data })
                    .then(res => {
                        if (res.data.status === 200) {
                            this.$message.success(res.data.msg);
                            this.dia_dish_edit = false;
                            this.loadDishes();
                        } else {
                            this.$message.error(res.data.msg);
                        }
                    })
                    .catch(error => {
                        console.error('保存菜品失败:', error);
                        this.$message.error('保存菜品失败');
                    })
                    .finally(() => {
                        this.dishSubmitLoading = false;
                    });
            });
        },

        // 删除菜品
        deleteDish(dish) {
            this.$confirm(`确定删除菜品"${dish.dish_name}"吗？`, '提示', {
                type: 'warning'
            }).then(() => {
                this.$axios.delete(`/api/manager/shop/${this.currentShop.shop_id}/dishes`, {
                    data: { dish_id: dish.dish_id }
                }).then(res => {
                    if (res.data.status === 200) {
                        this.$message.success(res.data.msg);
                        this.loadDishes();
                    } else {
                        this.$message.error(res.data.msg);
                    }
                }).catch(error => {
                    console.error('删除菜品失败:', error);
                    this.$message.error('删除菜品失败');
                });
            });
        },

        // 更新菜品排序
        updateDishSort(dish) {
            this.$axios.put(`/api/manager/shop/${this.currentShop.shop_id}/dishes`, {
                dish_id: dish.dish_id,
                sort_order: dish.sort_order
            }).then(res => {
                if (res.data.status !== 200) {
                    this.$message.error('更新排序失败');
                }
            }).catch(error => {
                console.error('更新排序失败:', error);
                this.$message.error('更新排序失败');
            });
        },

        // 菜品图片加载失败处理
        handleDishImageError(event) {
            event.target.src = '/images/dish/default-dish.jpg';
        },

        // 预览菜品图片
        previewDishImage(url) {
            if (url) {
                window.open(url, '_blank');
            } else {
                this.$message.warning('请输入图片URL');
            }
        }
    }
}
</script>

<style scoped>
.shop-management {
    padding: 20px;
}

.management-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
}

.stat-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.stat-icon {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;
}

.stat-icon i {
    font-size: 28px;
    color: white;
}

.stat-content h3 {
    margin: 0 0 8px 0;
    color: #666;
    font-size: 14px;
}

.stat-content .number {
    margin: 0;
    font-size: 28px;
    font-weight: bold;
    color: #333;
}

.operation-bar {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.search-section {
    display: flex;
    gap: 15px;
    align-items: center;
}

.action-section {
    display: flex;
    gap: 10px;
}

.shop-table-container {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    overflow-x: auto;
}

/* 店铺图片样式 */
.shop-image-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 60px;
}

.shop-image {
    width: 50px;
    height: 50px;
    object-fit: cover;
    border-radius: 6px;
    border: 1px solid #eaeaea;
}

.shop-info {
    display: flex;
    align-items: flex-start;
    text-align: left;
    padding: 8px 0;
}

.shop-avatar {
    margin-right: 12px;
    flex-shrink: 0;
}

.shop-details {
    flex: 1;
    min-width: 0;
}

.shop-name {
    font-weight: 600;
    color: #333;
    font-size: 14px;
    margin-bottom: 4px;
    line-height: 1.4;
}

.shop-description {
    font-size: 12px;
    color: #666;
    line-height: 1.4;
    word-wrap: break-word;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* 优化价格显示 */
.price {
    font-weight: bold;
    color: #e6a23c;
    font-size: 14px;
}

/* 优化销量显示 */
.sales-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
}

.sales-number {
    font-weight: 600;
    color: #333;
    font-size: 14px;
}

/* 优化操作按钮 */
.el-button--mini {
    padding: 5px 8px;
    margin: 2px;
}

.pagination-container {
    display: flex;
    justify-content: center;
    margin-top: 20px;
    padding: 20px 0 0 0;
}

.dialog-footer {
    text-align: center;
}

/* 图片预览样式 */
.image-preview {
    display: flex;
    justify-content: center;
    margin-top: 10px;
}

.preview-image {
    max-width: 200px;
    max-height: 150px;
    object-fit: cover;
    border-radius: 6px;
    border: 1px solid #eaeaea;
}

/* 响应式调整 */
@media (max-width: 1200px) {
    .shop-info {
        min-width: 250px;
    }
}

@media (max-width: 768px) {
    .shop-info {
        min-width: 200px;
    }

    .shop-description {
        -webkit-line-clamp: 1;
    }

    .operation-bar {
        flex-direction: column;
        gap: 15px;
        align-items: stretch;
    }

    .search-section {
        flex-direction: column;
    }

    .search-section .el-input,
    .search-section .el-select {
        width: 100% !important;
    }
}

/* 菜品管理对话框样式 */
.dish-management-dialog .el-dialog__body {
    padding: 20px;
    max-height: 70vh;
    overflow-y: auto;
}

.dish-operation-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 15px;
    background: #f5f7fa;
    border-radius: 8px;
}

.dish-stats {
    display: flex;
    align-items: center;
    color: #666;
    font-size: 14px;
}

.stat-divider {
    margin: 0 12px;
    color: #dcdfe6;
}

/* 菜品图片样式 */
.dish-image-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 60px;
}

.dish-image {
    width: 50px;
    height: 50px;
    object-fit: cover;
    border-radius: 6px;
    border: 1px solid #eaeaea;
}

/* 菜品信息样式 */
.dish-info {
    text-align: left;
}

.dish-name {
    font-weight: 600;
    color: #333;
    margin-bottom: 4px;
}

.dish-description {
    font-size: 12px;
    color: #999;
    line-height: 1.4;
}

/* 销量样式 */
.sales {
    font-weight: 600;
    color: #f56c6c;
}

/* 响应式调整 */
@media (max-width: 768px) {
    .dish-operation-bar {
        flex-direction: column;
        gap: 10px;
        align-items: flex-start;
    }

    .dish-stats {
        flex-wrap: wrap;
        gap: 8px;
    }

    .stat-divider {
        display: none;
    }
}
</style>