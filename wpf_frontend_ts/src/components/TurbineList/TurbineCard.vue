<template>
  <el-empty v-if="props.turbines.length===0" description="暂无数据" />
  <el-card class="box-card"  v-for="turbine in props.turbines" :key="turbine.turbine_id">
    <template #header>
      <div class="card-header">
        <span>
          <span class="card-header">
            <span class="card-header"
                  style="margin-right: 28px"
            >
              <el-icon>
                <img
                    src="../../assets/static/img/turbine_icon.png"
                    style="height: 42px;"
                />
              </el-icon>
            </span>
            <span>
              <el-icon>
                <WindPower />
              </el-icon>
              {{turbine.turbine_name}}
            </span>
          </span>
        </span>
        <div>
          <el-button
              size="small"
              type="primary"
              @click="addForecastTask=true;
              currentTurbine=turbine.turbine_id"
          >
            下达预测任务</el-button>
          <el-popover :visible="turbine.delete_visible" placement="top" :width="160">
            <p>确定删除风机？</p><p>风机的所有数据及模型将被清除。</p>
            <div style="text-align: right; margin: 0">
              <el-button size="small"  @click="turbine.delete_visible = false">取消</el-button>
              <el-button size="small" type="danger" @click="removeTurbine(turbine.turbine_id); turbine.delete_visible = false"
              >确定</el-button
              >
            </div>
            <template #reference>
              <el-button size="small" @click="turbine.delete_visible = true">删除风机</el-button>
            </template>
          </el-popover>
        </div>
      </div>
    </template>
    <div style="text-align: left">
      <span class="text-item">风机号：{{turbine.turbine_id}}</span>
      <el-divider direction="vertical"/>

      <span class="text-item">风机备注：{{turbine.turbine_comment}}</span>
      <el-divider direction="vertical"/>
      <span>
        <span class="text-item" style="margin-right:0; ">风机状态：</span>
        <el-tag class="ml-2" type="success">正常</el-tag>
      </span>
      <el-divider direction="vertical"/>
      <span>
        <span class="text-item" style="margin-right:0; ">风机模型：</span>
        <template v-if="turbine.turbine_id in turbineModelDict">
          <ModelTypeTag
              v-if="turbineModelDict[turbine.turbine_id]['MLP']"
              model-type="MLP"
              :model-status="turbineModelDict[turbine.turbine_id]['MLP']['model_status']"
          />
          <ModelTypeTag
              v-if="turbineModelDict[turbine.turbine_id]['GCN+LSTM']"
              model-type="GCN+LSTM"
              :model-status="turbineModelDict[turbine.turbine_id]['GCN+LSTM']['model_status']"
          />
          <ModelTypeTag
              v-if="turbineModelDict[turbine.turbine_id]['GCN+LSTM+MLP']"
              model-type="GCN+LSTM+MLP"
              :model-status="turbineModelDict[turbine.turbine_id]['GCN+LSTM+MLP']['model_status']"
          />
        </template>
      </span>
    </div>
    <el-divider>
      <el-popover
          trigger="hover"
          title="实时功率预测"
          width="240"
      >
        <template #reference>
          <el-switch
              v-model="realtimeForecast[turbine.turbine_id]"
              :is-loading="realtimeChangeLoading[turbine.turbine_id]"
              inline-prompt
              :before-change="()=>{
                realtimeChangeLoading[turbine.turbine_id]= false
                if(turbine.turbine_id in turbineModelDict){
                  realtimeChangeLoading[turbine.turbine_id]= true
                  if(turbineModelDict[turbine.turbine_id]['MLP']['model_status'] === '准备就绪') {
                    realtimeChangeLoading[turbine.turbine_id]= false
                    return true
                  }
                  else {
                    ElMessage({
                      message: '该风机无训练完成的MLP模型，无法开启实时预测',
                      type: 'warning'
                    });
                    realtimeChangeLoading[turbine.turbine_id]= false
                    return false
                  }
                }
                ElMessage({
                    message: '该风机无训练完成的MLP模型，无法开启实时预测',
                    type: 'warning'
                  });
                realtimeChangeLoading[turbine.turbine_id]= false
                return false
              }"
              active-text="24小时实时功率预测"
              inactive-text="关闭实时预测"
          />
        </template>
        <p>在当前时间点，根据未来24小时的天气预报数据，预测风机功率。</p>
        <span style="margin-right: 4px">该功能需要风机具有</span>
        <ModelTypeTag
            v-if=" turbine.turbine_id in turbineModelDict && 'MLP' in turbineModelDict[turbine.turbine_id]"
            model-type="MLP"
            :model-status="turbineModelDict[turbine.turbine_id]['MLP']['model_status']"
        />
        <ModelTypeTag
            v-else
            model-type="MLP"
            model-status="未添加"
        />
        <span>模型</span>
      </el-popover>
    </el-divider>
    <div class="card-header" v-if="realtimeForecast[turbine.turbine_id]">
      <ChartVisualize
          :is-dark="props.isDark"
          :turbine-id="turbine.turbine_id"
      />
    </div>
  </el-card>
  <AddForecastTask
      v-model="addForecastTask"
      :turbine_id="currentTurbine"
      @closeDialog="addForecastTask = false"/>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.text-item{
  margin-right: 18px;
}
.box-card {
  margin-bottom: 32px;
}
</style>

