# Friday Reports 数据库重构项目

## 项目概述

将 Friday Reports 系统从静态文件扫描架构重构为数据库驱动架构。

## 已完成的变更

### 1. 数据库设计
- ✅ 创建 `reports` 表存储报告内容
- ✅ 创建 `report_categories` 表存储分类信息
- ✅ 添加索引优化查询性能
- ✅ 添加更新时间触发器
- ✅ 初始化8个报告分类

**文件**: `migrations/create_reports_table.sql`

### 2. API 端点
- ✅ `GET /api/reports` - 列出报告，支持分页和筛选
- ✅ `GET /api/reports/:id` - 获取单个报告详情
- ✅ `POST /api/reports` - 创建/更新报告（需鉴权）
- ✅ `GET /api/reports/categories` - 获取分类列表
- ✅ `GET /api/reports/stats` - 获取统计数据
- ✅ 向后兼容旧路由 `/list` 和 `/scan`

**文件**: `api/routes/reports.py` (已更新)

### 3. 前端页面
- ✅ 完全重写为数据库驱动
- ✅ 支持分页（每页9条 = 3天 x 3份）
- ✅ 支持按类别筛选
- ✅ 支持按时间范围筛选（今日/本周/本月/全部）
- ✅ 使用 marked.js 渲染 Markdown
- ✅ 模态框展示报告详情
- ✅ 响应式设计

**文件**: `reports/index.html` (已重写)

### 4. 同步脚本
- ✅ `sync_report_api.sh` - 调用 API 同步报告
- ✅ 自动检测类别、日期、标题
- ✅ 支持试运行模式 `--dry-run`
- ✅ 详细的命令行帮助

**文件**: 
- `scripts/sync_report_api.sh` (新增)
- `scripts/sync_report.sh` (更新为转发到新脚本)

### 5. Deep Research Skill 更新
- ✅ 添加数据同步步骤到工作流程
- ✅ 提供类别映射表
- ✅ 提供同步命令示例
- ✅ 更新 SKILL.md 和工作流指南

**文件**:
- `skills/gemini-deep-research/SKILL.md` (已更新)
- `skills/gemini-deep-research/references/workflow-guide.md` (已更新)

## 部署步骤

### 方式1: 自动部署（推荐）

在服务器上执行：

```bash
# 1. 上传更新包
scp friday_update.tar.gz ubuntu@43.134.37.253:~/friday/updates/

# 2. SSH 到服务器
ssh ubuntu@43.134.37.253

# 3. 解压并执行部署脚本
cd ~/friday/updates
tar xzf friday_update.tar.gz
cd ~/friday
bash updates/deploy_friday_db.sh
```

### 方式2: 手动部署

```bash
# 1. 数据库迁移
sqlite3 ~/friday/friday.db < ~/friday/migrations/create_reports_table.sql

# 2. 备份并更新 API
cp ~/friday/api/routes/reports.py ~/friday/api/routes/reports_old.py
cp ~/friday/updates/friday_api_reports.py ~/friday/api/routes/reports.py

# 3. 备份并更新前端
cp ~/friday/reports/index.html ~/friday/reports/index_old.html
cp ~/friday/updates/friday_reports_index.html ~/friday/reports/index.html

# 4. 安装同步脚本
cp ~/friday/updates/sync_report_api.sh ~/friday/scripts/
chmod +x ~/friday/scripts/sync_report_api.sh

# 5. 设置环境变量
echo 'export FRIDAY_API_TOKEN="your-secure-token"' >> ~/.bashrc
source ~/.bashrc

# 6. 重启 API 服务
pkill -f "python.*app.py"
cd ~/friday/api && nohup python3 app.py > ../logs/api.log 2>&1 &
```

## 测试验证

### API 测试
```bash
# 获取分类列表
curl https://danielzhuang.xyz/api/reports/categories

# 获取报告列表
curl "https://danielzhuang.xyz/api/reports?page=1&per_page=9"

# 获取统计数据
curl https://danielzhuang.xyz/api/reports/stats

# 创建测试报告
curl -X POST https://danielzhuang.xyz/api/reports \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "title": "测试报告",
    "category": "investment_logic",
    "report_date": "2026-02-12",
    "content_md": "# 测试内容"
  }'
```

### 页面测试
访问 https://danielzhuang.xyz/Friday/reports/ 验证：
- 报告列表加载正常
- 分页功能正常
- 筛选功能正常
- 报告详情弹窗正常
- Markdown 渲染正常

## 数据迁移

### 迁移现有 Markdown 报告
```bash
# 批量导入所有现有报告
for file in ~/friday/reports/*.md; do
    ~/friday/scripts/sync_report_api.sh "$file"
done
```

### 从 task_results 迁移
```sql
-- 将历史任务结果导入 reports 表
INSERT INTO reports (title, category, report_date, content_md, source, status, created_at)
SELECT 
    title,
    CASE task_type
        WHEN 'morning_report' THEN 'morning_brief'
        WHEN 'davies_double' THEN 'davis_double'
        ELSE task_type
    END as category,
    task_date as report_date,
    content as content_md,
    'task_migration' as source,
    'published' as status,
    created_at
FROM task_results 
WHERE task_type IN ('morning_report', 'davies_double', 'investment_logic');
```

## 回滚方案

如果出现问题，可快速回滚：

```bash
# 恢复旧 API
cp ~/friday/api/routes/reports_old.py ~/friday/api/routes/reports.py

# 恢复旧前端
cp ~/friday/reports/index_old.html ~/friday/reports/index.html

# 重启服务
pkill -f "python.*app.py"
cd ~/friday/api && nohup python3 app.py > ../logs/api.log 2>&1 &
```

## 安全注意事项

1. **API Token**: 生产环境使用强随机字符串，通过环境变量传递
2. **HTTPS**: 确保所有 API 调用通过 HTTPS
3. **输入验证**: API 已添加基本的输入验证
4. **SQL 注入防护**: 使用参数化查询

## 性能优化

- 数据库索引已添加 (`idx_reports_category_date` 等)
- 列表接口限制返回内容长度（content_md 截断至500字符）
- 分页支持，默认每页9条
- 支持按日期和类别筛选，减少数据传输

## 监控和维护

```bash
# 查看 API 日志
tail -f ~/friday/logs/api.log

# 数据库统计
sqlite3 ~/friday/friday.db "SELECT category, COUNT(*) FROM reports GROUP BY category;"

# 检查最近报告
sqlite3 ~/friday/friday.db "SELECT title, report_date FROM reports ORDER BY report_date DESC LIMIT 5;"
```

## 文件清单

### 新增文件
- `api/routes/reports.py` - 新的数据库驱动 API
- `reports/index.html` - 新的前端页面
- `migrations/create_reports_table.sql` - 数据库迁移脚本
- `scripts/sync_report_api.sh` - API 同步脚本
- `updates/deploy_friday_db.sh` - 自动部署脚本

### 修改文件
- `skills/gemini-deep-research/SKILL.md` - 添加同步步骤
- `skills/gemini-deep-research/references/workflow-guide.md` - 更新工作流
- `skills/friday-report-sync/scripts/sync_report.sh` - 转发到新脚本

### 备份文件（部署时自动创建）
- `api/routes/reports_old.py` - 旧 API 备份
- `reports/index_old.html` - 旧前端备份

## 后续优化建议

1. 添加全文搜索功能 (SQLite FTS)
2. 添加报告缓存机制
3. 实现报告版本控制
4. 添加报告评论/笔记功能
5. 添加报告订阅和通知
