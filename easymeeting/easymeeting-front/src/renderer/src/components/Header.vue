<template>
  <div class="header" :style="{ 'border-bottom': showBottomBorder ? ' 1px solid #ddd' : 'none' }">
    <div class="title" v-if="title">{{ title }}</div>
    <Titlebar :closeType="closeType" :showMax="showMax" ref="titlebarRef"></Titlebar>
  </div>
</template>

<script setup>
import { ref, reactive, getCurrentInstance, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()

const props = defineProps({
  title: {
    type: String
  },
  showMax: {
    type: Boolean,
    default: false
  },
  showBottomBorder: {
    type: Boolean,
    default: false
  },
  closeType: {
    type: Number,
    default: 0
  }
})

const titlebarRef = ref()

const close = () => {
  titlebarRef.value.custClose()
}

defineExpose({
  close
})
</script>

<style lang="scss" scoped>
.header {
  height: 30px;
  -webkit-app-region: drag;
  text-align: center;
  padding-top: 5px;
}
</style>
