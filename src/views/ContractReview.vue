<template>
  <main class="workspace-page contract-page">
    <!-- 页面标题和文书生成页保持同一套层次：眉题、主标题、说明文字。 -->
    <section class="contract-hero">
      <p class="workspace-heading__eyebrow">CONTRACT RISK REVIEW</p>
      <h1>合同审查</h1>
      <p>上传 DOCX 或 PDF 合同，提取原文并获取结构化风险提示。</p>
    </section>

    <!-- 用三步流程提示当前进度，上传、解析和 AI 审查的状态一目了然。 -->
    <section class="contract-steps" aria-label="合同审查流程">
      <el-steps :active="reviewStep" align-center finish-status="success">
        <el-step title="上传合同" description="选择 DOCX 或 PDF 文件" />
        <el-step title="提取文本" description="读取合同原文" />
        <el-step title="智能审查" description="分析风险条款" />
      </el-steps>
    </section>

    <!-- 左侧负责文件生命周期，右侧负责结构化审查结果和历史记录。 -->
    <section class="contract-layout">
      <el-card class="upload-card" shadow="never">
        <template #header>
          <div class="card-header">
            <div class="card-heading">
              <span class="card-step">01</span>
              <div><strong>上传合同</strong><small>选择文件并提取合同原文</small></div>
            </div>
            <el-tag type="info">最大 10MB</el-tag>
          </div>
        </template>
        <!-- 使用隐藏原生 input 保留浏览器文件选择能力，按钮只负责触发选择器。 -->
        <div class="upload-dropzone" :class="{ 'upload-dropzone--selected': selectedFile }">
          <input ref="fileInputRef" class="file-input" type="file" accept=".docx,.pdf" @change="handleFileChange" />
          <div class="upload-icon"><el-icon><UploadFilled /></el-icon></div>
          <h2>{{ selectedFile ? selectedFile.name : '选择合同文件' }}</h2>
          <p>支持 .docx / .pdf 格式，文件大小不超过 10MB</p>
          <el-button type="primary" plain @click="openFilePicker">选择文件</el-button>
        </div>
        <div v-if="selectedFile" class="selected-file">
          <span><el-icon><Document /></el-icon>{{ selectedFile.name }}</span>
          <el-button link type="danger" @click="clearSelectedFile">移除</el-button>
        </div>
        <!-- 上传按钮在没有合法文件或正在上传时不可点击，避免重复创建合同记录。 -->
        <el-button class="upload-button" type="primary" size="large" :loading="uploading" :disabled="!selectedFile || uploading" @click="handleUpload">
          {{ uploading ? '正在上传并解析…' : '上传并提取文本' }}
        </el-button>

        <!-- 上传成功后展示后端提取的合同原文，并把合同 ID 用于后续审查。 -->
        <div v-if="currentContract" class="original-text-block">
          <div class="block-title">
            <div class="block-heading"><span class="block-step">02</span><div><strong>合同原文</strong><small>已完成文本提取，可在审查前核对</small></div></div>
            <el-tag size="small" type="success">已提取</el-tag>
          </div>
          <el-input v-model="currentContract.original_text" type="textarea" :rows="10" readonly resize="none" />
          <el-button class="review-button" type="primary" :loading="reviewing" :disabled="reviewing" @click="handleReview(currentContract.id)">
            {{ reviewing ? '正在审查…' : currentContract.review_result ? '重新审查' : '开始风险审查' }}
          </el-button>
        </div>
      </el-card>

      <section class="review-column">
        <el-card class="review-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div class="card-heading">
                <span class="card-step">03</span>
                <div><strong>审查结果</strong><small>AI 识别的风险等级与修改建议</small></div>
              </div>
              <el-tag v-if="reviewResult && !reviewResult.parse_error && reviewResult.risk_level" :type="riskTagType(reviewResult.risk_level)">
                {{ reviewResult.risk_level }}风险
              </el-tag>
            </div>
          </template>
          <div v-if="reviewResult" class="review-result">
            <template v-if="reviewResult.parse_error">
              <!-- parse_error 表示模型没有返回可解析 JSON，此时只展示 summary 原文。 -->
              <el-alert
                title="AI 返回格式异常，已展示原始文本"
                type="warning"
                :closable="false"
                show-icon
              >
                <template #default>
                  <span>模型结果未能解析为结构化风险清单（{{ reviewResult.parse_error || '未知解析错误' }}）。</span>
                </template>
              </el-alert>
              <pre class="raw-summary">{{ reviewResult.summary || '模型未返回原始文本。' }}</pre>
            </template>
            <template v-else>
              <div class="risk-overview">
                <div class="score-panel">
                  <el-progress
                    v-if="riskScore !== null"
                    type="circle"
                    :percentage="riskScore"
                    :color="scoreColor"
                    :width="116"
                    :stroke-width="10"
                  >
                    <template #default="{ percentage }">
                      <strong class="score-number">{{ percentage }}</strong>
                      <span class="score-unit">风险分</span>
                    </template>
                  </el-progress>
                  <div v-else class="score-missing">暂无风险分</div>
                  <span class="score-caption">综合风险评分</span>
                </div>
                <div class="stats-panel">
                  <div class="stats-panel__heading">
                    <span>风险概览</span>
                    <el-tag v-if="reviewResult.risk_level" size="small" :type="riskTagType(reviewResult.risk_level)">{{ reviewResult.risk_level }}风险</el-tag>
                  </div>
                  <div class="risk-stats">
                    <div class="risk-stat risk-stat--high"><b>{{ riskCount('高') }}</b><span>高风险</span></div>
                    <div class="risk-stat risk-stat--medium"><b>{{ riskCount('中') }}</b><span>中风险</span></div>
                    <div class="risk-stat risk-stat--low"><b>{{ riskCount('低') }}</b><span>低风险</span></div>
                  </div>
                </div>
              </div>
              <div class="review-summary">
                <div class="summary-label"><el-icon><ChatDotRound /></el-icon><span>总体审查意见</span></div>
                <strong>{{ reviewResult.summary || '模型未返回总体审查意见。' }}</strong>
              </div>
              <div v-if="reviewResult.risk_items?.length" class="risk-list">
                <article v-for="(item, index) in reviewResult.risk_items" :key="`${item.level}-${index}`" class="risk-item" :class="`risk-item--${riskClass(item.level)}`">
                  <div class="risk-item__header">
                    <span class="risk-item__number">{{ String(index + 1).padStart(2, '0') }}</span>
                    <el-tag v-if="item.level" :type="riskTagType(item.level)" effect="dark">{{ item.level }}风险</el-tag>
                    <strong>{{ item.category || `风险条款 ${index + 1}` }}</strong>
                  </div>
                  <div v-if="item.law" class="risk-law"><el-icon><Collection /></el-icon><span>法条依据：{{ item.law }}</span></div>
                  <blockquote v-if="item.clause">“{{ item.clause }}”</blockquote>
                  <p v-if="item.analysis"><b>风险分析：</b>{{ item.analysis }}</p>
                  <p v-if="item.suggestion"><b>修改建议：</b>{{ item.suggestion }}</p>
                </article>
              </div>
              <el-empty v-else description="模型未返回风险条目" :image-size="70" />
            </template>
          </div>
          <el-empty v-else description="上传合同后开始审查" :image-size="110" />
        </el-card>

        <el-card class="history-card" shadow="never">
          <template #header><div class="card-header"><span>审查历史</span><el-button link :icon="Refresh" @click="loadHistory">刷新</el-button></div></template>
          <div v-loading="loadingHistory" class="history-list">
            <button v-for="item in history" :key="item.id" type="button" class="history-item" @click="selectHistory(item)">
              <span><el-icon><Document /></el-icon><b>{{ item.file_name }}</b></span>
              <span class="history-item__status">{{ item.review_result ? '已审查' : '待审查' }}</span>
            </button>
            <el-empty v-if="!loadingHistory && !history.length" description="暂无审查记录" :image-size="60" />
          </div>
        </el-card>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Collection, Document, Refresh, UploadFilled } from '@element-plus/icons-vue'
