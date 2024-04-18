<script setup >
import {defineProps, onMounted} from "vue";
import { Configuration, OpenAIApi } from "openai";
const configuration = new Configuration({
  
});

const openai = new OpenAIApi(configuration);

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

onMounted(() => {
  const completion = openai.createChatCompletion({
    model: "gpt-3.5-turbo",
    messages: [{"role": "system", "content": "You are a helpful assistant."}, {role: "user", content: "Hello world"}],
  });
})
</script>

<template>
  <p>Hello OpenAI!</p>
</template>

<style scoped>

</style>