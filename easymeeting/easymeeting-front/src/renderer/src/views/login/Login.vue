<template>
  <Header :showMax="false" :closeType="0" :showBottomBorder="false"></Header>
  <div class="loading-panel" v-if="showLoading">
    <img src="../../assets/loading.gif" />
    <div>正在登录中......</div>
  </div>
  <div class="login-form" v-else>
    <div class="error-msg">{{ errorMsg }}</div>
    <el-form :model="formData" ref="formDataRef" label-width="0px" @submit.prevent>
      <el-form-item prop="email">
        <div class="email-panel">
          <el-input
            class="input"
            size="large"
            clearable
            placeholder="请输入邮箱"
            v-model.trim="formData.email"
            maxLength="30"
            @focus="clearVerify"
            :input-style="{ border: 'none' }"
          >
            <template #prefix>
              <span class="iconfont icon-email"></span>
            </template>
          </el-input>
        </div>
      </el-form-item>
      <el-form-item prop="nickName" v-if="!isLogin">
        <el-input
          size="large"
          clearable
          placeholder="请输入昵称"
          v-model.trim="formData.nickName"
          maxLength="15"
          @focus="clearVerify"
        >
          <template #prefix>
            <span class="iconfont icon-user-nick"></span>
          </template>
        </el-input>
      </el-form-item>
      <!--登录密码-->
      <el-form-item prop="password">
        <el-input
          type="password"
          size="large"
          placeholder="请输入密码"
          v-model.trim="formData.password"
          show-password
          @focus="clearVerify"
          maxLength="18"
        >
          <template #prefix>
            <span class="iconfont icon-password"></span>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item prop="rePassword" v-if="!isLogin">
        <el-input
          type="password"
          size="large"
          placeholder="请再次输入密码"
          v-model.trim="formData.rePassword"
          show-password
          @focus="clearVerify"
          maxLength="18"
        >
          <template #prefix>
            <span class="iconfont icon-password"></span>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item prop="checkCode">
        <div class="check-code-panel">
          <el-input
            size="large"
            placeholder="请输入验证码"
            v-model.trim="formData.checkCode"
            @focus="clearVerify"
            @keyup.enter="submit"
          >
            <template #prefix>
              <span class="iconfont icon-checkcode"></span>
            </template>
          </el-input>
          <img :src="checkCodeUrl" class="check-code" @click="changeCheckCode" />
        </div>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submit" class="login-btn" size="large">{{
          isLogin ? '登录' : '注册'
        }}</el-button>
      </el-form-item>
      <div class="bottom-link">
        <span class="a-link no-account" @click="changeOpType">{{
          isLogin ? '没有账号?' : '已有账号?'
        }}</span>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, getCurrentInstance, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()
import { ElLoading } from 'element-plus'

import { useUserInfoStore } from '@/stores/UserInfoStore'
const userInfoStore = useUserInfoStore()

import md5 from 'js-md5'

const checkCodeUrl = ref(null)
const changeCheckCode = async () => {
  let result = await proxy.Request({
    url: proxy.Api.checkCode
  })
  if (!result) {
    return
  }
  checkCodeUrl.value = result.data.checkCode
  localStorage.setItem('checkCodeKey', result.data.checkCodeKey)
}
changeCheckCode()

const isLogin = ref(true)
const formData = ref({})
const formDataRef = ref()

const changeOpType = async () => {
  await window.electron.ipcRenderer.invoke('loginOrRegister', !isLogin.value)
  isLogin.value = !isLogin.value
  nextTick(() => {
    formDataRef.value.resetFields()
    formData.value = {}
    changeCheckCode()
    clearVerify()
  })
}

const errorMsg = ref()
const checkValue = (type, value, msg) => {
  if (proxy.Utils.isEmpty(value)) {
    errorMsg.value = msg
    return false
  }
  if (type && !proxy.Verify[type](value)) {
    errorMsg.value = msg
    return false
  }
  return true
}

const clearVerify = () => {
  errorMsg.value = ''
}

const showLoading = ref(false)
const submit = async () => {
  clearVerify()
  if (!checkValue('checkEmail', formData.value.email, '请输入正确的邮箱')) {
    return
  }
  if (!isLogin.value && !checkValue(null, formData.value.nickName, '请输入昵称')) {
    return
  }
  if (
    !checkValue('checkPassword', formData.value.password, '密码只能是数字、字母、特殊字符8~18位')
  ) {
    return
  }
  if (!checkValue(null, formData.value.checkCode, '请输入验证码')) {
    return
  }

  if (!isLogin.value && !checkValue(null, formData.value.rePassword, '请再次输入密码')) {
    return
  }
  if (!isLogin.value && formData.value.password != formData.value.rePassword) {
    errorMsg.value = '两次输入的密码不一致'
    return
  }

  if (isLogin.value) {
    showLoading.value = true
  }
  let result = await proxy.Request({
    url: isLogin.value ? proxy.Api.login : proxy.Api.register,
    showLoading: false,
    showError: false,
    params: {
      email: formData.value.email,
      password: isLogin.value ? md5(formData.value.password) : formData.value.password,
      checkCode: formData.value.checkCode,
      nickName: formData.value.nickName,
      checkCodeKey: localStorage.getItem('checkCodeKey')
    },
    errorCallback: (response) => {
      showLoading.value = false
      changeCheckCode()
      errorMsg.value = response.info
    }
  })
  if (!result) {
    return
  }
  if (isLogin.value) {
    await window.electron.ipcRenderer.invoke('loginSuccess', {
      userInfo: result.data,
      wsUrl: import.meta.env.VITE_WS
    })
    userInfoStore.setInfo(result.data)
    localStorage.setItem('userInfo', JSON.stringify(result.data))
    router.push('/home')
  } else {
    proxy.Message.success('注册成功')
    changeOpType()
  }
}
</script>

<style lang="scss" scoped>
.email-select {
  width: 250px;
}
.loading-panel {
  height: calc(100vh - 32px);
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  font-size: 14px;
  color: #727272;
  img {
    width: 30px;
    margin-right: 3px;
  }
}
.login-form {
  padding: 0px 15px;
  height: calc(100vh - 32px);
  :deep(.el-input__wrapper) {
    box-shadow: none;
    border-radius: none;
  }
  .el-form-item {
    border-bottom: 1px solid #ddd;
  }

  .email-panel {
    align-items: center;
    width: 100%;
    display: flex;
    .input {
      flex: 1;
    }
    .icon-down {
      margin-left: 3px;
      width: 16px;
      cursor: pointer;
      border: none;
    }
  }
  .error-msg {
    line-height: 30px;
    height: 30px;
    color: #fb7373;
  }
  .check-code-panel {
    display: flex;
    .check-code {
      cursor: pointer;
      width: 120px;
      margin-left: 5px;
    }
  }

  .login-btn {
    margin-top: 20px;
    width: 100%;
  }
  .bottom-link {
    text-align: right;
    font-size: 13px;
  }
}
</style>
