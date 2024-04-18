<script setup>
import {defineProps, defineEmits, ref, onMounted, onUnmounted} from "vue";
import * as echarts from 'echarts'

const props = defineProps({
  dataContent: {
    type: Object,
    required: true
  },
  requireRefresh: {
    type: Boolean,
    required: true
  }
})

const emits = defineEmits([
  'refreshChart'
])

const isloading = ref(true)
const chartContainer = ref(null)
const interval = ref(null)

const chartOption = {
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
  yAxis: [],
  series: []
}
var chart

onMounted(() => {
  if(chartContainer.value){
    chart = echarts.init(chartContainer.value);
  }
  interval.value = setInterval(() => {
    isloading.value = true

  }, 1000)
})

onUnmounted(() => {
  if(chart){
    chart.dispose()
    clearInterval(interval.value)
  }
})
</script>

<template>
  <div
  />
</template>

<style scoped>

</style>