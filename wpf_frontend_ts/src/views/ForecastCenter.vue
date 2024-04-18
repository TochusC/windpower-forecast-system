<script setup>
import AddForecastTask from "@/components/ForecastCenter/AddForecastTask.vue";
import { ref, onMounted, defineProps } from 'vue';
import ForecastTaskCard from "@/components/ForecastCenter/ForecastTaskCard.vue";
import {ElNotification} from "element-plus";

const addForecastTask = ref(false)

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

onMounted(() => {
  getForecastTask(null, "all", "all")
})


const forecastTask_Dict = ref({})

const assembleForecastTask = (data) => {
  forecastTask_Dict.value = {}
  for(let index in data) {
    let forecastTask = {};
    forecastTask = data[index].fields;
    forecastTask["task_id"] = data[index].pk;
    forecastTask["delete_visible"] = false;
    forecastTask_Dict.value[forecastTask["task_id"]] = forecastTask;
  }
}


const getForecastTask = (event=null, turbine_id="all", task_id="all") =>{
  fetch(`http://127.0.0.1:8000/api/get_forecastTask/?turbine_id=${turbine_id}&task_id=${task_id}`, {
  }).then((response) => {
    return response.json()
  }).then((data) => {
    assembleForecastTask(data)
  }).catch((e) => {
    console.log("Oops, error", e)
  })
}

const updateTaskStatus = (task_id) => {
  fetch(`http://127.0.0.1:8000/api/get_forecastTask/?turbine_id=all&task_id=${task_id}`, {
  }).then((response) => {
    return response.json()
  }).then((data) => {
    for(let index in data) {
      forecastTask_Dict.value[task_id]["task_status"] = data[index].fields["task_status"]
    }
  }).catch((e) => {
    console.log("Oops, error", e)
  })
}

const updateTask = (task_id) => {
  fetch(`http://127.0.0.1:8000/api/get_forecastTask/?turbine_id=all&task_id=${task_id}`, {
  }).then((response) => {
    return response.json()
  }).then((data) => {
    for(let index in data) {
      let forecastTask = {};
      forecastTask = data[index].fields;
      forecastTask["task_id"] = data[index].pk;
      forecastTask["delete_visible"] = false;
      forecastTask_Dict.value[forecastTask["task_id"]] = forecastTask;
    }
  }).catch((e) => {
    console.log("Oops, error", e)
  })
}


const startForecastTask = (task_id) =>{
  let formData = new FormData();
  formData.append("task_id", task_id);

  let intervalId = setInterval(updateTaskStatus, 1000, task_id)

  fetch('http://127.0.0.1:8000/api/start_forecastTask/', {
    method: 'POST',
    body: formData
  }).then((response) => {
    return response.json()
  }).then((data) => {
    if (data.status === "success") {
      ElNotification({
        title: '成功',
        message: '预测任务完成',
        type: 'success'
      });
    } else {
      ElNotification({
        title: '失败',
        message: '预测任务失败',
        type: 'error'
      });
    }
    clearInterval(intervalId)
    updateTask(task_id)
  }).catch((e) => {
    console.log("Oops, error", e)
  })
}
</script>

<template>
  <div class="centerFlex">
    <span style="margin-left: 24px">
      <el-text class="title">预测中心</el-text>
    </span>
    <span style="margin-right: 24px">
      <el-button
        style="width: 128px"
        type="success"
        @click="addForecastTask = true">
        新建预测任务
      </el-button>
    </span>
  </div>
  <el-divider style="margin-top: 16px"></el-divider>
  <ForecastTaskCard
      @refreshForecastTaskList="getForecastTask(null, 'all', 'all')"
      @startForecastTask="startForecastTask"
      :forecast_task_dict="forecastTask_Dict"
      :isDark="props.isDark"
  />
  <AddForecastTask
      v-model="addForecastTask"
      @refreshTaskList="getForecastTask(null, 'all', 'all')"
      @closeDialog="addForecastTask = false"/>
</template>

<style scoped>
.title {
  font-size: 24px;
  font-weight: bold;
}
</style>