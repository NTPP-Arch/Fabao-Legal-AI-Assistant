<template>
  <main class="home-page">
    <!-- 首屏使用 spotlight 光晕和网格纹理，营造统一的“法律智能工作台”氛围。 -->
    <section
      class="hero-section"
      aria-labelledby="hero-title"
      :style="spotlightStyle"
      @pointermove="handleSpotlightMove"
      @pointerleave="resetSpotlight"
    >
      <div class="hero-section__grid" aria-hidden="true"></div>

      <div class="hero-section__content">
        <!-- eyebrow 作为产品定位标签，使用英文短句降低视觉噪声。 -->
        <div class="hero-section__eyebrow">
          <span class="hero-section__eyebrow-line" aria-hidden="true"></span>
          <span>AI LEGAL INTELLIGENCE</span>
          <span class="hero-section__eyebrow-dot" aria-hidden="true"></span>
        </div>

        <!-- 标题是鼠标聚焦区域：圆形光标只在标题上方出现，离开后自然淡出。 -->
        <h1
          id="hero-title"
          class="hero-section__title"
          data-cursor="blend"
          @pointerenter="handleTitleCursorMove"
          @pointermove="handleTitleCursorMove"
          @pointerleave="handleTitleCursorLeave"
        >
          把复杂法律，<br />
          <span>交给法宝。</span>
        </h1>

        <!-- 使用 fixed 圆形叠加层模拟参考站点的 difference 光标效果。 -->
        <span
          class="hero-cursor"
          :class="{ 'hero-cursor--visible': titleCursor.visible }"
          :style="titleCursorStyle"
          aria-hidden="true"
        ></span>

        <p class="hero-section__subtitle">
          您的智能法律助手，让每一次决策都有据可依。
        </p>

        <div class="hero-section__actions">
          <!-- 搜索框样式 CTA 保留原有路由行为，点击后进入 AI 法律咨询。 -->
          <button class="hero-search" type="button" @click="goToConsult">
            <el-icon class="hero-search__search-icon" aria-hidden="true"><Search /></el-icon>
            <span class="hero-search__placeholder">描述您的法律问题，法宝马上为您解答</span>
            <span class="hero-search__action" aria-label="开始法律咨询">
              <el-icon aria-hidden="true"><ArrowRight /></el-icon>
            </span>
          </button>

          <!-- 锚点链接让用户可以先浏览三项能力，再决定使用哪项服务。 -->
          <a class="hero-section__explore" href="#features">
            探索法宝能力
            <el-icon aria-hidden="true"><ArrowDown /></el-icon>
          </a>
        </div>

        <p class="hero-section__hint">
          <el-icon aria-hidden="true"><Lock /></el-icon>
          您的咨询内容仅用于本次服务，安心表达每一个问题
        </p>
      </div>

      <!-- 右侧是轻量 CSS 工作台，不依赖外部图片，便于课堂环境离线预览。 -->
      <div class="hero-section__visual" aria-label="法宝智能工作台示意图">
        <div class="hero-orbit hero-orbit--outer" aria-hidden="true"></div>
        <div class="hero-orbit hero-orbit--inner" aria-hidden="true"></div>

        <div class="case-console">
          <div class="case-console__topbar">
            <div class="case-console__brand">
              <span class="case-console__brand-mark">法</span>
              <span>法宝工作台</span>
            </div>
            <span class="case-console__live"><i></i> 实时守护</span>
          </div>

          <div class="case-console__title-row">
            <div>
              <span class="case-console__overline">今日法律洞察</span>
              <strong>案件风险概览</strong>
            </div>
            <span class="case-console__date">今日 · 09:42</span>
          </div>

          <div class="case-console__score">
            <div class="case-console__score-ring">
              <span>98<small>%</small></span>
            </div>
            <div class="case-console__score-copy">
              <strong>风险识别完成</strong>
              <span>已为您标记 12 处关键内容</span>
            </div>
          </div>

          <div class="case-console__list">
            <div class="case-console__row">
              <span><el-icon><CircleCheck /></el-icon> 合同义务</span>
              <b>低风险</b>
            </div>
            <div class="case-console__row">
              <span><el-icon><CircleCheck /></el-icon> 责任边界</span>
              <b>已确认</b>
            </div>
            <div class="case-console__row case-console__row--muted">
              <span><el-icon><Document /></el-icon> 文书规范</span>
              <b>待生成</b>
            </div>
          </div>

          <div class="case-console__footer">
            <span>Powered by 法宝 AI</span>
            <span class="case-console__footer-line"></span>
          </div>
        </div>

        <!-- 浮动状态条借鉴产品化组件的“信息胶囊”，只补充信息层级，不改变功能。 -->
        <div class="hero-float hero-float--top">
          <span class="hero-float__icon"><el-icon><ChatDotRound /></el-icon></span>
          <span><b>24h</b> 智能响应</span>
        </div>
        <div class="hero-float hero-float--bottom">
          <span class="hero-float__icon hero-float__icon--gold"><el-icon><CircleCheck /></el-icon></span>
          <span>专业 · 私密 · 高效</span>
        </div>
      </div>
    </section>

    <!-- 功能区继续复用 FeatureCard，功能路由和文案接口保持不变。 -->
    <section id="features" class="features-section" aria-labelledby="features-title">
      <div class="section-heading">
        <div>
          <p class="section-heading__eyebrow">一站式法律服务</p>
          <h2 id="features-title" class="section-heading__title">从问题到答案，一步到位</h2>
        </div>
        <p class="section-heading__description">
          从咨询到审查，把专业能力放进每一个需要法律判断的时刻。
        </p>
      </div>

      <div class="features-grid">
        <FeatureCard
          v-for="feature in features"
          :key="feature.title"
          :icon="feature.icon"
          :title="feature.title"
          :description="feature.description"
          :to="feature.to"
        />
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, reactive } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowDown,
  ArrowRight,
  ChatDotRound,
  CircleCheck,
  Document,
  EditPen,
  Lock,
  Search
} from '@element-plus/icons-vue'
import FeatureCard from '../components/FeatureCard.vue'

