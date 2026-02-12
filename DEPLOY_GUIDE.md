# Friday Reports 数据库重构 - 部署指南

## 已完成的工作

### 1. 数据库设计 ✅
- 创建了 `reports` 表存储报告内容
- 创建了 `report_categories` 表存储分类信息
- 添加了索引和触发器

### 2. API 端点实现 ✅
- `GET /api/reports` - 列出报告，支持分页和筛选
- `GET /api/reports/:id` - 获取单个报告详情
- `POST /api/reports` - 创建/更新报告（需鉴权）
- `GET /api/reports/categories` - 获取分类列表
- `GET /api/reports/stats` - 获取统计数据

### 3. 前端页面改造 ✅
- 完全重写为数据库驱动
- 支持分页（每页9条 = 3天 x 3份）
- 支持按类别和时间筛选
- 使用 marked.js 渲染 Markdown

### 4. 同步脚本更新 ✅
- `sync_report_api.sh` - 调用 API 同步报告
- 自动检测类别、日期、标题
- 支持试运行模式

## 部署步骤

### 步骤1: 执行数据库迁移
```bash
ssh ubuntu@43.134.37.253
cd ~/friday
sqlite3 friday.db < migrations/create_reports_table.sql
```

### 步骤2: 更新 API 代码
```bash
# 备份旧文件
cp ~/friday/api/routes/reports.py ~/friday/api/routes/reports_old.py

# 上传新文件 (已包含在 friday_update.tar.gz 中)
cd ~/friday/updates
tar xzf friday_update.tar.gz
cp friday_api_reports.py ~/friday/api/routes/reports.py
```

### 步骤3: 设置环境变量
```bash
# 编辑 ~/.bashrc 或创建 ~/.env
export FRIDAY_API_TOKEN="your-secure-token-here"
```

### 步骤4: 重启 API 服务
```bash
cd ~/friday/api
# 如果使用 systemd
sudo systemctl restart friday-api

# 或者手动重启
pkill -f "python.*app.py"
nohup python3 app.py > logs/api.log 2>&1 &
```

### 步骤5: 部署前端页面
```bash
cp ~/friday/updates/friday_reports_index.html ~/friday/reports/index.html
```

### 步骤6: 测试 API
```bash
# 获取分类列表
curl https://danielzhuang.xyz/api/reports/categories

# 获取报告列表
curl https://danielzhuang.xyz/api/reports?page=1&per_page=9

# 创建测试报告
curl -X POST https://danielzhuang.xyz/api/reports \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "title": "测试报告",
    "category": "investment_logic",
    "report_date": "2026-02-12",
    "content_md": "# 测试\n这是测试内容"
  }'
```

## 迁移现有报告

### 方法1: 手动导入（推荐少量报告）
```bash
# 使用 sync_report_api.sh 脚本
./sync_report_api.sh ~/friday/reports/investment_logic_2026-02-11.md investment_logic
```

### 方法2: 批量导入
```bash
# 创建批量导入脚本
for file in ~/friday/reports/*.md; do
    ./sync_report_api.sh "$file"
done
```

### 方法3: SQL 直接导入（大量数据）
```sql
-- 从现有数据或文件导入
INSERT INTO reports (title, category, report_date, content_md, source, status)
SELECT title, 'investment_logic', task_date, content, 'migration', 'published'
FROM task_results WHERE task_type = 'investment_logic';
```

## 回滚方案

如果出现问题，可以回滚到文件扫描方式：

```bash
# 恢复旧 API
cp ~/friday/api/routes/reports_old.py ~/friday/api/routes/reports.py

# 恢复旧前端（从 git 恢复）
cd ~/friday/reports
git checkout index.html

# 重启服务
```

## 文件清单

### 新文件
- `~/friday/api/routes/reports.py` - 新的 API 路由
- `~/friday/reports/index.html` - 新的前端页面
- `~/friday/migrations/create_reports_table.sql` - 数据库迁移
- `~/friday/scripts/sync_report_api.sh` - 新的同步脚本

### 备份文件
- `~/friday/api/routes/reports_old.py` - 旧 API 备份

## API Token 安全

1. 使用强随机字符串作为 Token
2. 通过环境变量传递，不要硬编码
3. 考虑添加 Token 轮换机制
4. 生产环境使用 HTTPS

## 监控

```bash
# 检查 API 状态
curl https://danielzhuang.xyz/api/health

# 查看日志
tail -f ~/friday/api/logs/api.log

# 数据库统计
sqlite3 ~/friday/friday.db "SELECT category, COUNT(*) FROM reports GROUP BY category;"
```
