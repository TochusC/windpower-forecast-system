<script setup>
import {defineProps} from "vue";

const props = defineProps({
  isDark: {
    type: Boolean,
    required: true
  },
  windowsHeight: {
    type: Number,
    required: true
  },
  windowsWidth: {
    type: Number,
    required: true
  }
})
</script>

<template>
  <div>
  <el-menu
      default-active="1"
      :collapse="isCollapse"
      style="width:150px;"
  >
    <div
        v-if="!isCollapse"
    >
      <p>文档说明</p>
      <el-divider
          style="margin: 12px;width: 90%"
      />
    </div>
    <el-menu-item index="1" @click="$emit('changeGuides','1')">
      <template #title>风机列表</template>
    </el-menu-item>

    <el-menu-item index="2" @click="$emit('changeGuides','2')">
      <template #title>风机模型</template>
    </el-menu-item>
    <el-menu-item index="3" @click="$emit('changeGuides','3')">
      <template #title>数据中心</template>
    </el-menu-item>
    <el-menu-item index="4" @click="$emit('changeGuides','4')">
      <template #title>预测中心</template>
    </el-menu-item>
    <el-menu-item index="5" @click="$emit('changeGuides','5')">
      <template #title>统计界面</template>
    </el-menu-item>
  </el-menu>
  </div>
</template>


<style scoped>

</style>