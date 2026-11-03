<template>
  <div class="site-layout">
    <!-- 顶部导航在所有页面复用，保证不同路由下的品牌入口一致。 -->
    <AppHeader />

    <!-- 主体容器承载路由视图，具体页面组件内部再定义自己的 main 区域。 -->
    <div class="site-main">
      <router-view v-slot="{ Component, route }">
        <!-- 通过路由地址作为 key，确保同一路由参数变化时页面能够正确刷新。 -->
        <transition name="page-fade" mode="out-in">
          <component :is="Component" :key="route.fullPath" />
        </transition>
      </router-view>
    </div>

    <!-- 底部信息在所有页面统一展示免责声明和版权信息。 -->
    <AppFooter />
  </div>
</template>

<script setup>
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
</script>
