<template>
    <div class="address-management-container">
        <div class="header">
            <h2>地址管理</h2>
            <p class="subtitle">管理您的收货地址</p>
        </div>

        <div class="content-body">
            <div class="address-container">
                <!-- 操作按钮区域 -->
                <div class="action-header">
                    <el-button
                        type="primary"
                        icon="el-icon-circle-plus"
                        @click="showAddDialog"
                        class="add-btn">
                        新增地址
                    </el-button>
                    <div class="search-box">
                        <el-input
                            v-model="searchKeyword"
                            placeholder="搜索地址..."
                            prefix-icon="el-icon-search"
                            clearable
                            @clear="clearSearch"
                            @input="handleSearch"
                            style="width: 300px;">
                        </el-input>
                    </div>
                </div>

                <!-- 地址列表 -->
                <div class="address-list" v-loading="loading">
                    <el-empty
                        v-if="filteredAddresses.length === 0 && !loading"
                        description="暂无收货地址"
                        :image-size="200">
                        <el-button
                            type="primary"
                            icon="el-icon-circle-plus"
                            @click="showAddDialog">
                            添加第一个地址
                        </el-button>
                    </el-empty>

                    <div class="address-grid" v-else>
                        <el-card
                            v-for="address in pagedAddresses"
                            :key="address.address_id"
                            class="address-card"
                            :class="{ 'default-address': address.is_default }"
                            shadow="hover">
                            <div class="address-header">
                                <div class="address-tags">
                                    <el-tag
                                        v-if="address.is_default"
                                        type="success"
                                        size="small"
                                        effect="dark">
                                        <i class="el-icon-star-on"></i>
                                        默认地址
                                    </el-tag>
                                    <el-tag
                                        v-if="address.address_label"
                                        :type="getAddressLabelColor(address.address_label)"
                                        size="small">
                                        {{ getAddressLabelText(address.address_label) }}
                                    </el-tag>
                                </div>
                                <div class="address-actions">
                                    <el-tooltip content="设为默认" placement="top" v-if="!address.is_default">
                                        <el-button
                                            type="text"
                                            icon="el-icon-star-off"
                                            @click="setDefaultAddress(address.address_id)"
                                            size="small">
                                        </el-button>
                                    </el-tooltip>
                                    <el-tooltip content="编辑" placement="top">
                                        <el-button
                                            type="text"
                                            icon="el-icon-edit"
                                            @click="editAddress(address)"
                                            size="small">
                                        </el-button>
                                    </el-tooltip>
                                    <el-tooltip content="删除" placement="top">
                                        <el-button
                                            type="text"
                                            icon="el-icon-delete"
                                            @click="deleteAddress(address.address_id)"
                                            class="delete-btn"
                                            size="small">
                                        </el-button>
                                    </el-tooltip>
                                </div>
                            </div>

                            <div class="address-content">
                                <div class="address-info">
                                    <div class="consignee-info">
                                        <span class="consignee-name">{{ address.cons_name || '未设置' }}</span>
                                        <span class="consignee-phone">{{ address.cons_phone || '未设置' }}</span>
                                    </div>
                                    <div class="address-detail">
                                        <p class="detail-text">
                                            <i class="el-icon-location-information"></i>
                                            {{ address.province }}{{ address.city }}{{ address.district }}{{ address.street }}
                                        </p>
                                    </div>
                                </div>

                                <div class="address-operations">
                                    <el-button
                                        type="primary"
                                        size="small"
                                        @click="useAddress(address)"
                                        plain>
                                        使用此地址
                                    </el-button>
                                </div>
                            </div>
                        </el-card>
                    </div>
                </div>

                <!-- 分页 -->
                <div class="pagination-container" v-if="filteredAddresses.length > 0 && total > pageSize">
                    <el-pagination
                        @size-change="handleSizeChange"
                        @current-change="handleCurrentChange"
                        :current-page="currentPage"
                        :page-sizes="[10, 20, 30, 50]"
                        :page-size="pageSize"
                        layout="total, sizes, prev, pager, next, jumper"
                        :total="total">
                    </el-pagination>
                </div>
            </div>
        </div>

        <!-- 新增/编辑地址对话框 -->
        <el-dialog
            :title="dialogTitle"
            :visible.sync="dialogVisible"
            width="600px"
            @close="resetDialog">
            <el-form
                ref="addressForm"
                :model="addressForm"
                :rules="addressRules"
                label-width="100px"
                class="address-form">
                <el-form-item label="收货人：" prop="cons_name">
                    <el-input
                        v-model="addressForm.cons_name"
                        placeholder="请输入收货人姓名"
                        maxlength="20"
                        show-word-limit>
                    </el-input>
                </el-form-item>

                <el-form-item label="联系电话：" prop="cons_phone">
                    <el-input
                        v-model="addressForm.cons_phone"
                        placeholder="请输入联系电话"
                        maxlength="11">
                    </el-input>
                </el-form-item>

                <el-form-item label="所在地区：" required>
                    <div class="region-selectors">
                        <el-select
                            v-model="addressForm.province"
                            placeholder="请选择省份"
                            @change="handleProvinceChange"
                            style="width: 32%; margin-right: 2%;">
                            <el-option
                                v-for="province in provinceOptions"
                                :key="province.value"
                                :label="province.label"
                                :value="province.value">
                            </el-option>
                        </el-select>

                        <el-select
                            v-model="addressForm.city"
                            placeholder="请选择城市"
                            @change="handleCityChange"
                            style="width: 32%; margin-right: 2%;"
                            :disabled="!addressForm.province">
                            <el-option
                                v-for="city in cityOptions"
                                :key="city.value"
                                :label="city.label"
                                :value="city.value">
                            </el-option>
                        </el-select>

                        <el-select
                            v-model="addressForm.district"
                            placeholder="请选择区县"
                            style="width: 32%;"
                            :disabled="!addressForm.city">
                            <el-option
                                v-for="district in districtOptions"
                                :key="district.value"
                                :label="district.label"
                                :value="district.value">
                            </el-option>
                        </el-select>
                    </div>
                    <div v-if="regionErrors.province || regionErrors.city || regionErrors.district" class="region-errors">
                        <span v-if="regionErrors.province" class="error-text">{{ regionErrors.province }}</span>
                        <span v-if="regionErrors.city" class="error-text">{{ regionErrors.city }}</span>
                        <span v-if="regionErrors.district" class="error-text">{{ regionErrors.district }}</span>
                    </div>
                </el-form-item>

                <el-form-item label="详细地址：" prop="street">
                    <el-input
                        v-model="addressForm.street"
                        type="textarea"
                        :rows="3"
                        placeholder="请输入详细地址（如街道、小区、门牌号等）"
                        maxlength="200"
                        show-word-limit>
                    </el-input>
                </el-form-item>

                <el-form-item label="地址标签：" prop="address_label">
                    <el-select
                        v-model="addressForm.address_label"
                        placeholder="请选择地址标签"
                        style="width: 100%">
                        <el-option label="家" value="home"></el-option>
                        <el-option label="公司" value="company"></el-option>
                        <el-option label="学校" value="school"></el-option>
                        <el-option label="其他" value="other"></el-option>
                    </el-select>
                </el-form-item>

                <el-form-item label="设为默认：" prop="is_default">
                    <el-switch
                        v-model="addressForm.is_default"
                        active-text="是"
                        inactive-text="否">
                    </el-switch>
                    <p class="hint-text">设置为默认地址后，下单时会优先使用此地址</p>
                </el-form-item>
            </el-form>

            <div slot="footer" class="dialog-footer">
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button
                    type="primary"
                    @click="saveAddress"
                    :loading="saving">
                    {{ isEditing ? '更新地址' : '保存地址' }}
                </el-button>
            </div>
        </el-dialog>

        <!-- 确认删除对话框 -->
        <el-dialog
            title="删除地址"
            :visible.sync="deleteDialogVisible"
            width="400px">
            <div class="delete-confirm">
                <i class="el-icon-warning warning-icon"></i>
                <div class="delete-content">
                    <p>确定要删除这个收货地址吗？</p>
                    <p class="delete-hint">删除后将无法恢复</p>
                </div>
            </div>
            <div slot="footer" class="dialog-footer">
                <el-button @click="deleteDialogVisible = false">取消</el-button>
                <el-button
                    type="danger"
                    @click="confirmDelete"
                    :loading="deleting">
                    确定删除
                </el-button>
            </div>
        </el-dialog>
    </div>
