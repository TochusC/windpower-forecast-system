<script setup>
import {defineProps,defineEmits, reactive, ref, onMounted} from "vue";
import UploadTurbineData from "@/components/ForecastCenter/UploadTurbineData.vue";
import {ElMessage, ElNotification} from "element-plus";

const formLabelWidth = '120px'
const addTurbineData = ref(false)
const taskForm = reactive({
  turbine_id: "",
  model_id:"",
  forecast_data:[],
  task_comment:"",
  date_range: {},
  startTime: {},
  endTime: {},
})

const props = defineProps({
  turbine_id : {
    type: String||Number,
  },
  model_id : {
    type: String||Number,
  },
})

const emit = defineEmits(['closeDialog', 'refreshTaskList'])
const dateRangeDict = ref({})
const timeRangeDict = ref({})
// 获取风机信息
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
/** **************** **/


/** 当对话框打开或关闭时，分别获取风机、清空表单 **/
const handleClose = () => {
  refreshForm()
  emit("closeDialog")
}

const handleOpen = () => {
  getTurbine()
  if(props.turbine_id !== undefined) {
    taskForm.turbine_id = props.turbine_id
    getTurbineModel(props.turbine_id)
    getForecastData(null, props.turbine_id, "forecast")
    if(props.model_id !== undefined) {
      taskForm.model_id = props.model_id
    }
  }

}
/** **************** **/


/** 从预测数据列表中删除预测数据 **/
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
        getForecastData(null, taskForm.turbine_id, "train");
        emit('removeData');
      })
}
/** **************** **/

/** 以下函数当在输入框中确定风机号会进行调用，分别获取风机预测模型信息和风机预测数据信息 **/
/*** 获取风机预测模型信息 ***/
const turbineModelList = ref([])
const assembleModel = (data) => {
  turbineModelList.value = []
  for(let index in data) {
    let forecastModel = {};
    forecastModel = data[index].fields;
    forecastModel["model_id"] = data[index].pk;
    forecastModel["delete_visible"] = false;
    turbineModelList.value.push(forecastModel);
  }
}
const getTurbineModel = (turbine_id) => {
  fetch(`http://127.0.0.1:8000/api/get_forecastModel/?turbine_id=${turbine_id}&model_id=all`, {
  }).then((response) => {
    return response.json()
  }).then((data) => {
    assembleModel(data)
  }).catch((e) => {
    console.log("Oops, error", e)
  })
}
/*** **************** ***/

const dateToString = (date) => {
  return date.getFullYear() + "-" + (date.getMonth() + 1).toString().padStart(2, '0') + "-" + date.getDate().toString().padStart(2, '0')
}

/*** 获取风机预测数据信息 ***/
const forecastDataList = ref([])
const assembleData = (data) => {
  forecastDataList.value = []
  for(let index in data) {
    let dataModel = {};
    dataModel = data[index].fields;
    dataModel["data_id"] = data[index].pk;
    dataModel["delete_visible"] = false;

    let start_time = dataModel["data_startTime"]
    let end_time = dataModel["data_endTime"]

    let tmpStartTime = new Date(end_time)
    tmpStartTime =  tmpStartTime.getTime() - (1 * 24 * 60 * 60 * 1000);
    tmpStartTime = new Date(tmpStartTime)
    tmpStartTime = dateToString(tmpStartTime)

    taskForm.date_range[dataModel['data_id']] =
        [tmpStartTime, end_time.slice(0,end_time.indexOf(' '))]

    dateRangeDict.value[dataModel['data_id']] =
        [start_time.slice(0,start_time.indexOf(' ')),
          end_time.slice(0,end_time.indexOf(' '))]

    start_time = new Date(start_time)
    end_time = new Date(end_time)

    taskForm.startTime[dataModel['data_id']] = "05:00"
    taskForm.endTime[dataModel['data_id']] =
        end_time.getHours().toString().padStart(2, '0') + ":" + end_time.getMinutes().toString().padStart(2, '0')
    timeRangeDict.value[dataModel['data_id']] =
        [start_time.getHours().toString().padStart(2, '0') + ":" + start_time.getMinutes().toString().padStart(2, '0'),
        end_time.getHours().toString().padStart(2, '0') + ":" + end_time.getMinutes().toString().padStart(2, '0'),]


    disabledDate_Fun_Dict.value[dataModel['data_id']] = (time) => {
      return !(time.getTime() >= start_time.getTime() &&
          time.getTime() <= end_time.getTime() &&
          time.getMinutes() % 15 === 0 && time.getSeconds() === 0);

    }
    forecastDataList.value.push(dataModel);
  }
}
const getForecastData = (event, turbine_id="all", data_type="forecast") => {
  fetch(`http://127.0.0.1:8000/api/get_turbineData/?turbine_id=${turbine_id}&data_type=${data_type}`, {
  }).then((response) => {
    return response.json()
  }).then((data) => {
    assembleData(data)
  }).catch((e) => {
    console.log("Oops, error", e)
  })
}
const handleTurbineChange = (val) => {
  getTurbineModel(val)
  getForecastData(null, val, "forecast")
}
const handleCurrentChange = (val) => {
  taskForm.forecast_data = val
}
/*** **************** ***/
/** **************** **/


