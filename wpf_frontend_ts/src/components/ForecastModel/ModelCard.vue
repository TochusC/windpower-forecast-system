<script setup>
import {CircleCheck, Loading, Warning, WarningFilled, WindPower} from "@element-plus/icons-vue";
import {defineProps, ref, onMounted} from "vue";
import UploadModel from "@/components/ForecastModel/UploadModel.vue";
import AddForecastTask from "@/components/ForecastCenter/AddForecastTask.vue";
import {ElNotification} from "element-plus";

const props = defineProps(
    {
      turbines: {
        type: Array,
        required: true
      }
    }
)

const addModel = ref(false)
const turbine_now = ref("")
const turbineModelDict = ref({})

const currentTurbine = ref("")
const currentModel = ref("")
const addForecastTask = ref(false)

const assembleModel = (data) => {
  for(let index in data) {
    let forecastModel = {};
    forecastModel = data[index].fields;
    forecastModel["model_id"] = data[index].pk;
    forecastModel["delete_visible"] = false;
    if(forecastModel.turbine_id in turbineModelDict.value){
      turbineModelDict.value[forecastModel.turbine_id].push(forecastModel)
    }else{
      turbineModelDict.value[forecastModel.turbine_id] = [forecastModel]
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
const deleteModel = (event, turbine_id, model_id) => {
  let formData = new FormData();
  formData.append("model_id", model_id);
  fetch('http://127.0.0.1:8000/api/delete_forecastModel/', {
    method: 'POST',
    body: formData
  }).then((response) => {
    return response.json()
  }).then((data) => {
    if (data.status === "success") {
      ElNotification({
        title: '成功',
        message: '模型删除成功',
        type: 'success'
      });
    } else {
      ElNotification({
        title: '失败',
        message: '模型删除失败',
        type: 'error'
      });
    }
    turbineModelDict.value[turbine_id] = []
    getForecastModel(null, turbine_id, "all")
  }).catch((e) => {
    console.log("Oops, error", e)
  })
}
const updateTurbineModel = (turbine_id, model_id) => {
  fetch(`http://127.0.0.1:8000/api/get_forecastModel/?turbine_id=${turbine_id}&model_id=${model_id}`, {
  }).then((response) => {
    return response.json()
  }).then((data) => {
    for(let index in data) {
      for(let turbineModel in turbineModelDict.value[turbine_id]){
        if(turbineModelDict.value[turbine_id][turbineModel].model_id === data[index].pk){
          turbineModelDict.value[turbine_id][turbineModel]["model_status"] = data[index].fields["model_status"]
        }
      }
    }
  }).catch((e) => {
    console.log("Oops, error", e)
  })
}

const trainModel = (event, turbine_id, model_id) =>{
  let formData = new FormData();
  formData.append("model_id", model_id);

  let intervalId = setInterval(updateTurbineModel, 1000, turbine_id, model_id)

  fetch('http://127.0.0.1:8000/api/train_forecastModel/', {
    method: 'POST',
    body: formData
  }).then((response) => {
    return response.json()
  }).then((data) => {
    if (data.status === "success") {
      ElNotification({
        title: '成功',
        message: '模型训练完成',
        type: 'success'
      });
    } else {
      ElNotification({
        title: '失败',
        message: '模型训练失败',
        type: 'error'
      });
    }
    clearInterval(intervalId)
    updateModel(null, turbine_id)
  }).catch((e) => {
    console.log("Oops, error", e)
  })
}

const updateModel = (event, turbine_id) => {
  turbineModelDict.value[turbine_id] = []
  getForecastModel(null, turbine_id, "all")
}

onMounted(() => {
  getForecastModel(null, "all")
})

const trainDataList = ref([])
const modelData = ref([])

const assembleData = (data) => {
  trainDataList.value = []
  for(let index in data) {
    let dataModel = {};
    dataModel = data[index].fields;
    dataModel["data_id"] = data[index].pk;
    dataModel["delete_visible"] = false;
    trainDataList.value.push(dataModel);
  }
}
const getTrainData = (event, turbine_id="all", data_type="train") => {
  fetch(`http://127.0.0.1:8000/api/get_turbineData/?turbine_id=${turbine_id}&data_type=${data_type}`, {
  }).then((response) => {
    return response.json()
  }).then((data) => {
    assembleData(data)
  }).catch((e) => {
    console.log("Oops, error", e)
  })
}
const handleChange = (val) => {
  modelData.value = val;
  console.log(modelData.value)
}
const selectAndTrain = (turbine_id, model_id)=>{
  let formData = new FormData();

  let model_data_string = ""
  for(let index in modelData.value){
    model_data_string += modelData.value[index].data_id + ","
  }

  formData.append("model_data", model_data_string);
  formData.append("model_id", model_id);

  fetch(`http://127.0.0.1:8000/api/alter_forecastModel/`, {
    method: 'POST',
    body: formData
  }).then((response) => {
    return response.json()
  }).then((data) => {
    if (data.status === "success") {
      trainModel(null, turbine_id, model_id)
    }
  }).catch((e) => {
    console.log("Oops, error", e)
  })
}

</script>

<template>
  <el-card
      class="box-card"
      v-for="turbine in props.turbines"
      :key="turbine.turbine_id">
    <template #header>
      <div class="card-header">
        <div>
          <span style="margin-right: 32px">
            <el-icon><WindPower /></el-icon>
            {{turbine.turbine_name}}
          </span>
          <el-tag type="info">
            风机号：{{turbine.turbine_id}}
          </el-tag>
        </div>
        <div>
          <el-button
              size="small"
              type="success"
              @click="
              turbine_now=turbine.turbine_id;
              addModel=true;
              "
          >添加预测模型</el-button>
        </div>
      </div>
    </template>
    <div style="text-align: left">
        <el-table
            :data="turbineModelDict[turbine.turbine_id]"
        >
          <el-table-column label="模型类型">
            <template #default="scope">
                <el-popover
                    v-if="scope.row.model_type === 'MLP'"
                    placement="top-start"
                    title="MLP模型"
                    :width="200"
                    trigger="hover"
                    content="仅需要未来天气预报数据即可进行预测"
                >
                  <template #reference>
                    <div style="display: flex; align-items: center">
                      <span style="margin-left: 10px">{{ scope.row.model_type }}</span>
                    </div>
                  </template>
                </el-popover>
              <el-popover
                  v-if="scope.row.model_type === 'GCN+LSTM'"
                  placement="top-start"
                  title="GCN+LSTM模型"
                  :width="200"
                  trigger="hover"
                  content="仅需要风机24小时前的历史数据即可进行预测"
              >
                <template #reference>
                  <div style="display: flex; align-items: center">
                    <span style="margin-left: 10px">{{ scope.row.model_type }}</span>
                  </div>
                </template>
              </el-popover>
              <el-popover
                  v-if="scope.row.model_type === 'GCN+LSTM+MLP'"
                  placement="top-start"
                  title="GCN+LSTM+MLP模型"
                  :width="200"
                  trigger="hover"
                  content="综合风机24小时前的历史数据和未来天气预报数据以进行预测"
              >
                <template #reference>
                  <div style="display: flex; align-items: center">
                    <span style="margin-left: 10px">{{ scope.row.model_type }}</span>
                  </div>
                </template>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column label="模型大小">
            <template #default="scope">
              <div style="display: flex; align-items: center">
                <span style="margin-left: 10px">{{ scope.row.model_size }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="模型状态">
            <template #default="scope">
              <div style="display: flex; align-items: center">
                <el-tag
                    v-if="scope.row.model_status === '待训练'"
                    type="warning"
                >
                `<span style="margin-left: 10px">{{ scope.row.model_status }}</span>
                  <el-icon><Warning /></el-icon>
                </el-tag>
                <el-tag
                    v-else-if="scope.row.model_status === '准备就绪'"
                    type="success">
                  <span style="margin-left: 10px">{{ scope.row.model_status }}</span>
                  <el-icon color="#67C23A"><CircleCheck /></el-icon>
                </el-tag>
                <el-tag
                    v-else-if="scope.row.model_status === '未选择数据'"
                    type="warning"
                >
                  <span style="margin-left: 10px">{{ scope.row.model_status }}</span>
                  <el-icon><Warning /></el-icon>
                </el-tag>
                <el-tag v-else>
                  <span style="margin-left: 10px">{{ scope.row.model_status }}</span>
                  <el-icon color="#409EFF" class="is-loading"
                  ><Loading /></el-icon>
                </el-tag>
              </div>

            </template>
          </el-table-column>
          <el-table-column label="模型备注">
            <template #default="scope">
              <div style="display: flex; align-items: center">
                <span style="margin-left: 10px">{{ scope.row.model_comment }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="训练时间">
            <template #default="scope">
              <div style="display: flex; align-items: center">
                <span style="margin-left: 10px">{{ scope.row.model_trainTime }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="135">
            <template #default="scope">
              <div v-if="scope.row.model_status.slice(0,3) === '训练中'">
                <el-progress :percentage="parseInt(scope.row.model_status.slice(scope.row.model_status.indexOf('...')+3,
                scope.row.model_status.indexOf('%')))" />
              </div>
              <template v-else>
                <el-button
                    v-if="scope.row.model_status === '准备就绪'"
                    size="small"
                    type="primary"
                    @click="
                    currentTurbine = scope.row.turbine_id;
                    currentModel = scope.row.model_id;
                    addForecastTask = true;">
                  预测
                </el-button>
                <template v-else>
                  <el-button
                      v-if="scope.row.model_status === '待训练'"
                      size="small"
                      type="primary"
                      @click="trainModel(null, scope.row.turbine_id, scope.row.model_id)"
                  >训练
                  </el-button>
                  <el-popover
                      v-else
                      placement="left"
                      :width="420"
                      trigger="click"
                  >
                    <template #reference>
                      <el-button
                          size="small"
                          type="primary"
                          @click="getTrainData(null, scope.row.turbine_id, 'train')"
                      >训练
                      </el-button>
                    </template>
                    <el-divider>选择训练数据</el-divider>
                    <el-table
                        :data="trainDataList"
                        :default-sort="{ prop: 'date_uploadTime', order: 'descending' }"
                        highlight-current-row
                        style="width: 100%; font-size: 4px"
                        @selection-change="handleChange"
                    >
                      <el-table-column type="selection" width="55" />
                      <el-table-column property="data_name" width="120" label="数据名称"></el-table-column>
                      <el-table-column property="data_comment" width="120" label="数据备注"></el-table-column>
                      <el-table-column property="data_startTime" width="160" label="起始时间"></el-table-column>
                      <el-table-column property="data_endTime" width="160" label="结束时间"></el-table-column>
                      <el-table-column property="data_size" label="数据大小" width="120" />
                      <el-table-column property="data_uploadTime" width="160" label="上传时间" sortable></el-table-column>
                    </el-table>
                    <el-button
                        style="
                        margin-top: 12px;
                        float: right"
                        size="small"
                        type="primary"
                        @click="selectAndTrain(scope.row.turbine_id, scope.row.model_id)"
                    >开始训练！
                    </el-button>
                  </el-popover>
                </template>
                <el-popconfirm
                    title="您确定删除此模型? "
                    :icon="WarningFilled"
                    confirm-button-text="确认"
                    cancel-button-text="取消"
                    @confirm="deleteModel(null,scope.row.turbine_id, scope.row.model_id)"
                >
                  <template #reference>
                    <el-button
                        size="small"
                        type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </template>
          </el-table-column>
        </el-table>
    </div>
  </el-card>
  <UploadModel
      v-model="addModel"
      :turbine_id="turbine_now"
      @closeDialog="addModel=false"
      @uploadSuccess="updateModel(null, turbine_now)"
  />
  <AddForecastTask
      v-model="addForecastTask"
      :turbine_id="currentTurbine"
      :model_id="currentModel"
      @closeDialog="addForecastTask=false"
  />
</template>

<style scoped>

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.box-card {
  margin-bottom: 32px;
}

</style>