</template>

<script>
export default {
    name: 'AddressManagement',
    created() {
        this.loadAddresses();
        this.initRegionData();
    },
    data() {
        // 电话号码验证
        const validatePhone = (rule, value, callback) => {
            if (!value) {
                callback(new Error('请输入联系电话'));
            } else if (!/^1[3-9]\d{9}$/.test(value)) {
                callback(new Error('请输入正确的手机号码'));
            } else {
                callback();
            }
        };

        return {
            // 地址列表数据
            addresses: [],
            filteredAddresses: [],
            loading: false,
            saving: false,
            deleting: false,

            // 分页相关
            currentPage: 1,
            pageSize: 10,
            total: 0,

            // 搜索相关
            searchKeyword: '',

            // 对话框相关
            dialogVisible: false,
            deleteDialogVisible: false,
            isEditing: false,
            editingAddressId: null,
            dialogTitle: '新增收货地址',

            // 地址表单数据
            addressForm: {
                cons_name: '',
                cons_phone: '',
                province: '',
                city: '',
                district: '',
                street: '',
                address_label: 'home',
                is_default: false
            },

            // 地区选择相关
            provinceOptions: [],
            cityOptions: [],
            districtOptions: [],
            regionErrors: {
                province: '',
                city: '',
                district: ''
            },

            // 删除相关
            addressToDelete: null,

            // 表单验证规则
            addressRules: {
                cons_name: [
                    { required: true, message: '请输入收货人姓名', trigger: 'blur' },
                    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
                ],
                cons_phone: [
                    { required: true, validator: validatePhone, trigger: 'blur' }
                ],
                street: [
                    { required: true, message: '请输入详细地址', trigger: 'blur' },
                    { min: 5, max: 200, message: '长度在 5 到 200 个字符', trigger: 'blur' }
                ],
                address_label: [
                    { required: true, message: '请选择地址标签', trigger: 'change' }
                ]
            }
        }
    },
    computed: {
        // 计算分页后的地址
        pagedAddresses() {
            const start = (this.currentPage - 1) * this.pageSize;
            const end = start + this.pageSize;
            return this.filteredAddresses.slice(start, end);
        }
    },
    methods: {
        // 加载地址列表
        loadAddresses() {
            this.loading = true;
            // 这里假设后端API返回的字段名与数据库一致
            this.$axios.get("/api/user/addresses")
                .then((res) => {
                    if (res.data.status === 200) {
                        this.addresses = res.data.data || [];
                        this.filteredAddresses = [...this.addresses];
                        this.total = this.filteredAddresses.length;
                        this.$message.success('地址列表加载成功');
                    } else {
                        this.$message.error(res.data.msg || '加载地址列表失败');
                    }
                })
                .catch((error) => {
                    console.error('加载地址列表失败:', error);
                    this.$message.error('加载地址列表失败');
                })
                .finally(() => {
                    this.loading = false;
                });
        },

        // 初始化地区数据
        initRegionData() {
            // 这里使用简化的地区数据，实际项目中应该从API获取完整数据
            this.provinceOptions = [
                { value: '河南省', label: '河南省' },
                { value: '北京市', label: '北京市' },
                { value: '上海市', label: '上海市' },
                { value: '广东省', label: '广东省' },
                { value: '浙江省', label: '浙江省' }
            ];
        },

        // 省份变化处理
        handleProvinceChange(value) {
            this.addressForm.city = '';
            this.addressForm.district = '';
            this.cityOptions = [];
            this.districtOptions = [];

            // 清除错误信息
            this.regionErrors.province = '';

            // 模拟根据省份获取城市数据
            if (value) {
                if (value === '河南省') {
                    this.cityOptions = [
                        { value: '郑州市', label: '郑州市' },
                        { value: '洛阳市', label: '洛阳市' },
                        { value: '开封市', label: '开封市' }
                    ];
                } else if (value === '北京市') {
                    this.cityOptions = [
                        { value: '北京市', label: '北京市' }
                    ];
                } else if (value === '广东省') {
                    this.cityOptions = [
                        { value: '广州市', label: '广州市' },
                        { value: '深圳市', label: '深圳市' },
                        { value: '珠海市', label: '珠海市' }
                    ];
                } else {
                    this.cityOptions = [
                        { value: `${value}市`, label: `${value}市` }
                    ];
                }
            }
        },

        // 城市变化处理
        handleCityChange(value) {
            this.addressForm.district = '';
            this.districtOptions = [];

            // 清除错误信息
            this.regionErrors.city = '';

            // 模拟根据城市获取区县数据
            if (value) {
                if (value === '郑州市') {
                    this.districtOptions = [
                        { value: '二七区', label: '二七区' },
                        { value: '金水区', label: '金水区' },
                        { value: '中原区', label: '中原区' },
                        { value: '管城回族区', label: '管城回族区' },
                        { value: '惠济区', label: '惠济区' }
                    ];
                } else if (value === '北京市') {
                    this.districtOptions = [
                        { value: '东城区', label: '东城区' },
                        { value: '西城区', label: '西城区' },
                        { value: '朝阳区', label: '朝阳区' },
                        { value: '海淀区', label: '海淀区' }
                    ];
                } else if (value === '广州市') {
                    this.districtOptions = [
                        { value: '天河区', label: '天河区' },
                        { value: '越秀区', label: '越秀区' },
                        { value: '海珠区', label: '海珠区' },
                        { value: '荔湾区', label: '荔湾区' }
                    ];
                } else {
                    this.districtOptions = [
                        { value: '中心区', label: '中心区' },
                        { value: '新区', label: '新区' }
                    ];
                }
            }
        },

        // 验证地区选择
        validateRegion() {
            this.regionErrors = { province: '', city: '', district: '' };
            let isValid = true;

            if (!this.addressForm.province) {
                this.regionErrors.province = '请选择省份';
                isValid = false;
            }

            if (!this.addressForm.city) {
                this.regionErrors.city = '请选择城市';
                isValid = false;
            }

            if (!this.addressForm.district) {
                this.regionErrors.district = '请选择区县';
                isValid = false;
            }

            return isValid;
        },

        // 显示新增地址对话框
        showAddDialog() {
            this.isEditing = false;
            this.dialogTitle = '新增收货地址';
            this.dialogVisible = true;
            this.$nextTick(() => {
                if (this.$refs.addressForm) {
                    this.$refs.addressForm.clearValidate();
                }
            });
        },

        // 编辑地址
        editAddress(address) {
            this.isEditing = true;
            this.editingAddressId = address.address_id;
            this.dialogTitle = '编辑收货地址';

            // 填充表单数据
            Object.assign(this.addressForm, {
                cons_name: address.cons_name,
                cons_phone: address.cons_phone,
                province: address.province,
                city: address.city,
                district: address.district,
                street: address.street,
                address_label: address.address_label || 'home',
                is_default: address.is_default || false
            });

            // 初始化地区选择器
            this.handleProvinceChange(address.province);
            if (address.city) {
                this.handleCityChange(address.city);
            }

            this.dialogVisible = true;
            this.$nextTick(() => {
                if (this.$refs.addressForm) {
                    this.$refs.addressForm.clearValidate();
                }
            });
        },

        // 保存地址（新增或更新）
        saveAddress() {
            // 先验证地区选择
            if (!this.validateRegion()) {
                this.$message.warning('请完善地区信息');
                return;
            }

            this.$refs.addressForm.validate((valid) => {
                if (valid) {
                    this.saving = true;

                    const addressData = {
                        cons_name: this.addressForm.cons_name,
                        cons_phone: this.addressForm.cons_phone,
                        province: this.addressForm.province,
                        city: this.addressForm.city,
                        district: this.addressForm.district,
                        street: this.addressForm.street,
                        address_label: this.addressForm.address_label,
                        is_default: this.addressForm.is_default ? 1 : 0
                    };

                    let apiUrl = "/api/user/addresses";
                    let method = 'post';

                    if (this.isEditing) {
                        apiUrl = `/api/user/addresses/${this.editingAddressId}`;
                        method = 'put';
                    }

                    this.$axios[method](apiUrl, addressData)
                        .then((res) => {
                            if (res.data.status === 200) {
                                this.$message.success(
                                    this.isEditing ? '地址更新成功' : '地址添加成功'
                                );
                                this.dialogVisible = false;
                                this.loadAddresses(); // 重新加载地址列表
                            } else {
                                this.$message.error(res.data.msg || '操作失败');
                            }
                        })
                        .catch((error) => {
                            console.error('保存地址失败:', error);
                            this.$message.error('保存地址失败');
                        })
                        .finally(() => {
                            this.saving = false;
                        });
                } else {
                    this.$message.warning('请完善表单信息');
                    return false;
                }
            });
        },

        // 删除地址
        deleteAddress(addressId) {
            this.addressToDelete = addressId;
            this.deleteDialogVisible = true;
        },

        // 确认删除
        confirmDelete() {
            this.deleting = true;
            this.$axios.delete(`/api/user/addresses/${this.addressToDelete}`)
                .then((res) => {
                    if (res.data.status === 200) {
                        this.$message.success('地址删除成功');
                        this.deleteDialogVisible = false;
                        this.loadAddresses(); // 重新加载地址列表
                    } else {
                        this.$message.error(res.data.msg || '删除失败');
                    }
                })
                .catch((error) => {
                    console.error('删除地址失败:', error);
                    this.$message.error('删除地址失败');
                })
                .finally(() => {
                    this.deleting = false;
                    this.addressToDelete = null;
                });
        },

        // 设置为默认地址
        setDefaultAddress(addressId) {
            this.$axios.patch(`/api/user/addresses/${addressId}/set-default`)
                .then((res) => {
                    if (res.data.status === 200) {
                        this.$message.success('已设置为默认地址');
                        this.loadAddresses(); // 重新加载地址列表
                    } else {
                        this.$message.error(res.data.msg || '设置失败');
                    }
                })
                .catch((error) => {
                    console.error('设置默认地址失败:', error);
                    this.$message.error('设置默认地址失败');
                });
        },

        // 使用此地址（例如在下单时使用）
        useAddress(address) {
            // 触发事件，通知父组件或其他组件使用这个地址
            this.$emit('address-selected', address);
            this.$message.success('已选择地址：' + address.province + address.city + address.district + address.street);
        },

        // 重置对话框
        resetDialog() {
            this.addressForm = {
                cons_name: '',
                cons_phone: '',
                province: '',
                city: '',
                district: '',
                street: '',
                address_label: 'home',
                is_default: false
            };
            this.cityOptions = [];
            this.districtOptions = [];
            this.regionErrors = { province: '', city: '', district: '' };
            this.isEditing = false;
            this.editingAddressId = null;
            if (this.$refs.addressForm) {
                this.$refs.addressForm.clearValidate();
            }
        },

        // 处理搜索
        handleSearch() {
            if (!this.searchKeyword.trim()) {
                this.filteredAddresses = [...this.addresses];
            } else {
                const keyword = this.searchKeyword.toLowerCase();
                this.filteredAddresses = this.addresses.filter(address =>
                    (address.cons_name && address.cons_name.toLowerCase().includes(keyword)) ||
                    (address.cons_phone && address.cons_phone.includes(keyword)) ||
                    (address.street && address.street.toLowerCase().includes(keyword)) ||
                    (address.province && address.province.toLowerCase().includes(keyword)) ||
                    (address.city && address.city.toLowerCase().includes(keyword)) ||
                    (address.district && address.district.toLowerCase().includes(keyword))
                );
            }
            this.total = this.filteredAddresses.length;
            this.currentPage = 1;
        },

        // 清空搜索
        clearSearch() {
            this.filteredAddresses = [...this.addresses];
            this.total = this.filteredAddresses.length;
            this.currentPage = 1;
        },

        // 获取地址标签颜色
        getAddressLabelColor(label) {
            const colors = {
                'home': 'success',
                'company': 'warning',
                'school': 'primary',
                'other': 'info'
            };
            return colors[label] || 'info';
        },

        // 获取地址标签文本
        getAddressLabelText(label) {
            const texts = {
                'home': '家',
                'company': '公司',
                'school': '学校',
                'other': '其他'
            };
            return texts[label] || '其他';
        },

        // 分页大小改变
        handleSizeChange(val) {
            this.pageSize = val;
            this.currentPage = 1;
        },

        // 当前页改变
        handleCurrentChange(val) {
            this.currentPage = val;
        }
    }
}
</script>

