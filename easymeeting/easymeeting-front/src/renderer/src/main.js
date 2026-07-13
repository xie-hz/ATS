import '@/assets/base.scss'

import { createApp } from 'vue'
import App from './App.vue'

import * as Pinia from 'pinia';
import router from '@/router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import "@/assets/icon/iconfont.css"
import '@/assets/base.scss';

import VueCookies from 'vue-cookies'


import Avatar from "@/components/Avatar.vue"
import Cover from "@/components/Cover.vue"
import DataLoadMoreList from "@/components/DataLoadMoreList.vue"
import NoData from "@/components/NoData.vue"
import Titlebar from "@/components/Titlebar.vue"
import Dialog from "@/components/Dialog.vue"
import Header from "@/components/Header.vue"
import Table from "@/components/Table.vue"

import Request from "@/utils/Request"
import Message from "@/utils/Message"
import Utils from "@/utils/Utils"
import { Confirm, Alert } from "@/utils/Confirm.js"
import { Api } from "@/utils/Api.js"
import Verify from "@/utils/Verify.js"

const app = createApp(App)
app.use(Pinia.createPinia());
app.use(router);
app.use(ElementPlus);

app.component("Cover", Cover);
app.component("Avatar", Avatar);
app.component("NoData", NoData);
app.component("Titlebar", Titlebar);
app.component("Header", Header);
app.component("DataLoadMoreList", DataLoadMoreList);
app.component("Dialog", Dialog);
app.component("Table", Table);

app.config.globalProperties.VueCookies = VueCookies;
app.config.globalProperties.Request = Request;
app.config.globalProperties.Message = Message;
app.config.globalProperties.Utils = Utils;
app.config.globalProperties.Api = Api
app.config.globalProperties.Confirm = Confirm;
app.config.globalProperties.Alert = Alert;
app.config.globalProperties.Verify = Verify;
app.config.globalProperties.imageAccept = ".jpg,.png,.gif,.bmp,.webp";

app.mount('#app')
