# Gemini Deep Research 稳定执行手册

## 核心原则

1. **必须使用已连接的标签页**（扩展 badge 显示 ON）
2. **轮询等待，永不 sleep 阻塞**
3. **记录每个步骤的状态，便于恢复**

---

## 执行前检查清单

```
□ 1. Chrome 浏览器已打开
□ 2. OpenClaw 扩展 badge 显示 ON（绿色）
□ 3. 至少有一个标签页处于连接状态
```

### 检查命令
```bash
browser status          # 检查浏览器服务状态
browser tabs            # 列出所有标签页，确认有连接状态
```

---

## 标准执行流程

### 步骤 1: 获取已连接的标签页

```bash
browser tabs
```

**成功标志**: 返回的列表中有一个 `targetId`，且该页面已加载 Gemini

**选择策略**:
- 优先使用标题为 "Google Gemini" 且 URL 为 `https://gemini.google.com/app` 的标签页
- 如果没有，使用任意已连接的标签页，然后导航到 Gemini

### 步骤 2: 聚焦到目标标签页

```bash
browser focus targetId=<targetId>
```

### 步骤 3: 获取页面快照确认状态

```bash
browser snapshot targetId=<targetId> refs=aria
```

**预期状态**: 看到 Gemini 首页，有输入框和"工具"按钮

### 步骤 4: 启用 Deep Research

1. **点击"工具"按钮**
   ```bash
   browser act targetId=<targetId> request='{"kind": "click", "ref": "<工具按钮ref>"}'
   ```

2. **点击 Deep Research 选项**
   ```bash
   browser act targetId=<targetId> request='{"kind": "click", "ref": "<Deep Research选项ref>"}'
   ```

3. **确认状态**
   ```bash
   browser snapshot targetId=<targetId> refs=aria
   ```
   
   **成功标志**: 看到"取消选择'Deep Research'"按钮

### 步骤 5: 输入研究提示词

```bash
browser act targetId=<targetId> request='{"kind": "type", "ref": "<输入框ref>", "text": "<研究提示词>"}'
```

### 步骤 6: 发送请求

```bash
browser act targetId=<targetId> request='{"kind": "press", "key": "Enter"}'
```

### 步骤 7: 确认研究方案已生成

```bash
browser snapshot targetId=<targetId> refs=aria
```

**预期状态**: 
- 看到"这是我拟定的方案"文本
- 有"开始研究"按钮

### 步骤 8: 点击"开始研究"

```bash
browser act targetId=<targetId> request='{"kind": "click", "ref": "<开始研究按钮ref>"}'
```

### 步骤 9: 轮询等待（关键步骤）

**每隔 10-15 秒检查一次页面状态**：

```bash
browser snapshot targetId=<targetId> refs=aria
```

**检查指标**:
1. **研究进行中**: 看到"正在研究 X 个网站…"
2. **分析结果中**: 看到"分析结果中…"
3. **已完成**: 看到"已完成" + 时间戳，且出现完整报告内容

**预期时间**:
- 简单研究：2-3 分钟
- 深度研究：4-6 分钟
- 复杂主题：6-10 分钟

### 步骤 10: 提取完整报告

当状态显示"已完成"后，获取完整页面内容：

```bash
browser snapshot targetId=<targetId> refs=aria limit=15000
```

**提取策略**:
- 报告内容通常在 `generic` 元素下
- 包含多个 `heading` 和 `paragraph` 元素
- 可能有 `table` 元素包含数据

---

## 常见问题与解决方案

### 问题 1: 页面重置/刷新后丢失进度

**原因**: 使用 sleep 阻塞或页面长时间未操作

**解决**: 
- 使用轮询（每10-15秒检查一次）而非 sleep
- 确保浏览器扩展保持连接

### 问题 2: 无法找到"开始研究"按钮

**原因**: Gemini 界面已更新，ref 值变化

**解决**:
- 每次操作后获取新 snapshot
- 使用文本内容定位（如"开始研究"）而非固定 ref

### 问题 3: 研究超时未完成

**判断标准**: 超过 10 分钟仍显示"分析结果中…"

**解决**:
- 继续等待，大型研究可能需要更长时间
- 或发送新消息询问 Gemini 进度

### 问题 4: 报告内容被截断

**解决**: 使用更大的 limit 值获取 snapshot
```bash
browser snapshot targetId=<targetId> refs=aria limit=20000
```

---

## 状态机记录模板

每次执行时记录以下状态：

```yaml
session_id: <会话ID>
target_id: <标签页ID>
start_time: <开始时间>
status_checks:
  - time: <检查时间>
    status: <进行中/分析中/已完成>
    websites_count: <研究的网站数量>
    notes: <备注>
end_time: <完成时间>
duration_minutes: <总耗时>
output_file: <输出文件路径>
```

---

## 示例：投资逻辑分析完整命令序列

```bash
# 1. 检查状态
browser status

# 2. 获取标签页
browser tabs
# 记录 targetId: 690CEE9C9711ED4CB79E4F811373FD06

# 3. 聚焦
browser focus targetId=690CEE9C9711ED4CB79E4F811373FD06

# 4. 输入提示词（已启用 Deep Research）
browser act targetId=690CEE9C9711ED4CB79E4F811373FD06 request='{"kind": "type", "ref": "e208", "text": "请对美股、港股、黄金、比特币进行深度研究..."}'

# 5. 发送
browser act targetId=690CEE9C9711ED4CB79E4F811373FD06 request='{"kind": "press", "key": "Enter"}'

# 6. 开始研究
browser act targetId=690CEE9C9711ED4CB79E4F811373FD06 request='{"kind": "click", "ref": "e465"}'

# 7. 轮询等待（每15秒执行一次）
browser snapshot targetId=690CEE9C9711ED4CB79E4F811373FD06 refs=aria

# 8. 完成后提取完整报告
browser snapshot targetId=690CEE9C9711ED4CB79E4F811373FD06 refs=aria limit=15000
```

---

## 注意事项

1. **不要新开标签页**: 使用 `browser open` 会创建新标签页，可能导致扩展连接不一致
2. **保持扩展活跃**: 不要长时间（>5分钟）不操作页面
3. **定期保存进度**: 如果研究时间长，可每隔几分钟保存一次中间结果
4. **错误恢复**: 如果页面崩溃，从步骤2重新开始，使用相同的 targetId

---

**文档版本**: 1.0
**更新日期**: 2026-02-10
**作者**: Friday
