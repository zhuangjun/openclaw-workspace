<!-- 这是每日晨报的详情展示模板，替换原文件中的对应部分 -->
<template v-if="taskType.task_type === 'daily_market_report'">
  <div class="full-report-section">
    <h4>📰 完整投资晨报</h4>
    
    <!-- 关键指标 -->
    <el-descriptions :column="3" border class="metrics-row">
      <el-descriptions-item label="分析股票数">
        {{ latestResultByType[taskType.task_type].result_data?.stocks_analyzed || 0 }}
      </el-descriptions-item>
      <el-descriptions-item label="买入信号">
        <span class="buy-signal">{{ latestResultByType[taskType.task_type].result_data?.buy_signals || 0 }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="卖出信号">
        <span class="sell-signal">{{ latestResultByType[taskType.task_type].result_data?.sell_signals || 0 }}</span>
      </el-descriptions-item>
    </el-descriptions>
    
    <!-- 完整报告内容 -->
    <div class="report-content" v-if="latestResultByType[taskType.task_type].result_data?.full_report">
      <div class="report-header">
        <el-tag type="info">AI生成报告</el-tag>
        <span class="report-length">
          {{ latestResultByType[taskType.task_type].result_data.full_report.length }} 字符
        </span>
      </div>
      <pre class="report-text">{{ latestResultByType[taskType.task_type].result_data.full_report }}</pre>
    </div>
    
    <!-- 如果没有完整报告，显示旧格式 -->
    <div v-else class="fallback-content">
      <p>{{ latestResultByType[taskType.task_type].result_summary }}</p>
    </div>
  </div>
</template>

<style>
.full-report-section {
  margin-top: 24px;
}

.full-report-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #303133;
  border-left: 4px solid #409eff;
  padding-left: 8px;
}

.metrics-row {
  margin-bottom: 16px;
}

.report-content {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e4e7ed;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.report-length {
  font-size: 12px;
  color: #909399;
}

.report-text {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
  word-wrap: break-word;
  background: transparent;
  border: none;
  max-height: 600px;
  overflow-y: auto;
}

.fallback-content {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
}

.buy-signal {
  color: #67c23a;
  font-weight: 600;
}

.sell-signal {
  color: #f56c6c;
  font-weight: 600;
}
</style>
