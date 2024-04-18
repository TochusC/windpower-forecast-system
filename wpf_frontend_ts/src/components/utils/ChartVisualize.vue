<script setup>
import {defineProps, ref, onMounted, onUnmounted} from 'vue'
import * as echarts from 'echarts';

const props = defineProps({
      turbineId: {
        type: String||Number,
        required: true
      },
      isDark: {
        type: Boolean,
        required: true
      }
    }
)
const loading = ref(true)
const dataContent = ref({})
const chartContainer = ref(null)
const chartOption = ref({})
const interval = ref(null)

const getDataContent = () => {
  fetch(`http://127.0.0.1:8000/api/get_realtimePredict/?turbine_id=${props.turbineId}`)
      .then(response => response.json())
      .then(data => {
        dataContent.value = JSON.parse(data);

        for (let key in dataContent.value) {
          dataContent.value[key] = Object.values(dataContent.value[key])
          if(key === 'DATATIME'){
            continue
          }
          dataContent.value[key].map((item, index) => {
            return dataContent.value[key][index] = parseFloat(item.toFixed(2))
          })
        }
        if(chartContainer.value){
          initialChart()
          refreshChart()
        }
        loading.value = false
      })
}
var chart
const requireInit = ref(true)
const previousIsDark = ref(props.isDark)
const initialChart = () => {
  if (previousIsDark.value !== props.isDark){
    chart.dispose()
    requireInit.value = true
    previousIsDark.value = props.isDark
  }
  if (requireInit.value){
    if (props.isDark){
      chart = echarts.init(chartContainer.value,'dark' );
    }
    else{
      chart = echarts.init(chartContainer.value);
    }
    requireInit.value = false
  }
}


const refreshChart = () =>{
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
  for (let key in dataContent.value) {
    if (key === 'DATATIME'){
      chartOption.value.xAxis.data = dataContent.value[key]
    }
    else{
      chartOption.value.series.push({
        name: key,
        type: 'line',
        symbol: 'none',
        data: dataContent.value[key],
      })
      chartOption.value.legend.data.push(key)
    }
  }
  chart.setOption(chartOption.value);
}
const resizeHandler = () => {
  if(chart){
    chart.resize();
  }
}

onMounted(() => {
  window.addEventListener('resize', resizeHandler);
  interval.value = setInterval(getDataContent, 1000)
})

onUnmounted(() => {
  clearInterval(interval.value)
  if(chart)
    chart.dispose()
  window.removeEventListener('resize', resizeHandler);
})
</script>
<template
  v-loading="loading"
>
  <div
      v-loading="loading"
      element-loading-text="准备中...^ ^"
      ref="chartContainer"
       style="width: 100%;
       height: 360px;
       margin-bottom: 0
        "
  >
  </div>
</template>

<style scoped>
</style>