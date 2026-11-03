<template>
  <header class="app-header">
    <div class="app-header__inner">
      <!-- 品牌 Logo：点击后回到首页，形成清晰的主导航入口。 -->
      <router-link class="brand" to="/" aria-label="返回法宝首页">
        <span class="brand__mark" aria-hidden="true">法</span>
        <span class="brand__name">法宝</span>
        <span class="brand__divider" aria-hidden="true"></span>
        <span class="brand__tagline">AI 法律助手</span>
      </router-link>

      <!-- 使用 router-link 连接各功能页面，当前路由会自动添加高亮样式。 -->
      <nav class="app-nav" aria-label="主导航">
        <div class="app-nav__pill">
          <router-link
            v-for="item in navigationItems"
            :key="item.to"
            class="app-nav__link"
            active-class="app-nav__link--active"
            :to="item.to"
          >
            <!-- 图标只承担识别作用，文字仍是导航的主要信息。 -->
            <el-icon class="app-nav__icon" aria-hidden="true"><component :is="item.icon" /></el-icon>
            <span>{{ item.label }}</span>
          </router-link>
        </div>
      </nav>

      <div class="header-account">
        <template v-if="authState.user">
          <span class="header-account__user">
            <el-icon><UserFilled /></el-icon>
            {{ authState.user.username }}
          </span>
          <el-button link class="header-account__logout" @click="handleLogout">退出</el-button>
        </template>
        <router-link v-else class="header-account__login" to="/login">登录 / 注册</router-link>
      </div>
    </div>
  </header>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound, Document, EditPen, House, UserFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { authState, clearAuth, loadCurrentUser } from '../stores/auth'

// 顶部导航数据集中维护，新增菜单时只需要补充一个对象即可。
const navigationItems = [
  // 显式提供首页入口，用户在任意功能页都能快速返回项目主页。
  { label: '首页', to: '/', icon: House },
  { label: 'AI法律咨询', to: '/ai-consult', icon: ChatDotRound },
  { label: '文书生成', to: '/doc-generate', icon: Document },
  { label: '合同审查', to: '/contract-review', icon: EditPen }
]

const router = useRouter()

async function refreshUser() {
  await loadCurrentUser()
}

function handleAuthExpired() {
  authState.user = null
  if (router.currentRoute.value.name !== 'login' && router.currentRoute.value.name !== 'register') {
    router.replace({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
  }
}

function handleLogout() {
  clearAuth()
  ElMessage.success('已退出登录')
  router.push('/')
}

onMounted(() => {
  refreshUser()
  window.addEventListener('fabao-auth-expired', handleAuthExpired)
})

onBeforeUnmount(() => {
  window.removeEventListener('fabao-auth-expired', handleAuthExpired)
})
</script>

<style scoped>
/* 顶部导航使用半透明白底和细边框，保持轻盈的专业感。 */
.app-header {
  position: sticky;
  z-index: 10;
  top: 0;
  border-bottom: 1px solid rgba(230, 235, 241, 0.92);
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(16px);
}

.app-header__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: min(var(--page-width), calc(100% - 48px));
  min-height: 76px;
  margin: 0 auto;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--color-text);
}

.brand__mark {
  display: inline-grid;
  width: 36px;
  height: 36px;
  place-items: center;
  border-radius: 10px 10px 10px 2px;
  color: #fff;
  background: var(--color-primary);
  box-shadow: 5px 5px 0 var(--color-gold-light);
  font-family: "STKaiti", "KaiTi", serif;
  font-size: 20px;
  font-weight: 700;
}

.brand__name {
  font-family: "STKaiti", "KaiTi", serif;
  font-size: 25px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.brand__divider {
  width: 1px;
  height: 18px;
  margin: 0 2px 0 4px;
  background: var(--color-border);
}

.brand__tagline {
  color: var(--color-text-secondary);
  font-size: 12px;
  letter-spacing: 0.08em;
}

.app-nav {
  display: flex;
  align-items: center;
}

.header-account {
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 112px;
  justify-content: flex-end;
}

.header-account__user {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 600;
}

.header-account__logout,
.header-account__login {
  color: var(--color-gold);
  font-size: 12px;
  font-weight: 600;
}

.header-account__logout:hover,
.header-account__login:hover {
  color: var(--color-primary);
}

.app-nav__pill {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 4px;
  border: 1px solid rgba(230, 235, 241, 0.95);
  border-radius: 15px;
  background: rgba(247, 249, 252, 0.82);
  box-shadow: 0 4px 15px rgba(26, 58, 92, 0.04);
}

.app-nav__link {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-height: 38px;
  padding: 0 13px;
  border: 1px solid transparent;
  border-radius: 10px;
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  transition: color 0.2s ease, background-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.app-nav__icon {
  color: currentColor;
  font-size: 15px;
}

.app-nav__link:hover,
.app-nav__link--active {
  color: var(--color-primary);
  background: #fff;
  box-shadow: 0 3px 10px rgba(26, 58, 92, 0.08);
  transform: translateY(-1px);
}

.app-nav__link--active {
  border-color: rgba(201, 169, 110, 0.32);
}

.app-nav__link--active .app-nav__icon {
  color: var(--color-gold);
}

@media (max-width: 640px) {
  .app-header__inner {
    width: min(var(--page-width), calc(100% - 32px));
    min-height: 68px;
  }

  .brand__divider,
  .brand__tagline {
    display: none;
  }

  .brand__name {
    font-size: 22px;
  }

  .app-nav {
    gap: 0;
  }

  .header-account {
    min-width: auto;
  }

  .header-account__user {
    max-width: 66px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .app-nav__pill {
    gap: 1px;
    padding: 3px;
  }

  .app-nav__link {
    gap: 4px;
    min-height: 34px;
    padding: 0 7px;
    font-size: 11px;
  }

  .app-nav__icon {
    display: none;
  }
}
</style>