// 路由实例用于处理首屏 CTA 的程序化跳转。
const router = useRouter()

// 首页三项核心能力的数据源；图标、文案和目标路由保持原有接口不变。
const features = [
  {
    icon: ChatDotRound,
    title: 'AI法律咨询',
    description: '智能问答，快速获取法律建议',
    to: '/ai-consult'
  },
  {
    icon: Document,
    title: '文书生成',
    description: '一键生成标准法律文书',
    to: '/doc-generate'
  },
  {
    icon: EditPen,
    title: '合同审查',
    description: '智能识别合同风险条款',
    to: '/contract-review'
  }
]

// 使用 CSS 自定义属性记录鼠标位置，让 spotlight 光晕跟随用户浏览产生轻微互动。
const spotlightStyle = reactive({
  '--spotlight-x': '72%',
  '--spotlight-y': '34%'
})

// 将指针在首屏中的相对坐标换算为百分比，避免依赖第三方动效库。
function handleSpotlightMove(event) {
  const section = event.currentTarget
  const rect = section.getBoundingClientRect()
  spotlightStyle['--spotlight-x'] = `${((event.clientX - rect.left) / rect.width) * 100}%`
  spotlightStyle['--spotlight-y'] = `${((event.clientY - rect.top) / rect.height) * 100}%`
}

// 鼠标离开首屏时恢复默认光源位置，避免光晕停留在边缘造成突兀效果。
function resetSpotlight() {
  spotlightStyle['--spotlight-x'] = '72%'
  spotlightStyle['--spotlight-y'] = '34%'
}

// 标题圆形光标的当前坐标和目标坐标分离保存，便于用插值制造柔和的跟随感。
const titleCursor = reactive({
  x: 0,
  y: 0,
  visible: false
})
const targetTitleCursor = reactive({ x: 0, y: 0 })
const titleCursorStyle = computed(() => ({
  left: `${titleCursor.x}px`,
  top: `${titleCursor.y}px`
}))
let titleCursorFrame = 0

// 每一帧只向目标坐标靠近一部分，避免圆形光标紧贴鼠标产生生硬抖动。
function animateTitleCursor() {
  const xDistance = targetTitleCursor.x - titleCursor.x
  const yDistance = targetTitleCursor.y - titleCursor.y
  titleCursor.x += xDistance * 0.24
  titleCursor.y += yDistance * 0.24

  if (Math.abs(xDistance) > 0.1 || Math.abs(yDistance) > 0.1) {
    titleCursorFrame = requestAnimationFrame(animateTitleCursor)
  } else {
    titleCursorFrame = 0
  }
}