/** 上传风机表单至后端 **/
const uploadTaskForm = () => {
  // 检查表单
  if(taskForm.turbine_id === ""){
    ElMessage({
      message: '请选择预测风机',
      type: 'error',
    })
    return
  }
  if(taskForm.model_id === ""){
    ElMessage({
      message: '请选择预测模型',
      type: 'error',
    })
    return
  }
  if(taskForm.forecast_data.length === 0){
    ElMessage({
      message: '请选择预测数据',
      type: 'error',
    })
    return
  }
  // 上传表单
  let formData = new FormData();
  formData.append('turbine_id', taskForm.turbine_id);
  formData.append('model_id', taskForm.model_id);
  formData.append('task_comment', taskForm.task_comment);
  let index = 0;
  for (;index < taskForm.forecast_data.length - 1; index++) {

    let data_id = taskForm.forecast_data[index]['data_id']

    formData.set('data_id', data_id)

    let startTime = new Date(taskForm.date_range[data_id][0])
    let endTime = new Date(taskForm.date_range[data_id][1])

    startTime = startTime.getFullYear() + "-" + (startTime.getMonth()+1).toString().padStart(2, '0') + "-" +
        startTime.getDate().toString().padStart(2, '0') + " " + taskForm.startTime[data_id]+":00"
    endTime = endTime.getFullYear() + "-" + (endTime.getMonth()+1).toString().padStart(2, '0') + "-" +
        endTime.getDate().toString().padStart(2, '0') + " " + taskForm.endTime[data_id]+":00"

    formData.set('task_startTime', startTime);
    formData.set('task_endTime', endTime);

    fetch('http://localhost:8000/api/add_forecastTask/', {
      method: 'POST',
      body: formData
    })

  }
  let data_id = taskForm.forecast_data[index]['data_id']

  formData.set('data_id', data_id)

  let startTime = new Date(taskForm.date_range[data_id][0])
  let endTime = new Date(taskForm.date_range[data_id][1])

  startTime = startTime.getFullYear() + "-" + (startTime.getMonth()+1).toString().padStart(2, '0') + "-" +
      startTime.getDate().toString().padStart(2, '0') + " " + taskForm.startTime[data_id]+":00"
  endTime = endTime.getFullYear() + "-" + (endTime.getMonth()+1).toString().padStart(2, '0') + "-" +
      endTime.getDate().toString().padStart(2, '0') + " " + taskForm.endTime[data_id]+":00"

  formData.set('task_startTime', startTime);
  formData.set('task_endTime', endTime);

  fetch('http://localhost:8000/api/add_forecastTask/', {
    method: 'POST',
    body: formData
  }).then(response => response.json())
      .then(data => {
        if (data.status === "success"){
          ElNotification({
                title: '成功',
                message: '任务添加成功',
                type: 'success'
              }
          );
        }
        refreshForm()
        emit('refreshTaskList')
        emit('closeDialog')
      })
}

/** **************** **/


/** 判断日期是被禁用的函数组 **/
const disabledDate_Fun_Dict = ref({})
/** **************** **/
const refreshForm = () =>{
  taskForm.turbine_id = ""
  taskForm.model_id = ""
  taskForm.forecast_data = []
  taskForm.task_comment = ""
  taskForm.date_range = {}
  taskForm.startTime = {}
  taskForm.endTime = {}
  dateRangeDict.value = {}
  timeRangeDict.value = {}
  turbineModelList.value = []
  forecastDataList.value = []
}
</script>

