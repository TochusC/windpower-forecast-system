<template>
  <el-menu
      default-active="1-1"
      :collapse="isCollapse"
  >
    <div
        v-if="!isCollapse"
    >
      <p>功能导航</p>
      <el-divider
          style="margin: 12px;width: 90%"
      />
    </div>
    <el-sub-menu index="1">
      <template #title>
        <el-icon><location /></el-icon>
        <span>风机管理</span>
      </template>
      <el-menu-item-group>
        <el-menu-item index="1-1" @click="$emit('changeIndex', '1-1')">风机列表</el-menu-item>
        <el-menu-item index="1-2" @click="$emit('changeIndex', '1-2')">风机模型</el-menu-item>
      </el-menu-item-group>
    </el-sub-menu>
    <el-menu-item index="2" @click="$emit('changeIndex', '2')">
      <el-icon><icon-menu /></el-icon>
      <template #title>数据空间</template>
    </el-menu-item>
    <el-menu-item index="3" @click="$emit('changeIndex', '3')">
      <el-icon><document /></el-icon>
      <template #title>预测中心</template>
    </el-menu-item>
    <el-menu-item index="4" @click="$emit('changeIndex', '4')">
      <el-icon><setting /></el-icon>
      <template #title>统计界面</template>
    </el-menu-item>
  </el-menu>

</template>

<script setup>
import { ref, onMounted} from 'vue'
import {
  Document,
  Menu as IconMenu,
  Location,
  Setting,
} from '@element-plus/icons-vue'

const title = ref(null)
const isCollapse = ref(true)

onMounted(() => {
  isCollapse.value = window.innerWidth < 768;
  window.addEventListener('resize', () => {
    isCollapse.value = window.innerWidth < 768;
  })
})
</script>

<style scoped>

</style>

