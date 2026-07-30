# 🛠️ Hermes Skills

> **Hermes Agent** 的可复用技能合集 — 让 AI 不仅能对话，更能动手干活。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📦 已收录技能

| 技能 | 描述 | 状态 |
|:----|:----|:----:|
| [`1panel-management`](skills/1panel-management/) | 通过 REST API 管理 1Panel Linux 面板 | ✅ 稳定 |
| *更多技能持续添加中...* | | |

---

## 🚀 安装

确保已安装 [Hermes Agent](https://hermes-agent.nousresearch.com)，然后：

```bash
# 安装单个技能
hermes skills install https://raw.githubusercontent.com/Satyachen/hermes-skills/main/skills/1panel-management/SKILL.md
```

查看已安装的技能：

```bash
hermes skills list
```

---

## 📖 技能使用

每个技能对应一个 `SKILL.md` 文件，包含：
- **触发条件** — 什么时候自动加载
- **步骤** — 具体执行流程
- **命令行示例** — 可直接复制的命令

加载技能后，在对话中提及对应关键词即可触发。

---

## 🤝 贡献

想加新技能？欢迎提 PR 或 Issue：

1. 在 `skills/` 下创建目录 `your-skill-name/`
2. 包含 `SKILL.md` 主文件
3. 可选的 `scripts/`、`references/`、`templates/` 目录

---

## 🔗 相关链接

- [Hermes Agent 官方文档](https://hermes-agent.nousresearch.com/docs)
- [Hermes Agent GitHub](https://github.com/NousResearch/hermes-agent)
- [我的 Obsidian 知识库](https://github.com/Satyachen/hermes-skills)

---

*由小哥的 GTR9 Pro 提供算力支持 🚀*