<script setup>
import {defineProps, defineEmits, ref, onMounted} from 'vue'
import {WindPower} from "@element-plus/icons-vue";
import {ElMessage, ElNotification} from "element-plus";
import ModelTypeTag from "@/components/utils/ModelTypeTag.vue";
import AddForecastTask from "@/components/ForecastCenter/AddForecastTask.vue";
import ChartVisualize from "@/components/utils/ChartVisualize.vue";

const currentTurbine = ref("")
const addForecastTask = ref(false)
const emit = defineEmits(['removeTurbine'])
const realtimeForecast = ref({})
const realtimeChangeLoading = ref({})

const props = defineProps(
    {
      turbines: {
        type: Array,
        required: true
      },
      isDark: {
        type: Boolean,
        required: true
      }
    }
)

const checkRealtimeForecast = ref([])

const removeTurbine = (turbine_id) => {
  let formData = new FormData();
  formData.append('turbine_id', turbine_id);
  fetch('http://localhost:8000/api/delete_turbine/', {
    method: 'POST',
    body: formData
  }).then(response => response.json())
    .then(data => {
        if (data.status === "success")
          ElNotification({
            title: '成功',
            message: '风机删除成功',
            type: 'success',
          });
          emit('removeTurbine');
      })
}

const turbineModelDict = ref({})
const assembleModel = (data) => {
  for(let index in data) {
    let forecastModel = {};
    forecastModel = data[index].fields;
    if (!(forecastModel.turbine_id in turbineModelDict.value))
      turbineModelDict.value[forecastModel.turbine_id] = {};
    if (!(forecastModel.model_type in turbineModelDict.value[forecastModel.turbine_id]))
      turbineModelDict.value[forecastModel.turbine_id][forecastModel.model_type] = {};
    if (turbineModelDict.value[forecastModel.turbine_id][forecastModel.model_type]["model_status"] !== "准备就绪")
      turbineModelDict.value[forecastModel.turbine_id][forecastModel.model_type]["model_status"] = forecastModel.model_status;
  }
  for(let key in turbineModelDict.value){
    if(turbineModelDict.value[key]['MLP']["model_status"] === "准备就绪"){
      realtimeForecast.value[key] = true
    }
    else {
      realtimeForecast.value[key] = false
    }
  }
}
const getForecastModel = (event, turbine_id="all", model_id="all") => {

  fetch(`http://127.0.0.1:8000/api/get_forecastModel/?turbine_id=${turbine_id}&model_id=${model_id}`, {
  }).then((response) => {
    return response.json()
  }).then((data) => {
    assembleModel(data)
  }).catch((e) => {
    console.log("Oops, error", e)
  })
}

onMounted(() => {
  getForecastModel(null, "all")
  for(let index in props.turbines){
    let turbineId = props.turbines[index].turbine_id

    realtimeChangeLoading.value[turbineId] = false
    checkRealtimeForecast.value[turbineId] = () => {
      console.log(turbineModelDict.value[turbineId]['MLP']['model_status'])
      realtimeChangeLoading.value[turbineId ]= true
      if(turbineModelDict.value[turbineId]['MLP']['model_status'] === '准备就绪') {
        realtimeChangeLoading.value[turbineId]= false
        return true
      }
      else {
        ElMessage({
          message: '该风机无训练完成的MLP模型，无法开启实时预测',
          type: 'warning'
        });
        realtimeChangeLoading.value[turbineId]= false
        return false
      }
    }
  }
})
</script>