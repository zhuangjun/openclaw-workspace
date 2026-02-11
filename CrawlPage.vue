<template>
  <div class="crawl-page">
    <div class="page-header">
      <h2 class="page-title">投资任务结果</h2>
      <p class="page-subtitle">查看AI投资分析任务的最新执行结果</p>
    </div>

    <el-tabs v-model="activeTab" class="crawl-tabs" type="border-card">
      <!-- 概览Tab - 显示所有任务的最新结果摘要 -->
      <el-tab-pane label="任务概览" name="overview">
        <div class="overview-content">
          <el-row :gutter="20">
            <el-col 
              :xs="24" 
              :sm="12" 
              :md="8" 
              v-for="task in latestResults" 
              :key="task.task_type"
            >
              <el-card 
                class="task-card" 
                :class="getStatusClass(task.status)"
                shadow="hover"
                @click="activeTab = task.task_type"
              >
                <template #header>
                  <div class="task-card-header">
                    <span class="task-name">{{ task.task_name }}</span>
                    <el-tag 
                      :type="getStatusTagType(task.status)" 
                      size="small"
                    >
                      {{ getStatusText(task.status) }}
                    </el-tag>
                  </div>
                </template>
                
                <div class="task-meta">
                  <div class="meta-item">
                    <el-icon><Clock /></el-icon>
                    <span>{{ formatTime(task.execution_time) }}</span>
                  </div>
                  <div class="meta-item" v-if="task.duration_seconds">
                    <el-icon><Timer /></el-icon>
                    <span>耗时 {{ task.duration_seconds }}s</span>
                  </div>
                </div>

                <div class="task-summary" v-if="task.result_summary">
                  <p class="summary-text">{{ task.result_summary }}</p>
                </div>

                <div class="task-preview" v-if="task.result_data">
                  <el-divider />
                  <div class="preview-content">
                    <template v-if="task.task_type === 'daily_market_report'">
                      <div class="stat-row">
                        <span class="stat-label">分析股票:</span>
                        <span class="stat-value">{{ task.result_data.stocks_analyzed || 0 }}</span>
                      </div>
                      <div class="stat-row">
                        <span class="stat-label">买入信号:</span>
                        <span class="stat-value buy">{{ task.result_data.buy_signals || 0 }}</span>
                      </div>
                      <div class="stat-row">
                        <span class="stat-label">卖出信号:</span>
                        <span class="stat-value sell">{{ task.result_data.sell_signals || 0 }}</span>
                      </div>
                    </template>
                    
                    <template v-else-if="task.task_type === 'davis_double_scan'">
                      <div class="stat-row">
                        <span class="stat-label">候选股票:</span>
                        <span class="stat-value">{{ task.result_data.candidates_found || 0 }}</span>
                      </div>
                      <div v-if="task.result_data.candidates" class="candidate-tags">
                        <el-tag 
                          v-for="(c, idx) in task.result_data.candidates.slice(0, 3)" 
                          :key="idx"
                          size="small"
                          class="candidate-tag"
                        >
                          {{ c.symbol || c }}
                        </el-tag>
                      </div>
                    </template>
                    
                    <template v-else-if="task.task_type === 'bitcoin_tracker'">
                      <div class="stat-row">
                        <span class="stat-label">BTC价格:</span>
                        <span class="stat-value">${{ formatPrice(task.result_data.btc_price) }}</span>
                      </div>
                      <div class="stat-row">
                        <span class="stat-label">24h变化:</span>
                        <span :class="getChangeClass(task.result_data.price_change_24h)">
                          {{ formatChange(task.result_data.price_change_24h) }}
                        </span>
                      </div>
                      <div v-if="task.result_data.signals" class="signal-tags">
                        <el-tag 
                          v-for="(s, idx) in task.result_data.signals.slice(0, 2)" 
                          :key="idx"
                          size="small"
                          type="warning"
                          class="signal-tag"
                        >
                          {{ s }}
                        </el-tag>
                      </div>
                    </template>
                  </div>
                </div>

                <div class="card-footer">
                  <el-button type="primary" size="small" text>
                    查看详情 <el-icon><ArrowRight /></el-icon>
                  </el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <el-empty 
            v-if="latestResults.length === 0 && !loading" 
            description="暂无任务数据"
          />
        </div>
      </el-tab-pane>

      <!-- 各任务的详细Tab - 显示完整结果 -->
      <el-tab-pane 
        v-for="taskType in taskTypes" 
        :key="taskType.task_type"
        :label="taskType.task_name" 
        :name="taskType.task_type"
      >
        <div class="task-detail-content" v-if="latestResultByType[taskType.task_type]">
          <el-card class="detail-card">
            <template #header>
              <div class="detail-header">
                <div class="header-left">
                  <h3>{{ taskType.task_name }}</h3>
                  <div class="header-meta">
                    <el-tag :type="getStatusTagType(latestResultByType[taskType.task_type].status)" size="small">
                      {{ getStatusText(latestResultByType[taskType.task_type].status) }}
                    </el-tag>
                    <span class="execution-time">
                      <el-icon><Clock /></el-icon>
                      {{ formatDateTime(latestResultByType[taskType.task_type].execution_time) }}
                    </span>
                    <span v-if="latestResultByType[taskType.task_type].duration_seconds" class="duration">
                      <el-icon><Timer /></el-icon>
                      {{ latestResultByType[taskType.task_type].duration_seconds }}s
                    </span>
                  </div>
                </div>
                <el-button 
                  type="primary" 
                  size="small"
                  @click="loadHistory(taskType.task_type)"
                >
                  查看历史
                </el-button>
              </div>
            </template>

            <!-- 结果摘要 -->
            <div class="detail-section" v-if="latestResultByType[taskType.task_type].result_summary">
              <h4>执行摘要</h4>
              <p class="summary-paragraph">{{ latestResultByType[taskType.task_type].result_summary }}</p>
            </div>

            <!-- 详细结果数据 -->
            <div class="detail-section" v-if="latestResultByType[taskType.task_type].result_data">
              <h4>详细结果</h4>
              
              <!-- 每日投资晨报格式 -->
              <template v-if="taskType.task_type === 'daily_market_report'">
                <el-descriptions :column="3" border>
                  <el-descriptions-item label="分析股票数">
                    {{ latestResultByType[taskType.task_type].result_data.stocks_analyzed || 0 }}
                  </el-descriptions-item>
                  <el-descriptions-item label="买入信号">
                    <span class="buy-signal">{{ latestResultByType[taskType.task_type].result_data.buy_signals || 0 }}</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="卖出信号">
                    <span class="sell-signal">{{ latestResultByType[taskType.task_type].result_data.sell_signals || 0 }}</span>
                  </el-descriptions-item>
                </el-descriptions>
                
                <div v-if="latestResultByType[taskType.task_type].result_data.market_sentiment" class="sentiment-badge">
                  市场情绪: 
                  <el-tag :type="latestResultByType[taskType.task_type].result_data.market_sentiment === 'bullish' ? 'success' : 'danger'">
                    {{ latestResultByType[taskType.task_type].result_data.market_sentiment === 'bullish' ? '看涨' : '看跌' }}
                  </el-tag>
                </div>
              </template>

              <!-- 戴维斯双击扫描格式 -->
              <template v-else-if="taskType.task_type === 'davis_double_scan'">
                <div class="candidates-section">
                  <div class="section-header">
                    <span>发现 {{ latestResultByType[taskType.task_type].result_data.candidates_found || 0 }} 只候选股票</span>
                  </div>
                  <el-table 
                    v-if="latestResultByType[taskType.task_type].result_data.candidates"
                    :data="latestResultByType[taskType.task_type].result_data.candidates" 
                    border
                    size="small"
                  >
                    <el-table-column prop="symbol" label="代码" width="120" />
                    <el-table-column prop="name" label="名称" width="180" />
                    <el-table-column prop="reason" label="入选理由" />
                  </el-table>
                </div>
              </template>

              <!-- 比特币追踪格式 -->
              <template v-else-if="taskType.task_type === 'bitcoin_tracker'">
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="当前价格">
                    ${{ formatPrice(latestResultByType[taskType.task_type].result_data.btc_price) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="24小时变化">
                    <span :class="getChangeClass(latestResultByType[taskType.task_type].result_data.price_change_24h)">
                      {{ formatChange(latestResultByType[taskType.task_type].result_data.price_change_24h) }}
                    </span>
                  </el-descriptions-item>
                </el-descriptions>
                
                <div v-if="latestResultByType[taskType.task_type].result_data.signals" class="signals-section">
                  <h5>技术信号</h5>
                  <div class="signal-list">
                    <el-tag 
                      v-for="(signal, idx) in latestResultByType[taskType.task_type].result_data.signals" 
                      :key="idx"
                      :type="signal.includes('卖出') || signal.includes('跌破') ? 'danger' : 'success'"
                      class="signal-item"
                    >
                      {{ signal }}
                    </el-tag>
                  </div>
                </div>
              </template>

              <!-- 通用JSON展示 -->
              <template v-else>
                <pre class="json-content">{{ JSON.stringify(latestResultByType[taskType.task_type].result_data, null, 2) }}</pre>
              </template>
            </div>

            <!-- 错误信息 -->
            <div class="detail-section" v-if="latestResultByType[taskType.task_type].error_message">
              <h4>错误信息</h4>
              <el-alert
                :title="latestResultByType[taskType.task_type].error_message"
                type="error"
                :closable="false"
                show-icon
              />
            </div>
          </el-card>

          <!-- 历史记录 -->
          <el-card v-if="taskHistory[taskType.task_type] && taskHistory[taskType.task_type].length > 0" class="history-card">
            <template #header>
              <h4>历史执行记录</h4>
            </template>
            <el-table :data="taskHistory[taskType.task_type]" size="small" border>
              <el-table-column prop="execution_date" label="日期" width="120" />
              <el-table-column prop="execution_time" label="时间" width="160">
                <template #default="{ row }">
                  {{ formatTime(row.execution_time) }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusTagType(row.status)" size="small">
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="result_summary" label="结果摘要" show-overflow-tooltip />
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Clock, Timer, ArrowRight } from '@element-plus/icons-vue'

const activeTab = ref('overview')
const loading = ref(false)
const latestResults = ref([])
const taskTypes = ref([])
const taskHistory = ref({})

// 计算属性：按类型索引的最新结果
const latestResultByType = computed(() => {
  const map = {}
  latestResults.value.forEach(r => {
    map[r.task_type] = r
  })
  return map
})

// 获取任务类型列表
const fetchTaskTypes = async () => {
  try {
    const response = await fetch('/api/cron-results/task-types')
    const result = await response.json()
    if (result.success) {
      taskTypes.value = result.data
    }
  } catch (error) {
    console.error('获取任务类型失败:', error)
  }
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

// 格式化时间
const formatTime = (isoString) => {
  if (!isoString) return '-'
  const date = new Date(isoString)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化日期时间
const formatDateTime = (isoString) => {
  if (!isoString) return '-'
  const date = new Date(isoString)
  return date.toLocaleString('zh-CN')
}

// 格式化价格
const formatPrice = (price) => {
  if (!price && price !== 0) return '-'
  return price.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// 格式化涨跌幅
const formatChange = (change) => {
  if (!change && change !== 0) return '-'
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

// 涨跌幅样式
const getChangeClass = (change) => {
  if (!change && change !== 0) return ''
  return change >= 0 ? 'positive-change' : 'negative-change'
}

// 状态样式
const getStatusClass = (status) => {
  return {
    'status-success': status === 'success',
    'status-failed': status === 'failed',
    'status-partial': status === 'partial'
  }
}

const getStatusTagType = (status) => {
  const map = {
    'success': 'success',
    'failed': 'danger',
    'partial': 'warning'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    'success': '成功',
    'failed': '失败',
    'partial': '部分成功'
  }
  return map[status] || status
}

onMounted(() => {
  fetchTaskTypes()
  fetchLatestResults()
})
</script>

<style scoped>
.crawl-page {
  padding: 20px;
  max-width: 1400px;
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

.overview-content {
  padding: 20px;
}

.task-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.task-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.task-card.status-success {
  border-left: 4px solid #67c23a;
}

.task-card.status-failed {
  border-left: 4px solid #f56c6c;
}

.task-card.status-partial {
  border-left: 4px solid #e6a23c;
}

.task-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-name {
  font-weight: 600;
  font-size: 16px;
}

.task-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #909399;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-summary {
  margin: 12px 0;
}

.summary-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.task-preview {
  margin-top: 12px;
}

.preview-content {
  padding: 8px 0;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.stat-label {
  color: #909399;
}

.stat-value {
  font-weight: 600;
  color: #303133;
}

.stat-value.buy {
  color: #67c23a;
}

.stat-value.sell {
  color: #f56c6c;
}

.candidate-tags, .signal-tags {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.candidate-tag, .signal-tag {
  margin: 0;
}

.card-footer {
  margin-top: 12px;
  text-align: right;
}

.task-detail-content {
  padding: 20px;
}

.detail-card {
  margin-bottom: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left h3 {
  margin: 0 0 8px 0;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #909399;
}

.header-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.detail-section {
  margin-top: 24px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #303133;
  border-left: 4px solid #409eff;
  padding-left: 8px;
}

.detail-section h5 {
  margin: 16px 0 8px 0;
  font-size: 14px;
  color: #606266;
}

.summary-paragraph {
  font-size: 15px;
  line-height: 1.8;
  color: #606266;
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin: 0;
}

.sentiment-badge {
  margin-top: 16px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.candidates-section, .signals-section {
  margin-top: 16px;
}

.section-header {
  margin-bottom: 12px;
  font-size: 14px;
  color: #606266;
}

.signal-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.signal-item {
  margin: 0;
}

.buy-signal {
  color: #67c23a;
  font-weight: 600;
}

.sell-signal {
  color: #f56c6c;
  font-weight: 600;
}

.positive-change {
  color: #67c23a;
  font-weight: 600;
}

.negative-change {
  color: #f56c6c;
  font-weight: 600;
}

.json-content {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.6;
}

.history-card {
  margin-top: 20px;
}
</style>
