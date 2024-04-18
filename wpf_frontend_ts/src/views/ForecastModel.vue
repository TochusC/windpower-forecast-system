<script setup>
import {defineProps, onMounted, ref} from "vue";
import ModelCard from "@/components/ForecastModel/ModelCard.vue";


const turbines = ref([])

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
const assembleTurbine = (data) => {
  turbines.value = []
  let turbineModel = "1";
  for (turbineModel in data) {
    let turbine = {};
    turbine["turbine_name"] = data[turbineModel].fields.turbine_name;
    turbine["turbine_id"] = data[turbineModel].pk
    turbine["turbine_comment"] = data[turbineModel].fields.turbine_comment;
    turbine["status"] = data[turbineModel].fields.turbine_status;
    turbine["delete_visible"] = false;
    turbines.value.push(turbine);
  }
}


const getTurbine = () => {
  fetch('http://127.0.0.1:8000/api/get_turbine/')
      .then(response => {
        return response.json()
      })
      .then((data) => {
        assembleTurbine(data)
      })
      .catch(e => console.log("Oops, error", e))
}

onMounted(() => {
  getTurbine()
})
</script>

<template>
  <div class="centerFlex">
    <span style="margin-left: 24px">
      <el-text class="title">模型列表</el-text>
    </span>
  </div>
  <el-divider style="margin-top: 16px"></el-divider>
  <ModelCard
      :turbines="turbines"
  />
</template>

<style scoped>
.title {
  font-size: 24px;
  font-weight: bold;
}
</style>