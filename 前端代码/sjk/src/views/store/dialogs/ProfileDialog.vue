<template>
    <el-dialog
        title="商家个人信息"
        :visible="visible"
        width="500px"
        center
        :close-on-click-modal="false"
        @close="handleClose"
        @update:visible="$emit('close')">
        <el-form :model="localFormData" :rules="rules" ref="formRef" label-width="100px">
            <el-form-item label="用户名" prop="user_name">
                <el-input v-model="localFormData.user_name" disabled></el-input>
            </el-form-item>
            <el-form-item label="真实姓名" prop="real_name">
                <el-input v-model="localFormData.real_name"></el-input>
            </el-form-item>
            <el-form-item label="性别" prop="sex">
                <el-radio-group v-model="localFormData.sex">
                    <el-radio label="男">男</el-radio>
                    <el-radio label="女">女</el-radio>
                </el-radio-group>
            </el-form-item>
            <el-form-item label="年龄" prop="age">
                <el-input-number
                    v-model="localFormData.age"
                    :min="1"
                    :max="120"
                    style="width: 100%">
                </el-input-number>
            </el-form-item>
            <el-form-item label="邮箱" prop="mail">
                <el-input v-model="localFormData.mail"></el-input>
            </el-form-item>
            <el-form-item label="手机号">
                <el-input v-model="localFormData.phone" disabled></el-input>
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
    name: 'ProfileDialog',
    props: {
        visible: {
            type: Boolean,
            default: false
        },
        formData: {
            type: Object,
            default: () => ({
                real_name: '',
                sex: '',
                age: null,
                mail: '',
                phone: '',
                user_name: ''
            })
        }
    },
    data() {
        return {
            loading: false,
            localFormData: {},
            rules: {
                real_name: [
                    { required: true, message: '请输入真实姓名', trigger: 'blur' }
                ],
                mail: [
                    { type: 'email', message: '请输入正确的邮箱格式', trigger: ['blur', 'change'] }
                ]
            }
        }
    },
    watch: {
        formData: {
            handler(newVal) {
                this.localFormData = { ...newVal };
            },
            immediate: true,
            deep: true
        },
        visible(newVal) {
            if (!newVal) {
                // 对话框关闭时重置 loading 状态
                this.loading = false;
                this.$refs.formRef.clearValidate();
            }
        }
    },
    methods: {
        handleClose() {
            this.$emit('close');
        },
        handleSave() {
            this.$refs.formRef.validate(valid => {
                if (valid) {
                    this.loading = true;
                    this.$emit('save', { ...this.localFormData });
                }
            });
        }
    }
}
</script>

<style scoped>
.dialog-footer {
    text-align: center;
}
</style>