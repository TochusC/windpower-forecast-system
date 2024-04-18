<template>
  <el-menu
      default-active="0"
      :collapse="isCollapse"
  >
    <div
        v-if="!isCollapse"
    >
      <p>使用文档</p>
      <el-divider
          style="margin: 12px;width: 90%"
      />
    </div>
    <el-menu-item
        index="0"
        @click="$emit('changeIndex', '0')"
    >
      <el-icon><Star /></el-icon>
      <template #title>快速上手</template>
    </el-menu-item>
    <el-sub-menu index="1">
      <template #title>
        <el-icon><location /></el-icon>
        <span>风机管理指南</span>
      </template>
      <el-menu-item-group>
        <el-menu-item index="1-1" @click="$emit('changeIndex', '1-1')">风机列表指南</el-menu-item>
        <el-menu-item index="1-2" @click="$emit('changeIndex', '1-2')">风机模型指南</el-menu-item>
      </el-menu-item-group>
    </el-sub-menu>
    <el-menu-item index="2" @click="$emit('changeIndex', '2')">
      <el-icon><icon-menu /></el-icon>
      <template #title>数据空间指南</template>
    </el-menu-item>
    <el-menu-item index="3" @click="$emit('changeIndex', '3')">
      <el-icon><document /></el-icon>
      <template #title>预测中心指南</template>
    </el-menu-item>
    <el-menu-item index="4" @click="$emit('changeIndex', '4')">
      <el-icon><setting /></el-icon>
      <template #title>统计界面指南</template>
    </el-menu-item>
  </el-menu>

</template>

<script setup>
import { ref, onMounted} from 'vue'
import {
  Document,
  Menu as IconMenu,
  Location,
  Setting, Star,
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

