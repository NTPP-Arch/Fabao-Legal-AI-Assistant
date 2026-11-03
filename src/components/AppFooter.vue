<template>
  <footer class="app-footer">
    <div class="app-footer__inner">
      <!-- 版权信息使用当前品牌名，年份通过脚本自动获取，避免每年手动修改。 -->
      <p class="app-footer__copyright">© {{ currentYear }} 法宝 · AI法律助手</p>

      <!-- 免责声明明确产品定位，避免用户将 AI 输出直接视为正式法律意见。 -->
      <p class="app-footer__disclaimer">
        免责声明：AI 生成内容仅供参考，不构成正式法律意见，重要事项请咨询专业律师。
      </p>
    </div>
  </footer>
</template>

<script setup>
// 底部栏当前为纯展示组件；年份只在组件创建时读取一次即可满足展示需求。
const currentYear = new Date().getFullYear()
</script>

<style scoped>
.app-footer {
  border-top: 1px solid var(--color-border);
  background: #fff;
}

.app-footer__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  width: min(var(--page-width), calc(100% - 48px));
  min-height: 84px;
  margin: 0 auto;
}

.app-footer__copyright,
.app-footer__disclaimer {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 12px;
  line-height: 1.7;
}

.app-footer__copyright {
  color: var(--color-primary);
  font-weight: 600;
}

@media (max-width: 640px) {
  .app-footer__inner {
    align-items: flex-start;
    flex-direction: column;
    gap: 4px;
    width: min(var(--page-width), calc(100% - 32px));
    padding: 20px 0;
  }
}
</style>
