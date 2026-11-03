<template>
  <main class="document-page">
    <!-- 页面头部采用参考图中的居中标题，并把历史记录放在右上角作为辅助入口。 -->
    <section class="document-hero">
      <div class="document-hero__copy">
        <p class="document-hero__eyebrow">DOCUMENT GENERATION</p>
        <h1>文书生成</h1>
        <p>一键生成标准法律文书，选择类型并填写信息即可获取专业文书全文。</p>
      </div>
      <el-button class="history-button" :icon="Clock" @click="openHistory">历史记录</el-button>
    </section>

    <!-- 三步进度条用于明确当前所在阶段，已完成步骤会自动显示完成状态。 -->
    <section class="step-panel" aria-label="文书生成进度">
      <el-steps :active="activeStep" align-center finish-status="success">
        <el-step title="选择文书类型" />
        <el-step title="填写基本信息" />
        <el-step title="生成文书" />
      </el-steps>
    </section>

    <section class="document-workbench">
      <!-- 第一步：以卡片代替下拉框，让用户快速理解每一种文书的用途。 -->
      <div v-if="activeStep === 0" class="type-stage">
        <div class="stage-heading">
          <span class="stage-heading__index">01</span>
          <div><h2>选择文书类型</h2><p>请选择您需要生成的法律文书</p></div>
        </div>

        <div class="document-type-grid">
          <button
            v-for="item in documentTypes"
            :key="item.value"
            type="button"
            class="document-type-card"
            :class="{ 'document-type-card--active': selectedType === item.value }"
            :aria-pressed="selectedType === item.value"
            @click="selectDocumentType(item.value)"
          >
            <span class="document-type-card__icon"><el-icon><component :is="item.icon" /></el-icon></span>
            <strong>{{ item.label }}</strong>
            <span>{{ item.description }}</span>
            <i v-if="selectedType === item.value" class="document-type-card__check">✓</i>
          </button>
        </div>

        <div class="stage-actions stage-actions--center">
          <el-button type="primary" size="large" :disabled="!selectedType" @click="goToForm">
            下一步<el-icon class="button-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 第二步：字段由所选文书配置动态生成，中文字段名原样提交给后端。 -->
      <div v-else-if="activeStep === 1" class="form-stage">
        <div class="stage-heading">
          <span class="stage-heading__index">02</span>
          <div><h2>填写基本信息</h2><p>当前文书：{{ selectedType }}，信息越完整，生成内容越准确</p></div>
          <el-button link type="primary" @click="activeStep = 0">重新选择类型</el-button>
        </div>

        <el-form class="document-form" label-position="top" @submit.prevent="handleGenerate">
          <div class="form-grid" :key="selectedType">
            <el-form-item v-for="field in currentFields" :key="field.key" :label="field.label">
              <el-input
                v-model="formData[field.key]"
                :type="field.multiline ? 'textarea' : 'text'"
                :rows="field.multiline ? 5 : 1"
                resize="vertical"
                :disabled="generating"
                :placeholder="field.placeholder || `请输入${field.label}`"
              />
            </el-form-item>
          </div>

          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>至少填写一项信息即可生成；未填写的内容将由 AI 使用“待填写”占位。</span>
          </div>

          <div class="stage-actions">
            <el-button size="large" :disabled="generating" @click="activeStep = 0">
              <el-icon class="button-icon--left"><ArrowLeft /></el-icon>上一步
            </el-button>
            <el-button type="primary" size="large" :loading="generating" :disabled="generating" @click="handleGenerate">
              <el-icon v-if="!generating" class="button-icon--left"><MagicStick /></el-icon>
              {{ generating ? 'AI 正在生成，请稍候…' : '生成文书' }}
            </el-button>
          </div>
        </el-form>
      </div>

      <!-- 第三步：使用 pre 保留真实 AI 返回内容的换行，不对正文进行 Markdown 解析。 -->
      <div v-else class="result-stage">
        <div class="stage-heading">
          <span class="stage-heading__index stage-heading__index--done">✓</span>
          <div><h2>文书生成完成</h2><p>请核对当事人信息、金额、日期及法律条款后再正式使用</p></div>
          <!-- 导出按钮与复制入口集中放置；无有效结果时统一禁用，避免生成空文件。 -->
          <div class="result-actions">
            <el-button :icon="CopyDocument" :disabled="!result" @click="copyResult">复制全文</el-button>
            <el-button
              type="primary"
              plain
              :icon="Download"
              :loading="exportingWord"
              :disabled="!result || exportingWord"
              @click="exportWord"
            >
              导出 Word
            </el-button>
            <el-button type="primary" :icon="Printer" :disabled="!result" @click="exportPdf">导出 PDF</el-button>
          </div>
        </div>

        <div v-if="result" class="document-result">
          <div class="document-result__meta">
            <el-tag type="warning" effect="plain">{{ result.doc_type }}</el-tag>
            <span>生成时间：{{ formatDate(result.created_at) }}</span>
          </div>
          <pre>{{ result.generated_content }}</pre>
        </div>
        <el-empty v-else description="暂无生成结果" />

        <div class="stage-actions">
          <el-button size="large" @click="activeStep = 1">
            <el-icon class="button-icon--left"><ArrowLeft /></el-icon>返回修改
          </el-button>
          <el-button type="primary" size="large" plain @click="startAnotherDocument">生成其他文书</el-button>
        </div>
      </div>
    </section>

    <!-- 历史记录使用抽屉承载，点击记录即可将完整文书载入第三步查看。 -->
    <el-drawer v-model="historyVisible" class="history-drawer" title="生成历史" size="min(420px, 92vw)">
      <template #header>
        <div class="drawer-heading"><div><strong>生成历史</strong><span>查看此前生成的法律文书</span></div><el-button link :icon="Refresh" @click="loadHistory">刷新</el-button></div>
      </template>
      <div v-loading="loadingHistory" class="history-list">
        <button v-for="item in history" :key="item.id" type="button" class="history-item" @click="viewDocument(item.id)">
          <span class="history-item__icon"><el-icon><Document /></el-icon></span>
          <span class="history-item__content">
            <span><el-tag size="small" type="info">{{ item.doc_type }}</el-tag><b>{{ documentName(item) }}</b></span>
            <time>{{ formatDate(item.created_at) }}</time>
          </span>
          <el-icon class="history-item__arrow"><ArrowRight /></el-icon>
        </button>
        <el-empty v-if="!loadingHistory && !history.length" description="暂无生成记录" :image-size="80" />
      </div>
    </el-drawer>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { AlignmentType, Document as WordDocument, Packer, Paragraph, TextRun } from 'docx'
