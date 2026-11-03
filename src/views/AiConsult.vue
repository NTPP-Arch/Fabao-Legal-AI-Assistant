<template>
  <main class="workspace-page consult-page">
    <!-- 页面标题沿用全站工作台骨架，保持英文眉题、中文标题和说明文字的层级。 -->
    <section class="workspace-heading">
      <div>
        <p class="workspace-heading__eyebrow">AI LEGAL CONSULTATION</p>
        <h1>AI法律咨询</h1>
        <p>描述事实与疑问，法宝会结合对话上下文给出法律信息参考。</p>
      </div>
      <!-- 新建对话只创建空会话，不会把用户输入提前发送给 AI。 -->
      <el-button type="primary" :icon="Plus" @click="handleCreateConversation()">新建对话</el-button>
    </section>

    <!-- 主体采用固定宽度侧栏 + 自适应聊天区，适配桌面端法律工作台。 -->
    <section class="consult-layout">
      <aside class="conversation-sidebar" aria-label="对话列表">
        <!-- 侧栏顶部仅放列表标题和刷新动作，不设置分页，便于快速切换会话。 -->
        <div class="conversation-sidebar__header">
          <span>我的对话</span>
          <el-button link :icon="Refresh" :loading="loadingConversations" @click="loadConversations">刷新</el-button>
        </div>
        <div v-loading="loadingConversations" class="conversation-list">
          <!-- 当前会话通过 active 类高亮，时间使用后端 updated_at 字段。 -->
          <button
            v-for="conversation in conversations"
            :key="conversation.id"
            type="button"
            class="conversation-item"
            :class="{ 'conversation-item--active': conversation.id === activeConversationId }"
            @click="selectConversation(conversation.id)"
          >
            <span class="conversation-item__title">{{ conversation.title || '新建对话' }}</span>
            <span class="conversation-item__time">{{ formatTime(conversation.updated_at) }}</span>
          </button>
          <el-empty v-if="!loadingConversations && !conversations.length" description="还没有对话" :image-size="70" />
        </div>
      </aside>

      <section class="chat-panel" aria-label="法律咨询对话">
        <!-- 顶栏显示在线状态、当前标题和删除入口。删除操作由 el-popconfirm 二次确认。 -->
        <div class="chat-panel__topbar">
          <div>
            <span class="chat-panel__status"><i></i> 法宝 AI 助手</span>
            <strong>{{ activeConversation?.title || '请选择或新建对话' }}</strong>
          </div>
          <el-popconfirm
            v-if="activeConversation"
            title="确定删除这个对话吗？"
            confirm-button-text="删除"
            cancel-button-text="取消"
            @confirm="handleDeleteConversation"
          >
            <template #reference>
              <el-button link type="danger" :icon="Delete">删除</el-button>
            </template>
          </el-popconfirm>
        </div>

        <!-- 消息容器单独滚动，新消息或切换会话后都会滚动到最底部。 -->
        <div ref="messageListRef" class="message-list" v-loading="loadingMessages">
          <div v-if="!messages.length && !loadingMessages" class="chat-empty">
            <div class="chat-empty__icon"><el-icon><ChatDotRound /></el-icon></div>
            <h2>从一个问题开始</h2>
            <p>例如：劳动合同到期不续签，需要支付经济补偿吗？</p>
          </div>
          <article
            v-for="message in messages"
            :key="message.id"
            class="message-row"
            :class="`message-row--${message.role}`"
          >
            <div class="message-avatar">
              <el-icon v-if="message.role === 'assistant'"><MagicStick /></el-icon>
              <span v-else>我</span>
            </div>
            <div class="message-bubble">
              <span class="message-bubble__role">{{ message.role === 'assistant' ? '法宝 AI' : '我' }}</span>
              <p>{{ message.content }}</p>
            </div>
          </article>
        </div>

        <!-- 输入框使用原生 keydown 判断 Enter：Enter 发送，Shift+Enter 保留换行。 -->
        <form class="chat-composer" @submit.prevent="handleSend">
          <el-input
            v-model="draftMessage"
            type="textarea"
            :rows="3"
            resize="none"
            maxlength="20000"
            show-word-limit
            placeholder="请输入您的法律问题，尽量提供完整事实背景……"
            :disabled="sending || !activeConversation"
            @keydown="handleComposerKeydown"
          />
          <div class="chat-composer__footer">
            <span>AI 生成内容仅供参考，不构成正式法律意见</span>
            <el-button type="primary" native-type="submit" :loading="sending" :disabled="!draftMessage.trim() || !activeConversation">
              {{ sending ? '正在分析…' : '发送' }}
              <el-icon v-if="!sending"><Position /></el-icon>
            </el-button>
          </div>
        </form>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Delete, MagicStick, Plus, Position, Refresh } from '@element-plus/icons-vue'
