<template>
  <div class="screen-source-list">
    <div
      :class="['source-item', screenDisplayId == item.displayId ? 'active' : '']"
      v-for="item in screenSources"
      @click="selectSource(item)"
    >
      <Cover :source="item.thumbnail" borderRadius="0px"></Cover>
      <div class="name">{{ item.name }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, getCurrentInstance, nextTick, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()

const emit = defineEmits(['selectScreenDisplayId'])

const screenDisplayId = ref()
const selectSource = async (source) => {
  screenDisplayId.value = source.displayId
  emit('selectScreenDisplayId', screenDisplayId.value)
}

const screenSources = ref([])
const getScreen = async () => {
  screenSources.value = await window.electron.ipcRenderer.invoke('getScreenSource', {
    types: ['screen'], // 同时显示屏幕和窗口
    thumbnailSize: {
      width: 640,
      height: 360
    }
  })
  screenDisplayId.value = screenSources.value[0].displayId
  emit('selectScreenDisplayId', screenDisplayId.value)
}

onMounted(() => {
  getScreen()
})
</script>

<style lang="scss" scoped>
.screen-source-list {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-gap: 10px;
  flex-wrap: wrap;
  .source-item {
    overflow: hidden;
    border: 2px solid #ddd;
    border-radius: 5px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    &:hover {
      border-color: var(--blue);
    }
    .name {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      text-align: center;
      margin-top: 2px;
      padding: 4px 0px;
    }
  }
  .active {
    border-color: var(--blue);
    .name {
      color: var(--blue);
    }
  }
}
</style>
