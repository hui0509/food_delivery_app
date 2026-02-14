<template>
    <el-dialog
        :title="localFormData.shop_id ? '编辑店铺信息' : '创建店铺'"
        :visible="visible"
        width="600px"
        center
        :close-on-click-modal="false"
        @close="handleClose"
        @update:visible="$emit('close')">
        <el-form :model="localFormData" :rules="rules" ref="formRef" label-width="100px">
            <el-form-item label="店铺名称" prop="shop_name">
                <el-input v-model="localFormData.shop_name" placeholder="请输入店铺名称"></el-input>
            </el-form-item>
            <el-form-item label="店铺描述" prop="description">
                <el-input
                    type="textarea"
                    v-model="localFormData.description"
                    :rows="3"
                    placeholder="请输入店铺描述">
                </el-input>
            </el-form-item>
            <el-form-item label="店铺状态" prop="status">
                <el-switch
                    v-model="localFormData.status"
                    active-text="营业中"
                    inactive-text="已打烊">
                </el-switch>
            </el-form-item>
            <el-form-item label="店铺图片" prop="image_file">
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
                    <div slot="tip" class="el-upload__tip">请上传店铺图片，支持 jpg、png 格式，大小不超过 2MB</div>
                </el-upload>
                <!-- 图片预览 -->
                <div v-if="imagePreviewUrl" class="image-preview">
                    <img :src="imagePreviewUrl" alt="店铺图片预览" @error="handleImageError">
                </div>
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
    name: 'StoreDialog',
    props: {
        visible: {
            type: Boolean,
            default: false
        },
        formData: {
            type: Object,
            default: () => ({
                shop_name: '',
                description: '',
                status: true,
                image_url: '/images/shop/default-shop.jpg'
            })
        },
        // 添加 username 作为 prop，从父组件传递
        username: {
            type: String,
            required: true,
            default: ''
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
                shop_name: [
                    { required: true, message: '请输入店铺名称', trigger: 'blur' },
                    { min: 1, max: 50, message: '店铺名称长度在 1 到 50 个字符', trigger: 'blur' }
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
            this.imagePreviewUrl = this.localFormData.image_url || '/images/shop/default-shop.jpg';
        },

        async handleSave() {
            this.$refs.formRef.validate(valid => {
                if (valid) {
                    this.loading = true;

                    const formData = new FormData();

                    // 添加表单数据
                    formData.append('shop_name', this.localFormData.shop_name);
                    formData.append('description', this.localFormData.description || '');
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

                if (this.localFormData.shop_id) {
                    // 编辑模式 - 使用新的接口格式
                    url = `/api/shop/${this.localFormData.shop_id}/owner/${this.username}`;
                    method = 'PUT';
                } else {
                    // 创建模式
                    url = `/api/shop/owner/${this.username}`;
                    method = 'POST';
                }

                // 使用 this.$axios 而不是 this.$http
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
                console.error('保存店铺失败:', error);
                this.$message.error('保存失败，请重试');
            } finally {
                this.loading = false;
            }
        },

        handleImageError(event) {
            event.target.src = '/images/shop/default-shop.jpg';
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