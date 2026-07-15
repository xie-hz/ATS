<script setup>
import { ref } from "vue"
import { ElMessage } from "element-plus"
import { guestJoin, setToken } from "../api"

const emit = defineEmits(["joined"])

const form = ref({
  meetingNo: "",
  password: "",
  nickName: "",
  email: "",
})
const loading = ref(false)

async function submit() {
  if (!form.value.meetingNo || !form.value.nickName) {
    ElMessage.warning("请填写会议号和昵称")
    return
  }
  loading.value = true
  try {
    const data = await guestJoin(form.value.meetingNo, form.value.password, form.value.nickName, form.value.email)
    setToken(data.token)
    // App.vue 的 onJoined 会把 session 存入 sessionStorage，刷新可恢复
    emit("joined", data)
  } catch (e) {
    ElMessage.error(e.message || "入会失败")
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-wrap">
    <div class="login-card">
      <h2>EasyMeeting 视频面试</h2>
      <p class="hint">输入会议号与密码加入面试</p>
      <el-form label-position="top" @submit.prevent="submit">
        <el-form-item label="会议号">
          <el-input v-model="form.meetingNo" placeholder="会议号" clearable />
        </el-form-item>
        <el-form-item label="会议密码">
          <el-input v-model="form.password" placeholder="会议密码（如无则留空）" clearable />
        </el-form-item>
        <el-form-item label="您的昵称">
          <el-input v-model="form.nickName" placeholder="如：候选人张三" clearable />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="用于标识身份，刷新可恢复" clearable />
        </el-form-item>
        <el-button type="primary" :loading="loading" style="width: 100%" @click="submit">
          加入会议
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.login-wrap {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-card {
  width: 360px;
  padding: 32px;
  background: #2a2f38;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
.login-card h2 {
  margin: 0 0 8px;
  text-align: center;
}
.hint {
  text-align: center;
  color: #909399;
  margin: 0 0 24px;
  font-size: 13px;
}
</style>
