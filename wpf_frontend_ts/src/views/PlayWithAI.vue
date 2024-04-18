<script setup>
  import {ref,onMounted,onUnmounted} from "vue";
  import {Close, Promotion, Refresh, Search, Star} from "@element-plus/icons-vue";
  const isCollapse = ref(false)
  const message = ref('')
  const showDialog = ref(false)
  const dynamicHeight = ref('540px')
  const dynamicMargin = ref('128px')
  const dynamicRows = ref('1')
  const pending = ref(false)
  const pendingRows = ref(1)
  const drawerRef = ref(null)
  const carouselItem = [
    {
      title: "让AI协助你完成繁杂的工作",
      input: "我应该如何使用风电预测系统？"
    },
    {
      title: "让AI聆听你的想法",
      input: "我们如果用风力发电来制氢储能，会有什么效益？"
    },
    {
      title: "让AI帮助你实现各种奇思妙想",
      input: "我怎样才能在控制台用字符画出一个风力发电机？"
    },
    {
      title: "让AI为你的创作赋能",
      input: "我希望你能帮我完善下这篇风机总结报告"
    }
  ]

  const messageHistory = ref([])
  const dynamicDrawerWidth = ref('64%')
  const dynamicDrawerMargin = ref('18%')

  const resizeHandler = () => {
    let heightRatio = window.innerHeight/1024
    let widthRatio = window.innerWidth/2048

    if(window.innerWidth < 620) {
      isCollapse.value = true
      dynamicDrawerWidth.value = '100%'
      dynamicDrawerMargin.value = '0px'
      dynamicRows.value = '4'
      dynamicMargin.value = '0px'
      dynamicHeight.value = heightRatio * 576 + 'px'
    }
    else{
      isCollapse.value = false
      dynamicRows.value = '4'
      dynamicDrawerWidth.value = '64%'
      dynamicDrawerMargin.value = '18%'
      dynamicHeight.value = heightRatio * 576 + 'px'
      dynamicMargin.value = widthRatio * 96 + 'px'
    }
  }
  const helloGPT = () => {
    if(message.value === ''){
      return
    }

    messageHistory.value.push(
        {role: 'user', content: message.value}
    )

    let formData = new FormData()
    let messageHistory_string = JSON.stringify(messageHistory.value )
    formData.append('messageHistory', messageHistory_string)

    pending.value = true
    pendingRows.value = (message.value.length / 12).toFixed(0)
    if(pendingRows.value < 1){
      pendingRows.value = 1
    }
    message.value = ''

    fetch("http://127.0.0.1:8000/api/hello_gpt/", {
      method:'POST',
      body:formData,
    }).then(response => response.json())
    .then(data => {
      pending.value = false;
      messageHistory.value.push(data.message);
    })
  }
  const initialDialog = () => {
    messageHistory.value = []
    pending.value = true
    setTimeout(()=>{
      messageHistory.value.push({role: "assistant", content: "你好！我是小风，风电预测系统的AI助手，很高兴为你服务！"})
      pending.value = false
    }, 720)
  }

  onMounted(() => {
    resizeHandler()
    window.addEventListener('resize', resizeHandler)
  })
  onUnmounted(() => {
    window.removeEventListener('resize', resizeHandler)
  })

</script>

