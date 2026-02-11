<template>
  <div class="crawl-page">
    <div class="page-header">
      <h2 class="page-title">AI投资分析</h2>
      <p class="page-subtitle">OpenCode GLM-4.7 生成的投资研究报告</p>
    </div>

    <el-tabs v-model="activeTab" class="crawl-tabs" type="border-card">
      <!-- 每日投资晨报 -->
      <el-tab-pane label="每日投资晨报" name="daily_market_report">
        <div class="report-container" v-if="latestResultByType['daily_market_report']">
          <el-card class="report-card">
            <template #header>
              <div class="report-header">
                <div class="header-title">
                  <h3>📰 每日投资晨报</h3>
                  <div class="header-meta">
                    <el-tag :type="getStatusTagType(latestResultByType['daily_market_report'].status)" size="small">
                      {{ getStatusText(latestResultByType['daily_market_report'].status) }}
                    </el-tag>
                    <span class="time">
                      <el-icon><Clock /></el-icon>
                      {{ formatDateTime(latestResultByType['daily_market_report'].execution_time) }}
                    </span>
                  </div>
                </div>
                <el-button type="primary" size="small" @click="loadHistory('daily_market_report')">
                  历史记录
                </el-button>
              </div>
            </template>

            <!-- 完整报告内容 -->
            <div class="full-report-content" v-if="latestResultByType['daily_market_report'].result_data?.full_report">
              <div class="markdown-body" v-html="renderMarkdown(latestResultByType['daily_market_report'].result_data.full_report)"></div>
            </div>
            <div v-else class="no-data">
              <el-empty description="暂无报告数据" />
            </div>
          </el-card>

          <!-- 历史记录 -->
          <el-card v-if="taskHistory['daily_market_report']?.length > 0" class="history-card">
            <template #header>
              <h4>历史记录</h4>
            </template>
            <el-table :data="taskHistory['daily_market_report']" size="small" border>
              <el-table-column prop="execution_date" label="日期" width="120" />
              <el-table-column prop="execution_time" label="时间" width="160">
                <template #default="{ row }">{{ formatTime(row.execution_time) }}</template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="showHistoryDetail(row)">查看</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
        <div v-else class="loading-container">
          <el-empty description="加载中..." />
        </div>
      </el-tab-pane>

      <!-- 戴维斯双击扫描 -->
      <el-tab-pane label="戴维斯双击扫描" name="davis_double_scan">
        <div class="report-container" v-if="latestResultByType['davis_double_scan']">
          <el-card class="report-card">
            <template #header>
              <div class="report-header">
                <div class="header-title">
                  <h3>🎯 戴维斯双击股票扫描</h3>
                  <div class="header-meta">
                    <el-tag :type="getStatusTagType(latestResultByType['davis_double_scan'].status)" size="small">
                      {{ getStatusText(latestResultByType['davis_double_scan'].status) }}
                    </el-tag>
                    <span class="time">
                      <el-icon><Clock /></el-icon>
                      {{ formatDateTime(latestResultByType['davis_double_scan'].execution_time) }}
                    </span>
                  </div>
                </div>
                <el-button type="primary" size="small" @click="loadHistory('davis_double_scan')">
                  历史记录
                </el-button>
              </div>
            </template>

            <!-- 完整报告内容 -->
            <div class="full-report-content" v-if="latestResultByType['davis_double_scan'].result_data?.full_report">
              <div class="markdown-body" v-html="renderMarkdown(latestResultByType['davis_double_scan'].result_data.full_report)"></div>
            </div>
            <!-- 候选股票表格 -->
            <div v-else-if="latestResultByType['davis_double_scan'].result_data?.candidates?.length > 0" class="candidates-content">
              <el-table :data="latestResultByType['davis_double_scan'].result_data.candidates" border>
                <el-table-column prop="symbol" label="代码" width="120" />
                <el-table-column prop="name" label="名称" width="200" />
                <el-table-column prop="reason" label="入选理由" />
              </el-table>
            </div>
            <div v-else class="no-data">
              <el-empty description="暂无扫描数据" />
            </div>
          </el-card>

          <!-- 历史记录 -->
          <el-card v-if="taskHistory['davis_double_scan']?.length > 0" class="history-card">
            <template #header><h4>历史记录</h4></template>
            <el-table :data="taskHistory['davis_double_scan']" size="small" border>
              <el-table-column prop="execution_date" label="日期" width="120" />
              <el-table-column prop="execution_time" label="时间" width="160">
                <template #default="{ row }">{{ formatTime(row.execution_time) }}</template>
              </el-table-column>
              <el-table-column prop="result_summary" label="结果摘要" show-overflow-tooltip />
            </el-table>
          </el-card>
        </div>
        <div v-else class="loading-container">
          <el-empty description="加载中..." />
        </div>
      </el-tab-pane>

      <!-- 比特币追踪 -->
      <el-tab-pane label="比特币追踪" name="bitcoin_tracker">
        <div class="report-container" v-if="latestResultByType['bitcoin_tracker']">
          <el-card class="report-card">
            <template #header>
              <div class="report-header">
                <div class="header-title">
                  <h3>₿ 比特币追踪分析</h3>
                  <div class="header-meta">
                    <el-tag :type="getStatusTagType(latestResultByType['bitcoin_tracker'].status)" size="small">
                      {{ getStatusText(latestResultByType['bitcoin_tracker'].status) }}
                    </el-tag>
                    <span class="time">
                      <el-icon><Clock /></el-icon>
                      {{ formatDateTime(latestResultByType['bitcoin_tracker'].execution_time) }}
                    </span>
                  </div>
                </div>
                <el-button type="primary" size="small" @click="loadHistory('bitcoin_tracker')">
                  历史记录
                </el-button>
              </div>
            </template>

            <!-- 完整报告内容 -->
            <div class="full-report-content" v-if="latestResultByType['bitcoin_tracker'].result_data?.full_report">
              <div class="markdown-body" v-html="renderMarkdown(latestResultByType['bitcoin_tracker'].result_data.full_report)"></div>
            </div>
            <!-- 简版数据 -->
            <div v-else-if="latestResultByType['bitcoin_tracker'].result_data" class="btc-simple">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="BTC价格">${{ formatPrice(latestResultByType['bitcoin_tracker'].result_data.btc_price) }}</el-descriptions-item>
                <el-descriptions-item label="24h变化">
                  <span :class="getChangeClass(latestResultByType['bitcoin_tracker'].result_data.price_change_24h)">
                    {{ formatChange(latestResultByType['bitcoin_tracker'].result_data.price_change_24h) }}
                  </span>
                </el-descriptions-item>
              </el-descriptions>
              <div v-if="latestResultByType['bitcoin_tracker'].result_data.signals" class="signals-list">
                <h5>技术信号</h5>
                <el-tag v-for="(signal, idx) in latestResultByType['bitcoin_tracker'].result_data.signals" :key="idx" class="signal-tag">
                  {{ signal }}
                </el-tag>
              </div>
            </div>
            <div v-else class="no-data">
              <el-empty description="暂无分析数据" />
            </div>
          </el-card>

          <!-- 历史记录 -->
          <el-card v-if="taskHistory['bitcoin_tracker']?.length > 0" class="history-card">
            <template #header><h4>历史记录</h4></template>
            <el-table :data="taskHistory['bitcoin_tracker']" size="small" border>
              <el-table-column prop="execution_date" label="日期" width="120" />
              <el-table-column prop="execution_time" label="时间" width="160">
                <template #default="{ row }">{{ formatTime(row.execution_time) }}</template>
              </el-table-column>
              <el-table-column prop="result_summary" label="结果摘要" show-overflow-tooltip />
            </el-table>
          </el-card>
        </div>
        <div v-else class="loading-container">
          <el-empty description="加载中..." />
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 历史详情对话框 -->
    <el-dialog v-model="historyDialog.visible" title="历史报告" width="70%">
      <div v-if="historyDialog.data" class="history-detail">
        <div class="dialog-header">
          <span>{{ formatDateTime(historyDialog.data.execution_time) }}</span>
          <el-tag :type="getStatusTagType(historyDialog.data.status)">{{ getStatusText(historyDialog.data.status) }}</el-tag>
        </div>
        <div class="dialog-content" v-if="historyDialog.data.result_data?.full_report">
          <div class="markdown-body" v-html="renderMarkdown(historyDialog.data.result_data.full_report)"></div>
        </div>
        <div v-else class="dialog-summary">
          {{ historyDialog.data.result_summary }}
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Clock } from '@element-plus/icons-vue'

