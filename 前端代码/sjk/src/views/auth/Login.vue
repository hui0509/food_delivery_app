<template>
    <div class="login-container">
        <!-- 背景装饰 -->
        <div class="background-decor">
            <div class="circle circle-1"></div>
            <div class="circle circle-2"></div>
            <div class="circle circle-3"></div>
        </div>

        <!-- 登录表单 -->
        <div class="login_box" v-show="target == 1">
            <!-- 登录表单内容保持不变 -->
            <div class="head">
                <div class="logo">
                    <i class="el-icon-food"></i>
                    <span>校园点餐平台</span>
                </div>
            </div>
            <el-form label-width="0" class="login_form" :model="login_form" :rules="login_rules" ref="login_form">
                <el-form-item prop="userortel">
                    <el-input v-model="login_form.userortel" spellcheck="false" placeholder="用户名或手机号"
                        prefix-icon="el-icon-user" class="custom-input">
                    </el-input>
                </el-form-item>
                <el-form-item prop="password">
                    <el-input v-model="login_form.password" show-password spellcheck="false" placeholder="密码"
                        prefix-icon="el-icon-lock" class="custom-input">
                    </el-input>
                </el-form-item>
                <el-form-item class="btns">
                    <el-button type="primary" @click="llogin()" class="login-btn">登录</el-button>
                </el-form-item>
            </el-form>
            <div class="operate">
                <span id="op1" @click="change(2)">注册</span>
                <span id="op2" @click="change(3)">忘记密码</span>
            </div>
        </div>

        <!-- 注册表单 -->
        <div class="reg_box" v-show="target == 2">
            <div class="head compact">
                <i class="el-icon-user-solid"></i>
                <span>注册账号</span>
            </div>
            <el-form class="reg_form" :model="reg_form" :rules="reg_rules" ref="reg_form">
                <el-form-item prop="username">
                    <el-input v-model="reg_form.username" spellcheck="false" placeholder="用户名"
                        prefix-icon="el-icon-user" class="custom-input">
                    </el-input>
                </el-form-item>
                <el-form-item prop="password">
                    <el-input v-model="reg_form.password" show-password spellcheck="false"
                        placeholder="密码(包含大小写字母、数字，长度在6-12之间)" prefix-icon="el-icon-lock" class="custom-input">
                    </el-input>
                </el-form-item>
                <el-form-item prop="telephone">
                    <el-input v-model="reg_form.telephone" spellcheck="false" placeholder="手机号码"
                        prefix-icon="el-icon-mobile-phone" class="custom-input">
                    </el-input>
                </el-form-item>
                <!-- 新增：角色选择 -->
                <el-form-item prop="role" class="role-selector">
                    <div class="role-label">选择角色：</div>
                    <el-radio-group v-model="reg_form.role" class="role-radio-group">
                        <el-radio :label="0">普通用户</el-radio>
                        <el-radio :label="1">商家</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item class="btns">
                    <el-button type="primary" @click="zhuce()" class="register-btn">注册</el-button>
                </el-form-item>
            </el-form>
            <div class="back-login">
                <span @click="change(1)" class="link-item">
                    <i class="el-icon-arrow-left"></i>返回登录
                </span>
            </div>
        </div>

        <!-- 找回密码 -->
        <div class="forget_box" v-show="target == 3">
            <div class="head compact">
                <i class="el-icon-key"></i>
                <span>找回密码</span>
            </div>
            <el-form class="reg_form" :model="findback_form" :rules="findback_rules" ref="findback_form">
                <el-form-item prop="userortel">
                    <el-input v-model="findback_form.userortel" spellcheck="false" placeholder="手机号码"
                        prefix-icon="el-icon-mobile-phone" class="custom-input">
                    </el-input>
                </el-form-item>
                <el-form-item prop="password">
                    <el-input v-model="findback_form.password" show-password spellcheck="false" placeholder="新密码"
                        prefix-icon="el-icon-lock" class="custom-input">
                    </el-input>
                </el-form-item>
                <el-form-item class="btns">
                    <el-button type="primary" @click="findback()" class="reset-btn">确认修改</el-button>
                </el-form-item>
            </el-form>
            <div class="back-login">
                <span @click="change(1)" class="link-item">
                    <i class="el-icon-arrow-left"></i>返回登录
                </span>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'MyLogin',
    data() {
        var checkPassword = (rule, value, cb) => {
            const regPassword = /(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{6,12}$/;
            if (regPassword.test(value)) {
                return cb()
            }
            cb(new Error('包含大写字母、小写字母、数字，长度在6-12位之间'))
        };
        var checkMobile = (rule, value, cb) => {
            const regMobile = /^1[3-9]\d{9}$/;
            if (regMobile.test(value)) {
                return cb()
            }
            cb(new Error('请输入正确的11位手机号码'))
        };
        var checkUserOrTel = (rule, value, cb) => {
            if (!value) {
                return cb(new Error('请输入用户名或手机号'))
            }
            if (/^\d+$/.test(value)) {
                const regMobile = /^1[3-9]\d{9}$/;
                if (!regMobile.test(value)) {
                    return cb(new Error('请输入正确的11位手机号码'))
                }
            }
            else if (value.length < 2 || value.length > 20) {
                return cb(new Error('用户名长度应在2-20位之间'))
            }
            cb()
        };

        return {
            target: 1,
            login_form: {
                userortel: '',
                password: '',
            },
            reg_form: {
                username: '',
                password: '',
                telephone: '',
                role: 0, // 新增：默认选择普通用户
            },
            findback_form: {
                userortel: '',
                password: '',
            },
            login_rules: {
                userortel: [
                    { required: true, message: '请输入用户名或手机号', trigger: 'blur' },
                    { validator: checkUserOrTel, trigger: 'blur' }
                ],
                password: [
                    { required: true, message: '请输入密码', trigger: 'blur' }
                ]
            },
            reg_rules: {
                username: [
                    { required: true, message: '请设置用户名', trigger: 'blur' },
                    { min: 2, max: 20, message: '用户名长度在 2 到 20 个字符', trigger: 'blur' }
                ],
                password: [
                    { required: true, message: '请设置密码', trigger: 'blur' },
                    { validator: checkPassword, trigger: 'blur' }
                ],
                telephone: [
                    { required: true, message: '请绑定手机号', trigger: 'blur' },
                    { validator: checkMobile, trigger: 'blur' }
                ],
                role: [
                    { required: true, message: '请选择角色类型', trigger: 'change' }
                ]
            },
            findback_rules: {
                userortel: [
                    { required: true, message: '请输入电话', trigger: 'blur' },
                    { validator: checkMobile, trigger: 'blur' }
                ],
                password: [
                    { required: true, message: '请输入密码', trigger: 'blur' }
                ]
            },
        }
    },
    methods: {
      findback() {
        this.$refs.findback_form.validate(valid => {
            if (!valid) return;

            this.$axios.post('/api/user/resetPassword', {
                telephone: this.findback_form.userortel,
                newPassword: this.findback_form.password
            }).then(res => {
                if (res.data.status === 200) {
                    this.$message.success('密码重置成功！请使用新密码登录');

                    // 自动填充登录表单
                    this.login_form.userortel = this.findback_form.userortel;
                    this.login_form.password = this.findback_form.password;

                    // 切换到登录面板
                    this.target = 1;

                    // 重置找回密码表单
                    this.$refs.findback_form.resetFields();

                } else {
                    this.$message.error(res.data.msg || '密码重置失败，请稍后重试');
                }
            }).catch(err => {
                console.error('密码重置请求失败:', err);
                this.$message.error('网络错误，请检查网络后重试');
            });
        });
    },
       zhuce() {
            this.$refs.reg_form.validate(valid => {
                if (!valid) return;

                this.$axios.post('/api/user/register/test', {
                    username: this.reg_form.username,
                    password: this.reg_form.password,
                    telephone: this.reg_form.telephone,
                    role: this.reg_form.role // 新增：传递角色参数
                }).then(res => {
                    if (res.data.status === 200) {
                        this.$message.success('注册成功！即将自动为您登录');

                        // 自动填充登录表单
                        this.login_form.userortel = this.reg_form.telephone;
                        this.login_form.password = this.reg_form.password;

                        // 切换到登录面板
                        this.target = 1;

                        // 延迟 800ms 后自动登录
                        setTimeout(() => {
                            this.llogin();
                        }, 800);

                    } else {
                        this.$message.error(res.data.msg || '注册失败，请稍后重试');
                    }
                }).catch(err => {
                    console.error('注册请求失败:', err);
                    this.$message.error('网络错误，请检查网络后重试');
                });
            });
        },
        change(id) {
            this.target = id;
        },
        llogin() {
            this.$refs.login_form.validate(valid => {
                if (!valid)
                    return;
                else
                    this.login();
            })
        },
        async login() {
            this.$axios.post("/api/user/login", this.login_form).then((res) => {
                if (res.data.code != 200) {
                    return this.$message({
                        message: res.data.msg,
                        type: 'error'
                    })
                } else {
                    this.$message({
                        message: '登录成功',
                        type: 'success'
                    })

                    const token = res.data.token;
                    const role = res.data.role;
                    const is_super = res.data.is_super;

                    console.log('登录响应数据:', res.data);

                    // 保存 token
                    if (role == 1) {
                        localStorage.setItem('admin_token', token);
                    }
                    localStorage.setItem("token", token);

                    // 保存角色信息
                    localStorage.setItem("role", role);
                    localStorage.setItem("isSuper", is_super);

                    // 保存用户信息
                    const userInfo = {
                        username: res.data.username || this.login_form.userortel,
                        role: role,
                        is_super: is_super,
                        id: res.data.id
                    };

                    console.log('保存的用户信息:', userInfo);
                    localStorage.setItem('userInfo', JSON.stringify(userInfo));

                    // 设置 axios 公共头部
                    this.$axios.defaults.headers.common['token'] = token;

                    // 路由跳转
                    if (is_super == 1) {
                        this.$router.push('/manage');
                    } else if (role == 1 && is_super == 0) {
                        this.$router.push('/store');
                    } else {
                        this.$router.push('/user');
                    }
                }
            }).catch((error) => {
                console.error('登录失败:', error);
                console.error('错误详情:', {
                    message: error.message,
                    code: error.code,
                    response: error.response,
                    config: error.config
                });
                
                // 显示详细的错误信息
                let errorMsg = "网络故障";
                if (error.friendlyMessage) {
                    errorMsg = error.friendlyMessage;
                } else if (error.response) {
                    errorMsg = `服务器错误(${error.response.status})`;
                } else if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
                    errorMsg = '无法连接到服务器，请检查：\n1. 后端服务是否运行\n2. 手机和电脑是否在同一局域网\n3. 电脑防火墙设置';
                }
                
                this.$message({
                    message: errorMsg,
                    type: 'error',
                    duration: 5000
                })
            })
        }
    }
}
</script>
<style lang="less" scoped>
.login-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    height: 100vh;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}