import { getContracts, reviewContract, uploadContract } from '../api/contract'

// 保存原生文件选择器引用，页面按钮通过它打开系统文件选择窗口。
const fileInputRef = ref(null)
// 当前待上传文件、已上传合同和历史记录分别独立保存，失败时不丢失用户选择。
const selectedFile = ref(null)
const currentContract = ref(null)
const history = ref([])
// 上传、审查、历史加载各自维护 loading，避免一个请求影响其他操作按钮。
const uploading = ref(false)
const reviewing = ref(false)
const loadingHistory = ref(false)
const reviewResult = computed(() => currentContract.value?.review_result || null)
// 进度条使用零基索引：未上传为 0，已提取文本为 1，已有审查结果为 2。
const reviewStep = computed(() => {
  if (reviewResult.value) return 2
  if (currentContract.value) return 1
  return 0
})
const riskScore = computed(() => {
  const value = Number(reviewResult.value?.risk_score)
  return Number.isFinite(value) ? Math.max(0, Math.min(100, value)) : null
})
const scoreColor = computed(() => {
  if (riskScore.value === null) return '#cbd8e2'
  if (riskScore.value >= 70) return '#f56c6c'
  if (riskScore.value >= 40) return '#e6a23c'
  return '#67c23a'
})

// 调用原生文件选择器；实际文件读取仍由 change 事件统一处理和校验。
function openFilePicker() {
  fileInputRef.value?.click()
}

