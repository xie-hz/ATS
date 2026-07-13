<template>
  <Dialog
    :show="dialogConfig.show"
    :title="dialogConfig.title"
    :buttons="dialogConfig.buttons"
    width="400px"
    :showCancel="false"
    @close="dialogConfig.show = false"
  >
    <el-form :model="formData" :rules="rules" ref="formDataRef" label-width="80px" @submit.prevent>
      <!--input输入-->
      <el-form-item label="会议号" prop="meetingNo">
        <el-input clearable placeholder="输入会议号" v-model.trim="formData.meetingNo"></el-input>
      </el-form-item>
    </el-form>
  </Dialog>
</template>

<script setup>
import { defaultProps } from 'element-plus/es/components/select-v2/src/useProps'
import { ref, reactive, getCurrentInstance, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()

const dialogConfig = ref({
  show: false,
  title: '共享屏幕',
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
const formData = ref({})
const formDataRef = ref()
const rules = {
  meetingNo: [{ required: true, message: '请输入会议号' }]
}

const show = () => {
  dialogConfig.value.show = true
}

defineExpose({
  show
})
</script>

<style lang="scss" scoped>
</style>