const activeTab = ref('daily_market_report')
const loading = ref(false)
const latestResults = ref([])
const taskHistory = ref({})
const historyDialog = ref({
  visible: false,
  data: null
})

// 按类型索引的最新结果
const latestResultByType = computed(() => {
  const map = {}
  latestResults.value.forEach(r => {
    map[r.task_type] = r
  })
  return map
})

// 简单的Markdown转HTML
const renderMarkdown = (text) => {
  if (!text) return ''
  
  let html = text
    // 标题
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    // 粗体
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    // 斜体
    .replace(/\*(.*)\*/gim, '<em>$1</em>')
    // 列表
    .replace(/^\- (.*$)/gim, '<li>$1</li>')
    // 段落
    .replace(/\n/gim, '<br>')
  
  // 包裹列表项
  html = html.replace(/(<li>.*<\/li>)/gims, '<ul>$1</ul>')
  
  return html
}

// 获取最新结果
const fetchLatestResults = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/cron-results/latest')
    const result = await response.json()
    if (result.success) {
      latestResults.value = result.data
    }
  } catch (error) {
    console.error('获取最新结果失败:', error)
    ElMessage.error('获取任务数据失败')
  } finally {
    loading.value = false
  }
}

// 加载历史记录
const loadHistory = async (taskType) => {
  if (taskHistory.value[taskType]) return
  
  try {
    const response = await fetch(`/api/cron-results/by-type/${taskType}?limit=10`)
    const result = await response.json()
    if (result.success) {
      taskHistory.value[taskType] = result.data
    }
  } catch (error) {
    console.error('获取历史记录失败:', error)
  }
}