// 前端先校验扩展名和大小，减少无效请求；后端仍会再次校验文件安全性。
function handleFileChange(event) {
  const file = event.target.files?.[0]
  if (!file) return
  const suffix = file.name.slice(file.name.lastIndexOf('.')).toLowerCase()
  if (!['.docx', '.pdf'].includes(suffix)) {
    ElMessage.error('仅支持 .docx 和 .pdf 文件')
    clearSelectedFile()
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 10MB')
    clearSelectedFile()
    return
  }
  selectedFile.value = file
}

// 清除待上传文件，同时重置 input，保证用户可以再次选择同名文件。
function clearSelectedFile() {
  selectedFile.value = null
  if (fileInputRef.value) fileInputRef.value.value = ''
}

// 上传接口使用现有 contract API 的 FormData；成功后展示原文并刷新历史。
async function handleUpload() {
  if (!selectedFile.value) return
  uploading.value = true
  try {
    const response = await uploadContract(selectedFile.value)
    currentContract.value = response.data
    await loadHistory()
    clearSelectedFile()
    ElMessage.success('合同上传并解析成功')
  } catch {
    // 错误消息由全局 http.js 拦截器展示，保留 selectedFile 便于重试。
  } finally {
    uploading.value = false
  }
}

// 对当前合同调用真实 AI 审查；接口返回后直接替换当前记录中的 review_result。
async function handleReview(id) {
  reviewing.value = true
  try {
    const response = await reviewContract(id)
    currentContract.value = response.data
    await loadHistory()
    ElMessage.success('合同审查完成')
  } catch {
    // 错误消息由全局 http.js 拦截器展示，页面只负责结束 reviewing 状态。
  } finally {
    reviewing.value = false
  }
}

// 点击历史记录后载入该条合同及已有审查结果。
function selectHistory(item) {
  currentContract.value = item
}

// 将后端中文风险等级映射为样式 class，未知值回退为中风险样式。
function riskClass(level) {
  return { 高: 'high', 中: 'medium', 低: 'low' }[level] || 'medium'
}

// 将后端风险等级映射为 Element Plus 标签类型。
function riskTagType(level) {
  return { 高: 'danger', 中: 'warning', 低: 'success' }[level] || 'info'
}

// 兼容后端当前中文 key，也兼容历史数据可能存在的英文 key。
function riskCount(level) {
  const stats = reviewResult.value?.risk_stats || {}
  const aliases = { 高: ['高', 'high'], 中: ['中', 'medium'], 低: ['低', 'low'] }
  return aliases[level].reduce((total, key) => total + (Number(stats[key]) || 0), 0)
}

// 页面进入时自动加载当前用户的合同历史。
async function loadHistory() {
  loadingHistory.value = true
  try {
    const response = await getContracts()
    history.value = response.data || []
  } catch {
    history.value = []
  } finally {
    loadingHistory.value = false
  }
}

onMounted(loadHistory)
</script>

<style scoped>
/* 页面整体与文书生成页使用同样的宽度、留白和浅色背景，减少不同功能页之间的跳变。 */
.contract-page { width: min(var(--page-width), calc(100% - 48px)); margin: 0 auto; padding: 58px 0 86px; }
.contract-hero { margin: 0 auto 42px; text-align: center; }
.workspace-heading__eyebrow { margin: 0 0 10px; color: var(--color-gold); font-size: 11px; font-weight: 700; letter-spacing: .2em; }
.contract-hero h1 { margin: 0; color: var(--color-primary); font-family: "STKaiti", "KaiTi", serif; font-size: clamp(36px, 4vw, 48px); letter-spacing: .08em; }
.contract-hero > p:last-child { margin: 14px 0 0; color: var(--color-text-secondary); font-size: 15px; line-height: 1.8; }

