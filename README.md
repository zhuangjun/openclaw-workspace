# Workspace

个人工作空间，按功能组织。

## 目录说明

| 目录 | 用途 |
|------|------|
| `projects/` | 代码项目，每个子目录是一个独立项目 |
| `documents/` | 文档资料，按类型分子目录 |
| `reports/` | 各类报告（财报、分析等），按年份组织 |
| `archive/` | 已完成或废弃的项目/文档 |
| `memory/` | AI 记忆文件（由系统自动管理） |
| `tmp/` | 临时文件，可随时清理 |

## Git 使用

```bash
# 查看状态
git status

# 添加更改
git add .
git commit -m "描述"

# 查看历史
git log --oneline
```

## 命名规范

- 项目目录：小写字母，短横线连接（如 `my-project`）
- 文档：日期前缀（如 `2026-02-04-会议记录.md`）
- 报告：`YYYYMMDD-类型.扩展名`
