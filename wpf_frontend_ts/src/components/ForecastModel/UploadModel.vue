<script setup>

import {Postcard} from "@element-plus/icons-vue";
import {ref, reactive, defineProps, defineEmits} from "vue";
import UploadTrainData from "@/components/ForecastModel/UploadTrainData.vue";
import {ElMessage, ElNotification} from "element-plus";

const props = defineProps({
  turbine_id : {
    type: String,
    required: true
  },
})

const emit = defineEmits(['closeDialog', 'uploadSuccess','uploadTrainData'])
const modelForm = reactive({
  turbine_id: "",
  model_type:[],
  model_comment:"",
  model_data:[],
})
const currentRow = ref([])
const addTurbineData = ref(false)
const formLabelWidth = '72px'
const trainDataList = ref([])
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
const getTrainData = (event, turbine_id="all", data_type="all") => {
  fetch(`http://127.0.0.1:8000/api/get_turbineData/?turbine_id=${turbine_id}&data_type=${data_type}`, {
  }).then((response) => {
    return response.json()
  }).then((data) => {
    assembleData(data)
  }).catch((e) => {
    console.log("Oops, error", e)
  })
}

const uploadModel = () => {
  if(modelForm.model_type.length === 0){
    ElMessage({
      message: '请选择模型类型',
      type: 'error',
    })
    return
  }
  if(modelForm.model_data.length === 0){
    ElMessage({
      message: '请选择训练数据',
      type: 'error',
    })
    return
  }
  let model_data_string = ""
  for(let index in modelForm.model_data){
    model_data_string += modelForm.model_data[index].data_id + ","
  }
  let formData = new FormData();
  formData.append("turbine_id", modelForm.turbine_id);
  formData.append("model_comment", modelForm.model_comment);
  formData.append("model_data", model_data_string);
  let index = 0
  for(;index < modelForm.model_type.length - 1; index++){
    formData.set("model_type", modelForm.model_type[index])
    fetch("http://127.0.0.1:8000/api/add_forecastModel/", {
      method: 'POST',
      body: formData
    })
  }
  formData.set("model_type", modelForm.model_type[index])
  fetch("http://127.0.0.1:8000/api/add_forecastModel/", {
    method: 'POST',
    body: formData
  }).then((response) => {
    return response.json()
  }).then((data) => {
    if (data.status === "success")
    {
      ElNotification({
        title: '成功',
        message: '模型添加成功',
        type: 'success',
      });
      emit('uploadSuccess')
    }
  }).catch((e) => {
    console.log("Oops, error", e)
  })

  modelForm.turbine_id = "";
  modelForm.model_type = [];
  modelForm.model_comment = "";
  modelForm.model_data = [];

  emit("closeDialog")
}

const handleClose = () => {
  modelForm.data_comment = "";
  modelForm.data_type = "";
  modelForm.turbine_id = "";
  emit("closeDialog")
}

const handleOpen = () => {
  modelForm.turbine_id = props.turbine_id
  getTrainData(null, props.turbine_id, "train")
}

const removeData = (data_id) => {
  let formData = new FormData();
  formData.append('data_id', data_id);
  fetch('http://localhost:8000/api/delete_data/', {
    method: 'POST',
    body: formData
  }).then(response => response.json())
      .then(data => {
        if (data.status === "success")
          ElNotification({
            title: '成功',
            message: '数据删除成功',
            type: 'success',
          }
          );
        getTrainData(null, props.turbine_id, "train");
        emit('removeData');
      })
}

const handleChange = (val) => {
  modelForm.model_data = val;
}
</script>

<template>
  <el-dialog title="模型信息" @open="handleOpen">
    <el-form :model="modelForm">
      <el-form-item label="所属风机" :label-width="formLabelWidth">
        <el-input
            v-model="modelForm.turbine_id"
            autocomplete="off"
            disabled
        >
          <template #append>
            <el-icon><Postcard /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item label="模型备注" :label-width="formLabelWidth">
        <el-input
            v-model="modelForm.model_comment"
            autocomplete="off">
          <template #append>
            <el-icon><Postcard /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item label="模型类型" :label-width="formLabelWidth">
        <el-select
            v-model="modelForm.model_type"
            collapse-tags
            multiple
            collapse-tags-tooltip
            placeholder="请选择预测模型"
            :max-collapse-tags="1"
            style="width: 360px"
        >
          <el-option
              key="MLP"
              label="仅需未来天气数据 (MLP)"
              value="MLP"
          />
          <el-option
              key="GCN+LSTM"
              label="仅需风机前24小时的历史数据 (GCN+LSTM)"
              value="GCN+LSTM"
          />
          <el-option
              key="GCN+LSTM+MLP"
              label="同时使用历史数据和未来天气数据 (GCN+LSTM+MLP)"
              value="GCN+LSTM+MLP"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="训练数据" :label-width="formLabelWidth">
        <el-table
            :data="trainDataList"
            :default-sort="{ prop: 'date_uploadTime', order: 'descending' }"
            highlight-current-row
            style="width: 100%"
            @selection-change="handleChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column property="data_name" label="数据名称"></el-table-column>
          <el-table-column property="data_comment" label="数据备注"></el-table-column>
          <el-table-column property="data_startTime" label="起始时间"></el-table-column>
          <el-table-column property="data_endTime" label="结束时间"></el-table-column>
          <el-table-column property="data_size" label="数据大小" width="120" />
          <el-table-column property="data_uploadTime" label="上传时间" sortable></el-table-column>
          <el-table-column label="操作">
              <template #default="scope">
                <el-popover :visible="scope.row.delete_visible" placement="top" :width="160">
                  <p>确定删除数据？</p><p>警告：操作不可逆</p>
                  <div style="text-align: right; margin: 0">
                    <el-button size="small" @click="scope.row.delete_visible = false">取消</el-button>
                    <el-button size="small" type="primary" @click="removeData(scope.row.data_id);
                    scope.row.delete_visible = false"
                    >确定</el-button
                    >
                  </div>
                  <template #reference>
                    <el-button @click="scope.row.delete_visible = true" type="danger">删除</el-button>
                  </template>
                </el-popover>
              </template>
          </el-table-column>
        </el-table>
      </el-form-item>
    </el-form>
    <el-button
        style="float: left; margin-left: 72px"
        @click="addTurbineData = true"
    >上传数据</el-button>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="uploadModel">
          添加
        </el-button>
      </span>
    </template>
    <UploadTrainData v-model="addTurbineData"
                     :turbine_id="modelForm.turbine_id"
                     @closeDialog="addTurbineData = false"
                     @uploadSuccess="addTurbineData = false;
                     getTrainData(null, modelForm.turbine_id, 'train')
                      " />
  </el-dialog>

</template>
<style scoped>

</style>