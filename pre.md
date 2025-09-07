# 基于 LangGraph 的多 Agent SEO & GEO 优化系统

> 本文档描述项目整体架构、关键组件、技术栈及开发路线图，帮助所有贡献者快速理解系统设计与实现思路。

---

## 项目概述

本项目利用LangGraph框架构建一个智能化的SEO和GEO优化工具，通过多个专业化的AI代理协作，为网站提供全面的搜索引擎优化和地理位置优化服务。

## 系统架构

### 核心Agent组件

1. **关键词分析Agent**
   - 关键词研究和竞争分析
   - 搜索量和难度评估
   - 长尾关键词挖掘

2. **内容优化Agent**
   - 页面内容SEO分析
   - 标题和描述优化建议
   - 内容结构改进方案

3. **技术SEO Agent**
   - 网站技术问题检测
   - 页面速度优化建议
   - 移动端适配检查

4. **地理定位优化Agent**
   - 本地搜索优化
   - Google My Business优化
   - 地理关键词策略

5. **链接建设Agent**
   - 外链机会识别
   - 内链结构优化
   - 链接质量评估

### 工作流程

```python
# 基本工作流示例
def seo_optimization_workflow():
    # 1. 网站分析阶段
    site_analysis = analyze_website()

    # 2. 多Agent并行分析
    keyword_results = keyword_agent.analyze(site_analysis)
    content_results = content_agent.analyze(site_analysis)
    technical_results = technical_agent.analyze(site_analysis)
    geo_results = geo_agent.analyze(site_analysis)

    # 3. 结果整合和优先级排序
    optimization_plan = integrate_results([
        keyword_results, content_results, 
        technical_results, geo_results
    ])

    return optimization_plan
```

## 主要功能特性

- **智能化分析**: 自动识别SEO和GEO优化机会
- **多维度优化**: 覆盖技术、内容、关键词、地理等多个维度
- **实时监控**: 持续跟踪优化效果和排名变化
- **协作决策**: 多Agent协同工作，提供综合优化方案
- **个性化建议**: 基于网站特点和行业特征的定制化建议

## 技术栈

| 领域 | 选型 | 说明 |
|------|------|------|
| 运行时 & 语言 | Python ≥3.10 | 生态成熟、LangGraph 原生支持 |
| 多 Agent 框架 | LangGraph | 用于有状态编排、节点/边定义、并行执行 |
| LLM 接入 | OpenAI / Azure OpenAI | 支持 GPT-4o / GPT-4-Turbo，可按环境切换 |
| Embedding & 向量库 | OpenAI Embedding + ChromaDB | 用于检索式增强（RAG）与知识共享 |
| Web 抓取 | Playwright (Headless) + Requests-HTML | 全面收集站点结构、Meta 数据与性能指标 |
| 数据持久化 | PostgreSQL | 存储抓取结果与优化建议，便于增量更新 |
| 缓存 | Redis | Agent 间共享中间结果，加速重复分析 |
| API 框架 | FastAPI | 暴露 REST/WS 接口，供前端或自动化调用 |
| 任务编排 | Celery + RabbitMQ | 批量站点分析、计划任务 |
| CI / CD | GitHub Actions | 代码质量、单元测试、Docker 构建、部署 |

## 目录结构（建议）

```
chat_agent/
├── agents/                # 各领域 Agent 实现
│   ├── keyword/           # 关键词分析 Agent
│   ├── content/           # 内容优化 Agent
│   ├── technical/         # 技术 SEO Agent
│   ├── geo/               # GEO 优化 Agent
│   └── link/              # 链接建设 Agent
├── graph/                 # LangGraph 流程 / 节点 / 边 定义
├── services/              # 站点抓取、数据存储、RAG、评分等服务层
├── api/                   # FastAPI 入口（REST/WS）
├── cli/                   # 命令行脚本 (invoke / typer)
├── tests/                 # pytest 单元与集成测试
├── scripts/               # 迁移、数据清洗等一次性脚本
├── docker/                # Dockerfile 与 compose 定义
└── pre.md                 # 本说明文档
```

## LangGraph 架构

### 全局共享状态（`SEOState`）
```python path=null start=null
@dataclass
class SEOState:
    target_url: str
    crawl_data: dict | None = None
    keyword_insights: dict | None = None
    content_insights: dict | None = None
    technical_insights: dict | None = None
    geo_insights: dict | None = None
    link_insights: dict | None = None
    optimization_plan: list | None = None
```

### 节点 & 边
| 节点 | 输入 | 输出 | 责任 |
|------|------|------|------|
| `CrawlerNode` | `SEOState.target_url` | `SEOState.crawl_data` | 使用 Playwright 全站抓取，抽取 meta / 速度 / schema 标记 |
| `KeywordAgentNode` | `SEOState.crawl_data` | `SEOState.keyword_insights` | 关键词研究、搜索量、竞争难度、长尾词 |
| `ContentAgentNode` | `SEOState.crawl_data` | `SEOState.content_insights` | 内容结构、标题/描述、TF-IDF / embedding 相似度 |
| `TechnicalAgentNode` | `SEOState.crawl_data` | `SEOState.technical_insights` | 栏目层级、加载性能、Core Web Vitals |
| `GeoAgentNode` | `SEOState.crawl_data` | `SEOState.geo_insights` | NAP 一致性、GMB、地理关键词覆盖 |
| `LinkAgentNode` | `SEOState.crawl_data` | `SEOState.link_insights` | 内/外链质量、失效链接、锚文本分布 |
| `IntegratorNode` | 所有 *insights | `SEOState.optimization_plan` | 合并并按照 Impact/Effort 打分排序 |

