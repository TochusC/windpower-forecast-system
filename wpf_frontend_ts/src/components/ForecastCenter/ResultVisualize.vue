<script setup>
import {defineProps, ref} from 'vue'
import * as echarts from 'echarts';
import {ElLoading} from "element-plus";

const props = defineProps({
  forecastTask: {
    type: Object,
    required: true
  },
  isDark: {
    type: Boolean,
    required: true
  }
}
)

const dataContent = ref({})

const startTime = ref('')
const endTime = ref('')
const startRange = ref('')
const endRange = ref('')

const timeRange = ref([])
const chartContainer = ref(null)
const chartOption = ref({})

const tableColumns = ref([])
const tableData = ref([])
const tableWidth = ref(window.innerWidth * 0.84)
const tableHeight = ref(640)


const resizeTable = () => {
  let widowWidth = window.innerWidth
  tableWidth.value = widowWidth * 0.84
}

const disabledDate = (time) => {
  return time.getTime() < new Date(startTime.value).getTime() || time.getTime() > new Date(endTime.value).getTime()
}

const handleTimeRangeChange = (value) => {
  if (value === null) {
    return
  }
  startRange.value = value[0]
  endRange.value = value[1]
  refreshChart()
}

const getDataContent = () => {
  const loading = ElLoading.service({
    lock: true,
    text: '准备中...^ ^',
  })
  fetch(`http://127.0.0.1:8000/api/get_dataContent/?data_id=${props.forecastTask.result_id}`)
      .then(response => response.json())
      .then(data => {
        dataContent.value = JSON.parse(data);

        for (let key in dataContent.value) {
          dataContent.value[key] = Object.values(dataContent.value[key])
          if(key === 'TurbID' || key === 'DATATIME'){
            continue
          }
          dataContent.value[key].map((item, index) => {
            return dataContent.value[key][index] = parseFloat(item.toFixed(2))
          })
        }

        startTime.value = dataContent.value.DATATIME[0]
        endTime.value = dataContent.value.DATATIME[dataContent.value.DATATIME.length - 1]

        startRange.value = new Date(dataContent.value.DATATIME[0])
        endRange.value = new Date(new Date(startTime.value).getTime() + 86400000 * 7)

        timeRange.value = [startRange.value, endRange.value]

        initialChart()

        refreshChart()
      }).then(() => {
    loading.close();
  })
}
var chart
const chartResizeHandler = () => {
  if(chart){
    chart.resize();
    chart.setOption(chartOption.value)
  }
}
const tableResizeHandler = () => {
  resizeTable()
}
const initialChart = () => {
  if (props.isDark){
    chart = echarts.init(chartContainer.value,'dark' );
  }
  else{
    chart = echarts.init(chartContainer.value);
  }

  window.addEventListener('resize', chartResizeHandler);
  window.addEventListener('resize', tableResizeHandler);
}

const convertToTableData = (data) => {
  let tableData = []

  for(let i = 0; i < data.DATATIME.length; i++){
    let dataObject = {}
    for (let key in data) {
      dataObject[key] = data[key][i]
    }
    dataObject["id"] = i
    dataObject["parentId"] = null
    tableData.push(dataObject)
  }
  return tableData
}

const refreshChart = () =>{
  let targetData = {}
  tableColumns.value = []

  for(let key in dataContent.value){
    targetData[key] = []
    if(key === 'TurbID' || key === 'ROUND(A.POWER,0)'){
      continue
    }
    if (key === 'DATATIME'){
      tableColumns.value.push({
        title: key,
        dataKey: key,
        key: key,
        width: 160,
      })
    }
    else{
      tableColumns.value.push({
        title: key,
        dataKey: key,
        key: key,
        width: 150,
      })
    }
  }

  let index = 0
  for (let i = 0; i < dataContent.value.DATATIME.length; i++) {
    if (new Date(dataContent.value.DATATIME[i]) >= startRange.value) {
      index = i
      break
    }
  }
  for (let i = index; i < dataContent.value.DATATIME.length; i++) {
    for(let key in dataContent.value){
      targetData[key].push(dataContent.value[key][i])
    }
    if (new Date(dataContent.value.DATATIME[i]) > endRange.value) {
      break
    }
  }
  chartOption.value = {
    backgroundColor: '#2c343c00',
    tooltip: {
      trigger: 'axis',
      textStyle: {
        align: 'left'
      }
    },
    toolbox: {
      show: true,
      feature: {
        restore: {},
        saveAsImage: {}
      }
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100,
      },
      {
        start: 0,
        end: 100,
      }
    ],
    legend: {
      data: []
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: []
    },
    yAxis: {
      type: 'value',
    },
    series: []
  }

  for (let key in targetData) {
    if(key === 'TurbID' || key === 'ROUND(A.POWER,0)'){
      continue
    }
    if (key === 'DATATIME'){
      chartOption.value.xAxis.data = targetData[key]
    }
    else{
      chartOption.value.series.push({
        name: key,
        type: 'line',
        symbol: 'none',
        symbolSize: 8,
        data: targetData[key],
      })
      chartOption.value.legend.data.push(key)
    }
  }
  chart.setOption(chartOption.value);
  tableData.value = convertToTableData(targetData)
}

const handleClose = () => {
  window.removeEventListener('resize', chartResizeHandler);
  window.removeEventListener('resize', tableResizeHandler);
  if(chart){
    chart.dispose()
  }
}

</script>

<template>
  <el-drawer
      direction="rtl"
      size="90%"
      @open="getDataContent"
      @close="handleClose"
  >
    <el-divider>
      <h3>预测任务详情</h3>
    </el-divider>
    <div class="taskInfo">
      <span>预测风机：{{forecastTask.turbine_id}}</span>
      <el-divider direction="vertical"/>
      <span>预测数据：{{forecastTask.data_name}}</span>
      <el-divider direction="vertical"/>
      <span>模型类型：{{forecastTask.model_type}}</span>
      <el-divider direction="vertical"/>
      <span>完成时间：{{forecastTask.task_finishTime}}</span>
      <el-divider direction="vertical"/>
      <span>起始时间：{{forecastTask.task_startTime}}</span>
      <el-divider direction="vertical"/>
      <span>结束时间：{{forecastTask.task_endTime}}</span>
    </div>
    <el-divider>
      数据可视化
    </el-divider>
    <el-date-picker
        v-model="timeRange"
        type="datetimerange"
        range-separator="至"
        unlink-panels
        :default-value="[new Date(startTime), new Date(endTime)]"
        @change="handleTimeRangeChange"
        start-placeholder="起始日期"
        end-placeholder="截止日期"
        :disabled-date="disabledDate"
        style="margin-bottom: 32px"
    />
    <div ref="chartContainer" style="width: 100%; height: 72%;"></div>
    <el-divider>
      数据表格
    </el-divider>
    <el-table-v2
        :columns="tableColumns"
        :data="tableData"
        :width="tableWidth"
        :height="tableHeight"
        fixed
    />
  </el-drawer>
</template>

<style scoped>
el-container {
  margin-bottom: 128px;
  height: 100%;
  width: 100%;
}
.taskInfo {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>