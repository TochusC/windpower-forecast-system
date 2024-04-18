import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as echarts from 'echarts';
import locale from 'element-plus/lib/locale/lang/zh-cn';
import App from './App.vue'
import {Vue} from "vue-class-component";

const app = createApp(App)

app.config.warnHandler = () => {
    console.log('error')
};
app.config.errorHandler = () => {
    console.log('error')
};

app.use(ElementPlus, { locale })
app.mount('#app')