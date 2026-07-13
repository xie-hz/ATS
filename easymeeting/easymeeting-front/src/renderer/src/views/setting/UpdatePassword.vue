<template>
  <Dialog :show="dialogConfig.show" :title="dialogConfig.title" :buttons="dialogConfig.buttons" width="400px"
    :showCancel="true" @close="dialogConfig.show = false">
    <el-form :model="formData" :rules="rules" ref="formDataRef" label-width="80px" @submit.prevent>
      <!--input输入-->
      <el-form-item label="原密码" prop="oldPassword">
        <el-input clearable placeholder="请输入原密码" type="password" show-password
          v-model.trim="formData.oldPassword"></el-input>
      </el-form-item>
      <!--textarea输入-->
      <el-form-item label="新密码" prop="password">
        <el-input clearable placeholder="请输入新密码" type="password" show-password
          v-model.trim="formData.password"></el-input>
      </el-form-item>
      <el-form-item label="确认密码" prop="rePassword">
        <el-input clearable placeholder="请再次输入新密码" type="rePassword" show-password
          v-model.trim="formData.rePassword"></el-input>
      </el-form-item>
    </el-form>
  </Dialog>
</template>

<script setup>
import { ref, reactive, getCurrentInstance, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()

const dialogConfig = ref({
  show: false,
  title: '修改密码',
  buttons: [
    {
      type: 'primary',
      text: '确定',
      click: (e) => {
        submitForm()
      }
    }
  ]
})

const checkRePassword = (rule, value, callback) => {
  if (value !== formData.value.password) {
    callback(new Error(rule.message))
  } else {
    callback()
  }
}

const formData = ref({})
const formDataRef = ref()
const rules = {
  oldPassword: [{ required: true, message: '请输入原密码' }],
  password: [
    { required: true, message: '请输入密码' },
    {
      validator: proxy.Verify.password,
      message: '密码只能是数字，字母，特殊字符 8-18位'
    }
  ],
  rePassword: [
    { required: true, message: '请再次输入密码' },
    {
      validator: checkRePassword,
      message: '两次输入的密码不一致'
    }
  ]
}

const submitForm = () => {
  formDataRef.value.validate(async (valid) => {
    if (!valid) {
      return
    }
    let params = {}
    Object.assign(params, formData.value)
    let result = await proxy.Request({
      url: proxy.Api.updatePassword,
      params
    })
    if (!result) {
      return
    }
    proxy.Message.success('请重新登录')
    dialogConfig.value.show = false
    await window.electron.ipcRenderer.invoke('logout')
    router.push('/')
  })
}

const show = async () => {
  dialogConfig.value.show = true
  await nextTick()
  formDataRef.value.resetFields()
}

defineExpose({
  show
})
</script>
<style lang="scss" scoped>
</style>