import {
  ArrowLeft,
  ArrowRight,
  Clock,
  CopyDocument,
  Document,
  Download,
  Files,
  InfoFilled,
  MagicStick,
  Message,
  Postcard,
  Printer,
  Refresh,
  Tickets
} from '@element-plus/icons-vue'
import { generateDocument, getDocument, getDocuments } from '../api/document'

// 文书类型同时提供用途说明与识别图标，卡片的 value 必须与后端枚举完全一致。
const documentTypes = [
  { value: '起诉状', label: '民事起诉状', description: '提起民事诉讼使用', icon: Document },
  { value: '答辩状', label: '民事答辩状', description: '针对起诉进行答辩', icon: Files },
  { value: '授权委托书', label: '授权委托书', description: '委托代理人办理法律事务', icon: Postcard },
  { value: '律师函', label: '律师函', description: '正式法律告知函件', icon: Message },
  { value: '合同模板', label: '合同模板', description: '生成基础合同文本', icon: Tickets }
]

// 不同文书对应不同的表单字段，key 会作为 form_data 的中文键名提交。
const fieldsByType = {
  起诉状: [
    { key: '当事人信息', label: '当事人信息', placeholder: '例如：原告张三，身份证号、住址、联系方式等' },
    { key: '对方信息', label: '对方信息', placeholder: '例如：被告李四，身份证号、住址、联系方式等' },
    { key: '诉讼请求', label: '诉讼请求', multiline: true, placeholder: '请逐项说明希望法院支持的请求' },
    { key: '事实与理由', label: '事实与理由', multiline: true, placeholder: '请按时间顺序说明事情经过、证据及理由' }
  ],
  答辩状: [
    { key: '当事人信息', label: '当事人信息' },
    { key: '答辩请求', label: '答辩请求', multiline: true },
    { key: '事实与理由', label: '事实与理由', multiline: true }
  ],
  律师函: [
    { key: '对方信息', label: '对方信息' },
    { key: '当事人信息', label: '当事人信息' },
    { key: '事由', label: '事由', multiline: true },
    { key: '要求', label: '要求', multiline: true }
  ],
  授权委托书: [
    { key: '当事人信息', label: '当事人信息' },
    { key: '受托人信息', label: '受托人信息' },
    { key: '授权事项', label: '授权事项', multiline: true },
    { key: '授权期限', label: '授权期限' }
  ],
  合同模板: [
    { key: '甲方', label: '甲方' },
    { key: '乙方', label: '乙方' },
    { key: '合同事项', label: '合同事项', multiline: true },
    { key: '权利义务', label: '权利义务', multiline: true }
  ]
}

