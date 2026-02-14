<template>
    <el-dialog
        :title="localFormData.dish_id ? '编辑菜品' : '添加菜品'"
        :visible="visible"
        width="600px"
        center
        :close-on-click-modal="false"
        @close="handleClose"
        @update:visible="$emit('close')">
        <el-form :model="localFormData" :rules="rules" ref="formRef" label-width="100px">
            <el-form-item label="菜品名称" prop="dish_name">
                <el-input
                    v-model="localFormData.dish_name"
                    placeholder="请输入菜品名称">
                </el-input>
            </el-form-item>
            <el-form-item label="价格" prop="price">
                <el-input-number
                    v-model="localFormData.price"
                    :min="0"
                    :precision="2"
                    :step="1"
                    style="width: 100%"
                    placeholder="请输入价格">
                </el-input-number>
            </el-form-item>
            <el-form-item label="菜品描述" prop="description">
                <el-input
                    type="textarea"
                    v-model="localFormData.description"
                    :rows="3"
                    placeholder="请输入菜品描述">
                </el-input>
            </el-form-item>
            <el-form-item label="菜品图片" prop="image_file">
                <!-- 文件上传组件 -->
                <el-upload
                    class="upload-demo"
                    action="#"
                    :auto-upload="false"
                    :on-change="handleImageChange"
                    :on-remove="handleImageRemove"
                    :file-list="fileList"
                    :limit="1"
                    accept="image/*">
                    <el-button size="small" type="primary">点击上传</el-button>
                    <div slot="tip" class="el-upload__tip">请上传菜品图片，支持 jpg、png 格式，大小不超过 2MB</div>
                </el-upload>
                <!-- 图片预览 -->
                <div v-if="imagePreviewUrl" class="image-preview">
                    <img :src="imagePreviewUrl" alt="菜品图片预览" @error="handleImageError">
                </div>
            </el-form-item>
            <el-form-item label="排序" prop="sort_order">
                <el-input-number
                    v-model="localFormData.sort_order"
                    :min="0"
                    :max="999"
                    style="width: 100%">
                </el-input-number>
            </el-form-item>
            <el-form-item label="菜品状态" prop="status">
                <el-switch
                    v-model="localFormData.status"
                    active-text="上架"
                    inactive-text="下架">
                </el-switch>
            </el-form-item>
        </el-form>
        <span slot="footer" class="dialog-footer">
            <el-button @click="handleClose">取 消</el-button>
            <el-button type="primary" @click="handleSave" :loading="loading">保 存</el-button>
        </span>
    </el-dialog>
</template>

<script>
export default {
    name: 'DishDialog',
    props: {
        visible: {
            type: Boolean,
            default: false
        },
        formData: {
            type: Object,
            default: () => ({
                dish_id: null,
                dish_name: '',
                price: 0,
                description: '',
                image_url: '/images/dish/default-dish.jpg',
                sort_order: 0,
                status: true,
                shop_id: null  // 添加 shop_id
            })
        },
        shopId: {
           type: [Number], // 只保留 Number，但允许 null 值
              default: null,
              required: false
        }
    },
    data() {
        return {
            loading: false,
            localFormData: {},
            fileList: [],
            imagePreviewUrl: '',
            imageFile: null,
            rules: {
                dish_name: [
                    { required: true, message: '请输入菜品名称', trigger: 'blur' },
                    { min: 1, max: 50, message: '菜品名称长度在 1 到 50 个字符', trigger: 'blur' }
                ],
                price: [
                    { required: true, message: '请输入价格', trigger: 'blur' },
                    { type: 'number', min: 0, message: '价格不能为负数', trigger: 'blur' }
                ]
            }
        }
    },
    watch: {
        formData: {
            handler(newVal) {
                this.localFormData = { ...newVal };
                this.imagePreviewUrl = newVal.image_url;
                this.fileList = [];
                this.imageFile = null;
            },
            immediate: true,
            deep: true
        },
        visible(newVal) {
            if (!newVal) {
                this.loading = false;
                if (this.$refs.formRef) {
                    this.$refs.formRef.clearValidate();
                }
            }
        }
    },
    methods: {
        handleClose() {
            this.fileList = [];
            this.imageFile = null;
            this.imagePreviewUrl = '';
            this.$emit('close');
        },

        // 处理图片文件选择
        handleImageChange(file, fileList) {
            const isImage = file.raw.type.includes('image');
            const isLt2M = file.raw.size / 1024 / 1024 < 2;

            if (!isImage) {
                this.$message.error('只能上传图片文件!');
                this.fileList = [];
                return;
            }
            if (!isLt2M) {
                this.$message.error('图片大小不能超过 2MB!');
                this.fileList = [];
                return;
            }

            this.fileList = fileList.slice(-1); // 只保留最后一个文件
            this.imageFile = file.raw;

            // 生成预览URL
            const reader = new FileReader();
            reader.onload = (e) => {
                this.imagePreviewUrl = e.target.result;
            };
            reader.readAsDataURL(file.raw);
        },

        // 处理图片移除
        handleImageRemove() {
            this.fileList = [];
            this.imageFile = null;
            this.imagePreviewUrl = this.localFormData.image_url || '/images/dish/default-dish.jpg';
        },

        async handleSave() {
            this.$refs.formRef.validate(valid => {
                if (valid) {
                    this.loading = true;

                    const formData = new FormData();

                    // 添加表单数据
                    formData.append('shop_id', this.shopId);
                    formData.append('dish_name', this.localFormData.dish_name);
                    formData.append('price', this.localFormData.price);
                    formData.append('description', this.localFormData.description || '');
                    formData.append('sort_order', this.localFormData.sort_order || 0);
                    formData.append('status', this.localFormData.status ? 1 : 0);

                    // 如果有上传文件，添加文件
                    if (this.imageFile) {
                        formData.append('image_file', this.imageFile);
                    }

                    // 发送请求
                    this.submitFormData(formData);
                }
            });
        },

        async submitFormData(formData) {
            try {
                let url;
                let method;

                if (this.localFormData.dish_id) {
                    // 编辑模式
                    url = `/api/dishes/${this.localFormData.dish_id}`;
                    method = 'PUT';
                } else {
                    // 创建模式
                    url = `/api/dishes`;
                    method = 'POST';
                }

                const response = await this.$axios({
                    url: url,
                    method: method,
                    data: formData,
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                });

                if (response.data.status === 200) {
                    this.$message.success(response.data.msg);
                    this.handleClose();
                    this.$emit('refresh'); // 通知父组件刷新列表
                } else {
                    this.$message.error(response.data.msg);
                }
            } catch (error) {
                console.error('保存菜品失败:', error);
                this.$message.error('保存失败，请重试');
            } finally {
                this.loading = false;
            }
        },

        handleImageError(event) {
            event.target.src = '/images/dish/default-dish.jpg';
        }
    }
}
</script>

<style scoped>
.upload-demo {
    width: 100%;
}

.image-preview {
    margin-top: 10px;
    text-align: center;
}

.image-preview img {
    max-width: 200px;
    max-height: 150px;
    border-radius: 4px;
    border: 1px solid #dcdfe6;
}

.dialog-footer {
    text-align: center;
}

.el-upload__tip {
    font-size: 12px;
    color: #606266;
    margin-top: 5px;
}
</style>