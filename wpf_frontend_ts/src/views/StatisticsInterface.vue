<script setup>
  import {ref, onMounted, onUnmounted, defineProps} from 'vue'
  import dayjs from 'dayjs'
  import {
    Calendar, Download, Finished, Sunset,
    Upload, WindPower, ChatDotSquare, Clock, Odometer, Position
  } from '@element-plus/icons-vue'
  import MessageCard from "@/components/utils/MessageCard.vue";

  const timeToNextDay = ref(dayjs().add(1, 'day').startOf('day'))
  const statisticsData = ref({})
  const visits = parseInt(localStorage.getItem('visits')) + 1;
  const currentRunningTime = ref(null)
  const displayTime = ref("")
  const interval = ref(null)

  const cpuUsage = ref(0)
  const gpuUsage = ref(0)
  const memoryUsage = ref(0)
  const diskUsage = ref(0)
  const dynamicSpan = ref(4)
  const props = defineProps({
    isDark: {
      type: Boolean,
      required: true
    },
    windowsHeight: {
      type: Number,
      required: true
    },
    windowsWidth: {
      type: Number,
      required: true
    }
  })

  const colors = [
    { color: '#f56c6c', percentage: 20 },
    { color: '#e6a23c', percentage: 40 },
    { color: '#5cb87a', percentage: 60 },
    { color: '#1989fa', percentage: 80 },
    { color: '#6f7ad3', percentage: 100 },
  ]
  const alt_colors = [
    { color: '#f56c6c', percentage: 100 },
    { color: '#e6a23c', percentage: 80 },
    { color: '#5cb87a', percentage: 60 },
    { color: '#1989fa', percentage: 40 },
    { color: '#6f7ad3', percentage: 20 },
  ]
  const formatTimestamp = (timestamp) => {
    var date = new Date(timestamp);

    var year = date.getFullYear() - 1970;
    var month = date.getMonth();
    var day = date.getDate() - 1;
    var hour = date.getHours();
    var minute = date.getMinutes();
    var second = date.getSeconds();

    let timeStr = day + "天 " + String(hour).padStart(2,'0')
        + "时" + String(minute).padStart(2,'0') + "分" + String(second).padStart(2,'0') + "秒";

    if(year === 0 && month === 0){
      return timeStr
    }
    else if(year === 0){
      return month + "月 " + timeStr
    }
    else{
      return year + "年 " + month + "月 " + timeStr
    }
  }

  const assembleUseage = (data) => {
    cpuUsage.value = data.cpu_usage
    gpuUsage.value = data.gpu_usage
    memoryUsage.value = data.memory_usage
    diskUsage.value = data.disk_usage
  }

  const get_useage = () => {
    fetch('http://127.0.0.1:8000/api/get_useAge/')
        .then(response => {
          return response.json()
        })
        .then((data) => {
          assembleUseage(data)
        })
        .catch(e => console.log("Oops, error", e))
  }

  const currentPercentage = ref(0)
  const assembleStatistics = (data) => {
    statisticsData.value = data[0].fields
    statisticsData.value['modelNum'] = data[0].modelNum
    statisticsData.value['turbineNum'] = data[0].turbineNum
    statisticsData.value['dataNum'] = data[0].dataNum
    statisticsData.value['taskNum'] = data[0].taskNum
    statisticsData.value['guestbookNum'] = data[0].guestbookNum
    console.log(statisticsData.value)
    currentRunningTime.value = new Date(statisticsData.value.statistics_time * 1000)
    displayTime.value = formatTimestamp(currentRunningTime.value)

    interval.value = setInterval(() => {
      currentRunningTime.value = currentRunningTime.value + 500;
      displayTime.value = formatTimestamp(currentRunningTime.value)

      let currentTime = dayjs()
      let pastTime = dayjs().startOf('day')
      let timeDiff = currentTime.diff(pastTime)
      currentPercentage.value = ((1 - timeDiff / 86400000 ) * 100).toFixed(2)

      get_useage()

    }, 500)
  }

  onMounted(() => {
    fetch('http://127.0.0.1:8000/api/get_statistics/')
        .then(response => {
          return response.json()
        })
        .then((data) => {
          assembleStatistics(data)
        })
        .catch(e => console.log("Oops, error", e))
    get_useage()
  })

  onUnmounted(() => {
    clearInterval(interval.value)
  })