并行边：五个 Agent Node 可并行依赖 `CrawlerNode`。

### 时序示意
```
CrawlerNode ─┬─► KeywordAgentNode ─┐
            ├─► ContentAgentNode ─┤
            ├─► TechnicalAgentNode┤
            ├─► GeoAgentNode ─────┼─► IntegratorNode
            └─► LinkAgentNode ────┘
```

## 数据模型
- **CrawlResult**: URL, status, load_time, title, meta_tags, headings, schema_org, images, lighthouse_scores
- **KeywordInsight**: keyword, volume, difficulty, intent, competitor_urls
- **OptimizationAction**: category (content/tech/link/geo), impact (1-5), effort (1-5), recommendation, evidence_url

## 外部集成
1. **Search Volume API** (e.g., Ahrefs / SEMrush) — 获取关键词流量与难度
2. **PageSpeed Insights API** — 获取性能分数
3. **Google My Business API** — 读取/更新 GMB 信息

## GEO 子系统规划
（已在上文阐述——EntityAgent、ContentStructAgent、CitationAgent、SentimentAgent、SERPSpyAgent 以及 Integration & Scoring Node）

---

## SEO 子系统规划
### 目标
1. 提升传统搜索引擎自然流量、排名与转化率。
2. 为 GEO 提供技术健康与权威基石（结构化数据、E-E-A-T 信号）。
3. 监控并量化 SEO KPI：Organic Visits、Avg Rank、CWV、E-E-A-T Score。

### LangGraph 拓扑
```
CrawlerNode ─► TechnicalAuditAgent
             ├► KeywordGapAgent
             ├► CompetitorAgent
             ├► ContentQualityAgent
             ├► LinkAuditAgent
             └─► Integration & Prioritizer ─► SEOActionPlan
```

### 核心 Agent
| Agent | 职责 |
|-------|------|
| TechnicalAuditAgent | Lighthouse + Schema 检查，输出 CWV & 技术修复建议 |
| KeywordGapAgent | GSC & SERP API → 关键词缺口、意图分层 |
| CompetitorAgent | 外链 / SERP Feature 差距分析 |
| ContentQualityAgent | 自动 E-E-A-T 评分，薄弱内容识别 |
| LinkAuditAgent | 内外链分布 & 失效链接检测 |
| Integration & Prioritizer | Impact/Effort 排序，生成 action plan |

### 数据表（PostgreSQL）
- seo_pages(url, keyword, current_rank, intent, cwv)
- backlink_profile(source, target, authority)
- seo_kpis_daily(date, organic_visits, avg_rank, cwv_score, e_e_a_t_score)

---

## 统一开发路线图
| Milestone | 内容 | 周期 |
|-----------|------|-----|
| M0 | 项目初始化：LangGraph 骨架、CI/CD、Docker | 1 周 |
| M1 | Web Crawler + SEOState + 存储层 | 1 周 |
| M2 | GEO 基础：Entity & SERPSpy Agent | 1 周 |
| M3 | SEO 基础：TechnicalAudit & KeywordGap Agent | 1 周 |
| M4 | 完成 GEO 五大 Agent & Integration | 2 周 |
| M5 | 完成 SEO 五大 Agent & Integration | 2 周 |
| M6 | KPI Dashboard + FastAPI/CLI | 1 周 |
| M7 | 前端仪表盘（可选） | 1 周 |

---
| Milestone | 目标 | 关键交付物 |
|-----------|------|-----------|
| M0 | 项目初始化 | LangGraph 骨架、基础目录、CI/CD, Dockerfile |
| M1 | 爬虫 + 全局状态 | CrawlerNode 完成，SEOState 定义，存储层 |
| M2 | 关键词 & 内容 Agent | KeywordAgentNode、ContentAgentNode, Keyword volume API 接入 |
| M3 | 技术 & GEO Agent | TechnicalAgentNode、GeoAgentNode, PageSpeed & GMB API 接入 |
| M4 | 链接 Agent & Integrator | LinkAgentNode、IntegratorNode, 优化计划评分模型 |
| M5 | REST API & CLI | FastAPI endpoints、命令行批量分析 |
| M6 | 前端仪表盘 (可选) | Next.js + Chakra UI, 可视化报告 |

## 部署与运维
- **开发环境**：`docker compose up` 运行 Postgres、Redis、localstack (S3 用) 等依赖
- **生产环境**：Kubernetes / ECS 部署，使用 Helm / Terraform 进行基础设施管理
- **监控**：Prometheus + Grafana，集中日志 Loki；关键指标：Agent 执行时长、API 延迟、计划完成率

---

> 本文档为持续演进文档。任何架构或技术决策变更请务必同步更新本文件，以保持团队对系统设计的统一认知。
