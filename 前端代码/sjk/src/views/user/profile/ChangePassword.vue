<template>
    <div class="change-password-container">
        <div class="header">
            <h2>修改密码</h2>
            <p class="subtitle">请谨慎操作，确保密码安全</p>
        </div>

        <div class="content-body">
            <div class="form-container">
                <el-form
                    ref="form"
                    :model="form"
                    label-width="30%"
                    class="password-form"
                    :rules="form_rules">

                    <el-form-item label="原密码：" prop="old_pwd">
                        <el-input
                            v-model="form.old_pwd"
                            type="password"
                            show-password
                            placeholder="请输入当前密码"
                            size="medium">
                        </el-input>
                    </el-form-item>

                    <el-form-item label="新密码：" prop="new_pwd">
                        <el-input
                            v-model="form.new_pwd"
                            type="password"
                            show-password
                            placeholder="请输入新密码"
                            size="medium">
                        </el-input>
                    </el-form-item>

                    <el-form-item label="确认密码：" prop="check_pwd">
                        <el-input
                            v-model="form.check_pwd"
                            type="password"
                            show-password
                            placeholder="请再次输入新密码"
                            size="medium">
                        </el-input>
                    </el-form-item>

                    <el-form-item class="form-actions">
                        <el-button
                            type="primary"
                            @click="change()"
                            size="medium"
                            class="submit-btn">
                            确认修改
                        </el-button>
                        <el-button
                            @click="resetForm()"
                            size="medium"
                            class="reset-btn">
                            重置
                        </el-button>
                    </el-form-item>
                </el-form>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        // 自定义密码验证规则
        const validateNewPassword = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('请输入新密码'));
            } else if (value.length < 6) {
                callback(new Error('密码长度不能少于6位'));
            } else {
                if (this.form.check_pwd !== '') {
                    this.$refs.form.validateField('check_pwd');
                }
                callback();
            }
        };

        const validateConfirmPassword = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('请再次输入密码'));
            } else if (value !== this.form.new_pwd) {
                callback(new Error('两次输入密码不一致!'));
            } else {
                callback();
            }
        };

        return {
            form: {
                old_pwd: '',
                new_pwd: '',
                check_pwd: '',
            },
            form_rules: {
                old_pwd: [
                    { required: true, message: "请输入原密码", trigger: 'blur' }
                ],
                new_pwd: [
                    { required: true, validator: validateNewPassword, trigger: 'blur' }
                ],
                check_pwd: [
                    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
                ]
            }
        }
    },
    methods: {
        change() {
            this.$refs.form.validate(valid => {
                if (!valid) {
                    this.$message({
                        message: '请完善表单信息',
                        type: 'warning'
                    });
                    return;
                }

                // 验证通过再发送请求
                if (this.form.check_pwd === this.form.new_pwd) {
                    this.$axios.post("/api/user/pwd_chg", this.form).then((res) => {
                        if (res.data.status == 200) {
                            this.$message({
                                message: res.data.msg,
                                type: "success"
                            });
                            // 清空表单
                            this.resetForm();
                        } else {
                            this.$message({
                                message: res.data.msg,
                                type: "error"
                            });
                        }
                    }).catch(() => {
                        this.$message({
                            message: '请求失败，请稍后重试',
                            type: "error"
                        });
                    });
                } else {
                    this.$message({
                        message: "新密码与确认密码不一致",
                        type: "error"
                    });
                }
            });
        },
        resetForm() {
            this.$refs.form.resetFields();
        }
    }
}
</script>

<style scoped>
.change-password-container {
    min-height: 100vh;
    background-color: #f7f9fc;
    padding: 20px;
}

.header {
    background: linear-gradient(135deg, #6a8dff 0%, #4a6cf7 100%);
    color: white;
    padding: 20px 30px;
    border-radius: 12px;
    margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(106, 141, 255, 0.2);
}

.header h2 {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
}

.header .subtitle {
    margin: 5px 0 0;
    font-size: 14px;
    opacity: 0.9;
}

.content-body {
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    overflow: hidden;
    padding: 30px;
}

.form-container {
    max-width: 600px;
    margin: 0 auto;
}

.password-form {
    padding: 20px 0;
}

::v-deep .password-form .el-form-item {
    margin-bottom: 28px;
}

::v-deep .password-form .el-form-item__label {
    font-size: 16px;
    font-weight: 500;
    color: #606266;
    line-height: 40px;
}

::v-deep .password-form .el-input__inner {
    height: 44px;
    line-height: 44px;
    border-radius: 8px;
    border: 1px solid #dcdfe6;
    transition: all 0.3s;
}

::v-deep .password-form .el-input__inner:focus {
    border-color: #6a8dff;
    box-shadow: 0 0 0 2px rgba(106, 141, 255, 0.2);
}

.form-actions {
    text-align: center;
    margin-top: 40px !important;
    padding-top: 20px;
    border-top: 1px solid #f0f0f0;
}

.submit-btn {
    background: linear-gradient(135deg, #6a8dff 0%, #4a6cf7 100%);
    border: none;
    border-radius: 8px;
    padding: 12px 30px;
    font-size: 16px;
    font-weight: 500;
    transition: all 0.3s;
}

.submit-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(106, 141, 255, 0.3);
}

.reset-btn {
    border-radius: 8px;
    padding: 12px 30px;
    font-size: 16px;
    font-weight: 500;
    margin-left: 20px;
}

/* 响应式调整 */
@media (max-width: 768px) {
    .change-password-container {
        padding: 10px;
    }

    .header {
        padding: 15px 20px;
    }

    .header h2 {
        font-size: 20px;
    }

    .content-body {
        padding: 20px 15px;
    }

    ::v-deep .password-form .el-form-item__label {
        font-size: 14px;
    }

    .form-actions {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }

    .reset-btn {
        margin-left: 0;
    }
}
</style>