// activeStep 使用 Element Plus 的零基索引：0 选择类型、1 填写信息、2 查看结果。
const activeStep = ref(0)
const selectedType = ref('')
const formData = reactive({})
const result = ref(null)
const history = ref([])
const historyVisible = ref(false)
const generating = ref(false)
const loadingHistory = ref(false)
// Word 打包需要短暂异步处理，独立状态用于防止用户连续触发多个下载。
const exportingWord = ref(false)
const currentFields = computed(() => fieldsByType[selectedType.value] || [])

// 切换类型时彻底清理上一种文书字段，防止把无关数据提交给后端。
function resetForm(initialData = {}) {
  Object.keys(formData).forEach((key) => delete formData[key])
  currentFields.value.forEach((field) => {
    formData[field.key] = initialData[field.key] || ''
  })
}

// 同步重置可确保从历史记录载入时，随后写入的旧表单数据不会再被异步 watch 清空。
watch(selectedType, () => resetForm(), { flush: 'sync' })

// 选择卡片只记录类型，用户点击“下一步”后再进入表单，符合参考图交互。
function selectDocumentType(type) {
  if (generating.value) return
  selectedType.value = type
}

function goToForm() {
  if (!selectedType.value) {
    ElMessage.warning('请先选择文书类型')
    return
  }
  activeStep.value = 1
}

// 至少填写一个非空字段才允许请求真实 AI，避免生成完全无上下文的空白文书。
function validateForm() {
  const hasValue = currentFields.value.some((field) => String(formData[field.key] || '').trim())
  if (!hasValue) {
    ElMessage.warning('请至少填写一项文书信息后再生成')
    return false
  }
  return true
}

// 调用既有 API；成功后进入结果步骤并刷新历史，失败时保留全部表单内容供重试。
async function handleGenerate() {
  if (generating.value || !validateForm()) return
  generating.value = true
  try {
    const response = await generateDocument({ doc_type: selectedType.value, form_data: { ...formData } })
    result.value = response.data
    activeStep.value = 2
    await loadHistory()
    ElMessage.success('文书生成成功')
  } catch {
    // 全局 HTTP 拦截器负责显示后端错误，当前页面只恢复 loading 状态。
  } finally {
    generating.value = false
  }
}

// 历史按钮打开抽屉时重新获取数据，确保刚生成的记录立即可见。
async function openHistory() {
  historyVisible.value = true
  await loadHistory()
}

