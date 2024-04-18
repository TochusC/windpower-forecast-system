<template>
  <el-empty v-if="props.dataList.length===0" description="暂无数据" />
  <template v-for="turbineData in dataList" :key="turbineData.name">
    <el-card v-if="turbineData.data_type !== 'result'" class="box-card">
      <template #header>
        <div class="card-header">

          <span>
            <el-icon><Document /></el-icon>
            数据名称：{{turbineData.data_name}}
            <el-divider direction="vertical"/>
            <span class="text-item">所属风机：{{turbineData.turbine_id}}</span>
            <el-divider direction="vertical"/>
            <span class="text-item" v-if="turbineData.data_type === 'train'">数据类型：<el-tag effect="plain" type="success">训练数据</el-tag></span>
            <span class="text-item" v-if="turbineData.data_type === 'forecast'">数据类型：<el-tag effect="plain">预测数据</el-tag></span>
            <span class="text-item" v-if="turbineData.data_type === 'result'">数据类型：<el-tag class="ml-2" type="success">预测结果</el-tag></span>
          </span>
          <span class="button-group">
            <el-button
                size="small"
                type="primary"
                @click="currentData= turbineData;
                dataVisualize=true;"
            >数据可视化</el-button>
            <el-popover :visible="turbineData.delete_visible" placement="top" :width="160">
              <p>确定删除数据？</p><p>警告：操作不可逆</p>
              <div style="text-align: right; margin: 0">
                <el-button size="small"  @click="turbineData.delete_visible = false">取消</el-button>
                <el-button size="small" type="danger" @click="removeData(turbineData.data_id); turbineData.delete_visible = false"
                >确定</el-button
                >
              </div>
              <template #reference>
                <el-button size="small" @click="turbineData.delete_visible = true">删除数据</el-button>
              </template>
            </el-popover>
          </span>
        </div>
      </template>
      <div style="text-align: left;
            display: flex;
            justify-content: space-between;
            ">
        <span>
        <el-divider direction="vertical"/>
        <span class="text-item">数据上传时间：{{turbineData.data_uploadTime}}</span>
        <el-divider direction="vertical"/>
        <span class="text-item">数据起始时间：{{turbineData.data_startTime}}</span>
        <el-divider direction="vertical"/>
        <span class="text-item">数据结束时间：{{turbineData.data_endTime}}</span>
        <el-divider direction="vertical"/>
        <span class="text-item">文件大小：{{turbineData.data_size}}</span>
        <el-divider direction="vertical"/>
        </span>
        <span>
        <el-button size="small"
                   type="success"
                   @click="downloadData(turbineData.data_id, turbineData.data_name)"
        >
          下载数据
        </el-button>
        </span>
      </div>
    </el-card>
  </template>
  <DataVisualize
      v-model="dataVisualize"
      :dataInfo="currentData"
      :isDark="props.isDark"
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

<script setup>
import {defineProps, defineEmits, ref} from 'vue'
  import {Document} from "@element-plus/icons-vue";
  import {ElNotification} from "element-plus";
import DataVisualize from "@/components/DataSpace/DataVisualize.vue";

  const props = defineProps(
      {
        dataList: {
          type: Array,
          required: true
        },
        isDark: {
          type: Boolean,
          required: true
        }
      }
  )

  const emit = defineEmits(['removeData', 'closeDialog'])
  const currentData = ref({})
  const dataVisualize = ref(false)
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
              message: '风机删除成功',
              type: 'success',
            });
          emit('removeData');
        })
  }

  const downloadData = (data_id, data_name) => {
    let formData = new FormData();
    formData.append('data_id', data_id);
    fetch('http://localhost:8000/api/download_data/', {
      method: 'POST',
      body: formData
    }).then(response => {
      return response.blob()})
        .then(blob => {
          // 创建一个新的Blob对象并创建一个URL来指向它
          const url = window.URL.createObjectURL(blob);

          // 创建一个<a>标签并设置相关属性
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', data_name); // 设置下载的文件名（替换为实际的文件名）

          // 添加<a>标签到文档中，并触发点击事件以下载文件
          document.body.appendChild(link);
          link.click();

          // 清理创建的URL对象
          window.URL.revokeObjectURL(url);
          setTimeout(() => {ElNotification({
            title: '成功',
            message: '开始下载数据',
            type: 'success',
          })}, 400);
        })
        .catch(error => {
          ElNotification({
            title: '失败',
            message: '数据下载失败',
            type: 'error',
          });
        });
  }
</script>