<template>
  <div class="chatbot-wrapper">
    <!-- 浮动聊天按钮 -->
    <div class="chat-toggle-btn" @click="toggleChat" :class="{ active: isOpen }">
      <i :class="isOpen ? 'el-icon-close' : 'el-icon-chat-dot-round'"></i>
    </div>

    <!-- 聊天面板 -->
    <transition name="chat-slide">
      <div v-show="isOpen" class="chat-panel">
        <!-- 头部 -->
        <div class="chat-header">
          <span>AI 智能助手</span>
          <i class="el-icon-close" @click="toggleChat"></i>
        </div>

        <!-- 消息区域 -->
        <div class="chat-messages" ref="messageArea">
          <!-- 欢迎消息 -->
          <div class="message ai-message">
            <div class="message-bubble">
              <p>你好！我是AI智能助手，可以帮你查询店铺、菜品、订单等信息。</p>
              <p class="hint">试试问我：评分最高的店铺是哪家？</p>
            </div>
          </div>

          <!-- 消息列表 -->
          <div v-for="(msg, index) in messages" :key="index"
               :class="['message', msg.type === 'user' ? 'user-message' : 'ai-message']">
            <div class="message-bubble">
              <p>{{ msg.text }}</p>

              <!-- SQL 展示（仅 AI 消息） -->
              <div v-if="msg.sql" class="sql-section">
                <div class="sql-toggle" @click="msg.showSql = !msg.showSql">
                  <span>{{ msg.showSql ? '隐藏' : '查看' }} SQL</span>
                  <i :class="msg.showSql ? 'el-icon-arrow-up' : 'el-icon-arrow-down'"></i>
                </div>
                <transition name="fade">
                  <pre v-show="msg.showSql" class="sql-code">{{ msg.sql }}</pre>
                </transition>
              </div>

              <!-- 错误信息 -->
              <p v-if="msg.error" class="error-text">{{ msg.error }}</p>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="loading" class="message ai-message">
            <div class="message-bubble loading-bubble">
              <i class="el-icon-loading"></i>
              <span>{{ loadingText }}</span>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input">
          <el-input
            v-model="inputText"
            placeholder="输入你的问题..."
            :disabled="loading"
            @keyup.enter.native="sendMessage"
            clearable
          >
            <el-button slot="append"
                       icon="el-icon-s-promotion"
                       :loading="loading"
                       @click="sendMessage">
            </el-button>
          </el-input>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { askChat } from '@/api/index'

export default {
  name: 'ChatBot',
  data() {
    return {
      isOpen: false,
      inputText: '',
      messages: [],
      loading: false,
      loadingText: '正在思考...'
    }
  },
  methods: {
    toggleChat() {
      this.isOpen = !this.isOpen
      if (this.isOpen) {
        this.$nextTick(() => this.scrollToBottom())
      }
    },

    async sendMessage() {
      const question = this.inputText.trim()
      if (!question || this.loading) return

      // 添加用户消息
      this.messages.push({
        type: 'user',
        text: question
      })
      this.inputText = ''
      this.loading = true
      this.loadingText = '正在生成SQL查询...'
      this.scrollToBottom()

      // 模拟进度提示
      const timer1 = setTimeout(() => {
        this.loadingText = '正在查询数据库...'
      }, 2000)
      const timer2 = setTimeout(() => {
        this.loadingText = '正在生成回答...'
      }, 4000)

      try {
        const res = await askChat(question)
        clearTimeout(timer1)
        clearTimeout(timer2)

        // 添加 AI 回复
        this.messages.push({
          type: 'ai',
          text: res.data.answer || '查询完成',
          sql: res.data.sql || '',
          showSql: false,
          error: null
        })
      } catch (err) {
        clearTimeout(timer1)
        clearTimeout(timer2)

        const errorMsg = err.response?.data?.error || err.friendlyMessage || '请求失败，请稍后再试'
        this.messages.push({
          type: 'ai',
          text: '抱歉，出现了问题：',
          sql: err.response?.data?.sql || '',
          showSql: false,
          error: errorMsg
        })
      } finally {
        this.loading = false
        this.$nextTick(() => this.scrollToBottom())
      }
    },

    scrollToBottom() {
      const area = this.$refs.messageArea
      if (area) {
        area.scrollTop = area.scrollHeight
      }
    }
  }
}
</script>

<style scoped>
.chatbot-wrapper {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 9999;
}

.chat-toggle-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
  transition: all 0.3s;
  font-size: 24px;
}

.chat-toggle-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.6);
}

.chat-toggle-btn.active {
  background: linear-gradient(135deg, #909399, #b4b7bd);
}

.chat-panel {
  position: absolute;
  bottom: 70px;
  right: 0;
  width: 380px;
  height: 520px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 14px 18px;
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  color: white;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header i {
  cursor: pointer;
  font-size: 18px;
  opacity: 0.8;
}

.chat-header i:hover {
  opacity: 1;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
}

.message {
  margin-bottom: 14px;
  display: flex;
}

.user-message {
  justify-content: flex-end;
}

.ai-message {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.user-message .message-bubble {
  background: #409EFF;
  color: white;
  border-bottom-right-radius: 4px;
}

.ai-message .message-bubble {
  background: white;
  color: #303133;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  border-bottom-left-radius: 4px;
}

.message-bubble p {
  margin: 0 0 6px 0;
}

.message-bubble p:last-child {
  margin-bottom: 0;
}

.hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.user-message .hint {
  color: rgba(255, 255, 255, 0.7);
}

.sql-section {
  margin-top: 8px;
  border-top: 1px solid #ebeef5;
  padding-top: 6px;
}

.sql-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #909399;
}

.sql-toggle:hover {
  color: #409EFF;
}

.sql-code {
  margin-top: 6px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 11px;
  color: #606266;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Courier New', monospace;
}

.error-text {
  color: #f56c6c;
  font-size: 13px;
}

.loading-bubble {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
}

.loading-bubble i {
  font-size: 16px;
}

.chat-input {
  padding: 12px;
  border-top: 1px solid #ebeef5;
  background: white;
}

/* 动画 */
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.3s ease;
}

.chat-slide-enter,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s ease;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
  max-height: 0;
}
</style>