// 鼠标进入或移动到标题时更新目标坐标；触摸设备不显示桌面端光标特效。
function handleTitleCursorMove(event) {
  if (event.pointerType === 'touch') return

  // 第一次进入标题时直接放到指针位置，避免圆形从浏览器左上角飞入。
  if (!titleCursor.visible) {
    titleCursor.x = event.clientX
    titleCursor.y = event.clientY
  }

  targetTitleCursor.x = event.clientX
  targetTitleCursor.y = event.clientY
  titleCursor.visible = true

  if (!titleCursorFrame) {
    titleCursorFrame = requestAnimationFrame(animateTitleCursor)
  }
}

// 离开标题后只隐藏圆形，不立即清零坐标，让下一次进入时仍然保持平滑过渡。
function handleTitleCursorLeave() {
  titleCursor.visible = false
}

// 组件销毁时取消未完成的动画帧，避免路由切换后仍访问旧页面状态。
onBeforeUnmount(() => {
  if (titleCursorFrame) {
    cancelAnimationFrame(titleCursorFrame)
  }
})

// 点击首屏 CTA 后进入 AI 咨询页面，后续可以在这里携带用户输入内容。
function goToConsult() {
  router.push('/ai-consult')
}
</script>

<style scoped>
/* 页面整体采用深海蓝背景，让金色成为唯一强调色，保证视觉语言统一。 */
.home-page {
  min-height: 100%;
  overflow: hidden;
  background: var(--color-background);
}

.hero-section {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(400px, 0.84fr);
  align-items: center;
  gap: 50px;
  min-height: 650px;
  padding: 74px max(24px, calc((100% - var(--page-width)) / 2)) 84px;
  overflow: hidden;
  background:
    radial-gradient(620px circle at var(--spotlight-x) var(--spotlight-y), rgba(201, 169, 110, 0.16), transparent 58%),
    radial-gradient(560px circle at 6% 100%, rgba(22, 91, 137, 0.22), transparent 66%),
    #071d30;
}

/* 细网格借鉴现代产品 landing page，用来增加空间层次但不抢正文注意力。 */
.hero-section__grid {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(171, 201, 224, 0.055) 1px, transparent 1px),
    linear-gradient(90deg, rgba(171, 201, 224, 0.055) 1px, transparent 1px);
  background-size: 58px 58px;
  mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.9), transparent 80%);
}

.hero-section__content,
.hero-section__visual {
  position: relative;
  z-index: 1;
}

.hero-section__content {
  max-width: 650px;
}

.hero-section__eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 11px;
  margin-bottom: 24px;
  color: var(--color-gold-light);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.22em;
}

.hero-section__eyebrow-line {
  width: 35px;
  height: 1px;
  background: var(--color-gold);
}

.hero-section__eyebrow-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--color-gold);
  box-shadow: 0 0 0 5px rgba(201, 169, 110, 0.12);
}

.hero-section__title {
  margin: 0;
  color: #f4f8fb;
  font-family: "STKaiti", "KaiTi", "PingFang SC", serif;
  font-size: clamp(49px, 6.4vw, 82px);
  font-weight: 700;
  letter-spacing: 0.045em;
  line-height: 1.16;
}

