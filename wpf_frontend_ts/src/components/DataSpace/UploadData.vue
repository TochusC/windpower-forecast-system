<script setup>

import {Memo, Postcard, UploadFilled} from "@element-plus/icons-vue";
import {reactive, ref, defineEmits} from "vue";
import {ElMessage, ElMessageBox} from "element-plus";

const emit = defineEmits(['closeDialog', 'uploadSuccess'])
const bug = ref(true)

const dataForm = reactive({
  turbine_id: '',
  data_comment: '',
  data_type: '',
})

const form_for_data = ref(null)
const uploadDataDict = ref({
  turbine_id: '',
  data_comment: '',
  data_type: '',
})

const formLabelWidth = '72px'

const fileList = ref([])

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

const uploadData = () => {
  if(dataForm.turbine_id === ""){
    ElMessage({
      message: '请输入风机编号',
      type: 'error',
    })
    return
  }
  if(dataForm.data_type === ""){
    ElMessage({
      message: '请选择数据类型',
      type: 'error',
    })
    return
  }
  if(fileList.value.length === 0){
    ElMessage({
      message: '请上传数据文件',
      type: 'error',
    })
    return
  }

  uploadDataDict.value.turbine_id = dataForm.turbine_id;
  uploadDataDict.value.data_comment = dataForm.data_comment;
  uploadDataDict.value.data_type = dataForm.data_type;

  form_for_data.value.submit();

  setTimeout(() => emit('uploadSuccess'), 400)

  fileList.value = [];
  dataForm.data_comment = "";
  dataForm.data_type = "";
  dataForm.turbine_id = "";
}

const turbines = ref([])

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
</script>

<template>
  <el-dialog title="数据信息" @open="getTurbine">
    <el-form :model="dataForm">
      <el-form-item label="所属风机" :label-width="formLabelWidth">
        <el-select
            v-model="dataForm.turbine_id"
            clearable
            placeholder="请选择所属风机"
            style="width: 240px"
        >
          <el-option
              v-for="turbine in turbines"
              :key="turbine.turbine_id"
              :label="turbine.turbine_id"
              :value="turbine.turbine_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="数据类型" :label-width="formLabelWidth">
        <el-select
            v-model="dataForm.data_type"
            collapse-tags
            placeholder="请选择数据类型"
            style="width: 240px"
        >
          <el-option
              key="train"
              label="训练数据（用于训练模型）"
              value="train"
          />
          <el-option
              key="forecast"
              label="预测数据（用于预测风机未来功率）"
              value="forecast"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="数据备注" :label-width="formLabelWidth">
        <el-input v-model="dataForm.data_comment" autocomplete="off" >
          <template #append>
            <el-icon><Memo /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item label="数据文件" :label-width="formLabelWidth">
        <el-upload
            ref="form_for_data"
            drag
            multiple
            method="POST"
            :data="uploadDataDict"
            action="http://127.0.0.1:8000/api/upload_data/"
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
        <el-button type="primary" @click="uploadData">
          上传
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<style scoped>

</style>