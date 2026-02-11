<template>
  <div class="cron-tasks-page">
    <div class="page-header">
      <h2 class="page-title">定时任务监控</h2>
      <p class="page-subtitle">查看投资相关定时任务的执行状态和结果</p>
    </div>

    <el-tabs v-model="activeTab" class="cron-tabs" type="border-card">
      <!-- 概览Tab - 显示所有任务的最新状态 -->
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
                
                <div class="task-info">
                  <div class="info-row">
                    <span class="label">执行日期:</span>
                    <span class="value">{{ task.execution_date }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">执行时间:</span>
                    <span class="value">{{ formatTime(task.execution_time) }}</span>
                  </div>
                  <div class="info-row" v-if="task.duration_seconds">
                    <span class="label">耗时:</span>
                    <span class="value">{{ task.duration_seconds }}秒</span>
                  </div>
                  <div class="info-row" v-if="task.items_processed > 0">
                    <span class="label">处理项目:</span>
                    <span class="value">
                      {{ task.items_succeeded }}成功
                      <span v-if="task.items_failed > 0" class="error-count">
                        / {{ task.items_failed }}失败
                      </span>
                    </span>
                  </div>
                </div>

                <div class="task-summary" v-if="task.result_summary">
                  <el-divider />
                  <p class="summary-text">{{ task.result_summary }}</p>
                </div>

                <div class="task-error" v-if="task.error_message">
                  <el-divider />
                  <el-alert
                    :title="task.error_message"
                    type="error"
                    :closable="false"
                    show-icon
                  />
                </div>

                <div class="task-actions">
                  <el-button 
                    type="primary" 
                    size="small"
                    @click="viewTaskHistory(task.task_type)"
                  >
                    查看历史
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

      <!-- 各任务的详细Tab -->
      <el-tab-pane 
        v-for="taskType in taskTypes" 
        :key="taskType.task_type"
        :label="taskType.task_name" 
        :name="taskType.task_type"
      >
        <div class="task-detail-content">
          <div class="detail-header">
            <h3>{{ taskType.task_name }}</h3>
            <div class="last-run-info" v-if="taskType.last_execution">
              <span>最后执行: {{ formatDateTime(taskType.last_execution) }}</span>
              <el-tag 
                :type="getStatusTagType(taskType.last_status)" 
                size="small"
                class="status-tag"
              >
                {{ getStatusText(taskType.last_status) }}
              </el-tag>
            </div>
          </div>

          <el-table 
            :data="taskHistory[taskType.task_type] || []" 
            v-loading="historyLoading[taskType.task_type]"
            stripe
            border
          >
            <el-table-column prop="execution_date" label="执行日期" width="120" />
            <el-table-column prop="execution_time" label="执行时间" width="180">
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
            <el-table-column prop="duration_seconds" label="耗时" width="100">
              <template #default="{ row }">
                {{ row.duration_seconds ? row.duration_seconds + '秒' : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="items_processed" label="处理数" width="100">
              <template #default="{ row }">
                <span v-if="row.items_processed > 0">
                  {{ row.items_succeeded }}/{{ row.items_processed }}
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="result_summary" label="结果摘要" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button 
                  type="primary" 
                  size="small"
                  @click="viewDetail(row.id)"
                >
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialog.visible"
      title="任务执行详情"
      width="60%"
    >
      <div v-if="detailDialog.data" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务名称">
            {{ detailDialog.data.task_name }}
          </el-descriptions-item>
          <el-descriptions-item label="任务类型">
            {{ detailDialog.data.task_type }}
          </el-descriptions-item>
          <el-descriptions-item label="执行日期">
            {{ detailDialog.data.execution_date }}
          </el-descriptions-item>
          <el-descriptions-item label="执行时间">
            {{ formatTime(detailDialog.data.execution_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(detailDialog.data.status)">
              {{ getStatusText(detailDialog.data.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="耗时">
            {{ detailDialog.data.duration_seconds ? detailDialog.data.duration_seconds + '秒' : '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-section" v-if="detailDialog.data.result_summary">
          <h4>执行摘要</h4>
          <p>{{ detailDialog.data.result_summary }}</p>
        </div>

        <div class="detail-section" v-if="detailDialog.data.error_message">
          <h4>错误信息</h4>
          <el-alert
            :title="detailDialog.data.error_message"
            type="error"
            :closable="false"
            show-icon
          />
        </div>

        <div class="detail-section" v-if="detailDialog.data.result_data">
          <h4>详细结果</h4>
          <pre class="json-content">{{ JSON.stringify(detailDialog.data.result_data, null, 2) }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('overview')
const loading = ref(false)
const latestResults = ref([])
const taskTypes = ref([])
const taskHistory = ref({})
const historyLoading = ref({})
const detailDialog = ref({
  visible: false,
  data: null
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

// 获取任务历史
const fetchTaskHistory = async (taskType) => {
  if (taskHistory.value[taskType]) return
  
  historyLoading.value[taskType] = true
  try {
    const response = await fetch(`/api/cron-results/by-type/${taskType}?limit=30`)
    const result = await response.json()
    if (result.success) {
      taskHistory.value[taskType] = result.data
    }
  } catch (error) {
    console.error('获取任务历史失败:', error)
  } finally {
    historyLoading.value[taskType] = false
  }
}

// 查看任务历史
const viewTaskHistory = (taskType) => {
  activeTab.value = taskType
  fetchTaskHistory(taskType)
}

// 查看详情
const viewDetail = async (id) => {
  try {
    const response = await fetch(`/api/cron-results/${id}`)
    const result = await response.json()
    if (result.success) {
      detailDialog.value.data = result.data
      detailDialog.value.visible = true
    }
  } catch (error) {
    console.error('获取详情失败:', error)
    ElMessage.error('获取详情失败')
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

// 监听Tab切换
watch(activeTab, (newTab) => {
  if (newTab !== 'overview') {
    fetchTaskHistory(newTab)
  }
})

onMounted(() => {
  fetchTaskTypes()
  fetchLatestResults()
})
</script>

<style scoped>
.cron-tasks-page {
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

.cron-tabs {
  background: #fff;
  border-radius: 8px;
}

.overview-content {
  padding: 20px;
}

.task-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.task-card:hover {
  transform: translateY(-2px);
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

.task-info {
  margin: 16px 0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-row .label {
  color: #909399;
}

.info-row .value {
  color: #303133;
  font-weight: 500;
}

.error-count {
  color: #f56c6c;
}

.task-summary {
  margin: 16px 0;
}

.summary-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.task-error {
  margin: 16px 0;
}

.task-actions {
  margin-top: 16px;
  text-align: right;
}

.task-detail-content {
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-header h3 {
  margin: 0;
}

.last-run-info {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #909399;
  font-size: 14px;
}

.detail-content {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-section {
  margin-top: 20px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #303133;
}

.json-content {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.6;
}
</style>