async function loadHistory() {
  loadingHistory.value = true
  try {
    const response = await getDocuments()
    history.value = response.data || []
  } catch {
    history.value = []
  } finally {
    loadingHistory.value = false
  }
}

// 点击历史记录后载入完整正文，同时恢复对应表单数据，便于用户继续修改。
async function viewDocument(id) {
  try {
    const response = await getDocument(id)
    result.value = response.data
    selectedType.value = response.data.doc_type
    resetForm(response.data.form_data || {})
    activeStep.value = 2
    historyVisible.value = false
  } catch {
    // 错误提示统一由 HTTP 拦截器处理。
  }
}

// 新建另一份文书时清空选择、表单和结果，回到第一步。
function startAnotherDocument() {
  selectedType.value = ''
  result.value = null
  resetForm()
  activeStep.value = 0
}

// 优先提取常见主体字段作为历史摘要，旧记录缺少这些字段时使用通用名称兜底。
function documentName(item) {
  return item.form_data?.当事人信息 || item.form_data?.甲方 || item.form_data?.对方信息 || '未命名文书'
}

function formatDate(value) {
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '' : date.toLocaleString('zh-CN', { dateStyle: 'medium', timeStyle: 'short' })
}

// 使用浏览器剪贴板复制完整正文；受浏览器权限限制时给出明确提示。
async function copyResult() {
  if (!result.value?.generated_content) return
  try {
    await navigator.clipboard.writeText(result.value.generated_content)
    ElMessage.success('文书内容已复制')
  } catch {
    ElMessage.warning('复制失败，请手动选择文本复制')
  }
}

// 将日期整理成 YYYYMMDD，用于生成简洁且便于归档的下载文件名。
function formatFileDate(value = new Date()) {
  const date = value instanceof Date ? value : new Date(value)
  const validDate = Number.isNaN(date.getTime()) ? new Date() : date
  const year = validDate.getFullYear()
  const month = String(validDate.getMonth() + 1).padStart(2, '0')
  const day = String(validDate.getDate()).padStart(2, '0')
  return `${year}${month}${day}`
}

// 文档内部标题沿用页面展示名称，例如后端的“起诉状”会显示为“民事起诉状”。
function getDocumentTitle(type) {
  return documentTypes.find((item) => item.value === type)?.label || type || '法律文书'
}

// 下载前移除 Windows 文件名中的保留字符，避免少数历史数据导致保存失败。
function getExportFileName(extension) {
  const type = String(result.value?.doc_type || '法律文书').replace(/[\\/:*?"<>|]/g, '-')
  return `${type}-${formatFileDate()}.${extension}`
}

// 使用 docx 逐段创建真正的 Word 文档；正文按 AI 返回的换行拆分并保留空行。
async function exportWord() {
  if (!result.value?.generated_content || exportingWord.value) return
  exportingWord.value = true

  try {
    const title = getDocumentTitle(result.value.doc_type)
    const contentLines = String(result.value.generated_content).replace(/\r\n/g, '\n').split('\n')
    const wordDocument = new WordDocument({
      sections: [
        {
          properties: {},
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              spacing: { after: 360 },
              children: [
                new TextRun({
                  text: title,
                  bold: true,
                  size: 36,
                  font: 'SimHei'
                })
              ]
            }),
            ...contentLines.map((line) => new Paragraph({
              spacing: { line: 420, after: 100 },
              children: [
                new TextRun({
                  // 空行写入一个空格，确保 Word 不会吞掉原文中的段落间距。
                  text: line || ' ',
                  size: 28,
                  font: 'FangSong'
                })
              ]
            }))
          ]
        }
      ]
    })

    const blob = await Packer.toBlob(wordDocument)
    const downloadUrl = URL.createObjectURL(blob)
    const downloadLink = document.createElement('a')
    downloadLink.href = downloadUrl
    downloadLink.download = getExportFileName('docx')
    document.body.appendChild(downloadLink)
    downloadLink.click()
    downloadLink.remove()
    URL.revokeObjectURL(downloadUrl)
    ElMessage.success('Word 文档已导出')
  } catch {
    ElMessage.error('Word 导出失败，请稍后重试')
  } finally {
    exportingWord.value = false
  }
}

