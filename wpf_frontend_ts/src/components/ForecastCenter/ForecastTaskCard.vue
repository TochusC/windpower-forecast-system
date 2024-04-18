<script setup>
import {defineProps, defineEmits, ref} from "vue";
import {CircleCheckFilled, Postcard} from "@element-plus/icons-vue";
import {ElNotification} from "element-plus";
import ResultVisualize from "@/components/ForecastCenter/ResultVisualize.vue";
import ModelTypeTag from "@/components/utils/ModelTypeTag.vue";

const props = defineProps({
  forecast_task_dict: {
    type: Object,
    required: true
  },
  isDark: {
    type: Boolean,
    required: true
  }
})

const emits = defineEmits(['refreshForecastTaskList',
'startForecastTask',])

/** 删除任务 **/
const removeTask = (event, task_id) => {
  let formData = new FormData();
  formData.append('task_id', task_id);
  fetch('http://localhost:8000/api/delete_forecastTask/', {
    method: 'POST',
    body: formData
  }).then(response => response.json())
      .then(data => {
        if (data.status === "success")
          ElNotification({
                title: '成功',
                message: '预测任务删除成功',
                type: 'success',
              }
          );
        emits('refreshForecastTaskList')
      })
}
/** ******* **/


/** 下载数据 **/
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
/** ******* **/


/** 下载结果 **/
const handleDownloadResult = (task_status, result_id, data_name) => {
  if (task_status === '任务完成'){
    if (data_name.includes('in'))
      data_name = data_name.replace('in', 'out')
    else
      data_name = data_name.slice(0, data_name.indexOf('.csv')) + 'out.csv'
    downloadData(result_id, `${data_name}`)
  }
  else {
    ElNotification({
      title: '失败',
      message: '预测任务尚未完成',
      type: 'error',
    })
  }
}
/** ******* **/

/** 可视化结果 **/
const resultVisualize = ref(false)
const currentTask = ref({})
</script>

<template>
  <el-empty v-if="Object.keys(props.forecast_task_dict).length===0" description="暂无任务" />
  <el-card
      class="box-card"
      v-for="forecast_task in props.forecast_task_dict"
      :key="forecast_task.task_id">
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
              <el-icon><Postcard /></el-icon>
              所属风机：{{forecast_task.turbine_id}}
              <el-divider direction="vertical"/>
              <span class="text-item">预测数据：{{forecast_task.data_name}}</span>
              <el-divider direction="vertical"/>
              <span>
                <span class="text-item">预测模型：</span>
                <ModelTypeTag :model-type="forecast_task.model_type"/>
              </span>
            </span>
          </span>
        </span>
        <span>
          <el-button
              type="primary"
              size="small"
              @click="$emit('startForecastTask', forecast_task.task_id)"
              v-if="forecast_task.task_status === '待预测'"
          >
            开始预测
          </el-button>
          <el-button
              size="small"
              type="primary"
              v-if="forecast_task.task_status === '任务完成'"
              @click="currentTask = forecast_task;resultVisualize = true"
          >
            数据可视化
          </el-button>
          <el-popover :visible="forecast_task.delete_visible" placement="top">
            <p>确定删除任务？</p><p>警告：操作不可逆</p>
            <div style="text-align: right; margin: 0">
              <el-button size="small"  @click="forecast_task.delete_visible = false">取消</el-button>
              <el-button size="small" type="danger" @click="removeTask(null, forecast_task.task_id); forecast_task.delete_visible = false"
              >确定</el-button>
            </div>
            <template #reference>
              <el-button
                  size="small"
                  @click="forecast_task.delete_visible = true">删除任务</el-button>
            </template>
          </el-popover>
        </span>
      </div>
    </template>
    <el-container>
      <el-aside
          width="24%"
          style="
            border-right: 1px dotted #2c3e50">
        <el-progress v-if="forecast_task.task_status === '待预测'" type="circle" :percentage="0" >
          <span class="percentage-value">0%</span>
          <span class="percentage-label">{{forecast_task.task_status}}</span>
        </el-progress>
        <el-progress v-else-if="forecast_task.task_status === '任务完成'"
                     type="circle"
                     :percentage="100"
                     status="success"
        >
          <el-icon size="36"><CircleCheckFilled /></el-icon>
        </el-progress>
        <el-progress v-else type="circle" :percentage="forecast_task.task_status.slice(6, forecast_task.task_status.indexOf('%'))" >
          <span class="percentage-value">{{forecast_task.task_status.slice(6)}}</span>
          <span class="percentage-label">{{forecast_task.task_status.slice(0, 6)}}</span>
        </el-progress>
      </el-aside>
      <el-container>
        <el-main>
          <div style="text-align: left">
            <span class="text-item">任务备注：{{forecast_task.task_comment}}</span>
            <el-divider direction="vertical"/>
            <span>
              <span class="text-item" style="margin-right:0; ">任务状态：</span>
              <el-tag v-if="forecast_task.task_status === '待预测'" class="ml-2" type="warning">{{forecast_task.task_status}}</el-tag>
              <el-tag v-else-if="forecast_task.task_status === '任务完成'" class="ml-2" type="success">{{forecast_task.task_status}}</el-tag>
              <el-tag v-else class="ml-2">{{forecast_task.task_status}}</el-tag>
            </span>
            <el-divider direction="vertical"/>
            <span>
              <span class="text-item" style="margin-right:0; ">预测起始时间：</span>
              <span>{{forecast_task.task_startTime}}</span>
            </span>
            <el-divider direction="vertical"/>
            <span>
              <span class="text-item" style="margin-right:0; ">预测结束时间：</span>
              <span>{{forecast_task.task_endTime}}</span>
            </span>
            <el-divider direction="vertical"/>
            <span>
              <span class="text-item" style="margin-right:0; ">任务完成时间：</span>
              <span>{{forecast_task.task_finishTime}}</span>
            </span>
            <el-divider direction="vertical"/>
          </div>
        </el-main>
        <el-footer style="text-align: right">
          <el-button size="small"
                     type="success"
                     @click="downloadData(forecast_task.data_id,
                      forecast_task.data_name)"
          >
            下载预测数据
          </el-button>
          <el-button
              size="small"
              type="success"
              @click="handleDownloadResult(forecast_task.task_status,
               forecast_task.result_id, forecast_task.data_name)">
            下载预测结果
          </el-button>
        </el-footer>
    </el-container>
    </el-container>
  </el-card>
  <ResultVisualize
    v-model="resultVisualize"
    :forecast-task="currentTask"
    @closeDialog="resultVisualize = false"
    :is-dark="isDark"
  />
</template>

<style scoped>
.percentage-value {
  display: block;
  margin-top: 10px;
  font-size: 28px;
}
.percentage-label {
  display: block;
  margin-top: 10px;
  font-size: 12px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.box-card {
  margin-bottom: 32px;
}

</style>