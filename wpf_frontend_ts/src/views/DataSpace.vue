<template>
  <div class="centerFlex">
    <span style="margin-left: 24px">
      <el-text class="title">数据空间</el-text>
    </span>
    <span style="margin-right: 24px">
       <el-button
         style="width: 128px"
         type="success"
         @click="addData = true">
        上传数据
      </el-button>
    </span>
  </div>
  <el-divider style="margin-top: 16px"></el-divider>
  <div>
    <DataCard
        :data-list="data_list"
        @removeData="getData"
        :isDark="props.isDark"
    />
  </div>
  <UploadData
      v-model="addData"
      @closeDialog="addData = false"
      @uploadSuccess="handleSuccess"/>
</template>


<script setup>
import {onMounted, ref, defineProps} from 'vue'
import {ElNotification} from "element-plus";
import DataCard from "@/components/DataSpace/DataCard.vue";
import UploadData from "@/components/DataSpace/UploadData.vue";


const data_list = ref([])
const addData = ref(false)

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

const assembleData = (data) => {
  data_list.value = []
  let index = "1";
  for (index in data) {
    let dataDict = {};
    dataDict = data[index].fields;
    dataDict["data_id"] = data[index].pk
    dataDict["delete_visible"] = false;
    data_list.value.push(dataDict);
  }
}
const getData = (turbine_id) => {
  if (turbine_id === undefined){
    turbine_id = "all"
  }
  fetch(`http://127.0.0.1:8000/api/get_turbineData/?turbine_id=${turbine_id}`)
      .then(response => {
        return response.json()
      })
      .then((data) => {
        assembleData(data)
      })
      .catch(e => console.log("Oops, error", e))
}
const handleSuccess = () => {
  ElNotification({
    title: '成功',
    message: '数据上传成功',
    type: 'success',
  })
  getData("all")
  addData.value = false
}

onMounted(() => {
  getData("all")
})


</script>

<style scoped>
.title {
  font-size: 24px;
  font-weight: bold;
}
</style>