// 所有动态内容写入打印窗口前都必须转义，防止文书中的特殊字符被浏览器当作 HTML。
function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

// PDF 采用浏览器原生打印能力，避免前端字体嵌入造成中文乱码和额外的大体积依赖。
function exportPdf() {
  if (!result.value?.generated_content) return

  // 必须在用户点击事件中同步打开窗口，否则浏览器可能将其识别为弹窗并拦截。
  const printWindow = window.open('', '_blank', 'width=900,height=700')
  if (!printWindow) {
    ElMessage.warning('浏览器已拦截打印窗口，请允许本站弹出窗口后重试')
    return
  }

  const title = escapeHtml(getDocumentTitle(result.value.doc_type))
  const content = escapeHtml(result.value.generated_content)
  printWindow.document.open()
  printWindow.document.write(`<!doctype html>
    <html lang="zh-CN">
      <head>
        <meta charset="UTF-8" />
        <title>${title}</title>
        <style>
          @page { size: A4; margin: 24mm 22mm 24mm; }
          * { box-sizing: border-box; }
          body { margin: 0; color: #111; background: #fff; font-family: "FangSong", "仿宋", "SimSun", "宋体", serif; }
          h1 { margin: 0 0 24pt; text-align: center; font-family: "SimHei", "黑体", serif; font-size: 22pt; line-height: 1.4; }
          .document-content { font-size: 14pt; line-height: 1.85; white-space: pre-wrap; overflow-wrap: anywhere; }
          .print-tip { margin: 0 0 18px; padding: 10px 12px; color: #555; background: #f4f5f7; font: 13px/1.5 sans-serif; }
          @media print {
            .print-tip { display: none !important; }
            h1, p { break-after: avoid; }
            .document-content { orphans: 3; widows: 3; }
          }
        </style>
      </head>
      <body>
        <p class="print-tip">请在打印对话框中选择“另存为 PDF”。</p>
        <h1>${title}</h1>
        <div class="document-content">${content}</div>
      </body>
    </html>`)
  printWindow.document.close()

  // 等待打印窗口完成排版后再调起系统打印对话框，避免长文只渲染出第一页。
  // 不主动调用 focus()，防止用户切换或最小化窗口后浏览器再次抢占前台。
  printWindow.setTimeout(() => {
    printWindow.print()
  }, 300)
}

// 首次进入页面预加载历史，之后打开抽屉时仍会主动刷新。
onMounted(loadHistory)
</script>