<template>
  <div class="main" :style="{marginLeft: dynamicMargin}">
    <div style="width: 100%">
    <el-carousel
        height="168px"
        arrow="never"
        indicator-position="none"
        direction="vertical"
        interval="2600"
    >
      <el-carousel-item
          v-for="(item, index) in carouselItem"
          :key="index"
      >
        <el-text class="title">{{ item.title }}</el-text>
        <div>
        <el-input
            v-model="item.input"
            style="margin: 36px;width: 64%;height: 44px"
        >
          <template #append>
            <el-button :icon="Search" />
          </template>
          <template #prepend>
            你好，AI！
            <el-icon
                class="is-loading"
                size="14px"
            >
              <Star
                  color="#5968f4"/>
            </el-icon>
          </template>
        </el-input>
        </div>
      </el-carousel-item>
    </el-carousel>
    </div>
    <div style="width: 100%">
      <el-button
          v-if="isCollapse"
          type="primary"
          color="#5968f4"
          style="width: 96px; margin-top: 18px; margin-bottom: 0px"
          @click="showDialog = true;"
      >
        抢先体验
      </el-button>
      <el-button
          v-else
          type="primary"
          color="#5968f4"
          style="width: 96px; margin-top: 36px; margin-bottom: 48px"
          @click="showDialog = true;"
      >
        抢先体验
      </el-button>

    </div>
    <div class="displayDemo">
      <el-card class="messageDemo" :style="{ width:dynamicDrawerWidth }">
        <el-divider></el-divider>
        <div class='ai-message'>
          <span>
            <img
                src="../assets/static/img/turbine_icon.png"
                alt="avatar"
                style="height: 42px;margin-right: 9px"
            />
            </span>
          <span>
            <el-card
                style="margin-right: 48px; margin-bottom: 42px">
              <el-text
                  style="white-space: pre-line;">
                你好！我是小风，风电预测系统的AI助手，很高兴为你服务！
              </el-text>
            </el-card>
          </span>
        </div>
        <div class="user-message">
          <span>
            <el-card
                style="margin-left: 48px; margin-bottom: 42px">
              <el-text
                  style="white-space: pre-line;">
                我应该如何使用风电预测系统？
              </el-text>
            </el-card>
          </span>
          <span>
              <el-avatar
                  style="margin-left: 9px"
                  src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
              />
            </span>
        </div>
        <div
            class="ai-message">
              <span>
                <img
                    src="../assets/static/img/turbine_icon.png"
                    alt="avatar"
                    style="height: 42px;margin-right: 9px"
                />
              </span>
          <el-card style="width: 64%;margin-right: 48px; margin-bottom: 32px">
            <el-skeleton
                animated
            />
          </el-card>
        </div>
      </el-card>
    </div>
  </div>
  <el-drawer
      @open="()=>{
        if(messageHistory.length === 0){
          initialDialog()
        }
      }"
      ref="drawerRef"
      :show-close="true"
      v-model="showDialog"
      direction="btt"
      size = "99%"
      :with-header="false"
      :style="{width:dynamicDrawerWidth,
      marginLeft: dynamicDrawerMargin}"
      style="background-color: transparent;box-shadow: none"
  >
    <el-card class="messageDialog">
      <img
          v-if="!isCollapse"
          src="../assets/static/img/turbine_icon.png"
          alt="avatar"
          style="height: 46px;"
      />
      <el-divider>

      </el-divider>

      <div :style="{height: dynamicHeight}">
        <el-scrollbar>
          <div
              v-for="(message,index) in messageHistory"
              :key="index"
              :class="message.role === 'assistant'
              ? 'ai-message': 'user-message'"
          >
            <template v-if="message.role === 'assistant'">
              <span>
              <img
                  src="../assets/static/img/turbine_icon.png"
                  alt="avatar"
                  style="height: 42px;margin-right: 9px"
              />
              </span>
              <span>
              <el-card
                  style="margin-right: 48px; margin-bottom: 42px">
                <el-text
                    style="white-space: pre-line;">
                  {{ message.content }}
                </el-text>
              </el-card>
            </span>
            </template>
            <template v-else>
              <span>
                <el-card
                    style="margin-left: 48px; margin-bottom: 42px">
                  <el-text
                      style="white-space: pre-line;">
                    {{ message.content }}
                  </el-text>
                </el-card>
              </span>
              <span>
                <el-avatar
                    style="margin-left: 9px"
                    src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
                />
              </span>
            </template>
          </div>
          <div
              v-if="pending"
              class="ai-message"
          >
              <span>
                <img
                    src="../assets/static/img/turbine_icon.png"
                    alt="avatar"
                    style="height: 42px;margin-right: 9px"
                />
              </span>
            <el-card style="width: 64%;margin-right: 48px; margin-bottom: 32px">
              <el-skeleton
                  animated
                  :rows="pendingRows"
              />
            </el-card>
          </div>
        </el-scrollbar>
      </div>
      <el-divider style="margin-top: 32px; margin-bottom: 32px">
      </el-divider>
      <div>
        <el-input
            v-model=message
            ref="inputArea"
            :rows="dynamicRows"
            maxlength="1024"
            show-word-limit
            type="textarea"
            style="resize: none"
            @keyup.enter="message=message.slice(0,-1);helloGPT();"
            placeholder="在此输入你的想法..."
        />
        <div
            class="button-group"
        >
          <span>
            <el-button-group
                v-if="isCollapse"
                style="margin-right: 18px"
            >
              <el-button
                  style="width: 96px"
                  @click="drawerRef.close"
              >
                关闭
              </el-button>
              <el-button
                  style="width: 32px;"
                  :icon="Close"
                  @click="drawerRef.close"
              >
              </el-button>
            </el-button-group>
          </span>
          <span>
            <el-button-group
                style="margin-right: 18px"
            >
              <el-button
                  style="width: 96px"
                  @click="message='';initialDialog()"
              >
                清空
              </el-button>
              <el-button
                  style="width: 32px;"
                  :icon="Refresh"
                  @click="message='';initialDialog()"
              >
              </el-button>
            </el-button-group>
            <el-button-group>
              <el-button
                  style="width: 96px"
                  color="#5968f4"
                  @click="helloGPT"
              >
                发送
              </el-button>
              <el-button
                  style="width: 32px;"
                  color="#5968f4"
                  :icon="Promotion"
                  @click="helloGPT"
              >
              </el-button>
            </el-button-group>
          </span>
        </div>
      </div>
    </el-card>
  </el-drawer>
</template>


<style scoped>
.main {
  justify-content: center;
  margin-top: 64px;
  margin-left: 128px;
  margin-bottom: 0;
}
.title {
  font-size: 28px;
  text-align: left;
  font-weight: bold;
  margin-bottom: 20px;
}
.displayDemo{
  width: 100%;
  display: flex;
  justify-content: center;
}
.messageDemo{
  margin-top: 64px;
}
.messageDialog{
  height: 98%;
  margin-left: 12px;
  margin-top: 12px;
  margin-right: 12px;
}
.ai-message {
  display: flex;
  text-align: left;
  float: left;
  width: 100%;
}
.user-message{
  display: flex;
  justify-content: flex-end;
  text-align: right;
  width: 100%;
}
.button-group{
  display: flex;
  align-content: center;
  justify-content: space-between;
  margin-top: 12px;
}
.button {
  width: 128px;
}
</style>