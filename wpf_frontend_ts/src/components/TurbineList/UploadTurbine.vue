<script setup>

import {CollectionTag, Memo, Postcard, UploadFilled} from "@element-plus/icons-vue";
import {reactive, ref, defineEmits} from "vue";
import {ElMessageBox} from "element-plus";

const emit = defineEmits(['closeDialog', 'uploadSuccess'])

const turbineForm = reactive({
  turbine_name: '',
  turbine_id: '',
  turbine_comment: '',
  model_type: [],
  model_type_string: '',
})

const data_form = ref(null)
const uploadData = ref({
  data_type: "train",
  turbine_id: "id",
  data_comment: ""
})

const turbine = ref(null)
const fileList = ref([])
const uploadFileUrl = ref("http://127.0.0.1:8000/api/upload_data/")

const formLabelWidth = '72px'

const beforeRemove = (file, fileList) => {
  return ElMessageBox.confirm(
      `取消上传 ${file.name} ?`
  ).then(
      () => {
        return true
      },
      () => {
        return false
      }
  )
}

const uploadTurbine = () => {
  uploadData.value.turbine_id = turbineForm.turbine_id;
  data_form.value.submit();

  let modelType = '';
  for (modelType in turbineForm.model_type) {
    turbineForm.model_type_string += turbineForm.model_type[modelType] + ',';
  }

  let formData = new FormData();
  formData.append('turbine_id', turbineForm.turbine_id);
  formData.append('turbine_name', turbineForm.turbine_name);
  formData.append('turbine_comment', turbineForm.turbine_comment);
  formData.append('model_type', turbineForm.model_type_string);

  fetch("http://127.0.0.1:8000/api/add_turbine/", {
    method: 'POST',
    body: formData
  }).then((response) => {
    return response.json()
  }).then((data) => {
    if (data.status === "success")
     emit('uploadSuccess')
  }).catch((e) => {
    console.log("Oops, error", e)
  })

  fileList.value = [];
  turbineForm.turbine_id = '';
  turbineForm.turbine_name = '';
  turbineForm.turbine_comment = '';
  turbineForm.model_type = [];
  turbineForm.model_type_string = '';
}
</script>

<template>
  <el-dialog title="风机信息">
    <el-form :model="turbineForm" ref="turbine">
      <el-form-item label="风机名称" :label-width="formLabelWidth">
        <el-input
          v-model="turbineForm.turbine_name"
          autocomplete="off">
          <template #append>
            <el-icon><Postcard /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item label="风机号" :label-width="formLabelWidth">
        <el-input v-model="turbineForm.turbine_id" autocomplete="off">
          <template #append>
            <el-icon><CollectionTag /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item label="风机备注" :label-width="formLabelWidth">
        <el-input v-model="turbineForm.turbine_comment" autocomplete="off" >
          <template #append>
            <el-icon><Memo /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item label="模型类型" :label-width="formLabelWidth">
        <el-select
            v-model="turbineForm.model_type"
            collapse-tags
            multiple
            placeholder="请选择预测模型"
            collapse-tags-tooltip
            style="width: 240px"
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
        <el-upload
            ref="data_form"
            drag
            multiple
            method="POST"
            :data="uploadData"
            :action="uploadFileUrl"
            :before-remove="beforeRemove"
            v-model:file-list="fileList"
            :auto-upload="false"
            style="width: 100%"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖动或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              请上传含有风机数据的csv、xlxs文件
            </div>
          </template>
        </el-upload>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="$emit('closeDialog')">取消</el-button>
        <el-button type="primary" @click="uploadTurbine">
          上传
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<style scoped>

</style>