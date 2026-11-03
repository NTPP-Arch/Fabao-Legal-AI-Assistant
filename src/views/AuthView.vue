<template>
  <main class="auth-page">
    <section class="auth-card" aria-labelledby="auth-title">
      <div class="auth-card__intro">
        <span class="auth-card__eyebrow">FABAO · AI LEGAL ASSISTANT</span>
        <h1 id="auth-title">{{ isRegister ? '创建您的法宝账户' : '欢迎回到法宝' }}</h1>
        <p>{{ isRegister ? '注册后即可使用咨询、文书和合同审查服务。' : '登录后继续您的法律工作。' }}</p>
      </div>

      <el-tabs v-model="activeTab" class="auth-tabs" @tab-change="switchMode">
        <el-tab-pane label="登录" name="login" />
        <el-tab-pane label="注册" name="register" />
      </el-tabs>

      <el-form
        ref="formRef"
        class="auth-form"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="submit"
      >
        <el-form-item :label="isRegister ? '用户名' : '用户名或邮箱'" prop="username">
          <el-input
            v-model="form.username"
            size="large"
            :placeholder="isRegister ? '3-50 个字符' : '请输入用户名或邮箱'"
            autocomplete="username"
            clearable
            @keyup.enter="submit"
          />
        </el-form-item>

        <el-form-item v-if="isRegister" label="邮箱" prop="email">
          <el-input
            v-model="form.email"
            size="large"
            placeholder="name@example.com"
            autocomplete="email"
            clearable
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            size="large"
            type="password"
            show-password
            :placeholder="isRegister ? '至少 8 位密码' : '请输入密码'"
            autocomplete="current-password"
            @keyup.enter="submit"
          />
        </el-form-item>

        <el-form-item v-if="isRegister" label="确认密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            size="large"
            type="password"
            show-password
            placeholder="再次输入密码"
            autocomplete="new-password"
            @keyup.enter="submit"
          />
        </el-form-item>

        <el-button class="auth-submit" type="primary" size="large" native-type="submit" :loading="loading">
          {{ isRegister ? '注册并登录' : '登录' }}
        </el-button>
      </el-form>

      <p class="auth-card__hint">
        {{ isRegister ? '已有账号？' : '还没有账号？' }}
        <button type="button" @click="switchMode(isRegister ? 'login' : 'register')">
          {{ isRegister ? '立即登录' : '免费注册' }}
        </button>
      </p>
    </section>
  </main>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getCurrentUser, login, register } from '../api/auth'
import { setUser } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const formRef = ref()
const loading = ref(false)
const activeTab = ref(route.name === 'register' || route.query.mode === 'register' ? 'register' : 'login')
const form = reactive({ username: '', email: '', password: '', confirmPassword: '' })
const isRegister = computed(() => activeTab.value === 'register')

const validateConfirmPassword = (_, value, callback) => {
  if (!isRegister.value || value === form.password) callback()
  else callback(new Error('两次输入的密码不一致'))
}

const rules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
    { min: 3, max: 100, message: '请输入有效的用户名或邮箱', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 128, message: '密码长度为 8-128 位', trigger: 'blur' }
  ],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

function switchMode(mode) {
  activeTab.value = mode
  formRef.value?.clearValidate()
}

async function submit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    if (isRegister.value) {
      await register({ username: form.username, email: form.email, password: form.password })
      ElMessage.success('注册成功，正在登录')
    }

    const response = await login({ username: form.username, password: form.password })
    // 登录接口只返回 token，再请求 /me 将用户资料交给 Header 和页面共享。
    const userResponse = await getCurrentUser()
    setUser(userResponse.data)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    await router.replace(redirect)
    ElMessage.success('登录成功')
    return response
  } catch {
    // 错误消息已经由 axios 响应拦截器统一展示。
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: grid;
  min-height: 620px;
  padding: 64px 24px 88px;
  place-items: center;
  background:
    radial-gradient(circle at 20% 10%, rgba(201, 169, 110, 0.13), transparent 32%),
    var(--color-background);
}

.auth-card {
  width: min(460px, 100%);
  padding: 42px 42px 32px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-large);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}

.auth-card__intro {
  text-align: center;
}

.auth-card__eyebrow {
  color: var(--color-gold);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.18em;
}

.auth-card h1 {
  margin: 16px 0 9px;
  color: var(--color-primary);
  font-size: 27px;
}

.auth-card__intro p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.auth-tabs {
  margin: 27px 0 22px;
}

.auth-form :deep(.el-form-item__label) {
  color: var(--color-primary);
  font-weight: 600;
}

.auth-submit {
  width: 100%;
  margin-top: 7px;
  border: none;
  background: var(--color-primary);
}

.auth-card__hint {
  margin: 24px 0 0;
  color: var(--color-text-secondary);
  font-size: 13px;
  text-align: center;
}

.auth-card__hint button {
  padding: 0;
  border: 0;
  color: var(--color-gold);
  background: transparent;
  cursor: pointer;
  font: inherit;
  font-weight: 600;
}

@media (max-width: 520px) {
  .auth-card {
    padding: 32px 22px 26px;
  }
}
</style>