.background-decor {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    pointer-events: none;
}

.circle {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);

    &.circle-1 {
        width: 200px;
        height: 200px;
        top: 10%;
        left: 10%;
        animation: float 6s ease-in-out infinite;
    }

    &.circle-2 {
        width: 150px;
        height: 150px;
        bottom: 20%;
        right: 15%;
        animation: float 8s ease-in-out infinite reverse;
    }

    &.circle-3 {
        width: 100px;
        height: 100px;
        top: 50%;
        right: 20%;
        animation: float 10s ease-in-out infinite;
    }
}

@keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-20px) rotate(180deg); }
}

.login_box, .reg_box, .forget_box {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 40px;
    width: 450px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}

.login_box {
    height: auto; /* 改为自动高度 */
    min-height: 300px; /* 设置最小高度 */
}

.reg_box {
    height: auto; /* 改为自动高度 */
    min-height: 410px; /* 设置最小高度 */
    display: flex;
    flex-direction: column;
}

.forget_box {
    height: auto; /* 改为自动高度 */
    min-height: 320px; /* 设置最小高度 */
}

.head {
    text-align: center;
    height: 50px;
    line-height: 50px;
    font-size: larger;
    margin-bottom: 20px;

    .logo {
        display: flex;
        align-items: center;
        justify-content: center;

        i {
            font-size: 32px;
            color: #667eea;
            margin-right: 10px;
        }

        span {
            font-size: 24px;
            font-weight: 600;
            color: #333;
        }
    }

    &.compact {
        display: flex;
        align-items: center;
        justify-content: center;

        i {
            font-size: 24px;
            color: #667eea;
            margin-right: 8px;
        }

        span {
            font-size: 20px;
            font-weight: 600;
            color: #333;
        }
    }
}

