<template>
  <div :class="['member-item', LAYOUT_MAP[layoutType]]">
    <video autoplay playsinline ref="videoElement" :id="`member_${data.userId}`"></video>
    <!-- <template v-else>
      <Avatar :avatar="data.avatar"></Avatar>
      <div class="user-name">{{ data.name }}</div>
    </template> -->
  </div>
</template>

<script setup>
import { ref, reactive, getCurrentInstance, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()

const props = defineProps({
  data: {
    type: Object,
    default: {}
  },
  layoutType: {
    type: Number,
    default: 0
  }
})
const LAYOUT_MAP = {
  0: 'member-item',
  1: 'member-item-top',
  2: 'member-item-right'
}
</script>

<style lang="scss" scoped>
.member-item {
  background: #f7f7f7;
  position: relative;
  flex-shrink: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 8px;
  video {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transform: scaleX(-1);
  }
  .user-name {
    margin-top: 3px;
    font-size: 13px;
  }
}

.member-item-top {
  width: 100px;
  height: 100px;
  margin-right: 10px;
}
.member-item-right {
  width: 100px;
  height: 100px;
  margin-bottom: 10px;
}
</style>
