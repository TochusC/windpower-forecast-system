<template>
  <el-upload
      ref="upload"
      drag
      multiple
      method="POST"
      :data="uploadData"
      :action="uploadFileUrl"
      :before-remove="beforeRemove"
      v-model:file-list="fileList"
      :on-preview="handlePreview"
  >
    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
    <div class="el-upload__text">
      拖动或<em>点击上传</em>
    </div>
    <template #tip>
      <div class="el-upload__tip">
        请上传包含有风机数据的csv、xlxs文件
      </div>
    </template>
  </el-upload>
</template>

<script setup lang="ts">
  import { UploadFilled } from '@element-plus/icons-vue'
  import { ElMessageBox } from 'element-plus'
  import {ref, defineProps, onMounted} from 'vue'

  const props = defineProps({
    fileType : {
      type: String,
      default: 'train',
      required: true,
    },
    turbine_id:{
      type: String,
      default: '1',
      required: true,
    }
  })

  const upload = ref(null)
  const uploadData = ref({
    fileType: props.fileType,
    turbine_id: props.turbine_id,
  })
  const fileList = ref([])
  const uploadFileUrl = ref("http://127.0.0.1:8000/api/upload_data/")

  const handlePreview = (file: any) => {
    console.log("aalo")
    console.log(file)
  }
  const submitUpload = () => {
    upload.value!.submit()
  }
  const removeFile = (file: any) => {
    let formData = new FormData();
    formData.append('file_type', props.fileType);
    formData.append('turbine_id', props.turbine_id);
    formData.append('file_name', file.name);
    fetch("http://127.0.0.1:8000/api/delete_data/", {
      method: 'POST',
      body: formData
    })
        .then(response => response.json())
        .then(data => {
          console.log(data);
        })
        .catch(error => {
          console.error(error);
        });
  }
  const beforeRemove = (file: any, fileList: any) => {
    return ElMessageBox.confirm(
        `取消上传 ${file.name} ?`
    ).then(
        () => {
          removeFile(file);
          return true
        },
        () => {
          return false
        }
    )
  }
  onMounted(() => {
    if (props.fileType === 'train') {
      uploadFileUrl.value = "http://127.0.0.1:8000/api/delete_data/train/"
    } else if (props.fileType === 'forecast') {
      uploadFileUrl.value =  "http://127.0.0.1:8000/api/delete_data/forecast/"
    }
    else uploadFileUrl.value = "http://127.0.0.1:8000/api/delete_data/"
  })
</script>