/* 三步流程是页面的第一层导航，帮助用户理解合同从上传到审查的状态变化。 */
.contract-steps { width: min(820px, 100%); margin: 0 auto 42px; padding: 0 24px; }
.contract-steps :deep(.el-step__title) { color: #94a0ae; font-size: 14px; }
.contract-steps :deep(.el-step__title.is-process) { color: var(--color-primary); font-weight: 700; }
.contract-steps :deep(.el-step__description) { color: var(--color-text-secondary); font-size: 11px; }
.contract-steps :deep(.el-step__head.is-process) { color: var(--color-primary); border-color: var(--color-primary); }
.contract-steps :deep(.el-step__head.is-success) { color: var(--color-gold); border-color: var(--color-gold); }
.contract-steps :deep(.el-step__line) { background-color: #dce2e9; }

.contract-layout { display: grid; grid-template-columns: minmax(360px, .82fr) minmax(0, 1.18fr); gap: 24px; align-items: start; }
.upload-card, .review-card, .history-card { overflow: hidden; border-color: var(--color-border); border-radius: var(--radius-large); box-shadow: 0 14px 38px rgba(26,58,92,.05); }
.upload-card { position: sticky; top: 98px; }
.card-header { display: flex; align-items: center; justify-content: space-between; gap: 14px; color: var(--color-primary); }
.card-heading, .block-heading { display: flex; min-width: 0; align-items: center; gap: 11px; }
.card-heading > div, .block-heading > div { display: flex; min-width: 0; flex-direction: column; gap: 4px; }
.card-heading strong, .block-heading strong { color: var(--color-primary); font-size: 16px; line-height: 1.35; }
.card-heading small, .block-heading small { color: var(--color-text-secondary); font-size: 11px; font-weight: 400; line-height: 1.4; }
.card-step, .block-step { display: grid; flex: none; width: 32px; height: 32px; place-items: center; border: 1px solid rgba(201,169,110,.42); border-radius: 50%; color: var(--color-gold); background: #fffaf1; font-size: 11px; font-weight: 800; }
.block-step { width: 28px; height: 28px; font-size: 10px; }

/* 上传区域采用明确的主操作层级，文件选择、文件确认和提交各自独立。 */
.upload-dropzone { position: relative; display: flex; min-height: 222px; flex-direction: column; align-items: center; justify-content: center; padding: 25px; border: 1px dashed #cbd8e2; border-radius: 14px; background: #fbfcfe; text-align: center; transition: border-color .2s ease, background-color .2s ease, box-shadow .2s ease; }
.upload-dropzone:hover, .upload-dropzone--selected { border-color: var(--color-gold); background: #fffaf2; box-shadow: 0 8px 22px rgba(201,169,110,.1); }
.file-input { position: absolute; width: 1px; height: 1px; overflow: hidden; opacity: 0; }
.upload-icon { display: grid; width: 56px; height: 56px; margin-bottom: 14px; place-items: center; border-radius: 16px; color: var(--color-primary); background: var(--color-primary-soft); font-size: 27px; }
.upload-dropzone h2 { max-width: 100%; margin: 0 0 7px; overflow: hidden; color: var(--color-primary); font-size: 17px; text-overflow: ellipsis; white-space: nowrap; }
.upload-dropzone p { margin: 0 0 18px; color: var(--color-text-secondary); font-size: 12px; }
.selected-file { display: flex; align-items: center; justify-content: space-between; gap: 14px; margin-top: 14px; padding: 11px 13px; border: 1px solid #dce8f1; border-radius: 9px; color: var(--color-primary); background: var(--color-primary-soft); font-size: 13px; }
.selected-file span { display: inline-flex; min-width: 0; align-items: center; gap: 6px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.upload-button, .review-button { width: 100%; margin-top: 17px; }
.original-text-block { margin-top: 27px; padding-top: 23px; border-top: 1px solid var(--color-border); }
.block-title { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
.original-text-block :deep(.el-textarea__inner) { min-height: 236px !important; padding: 13px; border-color: #dfe6ed; color: #526171; background: #fbfcfe; font-size: 12px; line-height: 1.75; }
.review-button { margin-top: 13px; }

.review-column { display: grid; gap: 24px; }
.review-card { min-height: 440px; }
.review-card :deep(.el-card__body) { padding: 22px; }
.risk-overview { display: grid; grid-template-columns: 150px minmax(0, 1fr); gap: 24px; align-items: center; margin-bottom: 20px; padding: 20px; border: 1px solid #e2e8ef; border-radius: 15px; background: linear-gradient(135deg, #fbfcfe, #f7fafc); }
.score-panel { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.score-number { display: block; color: var(--color-primary); font-size: 27px; line-height: 1; }
.score-unit { display: block; margin-top: 4px; color: var(--color-text-secondary); font-size: 10px; font-weight: 500; }
.score-caption { color: var(--color-text-secondary); font-size: 11px; }
.score-missing { display: grid; width: 116px; height: 116px; place-items: center; border: 10px solid #edf1f4; border-radius: 50%; color: var(--color-text-secondary); font-size: 12px; }
.stats-panel { min-width: 0; }
.stats-panel__heading { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 15px; color: var(--color-primary); font-size: 13px; font-weight: 700; }
.risk-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.risk-stat { display: flex; min-height: 74px; flex-direction: column; justify-content: center; padding: 11px; border: 1px solid transparent; border-radius: 10px; }
.risk-stat b { margin-bottom: 6px; font-size: 25px; line-height: 1; }
.risk-stat span { font-size: 11px; }
.risk-stat--high { color: #c45656; border-color: #ffe0e0; background: #fff3f3; }
.risk-stat--medium { color: #b2761d; border-color: #ffebc6; background: #fff8ec; }
.risk-stat--low { color: #4b9666; border-color: #d8f0dc; background: #f0faf2; }
.review-summary { margin-bottom: 20px; padding: 15px 17px; border-left: 3px solid var(--color-gold); border-radius: 0 11px 11px 0; color: var(--color-primary); background: #fffaf1; font-size: 13px; line-height: 1.8; }
.summary-label { display: flex; align-items: center; gap: 6px; margin-bottom: 7px; color: #9a783e; font-size: 11px; font-weight: 700; letter-spacing: .04em; }
.raw-summary { min-height: 260px; max-height: 520px; margin: 18px 0 0; padding: 16px; overflow: auto; border: 1px solid #f0d59f; border-radius: 10px; color: var(--color-text); background: #fffaf1; font-family: inherit; font-size: 13px; line-height: 1.85; white-space: pre-wrap; }
.risk-list { display: grid; gap: 15px; }
.risk-item { padding: 17px 18px; border: 1px solid #e2e8ef; border-left: 4px solid #cbd8e2; border-radius: 11px; background: #fff; box-shadow: 0 4px 14px rgba(26,58,92,.025); }
.risk-item--high { border-left-color: #f56c6c; }
.risk-item--medium { border-left-color: #e6a23c; }
.risk-item--low { border-left-color: #67c23a; }
.risk-item__header { display: flex; align-items: center; gap: 9px; color: var(--color-text-secondary); font-size: 11px; }
.risk-item__number { color: #a8b3be; font-family: Georgia, serif; font-size: 12px; font-weight: 700; }
.risk-item__header strong { min-width: 0; color: var(--color-primary); font-size: 14px; line-height: 1.5; }
.risk-law { display: inline-flex; align-items: center; gap: 5px; margin-top: 12px; padding: 5px 9px; border: 1px solid rgba(201,169,110,.35); border-radius: 6px; color: #896b36; background: #fffaf1; font-size: 11px; line-height: 1.5; }
.risk-item blockquote { margin: 13px 0; padding: 10px 13px; border-radius: 7px; color: #5d6975; background: #f7f9fb; font-size: 12px; line-height: 1.7; }
.risk-item p { margin: 8px 0 0; color: var(--color-text-secondary); font-size: 12px; line-height: 1.8; }
.risk-item p b { color: var(--color-primary); }

.history-list { min-height: 90px; }
.history-item { display: flex; width: 100%; align-items: center; justify-content: space-between; gap: 12px; padding: 13px 3px; border: 0; border-bottom: 1px solid var(--color-border); color: var(--color-text); background: transparent; cursor: pointer; font: inherit; text-align: left; }
.history-item > span:first-child { display: inline-flex; min-width: 0; align-items: center; gap: 7px; overflow: hidden; }
.history-item b { overflow: hidden; color: var(--color-primary); font-size: 13px; text-overflow: ellipsis; white-space: nowrap; }
.history-item:hover b { color: var(--color-gold); }
.history-item__status { flex: none; color: var(--color-text-secondary); font-size: 11px; }

@media (max-width: 900px) {
  .contract-page { width: min(var(--page-width), calc(100% - 32px)); padding-top: 42px; }
  .contract-layout { grid-template-columns: 1fr; }
  .upload-card { position: static; }
}
@media (max-width: 600px) {
  .contract-page { padding-bottom: 64px; }
  .contract-hero { margin-bottom: 32px; }
  .contract-steps { margin-bottom: 30px; padding: 0; }
  .contract-steps :deep(.el-step__title) { font-size: 12px; }
  .contract-steps :deep(.el-step__description) { display: none; }
  .review-card :deep(.el-card__body) { padding: 16px; }
  .risk-overview { grid-template-columns: 1fr; gap: 16px; padding: 17px; }
  .risk-stats { gap: 6px; }
  .risk-stat { padding: 9px 5px; text-align: center; }
  .risk-stat b { font-size: 22px; }
  .card-heading small, .block-heading small { display: none; }
  .card-heading strong, .block-heading strong { font-size: 14px; }
}
</style>
