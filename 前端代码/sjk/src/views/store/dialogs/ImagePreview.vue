<template>
    <el-dialog
        title="图片预览"
        :visible="visible"
        width="400px"
        center
        @close="handleClose"
        @update:visible="$emit('close')">
        <div style="text-align: center;">
            <img :src="imageUrl" alt="预览图片" style="max-width: 100%; max-height: 400px;" @error="handleImageError">
        </div>
        <span slot="footer" class="dialog-footer">
            <el-button @click="handleClose">关闭</el-button>
        </span>
    </el-dialog>
</template>

<script>
export default {
    name: 'ImagePreview',
    props: {
        visible: {
            type: Boolean,
            default: false
        },
        imageUrl: {
            type: String,
            default: ''
        }
    },
    methods: {
        handleClose() {
            this.$emit('close');
        },
        handleImageError(event) {
            if (this.imageUrl) {
                event.target.src = '/images/default.jpg';
            }
        }
    }
}
</script>

<style scoped>
.dialog-footer {
    text-align: center;
}
</style>