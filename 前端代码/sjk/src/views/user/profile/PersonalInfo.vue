<template>
    <div class="user-info-container">
        <div class="header">
            <h2>个人信息</h2>
            <p class="subtitle">{{ editing ? '编辑您的个人资料' : '查看您的个人资料' }}</p>
        </div>

        <div class="content-body">
            <div class="form-container">
                <!-- 头像展示区域 -->
                <el-card class="avatar-card" shadow="never">
                    <div class="avatar-content">
                        <div class="avatar-preview">
                            <!-- 修改1：使用动态key强制重新渲染头像 -->
                            <el-avatar
                                :key="avatarKey"
                                :size="120"
                                :src="getAvatarUrl(form.avatar_url)"
                                class="user-avatar">
                                {{ form.user_name?.charAt(0) || 'U' }}
                            </el-avatar>
                            <div class="avatar-actions" v-if="editing">
                                <!-- 修改2：使用自定义上传，不使用element-ui的默认action -->
                                <el-upload
                                    ref="avatarUpload"
                                    class="avatar-uploader"
                                    :show-file-list="false"
                                    :before-upload="beforeAvatarUpload"
                                    :http-request="customAvatarUpload"
                                    accept=".jpg,.jpeg,.png,.gif,.webp">
                                    <el-button type="primary" size="small" icon="el-icon-upload">
                                        更换头像
                                    </el-button>
                                </el-upload>
                                <el-button
                                    type="danger"
                                    size="small"
                                    icon="el-icon-delete"
                                    @click="removeAvatar"
                                    :loading="removingAvatar"
                                    v-if="form.avatar_url && form.avatar_url !== '/images/user/default-avatar.jpg'">
                                    删除头像
                                </el-button>
                            </div>
                        </div>
                        <div class="avatar-info">
                            <h3>{{ form.user_name || '未设置用户名' }}</h3>
                            <p>{{ form.real_name ? `真实姓名：${form.real_name}` : '未设置真实姓名' }}</p>
                            <p v-if="form.mail">邮箱：{{ form.mail }}</p>
                        </div>
                    </div>
                </el-card>

                <el-card class="info-card" shadow="never">
                    <div class="card-header">
                        <i class="el-icon-user-solid"></i>
                        <span>基本信息</span>
                        <div class="header-actions">
                            <el-button
                                v-if="!editing"
                                type="primary"
                                icon="el-icon-edit"
                                @click="startEditing"
                                size="small">
                                编辑信息
                            </el-button>
                            <div v-else class="edit-actions">
                                <el-button
                                    type="success"
                                    icon="el-icon-check"
                                    @click="saveChanges"
                                    :loading="saving"
                                    size="small">
                                    保存
                                </el-button>
                                <el-button
                                    icon="el-icon-close"
                                    @click="cancelEditing"
                                    size="small">
                                    取消
                                </el-button>
                            </div>
                        </div>
                    </div>
                    <el-form ref="form" :model="form" :rules="formRules" label-width="120px" class="info-form">
                        <el-form-item label="用户名：" class="form-item" prop="user_name">
                            <div class="info-content">
                                <span v-if="!editing" class="info-value">{{ form.user_name || '未设置' }}</span>
                                <el-input
                                    v-else
                                    v-model="form.user_name"
                                    placeholder="请输入用户名"
                                    maxlength="20"
                                    show-word-limit>
                                </el-input>
                                <i class="el-icon-user info-icon"></i>
                            </div>
                        </el-form-item>

                        <el-form-item label="真实姓名：" class="form-item" prop="real_name">
                            <div class="info-content">
                                <span v-if="!editing" class="info-value">{{ form.real_name || '未设置' }}</span>
                                <el-input
                                    v-else
                                    v-model="form.real_name"
                                    placeholder="请输入真实姓名"
                                    maxlength="10"
                                    show-word-limit>
                                </el-input>
                                <i class="el-icon-s-custom info-icon"></i>
                            </div>
                        </el-form-item>

                        <el-form-item label="年龄：" class="form-item" prop="age">
                            <div class="info-content">
                                <span v-if="!editing" class="info-value">{{ form.age || '未设置' }}</span>
                                <el-input-number
                                    v-else
                                    v-model="form.age"
                                    :min="1"
                                    :max="120"
                                    controls-position="right"
                                    placeholder="请输入年龄">
                                </el-input-number>
                                <i class="el-icon-time info-icon"></i>
                            </div>
                        </el-form-item>

                        <el-form-item label="性别：" class="form-item" prop="sex">
                            <div class="info-content">
                                <span v-if="!editing" class="info-value">{{ form.sex || '未设置' }}</span>
                                <el-select
                                    v-else
                                    v-model="form.sex"
                                    placeholder="请选择性别"
                                    style="width: 100%">
                                    <el-option label="男" value="男"></el-option>
                                    <el-option label="女" value="女"></el-option>
                                </el-select>
                                <i class="el-icon-female info-icon" v-if="form.sex === '女'"></i>
                                <i class="el-icon-male info-icon" v-else-if="form.sex === '男'"></i>
                                <i class="el-icon-question info-icon" v-else></i>
                            </div>
                        </el-form-item>

                        <el-form-item label="电话：" class="form-item">
                            <div class="info-content">
                                <span class="info-value">{{ form.phone || '未设置' }}</span>
                                <i class="el-icon-phone info-icon"></i>
                            </div>
                        </el-form-item>

                        <el-form-item label="邮箱：" class="form-item" prop="mail">
                            <div class="info-content">
                                <span v-if="!editing" class="info-value">{{ form.mail || '未设置' }}</span>
                                <el-input
                                    v-else
                                    v-model="form.mail"
                                    placeholder="请输入邮箱地址"
                                    type="email">
                                </el-input>
                                <i class="el-icon-message info-icon"></i>
                            </div>
                        </el-form-item>

                        <!-- 头像URL字段（隐藏） -->
                        <el-form-item v-show="false">
                            <el-input v-model="form.avatar_url"></el-input>
                        </el-form-item>
                    </el-form>
                </el-card>

                <!-- 操作按钮 -->
                <div class="action-buttons">
                    <el-button
                        icon="el-icon-refresh"
                        @click="refreshData"
                        class="refresh-btn"
                        :loading="loading">
                        刷新信息
                    </el-button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    created() {
        this.getdata()
    },
    data() {
        // 邮箱验证规则
        const validateEmail = (rule, value, callback) => {
            if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                callback(new Error('请输入正确的邮箱格式'));
            } else {
                callback();
            }
        };

        return {
            avatarKey: 0, // 用于强制重新渲染头像
            form: {
                real_name: '',
                sex: '',
                age: '',
                mail: '',
                phone: '',
                user_name: '',
                avatar_url: '/images/user/default-avatar.jpg'
            },
            originalForm: {},
            editing: false,
            loading: false,
            saving: false,
            removingAvatar: false,
            uploadingAvatar: false,
            uploadHeaders: {
                'token': localStorage.getItem('token') || ''
            },
            formRules: {
                user_name: [
                    { required: true, message: '请输入用户名', trigger: 'blur' },
                    { min: 2, max: 20, message: '用户名长度在 2 到 20 个字符', trigger: 'blur' }
                ],
                real_name: [
                    { required: true, message: '请输入真实姓名', trigger: 'blur' },
                    { min: 2, max: 10, message: '真实姓名长度在 2 到 10 个字符', trigger: 'blur' }
                ],
                age: [
                    { type: 'number', min: 1, max: 120, message: '年龄必须在 1 到 120 之间', trigger: 'blur' }
                ],
                sex: [
                    { required: true, message: '请选择性别', trigger: 'change' }
                ],
                mail: [
                    { validator: validateEmail, trigger: 'blur' }
                ]
            }
        }
    },
    methods: {
        // 修改：添加获取完整头像URL的方法
        getAvatarUrl(url) {
            if (!url) return '/images/user/default-avatar.jpg';

            // 如果已经是完整URL，直接返回
            if (url.startsWith('http://') || url.startsWith('https://')) {
                return url;
            }

            // 如果是相对路径，添加时间戳防止缓存
            return url + (url.includes('?') ? '&' : '?') + 't=' + Date.now();
        },

        getdata() {
            this.loading = true;
            this.$axios.get("/api/user/usermsg").then((res) => {
                console.log('获取用户信息:', res.data);
                if (res.data.status == 200) {
                    // 使用Object.assign确保响应式更新
                    Object.assign(this.form, {
                        age: res.data.data.age,
                        mail: res.data.data.mail,
                        phone: res.data.data.phone,
                        real_name: res.data.data.real_name,
                        sex: res.data.data.sex,
                        user_name: res.data.data.user_name,
                        avatar_url: res.data.data.avatar_url || '/images/user/default-avatar.jpg'
                    });

                    // 保存原始数据
                    this.originalForm = { ...this.form };

                    // 强制重新渲染头像
                    this.avatarKey++;

                    this.$message({
                        message: '个人信息加载成功',
                        type: 'success',
                        duration: 2000
                    });
                } else {
                    this.$message.error(res.data.msg || '获取个人信息失败');
                }
            }).catch((error) => {
                console.error('获取个人信息失败:', error);
                this.$message.error('获取个人信息失败');
            }).finally(() => {
                this.loading = false;
            })
        },

        refreshData() {
            this.getdata();
        },

        startEditing() {
            this.editing = true;
            // 确保保存原始数据
            this.originalForm = { ...this.form };
        },

        cancelEditing() {
            this.editing = false;
            // 恢复原始数据
            Object.assign(this.form, { ...this.originalForm });
            // 清除验证状态
            if (this.$refs.form) {
                this.$refs.form.clearValidate();
            }
            // 强制重新渲染头像
            this.avatarKey++;
        },

        saveChanges() {
            this.$refs.form.validate((valid) => {
                if (valid) {
                    this.saving = true;
                    this.$axios.post("/api/user/usermsg", this.form).then((res) => {
                        if (res.data.status == 200) {
                            this.$message({
                                message: '个人信息更新成功',
                                type: 'success'
                            });
                            this.editing = false;
                            // 更新原始数据
                            this.originalForm = { ...this.form };
                            // 刷新数据确保一致性
                            this.getdata();
                        } else {
                            this.$message.error(res.data.msg || '更新失败');
                        }
                    }).catch((error) => {
                        console.error('更新个人信息失败:', error);
                        this.$message.error('更新个人信息失败');
                    }).finally(() => {
                        this.saving = false;
                    });
                } else {
                    this.$message.warning('请完善表单信息');
                    return false;
                }
            });
        },

        // 修改：自定义上传方法
        customAvatarUpload(file) {
            console.log('开始上传头像:', file.file);

            this.uploadingAvatar = true;

            // 创建FormData
            const formData = new FormData();
            formData.append('avatar', file.file);

            // 设置请求头
            const config = {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'token': localStorage.getItem('token') || ''
                },
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    console.log(`上传进度: ${percentCompleted}%`);
                }
            };

            // 发送请求
            this.$axios.post('/api/user/upload-avatar', formData, config)
                .then(res => {
                    console.log('上传响应:', res.data);
                    if (res.data.status === 200) {
                        // 直接更新表单中的头像URL
                        this.form.avatar_url = res.data.avatar_url;
                        // 强制重新渲染头像
                        this.avatarKey++;

                        this.$message.success('头像上传成功');

                        // 触发事件，通知其他组件头像已更新
                        this.$bus.$emit('avatar-updated', res.data.avatar_url);

                        // 自动保存头像URL到用户信息
                        this.saveAvatarToProfile(res.data.avatar_url);

                        // 调用成功回调
                        if (file.onSuccess) {
                            file.onSuccess(res.data, file.file);
                        }
                    } else {
                        this.$message.error(res.data.msg || '头像上传失败');
                        if (file.onError) {
                            file.onError(new Error(res.data.msg || '上传失败'), file.file);
                        }
                    }
                })
                .catch(error => {
                    console.error('上传失败:', error);
                    this.$message.error('头像上传失败: ' + (error.message || '网络错误'));
                    if (file.onError) {
                        file.onError(error, file.file);
                    }
                })
                .finally(() => {
                    this.uploadingAvatar = false;
                });
        },

        // 头像上传前验证
        beforeAvatarUpload(file) {
            console.log('上传前验证:', file);

            const isImage = /\.(jpg|jpeg|png|gif|bmp|webp)$/i.test(file.name);
            const isLt2M = file.size / 1024 / 1024 < 2;

            if (!isImage) {
                this.$message.error('只能上传图片文件!');
                return false;
            }
            if (!isLt2M) {
                this.$message.error('图片大小不能超过 2MB!');
                return false;
            }

            this.$message.info('正在上传头像...');
            return true;
        },

        // 保存头像URL到用户信息
        saveAvatarToProfile(avatarUrl) {
            this.$axios.post("/api/user/usermsg", {
                ...this.form,
                avatar_url: avatarUrl
            }).then((res) => {
                if (res.data.status === 200) {
                    console.log('头像信息已保存');
                    // 更新原始数据
                    this.originalForm.avatar_url = avatarUrl;
                } else {
                    console.warn('保存头像信息失败:', res.data.msg);
                }
            }).catch((error) => {
                console.error('保存头像信息失败:', error);
            });
        },

        // 头像上传成功处理
        handleAvatarSuccess(res) {
            if (res.status === 200) {
                this.form.avatar_url = res.avatar_url;
                this.$message.success('头像上传成功');

                // 触发事件，通知其他组件头像已更新
                this.$bus.$emit('avatar-updated', res.avatar_url);

                // 自动保存头像URL到用户信息
                this.saveAvatarToProfile(res.avatar_url);
            } else {
                this.$message.error(res.msg || '头像上传失败');
            }
        },

        // 删除头像
        removeAvatar() {
            this.$confirm('确定要删除当前头像吗？删除后将恢复默认头像', '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                this.removingAvatar = true;
                this.$axios.post("/api/user/remove-avatar").then((res) => {
                    if (res.data.status === 200) {
                        // 更新头像URL
                        this.form.avatar_url = res.data.avatar_url || '/images/user/default-avatar.jpg';
                        // 强制重新渲染头像
                        this.avatarKey++;

                        this.$message.success('头像已删除');

                        // 触发事件，通知其他组件头像已更新
                        this.$bus.$emit('avatar-updated', res.data.avatar_url);

                        // 更新原始数据
                        this.originalForm = { ...this.form };

                        // 刷新数据
                        this.getdata();
                    } else {
                        this.$message.error(res.data.msg || '删除失败');
                    }
                }).catch((error) => {
                    console.error('删除头像失败:', error);
                    this.$message.error('删除头像失败');
                }).finally(() => {
                    this.removingAvatar = false;
                });
            }).catch(() => {
                // 用户取消
            });
        }
    },
}
</script>