import { createConversation, deleteConversation, getConversations, getMessages, sendMessage } from '../api/chat'

// 会话列表和当前会话 ID 分开保存，切换列表时不会丢失当前输入状态以外的页面状态。
const conversations = ref([])
const activeConversationId = ref(null)
// 当前会话的消息按后端返回顺序保存，聊天内容始终以纯文本渲染。
const messages = ref([])
const draftMessage = ref('')
// 三类 loading 分别对应会话列表、历史消息和 AI 长耗时请求。
const loadingConversations = ref(false)
const loadingMessages = ref(false)
const sending = ref(false)
const messageListRef = ref(null)

// 通过计算属性读取当前会话，避免在新建、删除和刷新列表时手动同步对象。
const activeConversation = computed(() => conversations.value.find((item) => item.id === activeConversationId.value))

// 将 ISO 时间转换为简洁的月日格式，列表中不展示过多时间细节。
function formatTime(value) {
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '' : date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

// 等待 Vue 完成消息 DOM 更新后再设置滚动高度，确保新消息真正出现在底部。
async function scrollToBottom() {
  await nextTick()
  if (messageListRef.value) messageListRef.value.scrollTop = messageListRef.value.scrollHeight
}

// 页面进入或用户点击刷新时加载当前用户的会话列表。
async function loadConversations() {
  loadingConversations.value = true
  try {
    const response = await getConversations()
    conversations.value = response.data || []
    // 后端没有会话时自动创建一个空会话，进入页面即可直接输入问题。
    if (!conversations.value.length) {
      await handleCreateConversation(false)
    } else if (!activeConversationId.value || !conversations.value.some((item) => item.id === activeConversationId.value)) {
      await selectConversation(conversations.value[0].id)
    }
  } catch {
    // 错误消息由 API 拦截器展示。
  } finally {
    loadingConversations.value = false
  }
}

// 创建会话后立即插入列表并选中；showMessage=false 用于首次自动创建时避免打扰用户。
async function handleCreateConversation(showMessage = true) {
  try {
    const response = await createConversation({ title: '新建对话' })
    conversations.value.unshift(response.data)
    activeConversationId.value = response.data.id
    messages.value = []
    if (showMessage) ElMessage.success('新对话已创建')
  } catch {
    // 错误消息由 API 拦截器展示。
  }
}

// 切换会话时读取该会话的完整历史，失败时清空消息区但保留列表状态。
async function selectConversation(id) {
  activeConversationId.value = id
  loadingMessages.value = true
  try {
    const response = await getMessages(id)
    messages.value = response.data || []
    await scrollToBottom()
  } catch {
    messages.value = []
  } finally {
    loadingMessages.value = false
  }
}

// 删除成功后优先选中剩余第一条；如果已经没有会话则自动补建空会话。
async function handleDeleteConversation() {
  if (!activeConversationId.value) return
  try {
    const deletedId = activeConversationId.value
    await deleteConversation(deletedId)
    conversations.value = conversations.value.filter((item) => item.id !== deletedId)
    activeConversationId.value = null
    messages.value = []
    if (conversations.value.length) await selectConversation(conversations.value[0].id)
    else await handleCreateConversation(false)
    ElMessage.success('对话已删除')
  } catch {
    // 错误消息由 API 拦截器展示。
  }
}

// 发送消息前去除首尾空白，避免只发送空格；失败时不清空输入，方便用户重试。
async function handleSend() {
  const content = draftMessage.value.trim()
  if (!content || !activeConversationId.value || sending.value) return
  sending.value = true
  try {
    const response = await sendMessage(activeConversationId.value, content)
    messages.value.push(response.data.user_message, response.data.assistant_message)
    draftMessage.value = ''
    const current = conversations.value.find((item) => item.id === activeConversationId.value)
    if (current) {
      current.title = content.slice(0, 100)
      current.updated_at = new Date().toISOString()
    }
    await scrollToBottom()
  } catch {
    // 长请求失败时由全局 http.js 拦截器提示，页面只保留输入并结束 loading。
  } finally {
    sending.value = false
  }
}

// textarea 的 Enter 行为：普通 Enter 发送，Shift+Enter 交给 textarea 插入换行。
function handleComposerKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault()
    handleSend()
  }
}

// 页面挂载即执行列表加载，满足“进入页面自动加载并自动创建空会话”的交互要求。
onMounted(loadConversations)
</script>

