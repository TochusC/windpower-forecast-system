<script setup lang="ts">

import {ChatLineSquare, Warning} from "@element-plus/icons-vue";
</script>

<template>
  <div class="centerFlex">
    <span style="margin-left: 24px">
      <el-text tag="p" class="title">快速上手</el-text>
      <el-text>
        跟好本指南，本指南将带你
        <el-text class="grow" size="large">
          冲出重围
        </el-text>
        !
      </el-text>
    </span>
  </div>
  <el-divider style="margin-top: 16px"></el-divider>
  <div class="content">
    <el-text>简要来说...风机功率预测共分为五步:</el-text>
  </div>
  <div class="box">
    <el-steps :active="1" align-center>
      <el-step title="第一步" description="添加风机信息" />
      <el-step title="第二步" description="上传风机数据" />
      <el-step title="第三步" description="训练预测模型" />
      <el-step title="第四步" description="下达预测任务" />
      <el-step title="第五步" description="开始预测！" />
    </el-steps>
  </div>
  <div class="content">
    <el-text>下面我们将详细介绍每一步，来帮助您在最短时间内掌握本系统，并完成您的风电预测任务。</el-text>
  </div>
  <el-divider>
  </el-divider>
  <div class="box">
    <el-card shadow="never">
      <el-icon><ChatLineSquare /></el-icon>
      如果您感到跃跃欲试，可以随时点击右上角的导航栏，前往预测系统进行实践操作。
    </el-card>
  </div>
  <div class="content">
    <el-text class="secondTitle">第一步: 添加风机信息</el-text>
  </div>
  <div class="line">
    <el-text>风机管理页面列出了系统中所有的上线风机信息.</el-text>
  </div>
  <img
      class="illustrate"
      src="../../assets/static/img/guide/quick_start/1-1.png"
      alt="风机管理页面"
      style="width: 72%;height: auto;"
  />
  <div class="content">
    <el-text>通过单击右上角的
      <el-tag type="success">上传风机信息</el-tag>
      按钮，您可以添加风机信息至系统中。
    </el-text>
  </div>
  <div style="display: flex;justify-content: center">
  <img
      class="illustrate"
      src="../../assets/static/img/guide/quick_start/1-2.png"
      alt="风机信息表单"
      style="width: 42%;height: auto;"
  />
  </div>
  <div class="content">
    <el-text>您可能需要在
      <el-tag type="info">风机信息表单</el-tag>
      中做一些无趣的文书工作，但是不用烦心，
      您可以在信息表单中就提前完成第二步与第三步的一部分-添加风机模型及上传训练数据。
    </el-text>
  </div>
  <div class="line">
    <el-text>
      放心，我们会
      <el-text class="grow">
        罩着你
      </el-text>
      的。
    </el-text>
  </div>
  <div class="content">
    <el-text>
      在上传风机信息表单后，您应该会看到风机管理页面中成功添加一条风机信息记录，它是您所添加的风机。
    </el-text>
  </div>
  <div class="line">
    <el-text>
      至此，您已经完成了第一步-添加风机信息，很简单，是吧？
    </el-text>
  </div>

  <el-divider>
  </el-divider>

  <div class="content">
    <el-text class="secondTitle">第二步: 上传风机数据</el-text>
  </div>
  <div class="line">
    <el-text>
      在预测系统的各个部分都可以进行上传风机数据的操作，只要看到有
      <el-tag type="info">上传数据</el-tag>按钮，就可以通过单击按钮，呼出上传数据表单，进行数据上传操作。
      但是我们推荐您在数据空间页面进行上传操作。
    </el-text>
  </div>
  <img
      class="illustrate"
      src="../../assets/static/img/guide/quick_start/2-1.png"
      alt="数据空间页面"
      style="width: 72%;height: auto;"
  />
  <div class="content">
    <el-text>
      等一下，请先不要着急尝试，我们先来看看上传至预测系统的数据类型及格式。
    </el-text>
  </div>
  <div class="line">
    <el-text>
      风电预测系统中存储的数据类型一共有三种，分别是
      <el-tag effect="plain" type="success">训练数据</el-tag>、
      <el-tag effect="plain">预测数据</el-tag>
      和
      <el-tag effect="plain" type="info">预测结果</el-tag>；
      它们是一系列的.csv文件或.xlxs文件，每个文件中包含了一定时间范围内的风机数据。
    </el-text>
  </div>
  <div class="line">
    <el-text>
      <el-tag effect="plain" type="success">
        训练数据
      </el-tag>
      被用来训练风机的预测模型，预测模型的准确度一大部分取决于训练数据的质量。
      而
      <el-tag effect="plain">
        预测数据
      </el-tag>
      则用来进行风电未来功率的预测任务，预测数据的质量也会一定程度上影响预测结果的准确度。
    </el-text>
  </div>
  <div class="line">
    <el-text>
      对于这两类数据来说，它们都将由您上传至预测系统，来为系统提供"燃料"。
      而最后的
      <el-tag effect="plain" type="info">预测结果</el-tag>
      则是由系统生成的预测结果，您可以在预测中心页面中查看预测结果，并下载相应数据。
    </el-text>
  </div>
  <div class="line">
    <el-text>
      需要注意的是，这些数据的上传格式是有要求的，请您上传符合格式要求的数据。
      对于训练数据和预测数据，您可以在数据空间页面中下载模板文件，来查看数据格式要求。
    </el-text>
  </div>
  <img
      class="illustrate"
      src="../../assets/static/img/guide/quick_start/2-2.png"
      alt="数据空间页面"
      style="width: 64%;height: auto;"
  >
  <div class="content">
    至此您已经知晓了第二步-上传风机数据的方方面面，接下来是精彩的部分了---训练风机模型。
  </div>

  <el-divider>
  </el-divider>

  <div class="content">
    <el-text class="secondTitle">第三步: 训练风机模型</el-text>
  </div>
  <div class="line">
    <el-text>
      在风机模型页面，您可以查看到所有风机拥有的预测模型信息，并且您还可以在此页面
      进行风机模型的添加及训练功能；不过，在此之前，您需要先了解一下风机模型的类型。
    </el-text>
  </div>
  <div class="content">
    <el-text>
      风机模型一共分为三种，它们分别是
      <el-popover
          placement="top-start"
          title="MLP模型"
          :width="200"
          trigger="hover"
          content="仅需要未来天气预报数据即可进行预测"
      >
        <template #reference>
          <el-tag
              effect="plain"
          >MLP</el-tag>
        </template>
      </el-popover>
      、
      <el-popover
          placement="top-start"
          title="GCN+LSTM模型"
          :width="200"
          trigger="hover"
          content="仅需要风机历史数据即可进行预测"
      >
        <template #reference>
          <el-tag
              effect="plain"
          >GCN+LSTM</el-tag>
        </template>
      </el-popover>
      、
      <el-popover
          placement="top-start"
          title="GCN+LSTM+MLP模型"
          :width="200"
          trigger="hover"
          content="结合风机历史数据和未来天气预报数据进行预测"
      >
        <template #reference>
          <el-tag
              effect="plain"
          >GCN+LSTM+MLP</el-tag>
        </template>
      </el-popover>
      。
    </el-text>
  </div>
  <div class="line">
    <el-text>
      这三种模型各有优劣，其中MLP模型最为轻量快速，而GCN+LSTM+MLP模型则更为准确，
      至于GCN+LSTM模型？没人会记得家中老二的，对吧？
    </el-text>
  </div>
  <img
      class="illustrate"
      src="../../assets/static/img/guide/quick_start/3-1.png"
      alt="风机模型页面"
      style="width: 64%;height: auto;"
  />
  <div class="line">
  <el-text>
    您可以通过单击风机卡片右上角的<el-tag type="success">添加预测模型</el-tag>按钮，
    来为一个风机添加新预测模型；在简单填写模型信息表单并上传后，你的新模型就会被添加到风机模型列表中，
    并且蓄势待发，准备开始训练。
  </el-text>
  </div>
  <img
      class="illustrate"
      src="../../assets/static/img/guide/quick_start/3-2.png"
      alt="添加预测模型"
      style="width: 36%;height: auto;"
  />
  <div class="content">
    <el-text>
      而对于通过其他方式添加的风机模型，在开始训练之前，你可能需要先为它选择训练数据；
      你还可以同时选择多个训练数据，模型会依次以所选数据进行训练。
    </el-text>
  </div>
  <div class="line">
    <el-text>
      在确保万事俱备后，点击模型的
      <el-tag>
        开始训练
      </el-tag>按钮，即可开始训练。
    </el-text>
  </div>
  <div class="box">
    <el-card shadow="never">
      <el-icon><warning /></el-icon>
      请注意，训练预测模型是一个十分耗时的过程，需要占用系统大量计算量，因此请不要同时训练多个模型。
    </el-card>
  </div>
  <div class="line">
    <el-text>
      在开始训练后，模型的右方会出现当前训练的进度条，来显示当前的训练进度,
      训练完成时，系统右上方将会弹出消息框来进行提示。
    </el-text>
  </div>
  <div class="line">
    恭喜！至此您以完成了第三步-训练风机模型的所有操作，接下来是下达预测任务部分。
  </div>

  <el-divider>
  </el-divider>

  <div class="content">
    <el-text class="secondTitle">第四步: 下达预测任务</el-text>
  </div>
  <div class="line">
    <el-text>
      模型训练完成后，便可进行预测任务的下达，您可以通过单击模型右侧的
      <el-tag>预测</el-tag>
      按钮，呼出预测任务下达表单，在填写完表单信息并上传后，即可下达预测任务。
    </el-text>
  </div>
  <img
      class="illustrate"
      src="../../assets/static/img/guide/quick_start/4-1.png"
      alt="下达预测任务"
      style="width: 36%;height: auto;"
    />
  <div class="line">
    <el-text>
      您也可以在风机管理页面进行预测任务的下达，只需单击风机卡片右上角的开始预测即可，
      但我们推荐您在预测中心页面，完成相应的操作。
    </el-text>
  </div>
  <img
      class="illustrate"
      src="../../assets/static/img/guide/quick_start/4-2.png"
      alt="风机管理页面"
      style="width: 64%;height: auto;"
  />
  <div class="line">
    <el-text>
      您可以在预测中心页面查看当前所有的预测任务，或删除已有任务，
      预测任务的左端环形进度条显示了当前任务的进行程度。
    </el-text>
  </div>
  <div class="line">
    <el-text>
      通过单击预测任务卡片右上角的
      <el-tag>开始预测</el-tag>按钮，即可进行预测。
    </el-text>
  </div>
  <div class="line">
    <el-text>
      对于已完成的预测任务，您可以通过单击预测任务卡片右上角的
      <el-tag>数据可视化</el-tag>
      按钮，来查看预测结果。或点击右小角的
      <el-tag type="success">按钮</el-tag>
      ，来下载预测结果文件。
    </el-text>
  </div>
  <img
      class="illustrate"
      src="../../assets/static/img/guide/quick_start/4-3.png"
      alt="数据可视化页面"
      style="width: 64%;height: auto;"
  />
  <div class="line">
    <el-text>
      对了，您还可以在数据空间页面对训练数据及预测数据进行数据可视化，以便更好地了解数据情况。
      数据可视化页面十分有趣，您可以随心探索下它的功能妙用。
    </el-text>
  </div>
  <div class="line">
    <el-text>
      恭喜你！你已经完成了第四步，预测任务下达部分，接下来是最后一步，马上就要结束了！
    </el-text>
  </div>

  <el-divider>
  </el-divider>

  <div class="content">
    <el-text class="secondTitle">第五步: 开始预测</el-text>
  </div>

  <div class="line">
    <el-text>
      等等...我们搞错了，这里没有
      <el-tag effect="plain" type="info">
        第五步
      </el-tag>
    </el-text>
  </div>
  <div class="line">
    <el-text>
      您已经完成了指南的所有内容。
      那么，这里就是旅程的终点了，请不要想念我们。
    </el-text>
  </div>
  <div class="line">
    <el-text class="secondTitle">
      接下来是什么？...
    </el-text>
  </div>
  <div class="content">
    <el-text>
      您可以尝试下系统的其他功能，比如把右下角的方块模型转动到一个更美观的角度，或是去与我们的
      <img
        src="../../assets/static/img/guide/quick_start/robot.png"
        alt="机器人"
        style="width: 20px;height: auto;"
      >AI助手小风聊会天？
    </el-text>
  </div>
  <div class="line">
    <el-text>
      我们只能领你到这儿了，接下的区域需要您去
      <el-text class="grow">自行探索</el-text>
    </el-text>
  </div>
  <div class="line">
    <el-text>
      助您玩得愉快！
    </el-text>
  </div>
</template>

<style scoped>
.title {
  font-size: 28px;
  text-align: left;
  font-weight: bold;
  margin-bottom: 20px;
}
.secondTitle {
  font-size: 16px;
  text-align: left;
  font-weight: bold;
  margin-bottom: 20px;
}
.illustrate{
  margin:12px
}
.grow {
  flex-grow: 1;
  text-shadow: #ffffff 0 0 2px;
}
.content {
  margin-left: 24px;
  text-align: left;
}
.line {
  margin-top: 12px;
  margin-bottom: 12px;
  margin-left: 24px;
  text-align: left;
}
.box {
  margin-top: 24px;
  margin-bottom: 24px;
}
</style>