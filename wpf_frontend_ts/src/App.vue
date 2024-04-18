<template>
  <div id="app">
    <el-container>
      <el-header>
        <HeaderNavi
            @changePage="(n) =>{
              pageIndex = n
              if(pageIndex==='2'){
                activeIndex = '0'
              }
              else{
                activeIndex = '1-1'
              }
            }"
            @changeTheme="(n) => {
              isDark = n
              console
            }"
        />
      </el-header>
      <el-container>
        <el-aside
            v-if="pageIndex==='1' || pageIndex==='2'"
            :width="asideWidth">
          <AsideNavi
              v-if="pageIndex==='1'"
              @changeIndex="(n) => {
            activeIndex = n
          }"
          />
          <GuideAside
              v-if="pageIndex==='2'"
              @changeIndex="(n) => {
              activeIndex = n
              }"
          />
        </el-aside>
        <el-container>
          <el-main>
            <el-scrollbar
                ref="scrollbarRef"
                :height="windowsHeight*offsetRatio"
                @scroll="({ scrollTop })=>{
                  currentProgress = (scrollTop+(windowsHeight*offsetRatio))
                  / innerRef.clientHeight;
                }"
                style="margin: 0; padding: 0"
            >
              <div
                ref="innerRef"
                :style="{
                width: dynamicWidth,
                marginLeft: dynamicMargin }"
              >
                <template v-if="pageIndex === '1'">
                  <ForecastPage
                      v-if="activeIndex==='1-1'"
                      :isDark="isDark"
                      :windows-height="windowsHeight"
                      :windows-width="windowsWidth"
                  />
                  <ForecastModel
                      v-if="activeIndex==='1-2'"
                      :isDark="isDark"
                      :windows-height="windowsHeight"
                      :windows-width="windowsWidth"
                  />
                  <DataSpace
                      v-if="activeIndex==='2'"
                      :isDark="isDark"
                      :windows-height="windowsHeight"
                      :windows-width="windowsWidth"
                  />
                  <ForecastCenter
                      v-if="activeIndex==='3'"
                      :isDark="isDark"
                      :windows-height="windowsHeight"
                      :windows-width="windowsWidth"
                  />
                  <StatisticsInterface
                      v-if="activeIndex==='4'"
                      :isDark="isDark"
                      :windows-height="windowsHeight"
                      :windows-width="windowsWidth"
                  />
                </template>
                <template v-if="pageIndex==='2'">
                  <uQuickStart
                      v-if="activeIndex==='0'"
                      :isDark="isDark"
                      :windows-height="windowsHeight"
                      :windows-width="windowsWidth"
                  />
                  <uTurbineList
                      v-if="activeIndex==='1-1'"
                      :isDark="isDark"
                      :windows-height="windowsHeight"
                      :windows-width="windowsWidth"
                  />
                  <uForecastModel
                      v-if="activeIndex==='1-2'"
                      :isDark="isDark"
                      :windows-height="windowsHeight"
                      :windows-width="windowsWidth"
                  />
                  <uDataSpace
                      v-if="activeIndex==='2'"
                      :isDark="isDark"
                      :windows-height="windowsHeight"
                      :windows-width="windowsWidth"
                  />
                  <uForecastCenter
                      v-if="activeIndex==='3'"
                      :isDark="isDark"
                      :windows-height="windowsHeight"
                      :windows-width="windowsWidth"
                  />
                  <uStatisticsInterface
                      v-if="activeIndex==='4'"
                      :isDark="isDark"
                      :windows-height="windowsHeight"
                      :windows-width="windowsWidth"
                  />
                </template>
                <template v-if="pageIndex==='3'">
                  <PlayWithAI
                      :isDark="isDark"
                      :windows-width="windowsWidth"
                      :windows-height="windowsHeight"
                  />
                </template>
                <template v-if="pageIndex==='4'">
                  <AboutUs
                      :isDark="isDark"
                      :windows-width="windowsWidth"
                      :windows-height="windowsHeight"
                  />
                </template>
              </div>
            </el-scrollbar>
          </el-main>
          <el-aside
              v-if="pageIndex==='2'"
              :width="64">
            <nQuickStart
                :current-progress="currentProgress"
                @change-progress="handleChangeProgress"
            />
          </el-aside>
        </el-container>
      </el-container>
    </el-container>
  </div>
  <div
      ref="spline"
      style="left: 8%; top:60%; height:40%; width:24%;position: absolute;overflow: hidden; z-index: -1">
    <iframe
        src='https://my.spline.design/clonercubebinarycopy-4e0f9dd2c51fd342e11627b2877905c2/'
        width='720px'
        height='720px'
        style="border: none;"
    ></iframe>
  </div>
  <div
      style="left: 94%; top:90%; height:10%; width:6%;position: absolute;overflow: hidden;"
      @mouseover="spline.style.zIndex = '1'"
      @mouseout="spline.style.zIndex = '-1'"
  >
  </div>
