<template>
  <article class="feature-card">
    <!-- 功能图标使用父组件传入的 Element Plus 图标组件，保持卡片可复用。 -->
    <div class="feature-card__icon" aria-hidden="true">
      <el-icon :size="28"><component :is="icon" /></el-icon>
    </div>

    <!-- 卡片标题和描述由父组件传入，便于首页统一管理功能文案。 -->
    <h3 class="feature-card__title">{{ title }}</h3>
    <p class="feature-card__description">{{ description }}</p>

    <!-- router-link 负责路由跳转，按钮只负责呈现操作意图。 -->
    <router-link class="feature-card__link" :to="to">
      <el-button class="feature-card__button" type="primary">
        立即使用
        <el-icon class="feature-card__arrow"><ArrowRight /></el-icon>
      </el-button>
    </router-link>
  </article>
</template>

<script setup>
import { ArrowRight } from '@element-plus/icons-vue'

// 定义卡片所需的数据接口；icon 接收一个可渲染的 Vue 组件对象。
defineProps({
  icon: {
    type: Object,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  to: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.feature-card {
  position: relative;
  isolation: isolate;
  display: flex;
  flex: 1;
  flex-direction: column;
  min-height: 270px;
  padding: 30px 28px 26px;
  overflow: hidden;
  border: 1px solid rgba(230, 235, 241, 0.95);
  border-radius: var(--radius-large);
  background:
    radial-gradient(circle at 95% 0%, rgba(201, 169, 110, 0.12), transparent 34%),
    #fff;
  box-shadow: var(--shadow-card);
  transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
}

.feature-card::before {
  position: absolute;
  z-index: 0;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(135deg, rgba(201, 169, 110, 0.13), transparent 35%, transparent 70%, rgba(108, 170, 214, 0.08));
  content: "";
  opacity: 0;
  transition: opacity 0.25s ease;
}

.feature-card:hover {
  border-color: rgba(201, 169, 110, 0.6);
  box-shadow: var(--shadow-hover);
  transform: translateY(-6px);
}

.feature-card:hover::before {
  opacity: 1;
}

.feature-card > * {
  position: relative;
  z-index: 1;
}

.feature-card__icon {
  display: inline-grid;
  width: 58px;
  height: 58px;
  margin-bottom: 24px;
  place-items: center;
  border-radius: 16px;
  color: var(--color-primary);
  background: var(--color-primary-soft);
  box-shadow: inset 0 0 0 1px rgba(26, 58, 92, 0.08);
}

.feature-card__title {
  margin: 0 0 10px;
  color: var(--color-primary);
  font-size: 20px;
  font-weight: 700;
}

.feature-card__description {
  flex: 1;
  margin: 0 0 24px;
  color: var(--color-text-secondary);
  font-size: 14px;
  line-height: 1.8;
}

.feature-card__link {
  align-self: flex-start;
}

.feature-card__button {
  height: 38px;
  padding: 0 16px;
  border: none;
  border-radius: 9px;
  color: var(--color-primary-deep);
  background: var(--color-gold);
}

.feature-card__button:hover {
  color: var(--color-primary-deep);
  background: var(--color-gold-light);
}

.feature-card__arrow {
  margin-left: 6px;
}
</style>