.custom-input {
    margin-bottom: 20px;

    /deep/ .el-input__inner {
        border-radius: 12px;
        border: 2px solid #e1e5e9;
        padding: 12px 15px 12px 45px;
        font-size: 14px;
        transition: all 0.3s ease;
        height: 48px;

        &:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
    }

    /deep/ .el-input__prefix {
        left: 15px;
        display: flex;
        align-items: center;

        .el-input__icon {
            color: #667eea;
            font-size: 18px;
            margin-right: 8px;
        }
    }
}

/* 新增：角色选择样式 */
.role-selector {
    margin-bottom: 25px; /* 增加底部间距 */

    .role-label {
        margin-bottom: 12px; /* 增加标签底部间距 */
        font-weight: 500;
        color: #606266;
        font-size: 14px;
    }

    .role-radio-group {
        width: 100%;

        .el-radio {
            margin-right: 20px;
            margin-bottom: 8px; /* 单选按钮之间的间距 */
        }
    }
}

/* 修改：注册表单样式，确保有足够的间距 */
.reg_form {
    flex: 1; /* 占据剩余空间 */
    display: flex;
    flex-direction: column;
    justify-content: space-between; /* 在表单项之间均匀分布空间 */
}

.btns {
    text-align: center;
    margin-top: 30px; /* 增加顶部间距 */
    margin-bottom: 10px; /* 底部间距 */

    .login-btn, .register-btn, .reset-btn {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        padding: 12px;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.3s ease;

        &:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
    }
}

.operate {
    text-align: center;
    color: #000;
    opacity: .5;
    font-weight: 400;
    font-size: 16px;
    margin-top: 20px;
}

#op1 {
    padding-left: 15px;
    padding-right: 30px;
    border-right: 1px solid #bdb9b9;
    cursor: pointer;
    transition: color 0.3s ease;

    &:hover {
        color: #667eea;
    }
}

#op2 {
    padding-left: 30px;
    padding-right: 15px;
    cursor: pointer;
    transition: color 0.3s ease;

    &:hover {
        color: #667eea;
    }
}

.back-login {
    text-align: center;
    margin-top: 20px;

    .link-item {
        color: #667eea;
        font-size: 14px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        transition: color 0.3s ease;

        &:hover {
            color: #764ba2;
        }
    }
}

.el-form-item {
    width: 100%;
    margin-bottom: 20px;
}

/* 确保所有表单项有适当的间距 */
.reg_form .el-form-item:not(.btns) {
    margin-bottom: 20px;
}

/* 为注册按钮提供更多空间 */
.reg_form .btns {
    margin-top: auto; /* 将按钮推到底部 */
    padding-top: 20px; /* 顶部内边距 */
}
</style>