<style scoped>
.address-management-container {
    min-height: 100vh;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 20px;
}

.header {
    background: linear-gradient(135deg, #36d1dc 0%, #5b86e5 100%);
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
    width: 90%;
    margin: 0 auto;
    padding: 30px;
}

/* 操作头部 */
.action-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

.add-btn {
    padding: 10px 25px;
    font-size: 16px;
    font-weight: 500;
}

.search-box {
    display: flex;
    align-items: center;
    gap: 15px;
}

/* 地址列表 */
.address-list {
    min-height: 400px;
}

.address-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

/* 地址卡片 */
.address-card {
    border: 2px solid transparent;
    border-radius: 12px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.address-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
}

.address-card.default-address {
    border-color: #67c23a;
    background: linear-gradient(135deg, rgba(103, 194, 58, 0.05) 0%, rgba(103, 194, 58, 0.1) 100%);
}

.address-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #f0f0f0;
}

.address-tags {
    display: flex;
    gap: 8px;
}

.address-actions {
    display: flex;
    gap: 5px;
}

.address-actions .delete-btn {
    color: #f56c6c;
}

.address-actions .delete-btn:hover {
    color: #ff0000;
}

.address-content {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.consignee-info {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 10px;
}

.consignee-name {
    font-size: 18px;
    font-weight: 600;
    color: #333;
}

.consignee-phone {
    font-size: 16px;
    color: #666;
}

.address-detail {
    margin-bottom: 10px;
}

.detail-text {
    margin: 0;
    font-size: 16px;
    color: #333;
    line-height: 1.5;
}

.detail-text i {
    margin-right: 8px;
    color: #36d1dc;
}

.address-operations {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 10px;
    padding-top: 15px;
    border-top: 1px solid #f0f0f0;
}

/* 表单样式 */
.address-form {
    padding: 10px 20px;
}

.address-form ::v-deep .el-form-item__label {
    font-size: 16px;
    font-weight: 600;
    color: #333;
}

.region-selectors {
    display: flex;
    justify-content: space-between;
}

.region-errors {
    margin-top: 5px;
}

.error-text {
    color: #f56c6c;
    font-size: 12px;
    margin-right: 10px;
}

.hint-text {
    margin: 5px 0 0 0;
    font-size: 12px;
    color: #999;
}

/* 删除确认对话框 */
.delete-confirm {
    display: flex;
    align-items: center;
    padding: 20px;
}

.warning-icon {
    font-size: 40px;
    color: #e6a23c;
    margin-right: 20px;
}

.delete-content {
    flex: 1;
}

.delete-content p {
    margin: 0 0 10px 0;
    font-size: 16px;
}

.delete-hint {
    color: #999;
    font-size: 14px;
}

/* 分页 */
.pagination-container {
    display: flex;
    justify-content: center;
    margin-top: 30px;
    padding-top: 30px;
    border-top: 1px solid #f0f0f0;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .address-management-container {
        padding: 10px;
    }

    .header {
        padding: 20px 15px;
    }

    .header h2 {
        font-size: 22px;
    }

    .content-body {
        padding: 20px 15px;
        width: 95%;
    }

    .action-header {
        flex-direction: column;
        align-items: stretch;
        gap: 15px;
    }

    .search-box {
        width: 100%;
    }

    .search-box ::v-deep .el-input {
        width: 100%;
    }

    .address-grid {
        grid-template-columns: 1fr;
        gap: 15px;
    }

    .address-card {
        margin-bottom: 15px;
    }

    .consignee-info {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
    }

    .region-selectors {
        flex-direction: column;
        gap: 10px;
    }

    .region-selectors .el-select {
        width: 100% !important;
        margin-right: 0 !important;
    }
}

@media (max-width: 480px) {
    .address-grid {
        grid-template-columns: 1fr;
    }

    .address-form {
        padding: 5px 10px;
    }

    .address-form ::v-deep .el-form-item__label {
        font-size: 14px;
    }
}

/* 对话框样式优化 */
::v-deep .el-dialog__header {
    background: linear-gradient(135deg, #36d1dc 0%, #5b86e5 100%);
    padding: 20px;
    border-radius: 8px 8px 0 0;
}

::v-deep .el-dialog__title {
    color: white !important;
    font-size: 18px;
    font-weight: 600;
}

::v-deep .el-dialog__headerbtn .el-dialog__close {
    color: white !important;
}

/* 空状态样式 */
.address-list ::v-deep .el-empty__description {
    margin-top: 20px;
    font-size: 16px;
    color: #666;
}
</style>