// 显示历史详情
const showHistoryDetail = (row) => {
  historyDialog.value.data = row
  historyDialog.value.visible = true
}

// 格式化时间
const formatTime = (isoString) => {
  if (!isoString) return '-'
  const date = new Date(isoString)
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const formatDateTime = (isoString) => {
  if (!isoString) return '-'
  return new Date(isoString).toLocaleString('zh-CN')
}

// 格式化价格
const formatPrice = (price) => {
  if (!price && price !== 0) return '-'
  return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 格式化涨跌幅
const formatChange = (change) => {
  if (!change && change !== 0) return '-'
  return `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`
}

const getChangeClass = (change) => {
  return change >= 0 ? 'positive' : 'negative'
}

const getStatusTagType = (status) => {
  const map = { 'success': 'success', 'failed': 'danger', 'partial': 'warning' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { 'success': '成功', 'failed': '失败', 'partial': '部分成功' }
  return map[status] || status
}

onMounted(() => {
  fetchLatestResults()
})
</script>

<style scoped>
.crawl-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #303133;
}

.page-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.crawl-tabs {
  background: #fff;
  border-radius: 8px;
}

.report-container {
  padding: 20px;
}

.report-card {
  margin-bottom: 20px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #909399;
}

.header-meta .time {
  display: flex;
  align-items: center;
  gap: 4px;
}

.full-report-content {
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.markdown-body {
  font-size: 15px;
  line-height: 1.8;
  color: #303133;
}

.markdown-body :deep(h1) {
  font-size: 24px;
  font-weight: 600;
  margin: 24px 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
}

.markdown-body :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  margin: 20px 0 12px 0;
  color: #409eff;
}

.markdown-body :deep(h3) {
  font-size: 17px;
  font-weight: 600;
  margin: 16px 0 10px 0;
}

.markdown-body :deep(strong) {
  font-weight: 600;
  color: #1a1a1a;
}

.markdown-body :deep(ul) {
  margin: 12px 0;
  padding-left: 24px;
}

.markdown-body :deep(li) {
  margin: 6px 0;
}

.markdown-body :deep(br) {
  display: block;
  margin: 8px 0;
  content: "";
}

.no-data {
  padding: 40px;
}

.loading-container {
  padding: 60px;
}

.history-card {
  margin-top: 20px;
}

.history-card h4 {
  margin: 0;
}

.candidates-content {
  padding: 16px;
}

.btc-simple {
  padding: 16px;
}

.signals-list {
  margin-top: 16px;
}

.signals-list h5 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #606266;
}

.signal-tag {
  margin: 0 8px 8px 0;
}

.positive {
  color: #67c23a;
  font-weight: 600;
}

.negative {
  color: #f56c6c;
  font-weight: 600;
}

.history-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.dialog-content {
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.dialog-summary {
  padding: 16px;
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
}
</style>