<style scoped>
/* 页面使用大面积浅色背景和居中的内容区，保持参考图简洁、正式的法律产品气质。 */
.document-page { min-height: calc(100vh - 76px); padding: 64px 24px 96px; background: linear-gradient(180deg, #f8fafc 0%, #fff 42%); }
.document-hero { position: relative; width: min(1080px, 100%); margin: 0 auto; text-align: center; }
.document-hero__copy { max-width: 720px; margin: 0 auto; }
.document-hero__eyebrow { margin: 0 0 10px; color: var(--color-gold); font-size: 11px; font-weight: 700; letter-spacing: .2em; }
.document-hero h1 { margin: 0; color: var(--color-primary); font-family: "STKaiti", "KaiTi", serif; font-size: clamp(36px, 4vw, 48px); letter-spacing: .08em; }
.document-hero p:last-child { margin: 15px 0 0; color: var(--color-text-secondary); font-size: 15px; line-height: 1.8; }
.history-button { position: absolute; top: 4px; right: 0; border-color: rgba(26,58,92,.18); color: var(--color-primary); background: rgba(255,255,255,.82); }

/* 进度条只保留轻量线条与编号，让三个阶段清晰但不过度抢占视觉。 */
.step-panel { width: min(820px, 100%); margin: 50px auto 38px; padding: 0 24px; }
.step-panel :deep(.el-step__title) { color: #94a0ae; font-size: 15px; }
.step-panel :deep(.el-step__title.is-process) { color: var(--color-primary); font-weight: 700; }
.step-panel :deep(.el-step__head.is-process) { color: var(--color-primary); border-color: var(--color-primary); }
.step-panel :deep(.el-step__head.is-success) { color: var(--color-gold); border-color: var(--color-gold); }
.step-panel :deep(.el-step__line) { background-color: #dce2e9; }

.document-workbench { width: min(1080px, 100%); min-height: 430px; margin: 0 auto; padding: 38px 42px 34px; border: 1px solid rgba(225,231,238,.95); border-radius: 4px; background: rgba(255,255,255,.96); box-shadow: 0 18px 48px rgba(26,58,92,.07); }
.stage-heading { display: flex; align-items: center; gap: 14px; margin-bottom: 30px; }
.stage-heading__index { display: grid; flex: none; width: 38px; height: 38px; place-items: center; border: 1px solid rgba(201,169,110,.48); border-radius: 50%; color: var(--color-gold); background: #fffaf1; font-size: 12px; font-weight: 800; }
.stage-heading__index--done { color: #fff; background: var(--color-primary); border-color: var(--color-primary); font-size: 17px; }
.stage-heading > div { flex: 1; }
.stage-heading h2 { margin: 0 0 5px; color: var(--color-primary); font-size: 20px; }
.stage-heading p { margin: 0; color: var(--color-text-secondary); font-size: 13px; }
.result-actions { display: flex; flex: none; align-items: center; gap: 8px; }
.result-actions .el-button + .el-button { margin-left: 0; }

/* 类型卡采用大点击区域与选中状态，五种文书在桌面端保持一行显示。 */
.document-type-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 13px; }
.document-type-card { position: relative; display: flex; min-height: 188px; padding: 28px 14px 22px; align-items: center; flex-direction: column; justify-content: center; border: 1px solid #e3e8ee; border-radius: 3px; color: var(--color-text); background: #fff; cursor: pointer; font: inherit; text-align: center; transition: border-color .2s ease, box-shadow .2s ease, transform .2s ease, background-color .2s ease; }
.document-type-card:hover { border-color: rgba(201,169,110,.65); box-shadow: 0 10px 26px rgba(26,58,92,.08); transform: translateY(-3px); }
.document-type-card--active { border-color: var(--color-gold); background: linear-gradient(180deg, #fff 0%, #fffaf1 100%); box-shadow: 0 10px 28px rgba(201,169,110,.14); }
.document-type-card__icon { display: grid; width: 48px; height: 48px; margin-bottom: 17px; place-items: center; color: var(--color-primary); font-size: 31px; }
.document-type-card strong { color: var(--color-primary); font-size: 16px; line-height: 1.5; }
.document-type-card > span:last-of-type { margin-top: 8px; color: var(--color-text-secondary); font-size: 12px; line-height: 1.6; }
.document-type-card__check { position: absolute; top: 10px; right: 10px; display: grid; width: 21px; height: 21px; place-items: center; border-radius: 50%; color: #fff; background: var(--color-gold); font-size: 12px; font-style: normal; }

.stage-actions { display: flex; align-items: center; justify-content: space-between; gap: 14px; margin-top: 28px; }
.stage-actions--center { justify-content: center; }
.stage-actions .el-button { min-width: 142px; }
.button-icon--left { margin-right: 6px; }
.button-icon--right { margin-left: 7px; }

/* 表单在桌面端为两列，多行字段独占整行，窄屏自动改为单列。 */
.document-form { max-width: 900px; margin: 0 auto; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2px 20px; }
.form-grid :deep(.el-form-item:has(textarea)) { grid-column: 1 / -1; }
.form-grid :deep(.el-form-item__label) { color: var(--color-primary); font-weight: 600; }
.form-grid :deep(.el-input__wrapper), .form-grid :deep(.el-textarea__inner) { box-shadow: 0 0 0 1px #dfe5eb inset; }
.form-tip { display: flex; align-items: center; gap: 8px; padding: 11px 13px; border-radius: 6px; color: #80652f; background: #fffaf0; font-size: 12px; line-height: 1.6; }

.document-result { border: 1px solid #e1e6ec; background: #fff; }
.document-result__meta { display: flex; align-items: center; gap: 12px; padding: 14px 20px; border-bottom: 1px solid #e8ecf0; color: var(--color-text-secondary); font-size: 12px; }
.document-result pre { max-height: 620px; min-height: 310px; margin: 0; padding: 28px 34px; overflow: auto; color: #25384c; background: #fcfdfd; font-family: "Songti SC", "SimSun", serif; font-size: 15px; line-height: 2; white-space: pre-wrap; word-break: break-word; }

/* 历史抽屉中的每条记录保持整行可点击，并明确展示类型、摘要和时间。 */
.drawer-heading { display: flex; width: 100%; padding-right: 12px; align-items: center; justify-content: space-between; }
.drawer-heading > div { display: flex; flex-direction: column; gap: 4px; }
.drawer-heading strong { color: var(--color-primary); font-size: 18px; }
.drawer-heading span { color: var(--color-text-secondary); font-size: 12px; }
.history-list { min-height: 180px; }
.history-item { display: flex; width: 100%; padding: 15px 3px; align-items: center; gap: 12px; border: 0; border-bottom: 1px solid var(--color-border); color: var(--color-text); background: transparent; cursor: pointer; font: inherit; text-align: left; }
.history-item:hover { background: #fafbfd; }
.history-item__icon { display: grid; flex: none; width: 38px; height: 38px; place-items: center; border-radius: 8px; color: var(--color-primary); background: var(--color-primary-soft); font-size: 18px; }
.history-item__content { display: flex; min-width: 0; flex: 1; flex-direction: column; gap: 7px; }
.history-item__content > span { display: flex; min-width: 0; align-items: center; gap: 8px; }
.history-item b { overflow: hidden; color: var(--color-primary); font-size: 13px; text-overflow: ellipsis; white-space: nowrap; }
.history-item time { color: var(--color-text-secondary); font-size: 11px; }
.history-item__arrow { flex: none; color: #a7b0ba; }

@media (max-width: 900px) {
  .document-type-grid { grid-template-columns: repeat(3, 1fr); }
  .history-button { position: static; margin-top: 22px; }
}

@media (max-width: 640px) {
  .document-page { padding: 42px 16px 72px; }
  .step-panel { margin: 38px auto 28px; padding: 0; }
  .step-panel :deep(.el-step__title) { font-size: 12px; }
  .document-workbench { min-height: 0; padding: 26px 18px; }
  .document-type-grid { grid-template-columns: 1fr 1fr; }
  .document-type-card { min-height: 156px; }
  .form-grid { grid-template-columns: 1fr; }
  .form-grid :deep(.el-form-item:has(textarea)) { grid-column: auto; }
  .stage-heading { align-items: flex-start; flex-wrap: wrap; }
  .stage-heading .el-button { margin-left: 52px; }
  .result-actions { width: 100%; margin-left: 52px; flex-wrap: wrap; }
  .stage-heading .result-actions .el-button { margin-left: 0; }
  .stage-actions { flex-direction: column-reverse; }
  .stage-actions .el-button { width: 100%; margin-left: 0; }
  .document-result pre { padding: 22px 18px; }
}

@media (max-width: 400px) {
  .document-type-grid { grid-template-columns: 1fr; }
}
</style>
