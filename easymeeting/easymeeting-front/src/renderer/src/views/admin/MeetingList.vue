<template>
  <div class="top-panel">
    <el-form :model="searchForm" label-width="50px" label-position="right">
      <el-row>
        <el-col :span="8">
          <el-form-item label="会议主题">
            <el-input
              class="password-input"
              v-model="searchForm.meetingNameFuzzy"
              clearable
              placeholder="支持模糊搜索"
              @keyup.enter="loadDataList"
            >
            </el-input>
          </el-form-item>
        </el-col>
        <el-col :span="4" :style="{ paddingLeft: '10px' }">
          <el-button type="success" @click="loadDataList()">查询 </el-button>
        </el-col>
      </el-row>
    </el-form>
  </div>
  <Table :columns="columns" :fetch="loadDataList" :dataSource="tableData" :options="tableOptions">
    <template #slotStatus="{ index, row }">
      <span style="color: green" v-if="row.status == 0">进行中</span>
      <span style="color: #8a8a8a" v-else>已结束</span>
    </template>

    <template #slotOperation="{ index, row }">
      <span class="a-link" v-if="row.status == 0" @click="finishMeeting(row)">结束会议</span>
      <span v-else>-</span>
    </template>
  </Table>
</template>
<script setup>
import Avatar from '@/components/Avatar.vue'
import { getCurrentInstance, nextTick, ref } from 'vue'
const { proxy } = getCurrentInstance()

import { useUserInfoStore } from '@/stores/UserInfoStore'
const userInfoStore = useUserInfoStore()

const tableData = ref({})
const tableOptions = {}
const columns = [
  {
    label: '会议ID',
    prop: 'meetingId',
    width: 200
  },
  {
    label: '会议主题',
    prop: 'meetingName'
  },
  {
    label: '创建时间',
    prop: 'createTime',
    width: 200
  },
  {
    label: '创建人',
    prop: 'createUserName',
    width: 100
  },
  {
    label: '加入类型',
    prop: 'joinType',
    width: 100,
    scopedSlots: 'slotOnline'
  },
  {
    label: '状态',
    prop: 'status',
    width: 100,
    scopedSlots: 'slotStatus'
  },
  {
    label: '操作',
    prop: 'operation',
    width: 100,
    scopedSlots: 'slotOperation'
  }
]

const searchForm = ref({})

const loadDataList = async () => {
  let params = {
    pageNo: tableData.value.pageNo,
    pageSize: tableData.value.pageSize
  }
  Object.assign(params, searchForm.value)
  let result = await proxy.Request({
    url: proxy.Api.loadAdminMeeting,
    params: params
  })
  if (!result) {
    return
  }
  Object.assign(tableData.value, result.data)
}

const finishMeeting = (data) => {
  proxy.Confirm({
    message: `确认要结束会议【${data.meetingName}】吗？`,
    okfun: async () => {
      let result = await proxy.Request({
        url: proxy.Api.adminFinishMeeting,
        params: {
          meetingId: data.meetingId
        }
      })
      if (!result) {
        return
      }
      proxy.Message.success('操作成功')
      loadDataList()
    }
  })
}
</script>
<style lang="scss" scoped>
</style>