.hero-section__title > span {
  background: linear-gradient(110deg, #c9a96e 10%, #f1dfb7 52%, #c9a96e 94%);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}

/* 这个固定圆形是交互层，不占用文档流，也不会挡住标题或按钮的点击。 */
.hero-cursor {
  position: fixed;
  z-index: 40;
  /* 圆形尺寸接近标题字号，可以完整覆盖鼠标所在的一个汉字。 */
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: #fff;
  opacity: 0;
  pointer-events: none;
  mix-blend-mode: difference;
  transform: translate(-50%, -50%);
  transition: opacity 0.18s ease;
  will-change: left, top, opacity;
}

.hero-cursor--visible {
  opacity: 1;
}

.hero-section__subtitle {
  max-width: 510px;
  margin: 25px 0 31px;
  color: #a9bdcd;
  font-size: 17px;
  letter-spacing: 0.1em;
  line-height: 1.8;
}

.hero-section__actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.hero-search {
  display: flex;
  align-items: center;
  width: min(100%, 510px);
  min-height: 62px;
  padding: 7px 7px 7px 20px;
  border: 1px solid rgba(234, 216, 180, 0.32);
  border-radius: 14px;
  color: #abc0d0;
  background: rgba(8, 31, 50, 0.84);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.06);
  cursor: pointer;
  font: inherit;
  text-align: left;
  transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
}

.hero-search:hover {
  border-color: rgba(234, 216, 180, 0.85);
  box-shadow: 0 22px 48px rgba(0, 0, 0, 0.26), 0 0 34px rgba(201, 169, 110, 0.12);
  transform: translateY(-3px);
}

.hero-search:focus-visible {
  outline: 3px solid rgba(201, 169, 110, 0.34);
  outline-offset: 3px;
}

.hero-search__search-icon {
  flex: none;
  margin-right: 12px;
  color: var(--color-gold);
}

.hero-search__placeholder {
  flex: 1;
  overflow: hidden;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hero-search__action {
  display: inline-grid;
  width: 47px;
  height: 47px;
  flex: none;
  place-items: center;
  border-radius: 10px;
  color: var(--color-primary-deep);
  background: var(--color-gold);
}

.hero-section__explore {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #c5d4df;
  font-size: 12px;
  white-space: nowrap;
  transition: color 0.2s ease;
}

.hero-section__explore:hover {
  color: var(--color-gold-light);
}

.hero-section__hint {
  display: flex;
  align-items: center;
  gap: 7px;
  margin: 16px 0 0 4px;
  color: #7891a5;
  font-size: 11px;
}

/* 工作台视觉使用多个透明层和环形线条，呼应 spotlight/玻璃卡片组件。 */
.hero-section__visual {
  display: grid;
  min-height: 440px;
  place-items: center;
}

.hero-orbit {
  position: absolute;
  border: 1px solid rgba(201, 169, 110, 0.25);
  border-radius: 50%;
  transform: rotate(-22deg);
}

.hero-orbit--outer {
  width: 440px;
  height: 260px;
  box-shadow: 0 0 0 1px rgba(75, 143, 184, 0.08), 0 0 60px rgba(201, 169, 110, 0.08);
}

.hero-orbit--inner {
  width: 328px;
  height: 205px;
  border-color: rgba(114, 172, 207, 0.24);
  transform: rotate(35deg);
}

.case-console {
  position: relative;
  width: min(100%, 392px);
  min-height: 370px;
  padding: 22px 22px 18px;
  border: 1px solid rgba(205, 226, 240, 0.22);
  border-radius: 22px;
  background: linear-gradient(145deg, rgba(18, 57, 84, 0.88), rgba(6, 27, 45, 0.92));
  box-shadow: 0 30px 75px rgba(0, 0, 0, 0.34), inset 0 1px 0 rgba(255, 255, 255, 0.11);
  backdrop-filter: blur(18px);
  transform: rotate(2deg);
  transition: transform 0.35s ease;
}

.hero-section__visual:hover .case-console {
  transform: rotate(0deg) translateY(-5px);
}

.case-console__topbar,
.case-console__brand,
.case-console__live,
.case-console__title-row,
.case-console__score,
.case-console__row,
.case-console__footer {
  display: flex;
  align-items: center;
}

.case-console__topbar,
.case-console__title-row,
.case-console__row,
.case-console__footer {
  justify-content: space-between;
}

.case-console__topbar {
  padding-bottom: 22px;
  border-bottom: 1px solid rgba(171, 201, 224, 0.12);
}

.case-console__brand {
  gap: 8px;
  color: #eaf3f8;
  font-size: 12px;
  font-weight: 600;
}

.case-console__brand-mark {
  display: grid;
  width: 25px;
  height: 25px;
  place-items: center;
  border-radius: 7px 7px 7px 1px;
  color: var(--color-primary-deep);
  background: var(--color-gold);
  font-family: "STKaiti", "KaiTi", serif;
  font-size: 14px;
  font-weight: 700;
}

.case-console__live {
  gap: 5px;
  color: #a9d6bd;
  font-size: 10px;
}

.case-console__live i {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #79d19d;
  box-shadow: 0 0 0 4px rgba(121, 209, 157, 0.12);
}

.case-console__title-row {
  padding: 24px 0 20px;
}

.case-console__title-row strong,
.case-console__overline {
  display: block;
}

.case-console__overline {
  margin-bottom: 6px;
  color: #849eb2;
  font-size: 10px;
}

.case-console__title-row strong {
  color: #e8f2f7;
  font-size: 17px;
}

.case-console__date {
  color: #7f9aad;
  font-size: 10px;
}

.case-console__score {
  gap: 16px;
  padding: 15px;
  border: 1px solid rgba(201, 169, 110, 0.18);
  border-radius: 15px;
  background: rgba(201, 169, 110, 0.07);
}

.case-console__score-ring {
  display: grid;
  width: 65px;
  height: 65px;
  flex: none;
  place-items: center;
  border: 5px solid rgba(201, 169, 110, 0.22);
  border-top-color: var(--color-gold);
  border-right-color: var(--color-gold);
  border-radius: 50%;
  color: var(--color-gold-light);
  font-size: 20px;
  font-weight: 700;
}

.case-console__score-ring small {
  font-size: 11px;
}

.case-console__score-copy strong,
.case-console__score-copy span {
  display: block;
}

.case-console__score-copy strong {
  margin-bottom: 5px;
  color: #e8f2f7;
  font-size: 12px;
}

.case-console__score-copy span {
  color: #91a9ba;
  font-size: 10px;
}

.case-console__list {
  padding: 17px 0 16px;
}

.case-console__row {
  padding: 9px 0;
  color: #b4c7d4;
  font-size: 11px;
}

.case-console__row span {
  display: inline-flex;
  align-items: center;
  gap: 7px;
}

.case-console__row .el-icon {
  color: #89cca7;
}

.case-console__row b {
  color: #b9d8c5;
  font-size: 10px;
  font-weight: 500;
}

.case-console__row--muted {
  color: #7691a4;
}

.case-console__row--muted .el-icon,
.case-console__row--muted b {
  color: #8e9eaa;
}

.case-console__footer {
  padding-top: 13px;
  border-top: 1px solid rgba(171, 201, 224, 0.11);
  color: #6f899d;
  font-size: 9px;
  letter-spacing: 0.08em;
}

.case-console__footer-line {
  width: 38px;
  height: 2px;
  border-radius: 2px;
  background: var(--color-gold);
}

.hero-float {
  position: absolute;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 10px 13px 10px 9px;
  border: 1px solid rgba(205, 226, 240, 0.17);
  border-radius: 13px;
  color: #c2d2dc;
  background: rgba(10, 38, 60, 0.76);
  box-shadow: 0 13px 28px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(14px);
  font-size: 10px;
}

.hero-float b {
  color: var(--color-gold-light);
}

.hero-float--top {
  top: 37px;
  right: 1px;
}

.hero-float--bottom {
  bottom: 42px;
  left: -8px;
}

.hero-float__icon {
  display: grid;
  width: 25px;
  height: 25px;
  place-items: center;
  border-radius: 8px;
  color: #9bd0e8;
  background: rgba(86, 171, 213, 0.15);
}

.hero-float__icon--gold {
  color: var(--color-gold-light);
  background: rgba(201, 169, 110, 0.15);
}

.features-section {
  width: min(var(--page-width), calc(100% - 48px));
  margin: 0 auto;
  padding: 68px 0 102px;
}

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 32px;
  margin-bottom: 30px;
}

.section-heading__eyebrow {
  margin: 0 0 10px;
  color: var(--color-gold);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.17em;
}

.section-heading__title {
  margin: 0;
  color: #eaf3f8;
  font-size: 30px;
  letter-spacing: 0.04em;
}

.section-heading__description {
  max-width: none;
  margin: 0 0 2px;
  color: var(--color-text-secondary);
  font-size: 13px;
  line-height: 1.8;
  white-space: nowrap;
  text-align: right;
}

.features-grid {
  display: flex;
  gap: 22px;
}

@media (max-width: 1060px) {
  .hero-section {
    grid-template-columns: minmax(0, 1fr) minmax(340px, 0.76fr);
    gap: 22px;
  }

  .hero-section__visual {
    transform: scale(0.88);
    transform-origin: center right;
  }
}

@media (max-width: 820px) {
  .hero-section {
    display: block;
    min-height: auto;
    padding-top: 62px;
  }

  .hero-section__content {
    max-width: 680px;
  }

  .hero-section__visual {
    width: min(560px, 100%);
    min-height: 420px;
    margin: 20px auto -18px;
    transform: none;
  }
}

@media (max-width: 720px) {
  .features-section {
    width: min(var(--page-width), calc(100% - 32px));
    padding: 52px 0 68px;
  }

  .hero-section {
    padding-right: 16px;
    padding-left: 16px;
  }

  .hero-section__title {
    font-size: clamp(46px, 13vw, 68px);
  }

  /* 小屏标题字号更小，光标同步缩小，避免遮挡相邻文字。 */
  .hero-cursor {
    width: 76px;
    height: 76px;
  }

  .hero-section__actions {
    align-items: flex-start;
    flex-direction: column;
    gap: 16px;
  }

  .hero-search {
    width: 100%;
  }

  .hero-section__visual {
    min-height: 360px;
    margin-top: 5px;
    transform: scale(0.86);
    transform-origin: center center;
  }

  .hero-float--top {
    right: -5px;
  }

  .hero-float--bottom {
    left: 0;
  }

  .section-heading {
    align-items: flex-start;
    flex-direction: column;
    gap: 12px;
  }

  .section-heading__description {
    max-width: 100%;
    white-space: normal;
    text-align: left;
  }

  .features-grid {
    flex-direction: column;
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-search,
  .case-console,
  .feature-card,
  .hero-cursor {
    transition: none;
  }

  .hero-cursor {
    display: none;
  }
}

/* 浅色主题覆盖：保留 spotlight 和工作台结构，只把表面统一为暖白与浅蓝。 */
.home-page {
  background: var(--color-background);
}

.hero-section {
  background:
    radial-gradient(620px circle at var(--spotlight-x) var(--spotlight-y), rgba(201, 169, 110, 0.2), transparent 58%),
    radial-gradient(560px circle at 6% 100%, rgba(22, 91, 137, 0.08), transparent 66%),
    #fff;
}

.hero-section__grid {
  background-image:
    linear-gradient(rgba(26, 58, 92, 0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(26, 58, 92, 0.045) 1px, transparent 1px);
}

.hero-section__title {
  color: var(--color-primary);
}

.hero-section__eyebrow {
  color: #9b783c;
}

.hero-section__subtitle {
  color: var(--color-text-secondary);
}

.hero-search {
  border-color: rgba(26, 58, 92, 0.14);
  color: var(--color-text-secondary);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 16px 35px rgba(26, 58, 92, 0.09), inset 0 1px 0 #fff;
}

.hero-search:hover {
  border-color: rgba(201, 169, 110, 0.85);
  box-shadow: 0 20px 42px rgba(26, 58, 92, 0.13), 0 0 34px rgba(201, 169, 110, 0.12);
}

.hero-section__explore {
  color: var(--color-primary);
}

.hero-section__hint {
  color: var(--color-text-secondary);
}

.hero-orbit {
  border-color: rgba(201, 169, 110, 0.38);
}

.hero-orbit--outer {
  box-shadow: 0 0 0 1px rgba(75, 143, 184, 0.08), 0 0 60px rgba(201, 169, 110, 0.12);
}

.hero-orbit--inner {
  border-color: rgba(114, 172, 207, 0.28);
}

.case-console {
  border-color: rgba(26, 58, 92, 0.12);
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(245, 249, 252, 0.98));
  box-shadow: 0 30px 65px rgba(26, 58, 92, 0.16), inset 0 1px 0 #fff;
}

.case-console__topbar {
  border-bottom-color: rgba(26, 58, 92, 0.1);
}

.case-console__brand {
  color: var(--color-primary);
}

.case-console__live {
  color: #43855f;
}

.case-console__title-row strong {
  color: var(--color-primary);
}

.case-console__overline,
.case-console__date {
  color: var(--color-text-secondary);
}

.case-console__score {
  background: rgba(201, 169, 110, 0.09);
}

.case-console__score-copy strong {
  color: var(--color-primary);
}

.case-console__score-copy span,
.case-console__row,
.case-console__footer {
  color: var(--color-text-secondary);
}

.case-console__row b {
  color: #43855f;
}

.case-console__row--muted,
.case-console__row--muted b,
.case-console__row--muted .el-icon {
  color: #8d9aa6;
}

.case-console__footer {
  border-top-color: rgba(26, 58, 92, 0.1);
}

.hero-float {
  border-color: rgba(26, 58, 92, 0.12);
  color: var(--color-text-secondary);
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 14px 30px rgba(26, 58, 92, 0.12);
}

.hero-float b {
  color: var(--color-primary);
}

.hero-float__icon {
  color: #4d8eaf;
  background: rgba(86, 171, 213, 0.12);
}

.hero-float__icon--gold {
  color: #9b783c;
  background: rgba(201, 169, 110, 0.16);
}

.section-heading__title {
  color: var(--color-primary);
}
</style>