</template>

<script setup>
  import {onMounted, ref} from 'vue';
  import HeaderNavi from "@/components/main/HeadNavi.vue";
  import AsideNavi from "@/components/main/AsideNavi.vue";
  import ForecastPage from "@/views/TurbineList.vue";
  import DataSpace from "@/views/DataSpace.vue";
  import ForecastModel from "@/views/ForecastModel.vue";
  import ForecastCenter from "@/views/ForecastCenter.vue";
  import StatisticsInterface from "@/views/StatisticsInterface.vue";
  import UForecastCenter from "@/components/UserGuides/uForecastCenter.vue";
  import UForecastModel from "@/components/UserGuides/uForecastModel.vue";
  import UDataSpace from "@/components/UserGuides/uDataSpace.vue";
  import UTurbineList from "@/components/UserGuides/uTurbineList.vue";
  import UStatisticsInterface from "@/components/UserGuides/uStatisticsInterface.vue";
  import GuideAside from "@/components/main/GuideAside.vue";
  import AboutUs from "@/views/AboutUs.vue";
  import UQuickStart from "@/components/UserGuides/uQuickStart.vue";
  import NQuickStart from "@/components/UserGuides/sideNavi/nQuickStart.vue";
  import PlayWithAI from "@/views/PlayWithAI.vue";
  import {Star} from "@element-plus/icons-vue";

  const spline = ref(null)
  const activeIndex = ref('1-1')
  const pageIndex = ref('1')
  const isDark = ref(false)
  const windowsWidth = ref(window.innerWidth)
  const windowsHeight = ref(window.innerHeight)
  const asideWidth = ref('200px')
  const dynamicWidth = ref('100%')
  const dynamicMargin = ref('195px')
  const resizeRatio = ref(28)
  const isLogin = ref(false)

  const loginForm = ref({
    user:'',
    pwd:'',
  })


  // 滚动条相关属性
  let offsetRatio = 0.875
  const scrollbarRef = ref(null)
  const innerRef = ref(null)
  const currentProgress = ref(0)
  const handleChangeProgress = (index) => {
    let setProgress = index / 5
    let setScrollTop = innerRef.value.clientHeight * setProgress - windowsHeight.value * offsetRatio
    scrollbarRef.value.setScrollTop(setScrollTop)
  }

  onMounted(() => {
    windowsHeight.value = window.innerHeight
    windowsWidth.value = window.innerWidth

    let ratio = ((windowsWidth.value - 1000)/ windowsWidth.value *
        resizeRatio.value).toFixed(0)
    dynamicWidth.value = (100-ratio).toFixed(0) > 100 ?
        100 : (100-ratio).toFixed(0) + '%'
    dynamicMargin.value = (654 * ratio / 100).toFixed(0) < 0 ?
        0 : (654 * ratio / 100).toFixed(0)+ 'px'

    if (window.innerWidth < 768) {
      asideWidth.value = '64px'
    } else {
      asideWidth.value = '200px'
    }
    if(localStorage.getItem('visits')) {
      // 如果已经记录，则将访问次数加1
      const visits = parseInt(localStorage.getItem('visits')) + 1;
      localStorage.setItem('visits', visits.toString());
    } else {
      // 如果没有记录，则设置访问次数为1
      localStorage.setItem('visits', '1');
    }
    window.addEventListener('resize', () => {
      windowsHeight.value = window.innerHeight
      windowsWidth.value = window.innerWidth

      let ratio = ((windowsWidth.value - 1000)/ windowsWidth.value *
          resizeRatio.value).toFixed(0)
      dynamicWidth.value = (100-ratio).toFixed(0) > 100 ? 100 : (100-ratio).toFixed(0) + '%'
      dynamicMargin.value = (654 * ratio / 100).toFixed(0) < 0 ? 0 : (654 * ratio / 100).toFixed(0)+ 'px'

      if (window.innerWidth < 768) {
        asideWidth.value = '64px'
      } else {
        asideWidth.value = '200px'
      }
    })
  })
</script>

<style>
  #app {
    font-size: 14px;
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
  }

  .centerFlex {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  * {
    animation: ease-in-out 0.3s;
  }
</style>
