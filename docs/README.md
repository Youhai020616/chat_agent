# 项目文档

> 基于 LangGraph 的多 Agent SEO & GEO 优化系统 - 文档中心

## 📚 文档结构

```
docs/
├── README.md                          # 本文件，文档导航
├── architecture/                      # 系统架构文档
│   └── project-overview.md           # 项目概览、技术栈与开发路线图
├── methodology/                       # 方法论与理论文档
│   └── geo.md                        # GEO（生成式引擎优化）完整方法论
└── guides/                           # 实施指南与操作手册
    └── (待补充)
```

## 🚀 快速开始

1. **了解项目** - 阅读 [`architecture/project-overview.md`](architecture/project-overview.md) 了解：
   - 项目目标与整体架构
   - LangGraph 节点设计
   - SEO & GEO 子系统规划
   - 开发路线图 (M0-M7)

2. **学习方法论** - 阅读 [`methodology/geo.md`](methodology/geo.md) 深入理解：
   - GEO 核心概念与趋势 
   - 与传统 SEO 的区别
   - 实施策略与最佳实践
   - 法律与道德考量

3. **开发指南** - 参考 [`../WARP.md`](../WARP.md) 获取：
   - 开发环境配置
   - 命令行工具使用
   - 代码规范与架构约定

## 📖 文档详情

### 架构文档
- **[项目概览](architecture/project-overview.md)** - 系统总体设计与技术实现路径
- **[系统设计](architecture/system-design.md)** - 接口风格（REST/Realtime/GraphQL）、后端 + Worker + 数据库（Supabase）设计、部署与观测建议
- **[数据模型与 RLS](architecture/data-model.md)** - 表结构、索引与 RLS 策略（Supabase）
- **[成本与容量](architecture/cost-and-capacity.md)** - 成本优先与扩展路径

### 方法论文档  
- **[GEO 方法论](methodology/geo.md)** - 21万字生成式引擎优化白皮书，涵盖：
  - GEO 基础理论与背景
  - 核心技术（LLM、RAG、知识图谱）
  - 内容策略与优化技巧
  - 行业影响与未来趋势

### 操作指南
- **[Supabase 云端托管与 Mock 数据导入](guides/supabase-setup.md)**
- **[KPI 仪表盘上线规划](guides/kpi-dashboard.md)**

## 🤝 贡献指南

欢迎为项目文档做出贡献：

1. **更新文档** - 发现错误或需要补充的内容，请直接提交 PR
2. **新增指南** - 在 `guides/` 目录下添加操作手册和最佳实践
3. **保持同步** - 当代码架构发生变更时，请同步更新相关文档

## 📝 版本说明

- 项目文档随代码同步演进
- 重大架构变更会在文档中体现版本标记
- `methodology/geo.md` 基于外部权威资料，定期更新行业最新趋势

---

> 💡 提示：建议按照上述顺序阅读文档，以获得最佳的理解体验。