<style scoped>
.workspace-page { width: min(var(--page-width), calc(100% - 48px)); margin: 0 auto; padding: 58px 0 86px; }
.workspace-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 24px; margin-bottom: 28px; }
.workspace-heading__eyebrow { margin: 0 0 10px; color: var(--color-gold); font-size: 11px; font-weight: 700; letter-spacing: .18em; }
.workspace-heading h1 { margin: 0 0 9px; color: var(--color-primary); font-size: 34px; }
.workspace-heading > div > p:last-child { margin: 0; color: var(--color-text-secondary); font-size: 14px; }
.consult-layout { display: grid; grid-template-columns: 270px minmax(0, 1fr); min-height: 610px; overflow: hidden; border: 1px solid var(--color-border); border-radius: var(--radius-large); background: var(--color-surface); box-shadow: var(--shadow-card); }
.conversation-sidebar { border-right: 1px solid var(--color-border); background: #f8fafc; }
.conversation-sidebar__header, .chat-panel__topbar, .chat-composer__footer { display: flex; align-items: center; justify-content: space-between; }
.conversation-sidebar__header { padding: 21px 18px 16px; color: var(--color-primary); font-size: 14px; font-weight: 700; }
.conversation-list { max-height: 520px; padding: 0 10px 15px; overflow-y: auto; }
.conversation-item { display: flex; width: 100%; flex-direction: column; align-items: flex-start; gap: 7px; margin-bottom: 5px; padding: 13px 12px; border: 1px solid transparent; border-radius: 11px; color: var(--color-text-secondary); background: transparent; cursor: pointer; font: inherit; text-align: left; transition: .2s ease; }
.conversation-item:hover, .conversation-item--active { border-color: rgba(201,169,110,.35); color: var(--color-primary); background: #fff; }
.conversation-item__title { width: 100%; overflow: hidden; font-size: 13px; font-weight: 600; text-overflow: ellipsis; white-space: nowrap; }
.conversation-item__time { color: #97a5b1; font-size: 11px; }
.chat-panel { display: flex; min-width: 0; flex-direction: column; }
.chat-panel__topbar { min-height: 72px; padding: 14px 24px; border-bottom: 1px solid var(--color-border); }
.chat-panel__status, .chat-panel__topbar strong { display: block; }
.chat-panel__status { margin-bottom: 5px; color: #4b9666; font-size: 11px; }
.chat-panel__status i { display: inline-block; width: 6px; height: 6px; margin-right: 4px; border-radius: 50%; background: #59ad77; }
.chat-panel__topbar strong { max-width: 430px; overflow: hidden; color: var(--color-primary); font-size: 15px; text-overflow: ellipsis; white-space: nowrap; }
.message-list { display: flex; min-height: 390px; flex: 1; flex-direction: column; gap: 21px; padding: 27px 30px; overflow-y: auto; background: linear-gradient(180deg, #fff, #fbfcfe); }
.message-row { display: flex; align-items: flex-start; gap: 11px; max-width: 88%; }
.message-row--user { align-self: flex-end; flex-direction: row-reverse; }
.message-avatar { display: grid; width: 32px; height: 32px; flex: none; place-items: center; border-radius: 10px; color: var(--color-primary); background: var(--color-primary-soft); font-size: 12px; font-weight: 700; }
.message-row--user .message-avatar { color: #896b36; background: #f8eedb; }
.message-bubble { padding: 12px 15px; border: 1px solid var(--color-border); border-radius: 4px 15px 15px 15px; background: #fff; box-shadow: 0 6px 16px rgba(26,58,92,.05); }
.message-row--user .message-bubble { border-color: rgba(201,169,110,.25); border-radius: 15px 4px 15px 15px; background: #fffaf1; }
.message-bubble__role { display: block; margin-bottom: 6px; color: var(--color-gold); font-size: 10px; font-weight: 700; }
.message-bubble p { margin: 0; color: var(--color-text); font-size: 14px; line-height: 1.8; white-space: pre-wrap; }
.chat-empty { margin: auto; color: var(--color-text-secondary); text-align: center; }
.chat-empty__icon { display: grid; width: 56px; height: 56px; margin: 0 auto 14px; place-items: center; border-radius: 17px; color: var(--color-primary); background: var(--color-primary-soft); font-size: 27px; }
.chat-empty h2 { margin: 0 0 7px; color: var(--color-primary); font-size: 20px; }
.chat-empty p { margin: 0; font-size: 13px; }
.chat-composer { padding: 17px 22px 19px; border-top: 1px solid var(--color-border); background: #fff; }
.chat-composer__footer { gap: 15px; margin-top: 10px; }
.chat-composer__footer span { color: #9aa7b2; font-size: 11px; }
@media (max-width: 820px) { .workspace-page { width: min(var(--page-width), calc(100% - 32px)); padding-top: 38px; } .consult-layout { grid-template-columns: 1fr; } .conversation-sidebar { border-right: 0; border-bottom: 1px solid var(--color-border); } .conversation-list { display: flex; max-height: 130px; gap: 5px; overflow-x: auto; } .conversation-item { width: 170px; flex: none; } }
@media (max-width: 560px) { .workspace-heading { align-items: flex-start; flex-direction: column; } .message-list { padding: 22px 15px; } .message-row { max-width: 96%; } .chat-panel__topbar { padding: 12px 15px; } }
</style>
