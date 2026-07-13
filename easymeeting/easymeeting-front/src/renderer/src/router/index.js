import { createRouter, createWebHashHistory } from 'vue-router'
const router = createRouter({
  mode: "hash",
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "登录",
      component: () => import('@/views/login/Login.vue'),
    },
    {
      path: "/home",
      name: "主页",
      component: () => import('@/views/Layout.vue'),
      redirect: "/meetingMain",
      children: [{
        path: "/meetingMain",
        name: "首页",
        component: () => import('@/views/meeting/MeetingMain.vue'),
        meta: {
          code: "meeting",
        }
      }, {
        path: "/contact",
        name: "联系人",
        component: () => import('@/views/contact/Contact.vue'),
        meta: {
          code: "contact"
        }
      }, {
        path: "/screencap",
        name: "录屏",
        component: () => import('@/views/screencap/ScreenCap.vue'),
        meta: {
          code: "screencap"
        }
      }, {
        path: "/setting",
        name: "设置",
        component: () => import('@/views/setting/Setting.vue'),
        meta: {
          code: "setting"
        }
      }]
    },
    {
      path: "/meeting",
      name: "会议详情",
      component: () => import('@/views/meeting/meeting/Meeting.vue'),
    },
    {
      path: "/showMedia",
      name: "媒体详情",
      component: () => import('@/views/meeting/chat/ShowMedia.vue'),
    },
    {
      path: "/meetingAll",
      name: "全部会议",
      component: () => import('@/views/meeting/history/MeetingAll.vue'),
    },
    {
      path: "/meetingMessage",
      name: "会议聊天记录",
      component: () => import('@/views/meeting/history/MeetingMessage.vue'),
    },
    {
      path: "/meetingMember",
      name: "会议成员",
      component: () => import('@/views/meeting/history/MeetingMember.vue'),
    },
    {
      path: "/meetingReserve",
      name: "预定会议",
      component: () => import('@/views/meeting/reserve/MeetingReserve.vue'),
    },
    {
      path: "/admin",
      name: "管理后台",
      component: () => import('@/views/admin/AdminLayout.vue'),
      redirect: "/userList",
      children: [{
        path: "/userList",
        name: "用户管理",
        component: () => import('@/views/admin/UserList.vue'),
      }, {
        path: "/appUpdate",
        name: "应用更新",
        component: () => import('@/views/admin/Update.vue'),
      }, {
        path: "/sysSetting",
        name: "系统设置",
        component: () => import('@/views/admin/SysSetting.vue'),
      }, {
        path: "/meetingMange",
        name: "会议管理",
        component: () => import('@/views/admin/MeetingList.vue'),
      }]
    }
  ]
})


export default router