<template>
  <el-dialog title="任务信息" @open="handleOpen">
    <el-form :taskForm="taskForm">s
      <el-form-item label="预测风机" :label-width="formLabelWidth">
        <el-select
        v-model="taskForm.turbine_id"
        collapse-tags
        collapse-tags-tooltip
        placeholder="请选择预测风机"
        style="width: 360px"
        @change="handleTurbineChange"
        >
          <el-option
              v-for="turbine in turbines"
              :key="turbine.turbine_id"
              :value="turbine.turbine_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="预测模型" :label-width="formLabelWidth">
        <el-select
            v-model="taskForm.model_id"
            placeholder="请选择预测模型"
            style="width: 360px"
        >
          <el-popover
              v-for="turbineModel in turbineModelList"
              :key="turbineModel.model_id"
              placement="top-start"
              title="模型信息"
              :width="200"
              trigger="hover"
          >
            <template #reference>
              <el-option
                  :label="turbineModel.model_type"
                  :value="turbineModel.model_id"
                  :disabled="turbineModel.model_status !== '准备就绪'"
              />
            </template>
            <div>模型备注: {{turbineModel.model_comment}}</div>
            <div>训练时间: {{turbineModel.model_trainTime}}</div>
          </el-popover>
        </el-select>
      </el-form-item>
      <el-form-item label="任务备注" :label-width="formLabelWidth">
        <el-input
            v-model="taskForm.task_comment"
            placeholder="请输入任务备注"
        />
      </el-form-item>
      <el-form-item label="预测数据" :label-width="formLabelWidth">
        <el-table
            ref="TableRef"
            :data="forecastDataList"
            :default-sort="{ prop: 'date_uploadTime', order: 'descending' }"
            highlight-current-row
            style="width: 100%"
            @selection-change="handleCurrentChange"
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
    <el-form-item>
      <el-button
          style="float: left; margin-left: 72px"
          @click="addTurbineData = true"
      >上传数据</el-button>
    </el-form-item>
    <template
        v-for="item in taskForm.forecast_data"
        :key="item['data_id']"
    >
      <el-divider>
        {{ item['data_name'] }}
      </el-divider>
      <el-form-item
          label="预测区间"
          :label-width="formLabelWidth">
        <el-date-picker
            v-model="taskForm.date_range[item['data_id']]"
            type="daterange"
            range-separator="至"
            start-placeholder="起始日期"
            clearable
            unlink-panels
            :default-value="taskForm.date_range[item['data_id']][1]"
            :disabled-date="disabledDate_Fun_Dict[item['data_id']]"
            end-placeholder="结束日期"
            style="width: 360px"
        />
      </el-form-item>
      <el-form-item
          label="起止时间"
          :label-width="formLabelWidth">
        <div
            style="  display: flex;
            justify-content: space-between;
            align-items: center;
            text-align: center"
        >
          <span style="margin-right: 16px">
            <el-time-select
                start="00:00"
                end="23:45"
                v-model="taskForm.startTime[item['data_id']]"
                class="mr-4"
                placeholder="起始时间"
                clearable
                step="00:15"
            />
          </span>
          <el-divider direction="vertical"/>
          <span style="margin-left: 16px">
            <el-time-select
                start="00:00"
                end="23:45"
                v-model="taskForm.endTime[item['data_id']]"
                placeholder="结束时间"
                step="00:15"
                clearable
            />
          </span>
        </div>
      </el-form-item>
    </template>
    <template #footer>
        <span>
          <el-button @click="handleClose">取消</el-button>
          <el-button type="primary" @click="uploadTaskForm">
            添加
          </el-button>
        </span>
    </template>
    <UploadTurbineData v-model="addTurbineData"
                     :turbine_id="taskForm.turbine_id"
                     @closeDialog="addTurbineData = false"
                     @uploadSuccess="addTurbineData = false;
                     getForecastData(null, taskForm.turbine_id, 'forecast')
                        " />
  </el-dialog>
</template>

<style scoped>

</style>