<style scoped>
.user-info-container {
    min-height: 100vh;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 20px;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

.form-container {
    max-width: 800px;
    margin: 0 auto;
}

/* 头像卡片样式 */
.avatar-card {
    border: none;
    border-radius: 12px;
    margin-bottom: 30px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.avatar-content {
    display: flex;
    align-items: center;
    padding: 20px;
    gap: 30px;
}

.avatar-preview {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px;
}

.user-avatar {
    border: 4px solid #667eea;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    transition: all 0.3s ease;
}

.user-avatar:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

.avatar-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: center;
}

.avatar-uploader {
    display: inline-block;
}

.avatar-info {
    flex: 1;
}

.avatar-info h3 {
    margin: 0 0 10px 0;
    font-size: 24px;
    color: #333;
    font-weight: 600;
}

.avatar-info p {
    margin: 8px 0;
    color: #666;
    font-size: 16px;
}

.info-card {
    border: none;
    border-radius: 12px;
    margin-bottom: 30px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
    background: linear-gradient(135deg, #f8f9fc 0%, #eaecf4 100%);
    padding: 20px;
    border-bottom: 1px solid #eaeaea;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 18px;
    font-weight: 600;
    color: #333;
}

.card-header > div:first-child {
    display: flex;
    align-items: center;
}

.card-header i {
    margin-right: 10px;
    font-size: 20px;
    color: #667eea;
}

.header-actions {
    display: flex;
    align-items: center;
}

.edit-actions {
    display: flex;
    gap: 10px;
}

.info-form {
    padding: 30px;
}

.form-item {
    margin-bottom: 25px;
    padding: 15px 0;
    border-bottom: 1px solid #f0f0f0;
}

.form-item:last-child {
    border-bottom: none;
    margin-bottom: 0;
}

::v-deep .info-form .el-form-item__label {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    line-height: 40px;
}

.info-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
}

.info-value {
    font-size: 16px;
    color: #666;
    font-weight: 500;
    flex: 1;
}

.info-icon {
    font-size: 20px;
    color: #667eea;
    margin-left: 15px;
}

.action-buttons {
    display: flex;
    justify-content: center;
    margin-top: 30px;
    padding-top: 30px;
    border-top: 1px solid #f0f0f0;
}

.refresh-btn {
    padding: 12px 30px;
    font-size: 16px;
    font-weight: 500;
    border-radius: 8px;
    border-color: #667eea;
    color: #667eea;
    transition: all 0.3s ease;
}

.refresh-btn:hover {
    background-color: #f0f4ff;
    transform: translateY(-2px);
}

/* 编辑模式下特殊样式 */
::v-deep .info-form .el-input,
::v-deep .info-form .el-input-number,
::v-deep .info-form .el-select {
    width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .user-info-container {
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

    .avatar-content {
        flex-direction: column;
        text-align: center;
        gap: 20px;
    }

    .avatar-actions {
        flex-direction: column;
        width: 100%;
    }

    .avatar-actions .el-button {
        width: 100%;
    }

    .avatar-info h3 {
        font-size: 20px;
    }

    .info-form {
        padding: 20px 10px;
    }

    .form-item {
        margin-bottom: 20px;
        padding: 10px 0;
    }

    .action-buttons {
        flex-direction: column;
    }

    .refresh-btn {
        width: 100%;
    }

    .info-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .info-icon {
        align-self: flex-end;
    }

    .card-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }

    .header-actions {
        width: 100%;
        justify-content: center;
    }
}

@media (max-width: 480px) {
    ::v-deep .info-form .el-form-item__label {
        font-size: 14px;
    }

    .info-value {
        font-size: 14px;
    }

    .card-header {
        font-size: 16px;
        padding: 15px;
    }

    .user-avatar {
        width: 100px !important;
        height: 100px !important;
    }
}

/* 上传按钮样式 */
.avatar-uploader ::v-deep .el-upload {
    display: inline-block;
}

.avatar-uploader ::v-deep .el-upload .el-button {
    margin: 0;
}
</style>