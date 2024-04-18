<template>
  <div class="centerFlex">
    <span style="margin-left: 24px">
      <el-text class="title">风机列表</el-text>
    </span>
    <span style="margin-right: 24px">
            <el-button
                  style="width: 128px"
                  type="success"
                  @click="addTurbine = true">
          上传风机信息
        </el-button>
    </span>
  </div>
  <el-divider style="margin-top: 16px"></el-divider>
    <div>
    <TurbineCard
        :turbines="turbines"
        :is-dark="props.isDark"
        @removeTurbine="getTurbine"
    />
    </div>
    <UploadTurbine
        v-model="addTurbine"
        @closeDialog="addTurbine = false"
        @uploadSuccess="handleSuccess"
    />
</template>


<script setup>
  import {onMounted, ref, defineProps} from 'vue'
  import TurbineCard from "@/components/TurbineList/TurbineCard.vue";
  import UploadTurbine from "@/components/TurbineList/UploadTurbine.vue";
  import {ElNotification} from "element-plus";


  const turbines = ref([])

  const addTurbine = ref(false)

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
  const handleSuccess = () => {
    ElNotification({
      title: '成功',
      message: '风机上传成功',
      type: 'success',
    })
    getTurbine()
    addTurbine.value = false
  }
  onMounted(() => {
    getTurbine()
  })


</script>

<style scoped>
.el-row {
  margin-bottom: 16px;
}
.title {
  font-size: 24px;
  font-weight: bold;
}
</style>
