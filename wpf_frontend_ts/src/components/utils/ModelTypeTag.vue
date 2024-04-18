<script setup>
import {defineProps} from 'vue'

const props = defineProps({
  modelType: {
    type: String,
    required: true
  },
  modelStatus: {
    type: String,
    default: '准备就绪'
  }
})
</script>

<template>
  <el-popover
      v-if="modelType === 'MLP'"
      placement="top-start"
      title="MLP模型"
      :width="200"
      trigger="hover"
      content="仅需要未来天气预报数据即可进行预测"
  >
    <template #reference>
      <el-tag
          effect="plain"
          :type="modelStatus === '准备就绪' ? null : 'info'"
          style="margin-right: 6px"
      >MLP</el-tag>
    </template>
    <p>仅需要未来天气预报数据即可进行预测</p>
    <span>模型状态：</span>
    <el-tag
        effect="plain"
        :type="modelStatus === '准备就绪' ? null : 'warning'"
        style="margin-right: 6px"
    >{{ modelStatus }}</el-tag>
  </el-popover>

  <el-popover
      v-if="modelType === 'GCN+LSTM'"
      placement="top-start"
      title="GCN+LSTM模型"
      :width="200"
      trigger="hover"
  >
    <template #reference>
      <el-tag
          effect="plain"
          style="margin-right: 6px"
          :type="modelStatus === '准备就绪' ? null : 'info'"
      >GCN+LSTM</el-tag>
    </template>
    <p>仅需要风机24小时前的历史数据即可进行预测</p>
    <span>模型状态：</span>
    <el-tag
        effect="plain"
        :type="modelStatus === '准备就绪' ? null : 'warning'"
        style="margin-right: 6px"
    >{{ modelStatus }}</el-tag>
  </el-popover>
  <el-popover
      v-if="modelType === 'GCN+LSTM+MLP'"
      placement="top-start"
      title="GCN+LSTM+MLP模型"
      :width="200"
      trigger="hover"
  >
    <template #reference>
      <el-tag
          effect="plain"
          style="margin-right: 6px"
          :type="modelStatus === '准备就绪' ? null : 'info'"
      >GCN+LSTM+MLP</el-tag>
    </template>
    <p>综合风机24小时前的历史数据和未来天气预报数据以进行预测</p>
    <span>模型状态：</span>
    <el-tag
        effect="plain"
        :type="modelStatus === '准备就绪' ? null : 'warning'"
        style="margin-right: 6px"
    >{{ modelStatus }}</el-tag>
  </el-popover>
</template>

<style scoped>

</style>