</script>

<template>
  <div class="centerFlex">
    <span style="margin-left: 24px">
      <el-text class="title">统计界面</el-text>
    </span>
  </div>
  <el-divider style="margin-top: 16px"></el-divider>

  <el-row>
    <el-col :span="6">
      <el-statistic :value="visits">
        <template #title>
          <div class="statistic-label">
            系统访问次数
            <el-icon style="margin-left: 4px" :size="12">
              <Position />
            </el-icon>
          </div>
        </template>
      </el-statistic>
    </el-col>
    <el-col :span="6">
      <el-statistic :value="statisticsData.statistics_upload">
        <template #title>
          <div class="statistic-label">
            数据上传总数
            <el-icon style="margin-left: 4px" :size="12">
              <Upload />
            </el-icon>
          </div>
        </template>
      </el-statistic>
    </el-col>
    <el-col :span="6">
      <el-statistic :value="statisticsData.statistics_download">
        <template #title>
          <div class="statistic-label">
            数据下载总次数
            <el-icon style="margin-left: 4px" :size="12">
              <Download />
            </el-icon>
          </div>
        </template>
      </el-statistic>
    </el-col>
    <el-col :span="6">
      <el-statistic :value="statisticsData.statistics_uploadTurbine">
        <template #title>
          <div class="statistic-label">
            风机上传总数
            <el-icon style="margin-left: 4px" :size="12">
              <WindPower />
            </el-icon>
          </div>
        </template>
      </el-statistic>
    </el-col>
  </el-row>

  <el-divider class="large-divider">

  </el-divider>

  <el-row>
    <el-col :span="8">
      <el-statistic :value="statisticsData.statistics_train">
        <template #title>
          <div class="statistic-label">
             训练模型总数
            <el-icon style="margin-left: 4px" :size="12">
              <Odometer />
            </el-icon>
          </div>
        </template>
      </el-statistic>
    </el-col>
    <el-col :span="8">
      <el-statistic :value="statisticsData.statistics_upload">
        <template #title>
          <div class="statistic-label">
            预测任务下达数
            <el-icon style="margin-left: 4px" :size="12">
              <Finished />
            </el-icon>
          </div>
        </template>
      </el-statistic>
    </el-col>
    <el-col :span="8">
      <el-statistic :value="statisticsData.guestbookNum">
        <template #title>
          <div class="statistic-label">
            系统留言数
            <el-icon style="margin-left: 4px" :size="12">
              <ChatDotSquare />
            </el-icon>
          </div>
        </template>
      </el-statistic>
    </el-col>
  </el-row>

  <el-divider class="large-divider">

  </el-divider>

  <el-row>
    <el-col :span="12">
      <el-statistic :value="displayTime">
        <template #title>
          <div class="statistic-label">
            系统运行总时长
            <el-icon style="margin-left: 4px" :size="12">
              <Clock />
            </el-icon>
          </div>
        </template>
      </el-statistic>
    </el-col>
    <el-col :span="12">
      <el-countdown format="HH:mm:ss" :value="timeToNextDay">
        <template #title>
          <div class="statistic-label">
            今天剩余时间
            <el-icon style="margin-left: 4px" :size="12">
              <Sunset />
            </el-icon>
          </div>
        </template>
      </el-countdown>
      <div class="countdown-footer">{{ dayjs().format('YYYY-MM-DD') }}</div>
    </el-col>
  </el-row>

  <el-divider class="large-divider">
  </el-divider>
  <template v-if="windowsWidth > 1186">
    <el-row>
      <el-col :span="4" :offset="2">
        <el-progress
            type="dashboard"
            :percentage="memoryUsage"
            :color="alt_colors" >
          <template #default="{ percentage }">
            <span class="percentage-value">{{ percentage }}%</span>
            <span class="percentage-label">系统RAM占用率</span>
          </template>
        </el-progress>
      </el-col>
      <el-col :span="4">
        <el-progress
            type="dashboard"
            :percentage="diskUsage"
            :color="alt_colors" >
          <template #default="{ percentage }">
            <span class="percentage-value">{{ percentage }}%</span>
            <span class="percentage-label">系统ROM占用率</span>
          </template>
        </el-progress>
      </el-col>
      <el-col :span="4">
        <el-progress
            type="dashboard"
            :percentage="currentPercentage"
            :color="colors" >
          <template #default="{ percentage }">
            <span class="percentage-value">{{ percentage }}%</span>
            <span class="percentage-label">今日</span>
          </template>
        </el-progress>
      </el-col>
      <el-col :span="4">
        <el-progress
            type="dashboard"
            :percentage="cpuUsage"
            :color="alt_colors" >
          <template #default="{ percentage }">
            <span class="percentage-value">{{ percentage }}%</span>
            <span class="percentage-label">系统CPU占用率</span>
          </template>
        </el-progress>
      </el-col>
      <el-col :span="4">
        <el-progress
            type="dashboard"
            :percentage="gpuUsage"
            :color="alt_colors" >
          <template #default="{ percentage }">
            <span class="percentage-value">{{ percentage }}%</span>
            <span class="percentage-label">系统GPU占用率</span>
          </template>
        </el-progress>
      </el-col>
    </el-row>
  </template>
  <template v-else>
    <el-row>
      <el-col :span="12">
        <el-progress
            type="dashboard"
            :percentage="cpuUsage"
            :color="alt_colors" >
          <template #default="{ percentage }">
            <span class="percentage-value">{{ percentage }}%</span>
            <span class="percentage-label">系统CPU占用率</span>
          </template>
        </el-progress>
      </el-col>
      <el-col :span="12">
        <el-progress
            type="dashboard"
            :percentage="gpuUsage"
            :color="alt_colors" >
          <template #default="{ percentage }">
            <span class="percentage-value">{{ percentage }}%</span>
            <span class="percentage-label">系统GPU占用率</span>
          </template>
        </el-progress>
      </el-col>
      <el-col :span="8">
        <el-progress
            type="dashboard"
            :percentage="memoryUsage"
            :color="alt_colors" >
          <template #default="{ percentage }">
            <span class="percentage-value">{{ percentage }}%</span>
            <span class="percentage-label">系统RAM占用率</span>
          </template>
        </el-progress>
      </el-col>
      <el-col :span="8">
        <el-progress
            type="dashboard"
            :percentage="currentPercentage"
            :color="colors" >
          <template #default="{ percentage }">
            <span class="percentage-value">{{ percentage }}%</span>
            <span class="percentage-label">今日</span>
          </template>
        </el-progress>
      </el-col>
      <el-col :span="8">
        <el-progress
            type="dashboard"
            :percentage="diskUsage"
            :color="alt_colors" >
          <template #default="{ percentage }">
            <span class="percentage-value">{{ percentage }}%</span>
            <span class="percentage-label">系统ROM占用率</span>
          </template>
        </el-progress>
      </el-col>
    </el-row>
  </template>
  <MessageCard />
</template>

<style scoped>
  .large-divider {
    margin-top: 36px;
    margin-bottom: 37px;
  }
  .statistic-label {
    display: inline-flex;
    align-items: center;
  }
  .countdown-footer {
    margin-top: 8px;
  }
  .percentage-value {
    display: block;
    margin-top: 10px;
    font-size: 24px;
  }
  .percentage-label {
    display: block;
    margin-top: 10px;
    font-size: 12px;
  }
  .title {
    font-size: 24px;
    font-weight: bold;
  }
</style>