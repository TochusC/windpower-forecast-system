<script setup>
import {defineProps, defineEmits} from "vue";

const props = defineProps({
  currentProgress: {
    type: Number,
    default: 1
  }
})

const emits = defineEmits(['changeProgress'])

const changeProgress = (index) => {
  emits('changeProgress', index)
}
</script>

<template>
  <div style="height: 560px;margin-top: 32px">
    <el-steps direction="vertical" :active="(props.currentProgress * 5).toFixed(0)">
      <el-step title="" @click="changeProgress(1)"/>
      <el-step title="" @click="changeProgress(2)"/>
      <el-step title="" @click="changeProgress(3)"/>
      <el-step title="" @click="changeProgress(4)"/>
      <el-step title="" @click="changeProgress(5)"/>
    </el-steps>
  </div>
</template>

<style scoped>

</style>