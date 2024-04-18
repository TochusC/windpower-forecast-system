<script setup>
import {ref, onMounted} from 'vue'
import {Calendar, Document, User} from "@element-plus/icons-vue";
import {ElNotification} from "element-plus";

const addGuestbook = ref(false)
const guestbookList = ref([])
const guestbookForm = ref({
  guest_name: '',
  guest_comment: ''
})

const submitGuestbook = () => {
  let formData = new FormData()

  formData.append('guest_name', guestbookForm.value.guest_name)
  formData.append('guest_comment', guestbookForm.value.guest_comment)

  fetch("http://127.0.0.1:8000/api/add_guestbook/", {
    method: 'POST',
    body: formData
  }).then(response => response.json())
      .then(data => {
        if (data.status === "success"){
          ElNotification({
            title: '成功',
            message: '留言成功 ;)',
            type: 'success',
          });
          getGuestbook()
        }
      })
      .catch(e => console.log("Oops, error", e))

}
const assembleMessage = (data) => {
  guestbookList.value = []
  for (let index in data) {
    let message = {}
    message = data[index].fields
    message.id = data[index].pk
    guestbookList.value.push(message)
  }
}
const getGuestbook = () => {
  fetch('http://127.0.0.1:8000/api/get_guestbook/')
      .then(response => {
        return response.json()
      })
      .then((data) => {
        assembleMessage(data)
      })
      .catch(e => console.log("Oops, error", e))
}

onMounted(() => {
  getGuestbook()
  }
)
</script>

<template>
  <el-divider style="margin-top: 46px;
  margin-bottom: 46px"
  >
    <el-button
        class="btn"
        @click="addGuestbook=true"
    >
      留言
    </el-button>
  </el-divider>
  <el-empty
      v-if="guestbookList.length===0"
      description="暂无数据"
  />
  <template
      v-for="guestbook in guestbookList"
      :key="guestbook.id"
  >
    <el-card class="box-card">
      <template #header>
          <div class="card-header">
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
                <el-icon><User /></el-icon>
                留言人：{{guestbook.guest_name}}
                <el-divider direction="vertical"/>
              </span>
            </span>
            <span>
               <el-icon><Calendar /></el-icon>
                时间：{{guestbook.guest_time}}
                <el-divider direction="vertical"/>
            </span>
          </div>
      </template>
          <div style="text-align: left;
                display: flex;
                justify-content: space-between;
                ">
            <span>
              {{guestbook.guest_comment}}
            </span>
          </div>
    </el-card>
  </template>
  <el-drawer
      size="34%"
      direction="btt"
      v-model="addGuestbook"
  >
    <template #title>
      <el-divider style="margin: 0">
         留下你的足迹
      </el-divider>
    </template>
    <el-form style="margin: 0">
      <el-form-item
          label="留言人"
          label-width="120px"
      >
        <el-input
            v-model="guestbookForm.guest_name"
        ></el-input>
      </el-form-item>
      <el-form-item
          label="留言内容"
          label-width="120px"
      >
        <el-input
            v-model="guestbookForm.guest_comment"
        ></el-input>
      </el-form-item>
    </el-form>
    <el-button class="btn"
               type="primary"
               style="float: right"
               @click="addGuestbook=false;
               submitGuestbook();"
    >提交</el-button>
  </el-drawer>
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
.btn {
  width: 128px;
}
</style>