# 系统架构图

> 使用 Mermaid 语法定义的系统架构可视化图表

## 1. 系统整体架构图

```mermaid
graph TB
    subgraph "前端层"
        FE[React Frontend<br/>TypeScript + Vite]
    end
    
    subgraph "API网关层"
        GW[Kong Gateway<br/>认证/限流/路由]
    end
    
    subgraph "应用服务层"
        API[FastAPI Backend<br/>REST + SSE]
        WORKER[Celery Workers<br/>任务处理]
    end
    
    subgraph "编排层"
        LG[LangGraph<br/>工作流编排]
    end
    
    subgraph "Agent层"
        A1[Keyword Agent]
        A2[Content Agent]
        A3[Technical Agent]
        A4[GEO Agent]
        A5[Link Agent]
    end
    
    subgraph "数据层"
        PG[(PostgreSQL<br/>主数据库)]
        REDIS[(Redis<br/>缓存)]
    end
    
    subgraph "外部服务"
        EXT1[Google APIs]
        EXT2[SEO Tools]
        EXT3[OpenAI]
    end
    
    FE --> GW
    GW --> API
    API --> WORKER
    WORKER --> LG
    LG --> A1 & A2 & A3 & A4 & A5
    API --> PG
    API --> REDIS
    WORKER --> PG
    A1 & A2 & A3 & A4 & A5 --> EXT1 & EXT2 & EXT3
```

## 2. 数据流架构图

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant A as API服务
    participant W as Worker
    participant L as LangGraph
    participant AG as Agents
    participant DB as 数据库
    
    U->>F: 提交分析请求
    F->>A: POST /tasks
    A->>DB: 创建任务记录
    A->>W: 发送任务到队列
    A-->>F: 返回任务ID
    
    W->>L: 启动工作流
    L->>AG: 并行执行Agents
    AG->>AG: 分析处理
    AG-->>L: 返回结果
    L-->>W: 整合结果
    W->>DB: 保存结果
    W-->>A: 发送进度事件
    A-->>F: SSE推送进度
    F-->>U: 实时更新UI
```

## 3. 前端组件架构图

```mermaid
graph TD
    subgraph "App Root"
        APP[App.tsx]
    end
    
    subgraph "Providers"
        QC[QueryClientProvider]
        AUTH[AuthProvider]
        THEME[ThemeProvider]
        I18N[I18nProvider]
    end
    
    subgraph "Routing"
        ROUTER[Router]
    end
    
    subgraph "Layouts"
        MAIN[MainLayout]
        AUTHL[AuthLayout]
    end
    
    subgraph "Pages"
        DASH[Dashboard]
        ANALYSIS[Analysis]
        RESULTS[Results]
        KPI[KPI]
    end
    
    subgraph "Features"
        BATCH[BatchAnalysis]
        FLOW[AgentFlow]
        OPT[Optimization]
    end
    
    subgraph "Stores"
        AS[authStore]
        TS[taskStore]
        SS[siteStore]
        US[uiStore]
    end
    
    APP --> QC & AUTH & THEME & I18N
    QC --> ROUTER
    ROUTER --> MAIN & AUTHL
    MAIN --> DASH & ANALYSIS & RESULTS & KPI
    DASH --> SS
    ANALYSIS --> BATCH & TS
    RESULTS --> FLOW & OPT
    KPI --> SS
```

## 4. LangGraph 工作流图

```mermaid
graph LR
    START((开始)) --> CRAWL[网站爬虫]
    CRAWL --> FORK{并行分支}
    
    FORK --> KW[关键词分析]
    FORK --> CONT[内容优化]
    FORK --> TECH[技术SEO]
    FORK --> GEO[地理优化]
    FORK --> LINK[链接建设]
    
    KW --> MERGE{结果合并}
    CONT --> MERGE
    TECH --> MERGE
    GEO --> MERGE
    LINK --> MERGE
    
    MERGE --> INT[结果整合]
    INT --> PLAN[生成优化计划]
    PLAN --> END((结束))
    
    style START fill:#90EE90
    style END fill:#FFB6C1
    style FORK fill:#87CEEB
    style MERGE fill:#87CEEB
```

## 5. 部署架构图

```mermaid
graph TB
    subgraph "生产环境"
        subgraph "Kubernetes Cluster"
            subgraph "Frontend Pods"
                FP1[Nginx Pod 1]
                FP2[Nginx Pod 2]
                FP3[Nginx Pod 3]
            end
            
            subgraph "API Pods"
                AP1[API Pod 1]
                AP2[API Pod 2]
                AP3[API Pod 3]
            end
            
            subgraph "Worker Pods"
                WP1[Worker Pod 1]
                WP2[Worker Pod 2]
                WP3[Worker Pod 3]
                WP4[Worker Pod 4]
            end
        end
        
        subgraph "数据服务"
            PGC[(PostgreSQL<br/>主从集群)]
            RC[(Redis Cluster)]
            MQ[RabbitMQ Cluster]
        end
        
        subgraph "监控服务"
            PROM[Prometheus]
            GRAF[Grafana]
            JAEG[Jaeger]
        end
    end
    
    LB[负载均衡器] --> FP1 & FP2 & FP3
    FP1 & FP2 & FP3 --> AP1 & AP2 & AP3
    AP1 & AP2 & AP3 --> PGC & RC
    AP1 & AP2 & AP3 --> MQ
    MQ --> WP1 & WP2 & WP3 & WP4
    WP1 & WP2 & WP3 & WP4 --> PGC
    
    AP1 & AP2 & AP3 --> PROM
    WP1 & WP2 & WP3 & WP4 --> PROM
    PROM --> GRAF
    AP1 & AP2 & AP3 --> JAEG
```

## 6. 安全架构图

```mermaid
graph TB
    subgraph "外部访问"
        USER[用户]
        EXT[外部API]
    end
    
    subgraph "边界安全"
        WAF[Web应用防火墙]
        CDN[CDN]
        DDOS[DDoS防护]
    end
    
    subgraph "API网关"
        KONG[Kong Gateway]
        JWT[JWT验证]
        RATE[限流控制]
        CORS[CORS策略]
    end
    
    subgraph "应用安全"
        TLS[TLS 1.3]
        MTLS[mTLS认证]
        RBAC[RBAC授权]
    end
    
    subgraph "数据安全"
        VAULT[HashiCorp Vault<br/>密钥管理]
        KMS[AWS KMS<br/>数据加密]
        BACKUP[加密备份]
    end
    
    USER --> CDN
    CDN --> WAF
    WAF --> DDOS
    DDOS --> KONG
    KONG --> JWT & RATE & CORS
    JWT --> TLS
    TLS --> MTLS
    MTLS --> RBAC
    RBAC --> VAULT
    VAULT --> KMS
    KMS --> BACKUP
    
    EXT -.->|OAuth2/API Key| KONG
```

## 7. 数据模型关系图

```mermaid
erDiagram
    USERS ||--o{ SITES : owns
    USERS ||--o{ TASKS : creates
    SITES ||--o{ TASKS : has
    SITES ||--o{ KPIS : tracks
    TASKS ||--o{ RESULTS : produces
    TASKS ||--o{ OPTIMIZATION_PLANS : generates
    
    USERS {
        uuid id PK
        string email UK
        string password_hash
        string name
        enum role
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    SITES {
        uuid id PK
        uuid user_id FK
        string url UK
        string name
        enum status
        jsonb crawl_config
        jsonb analysis_config
        timestamp last_analysis_at
    }
    
    TASKS {
        uuid id PK
        uuid site_id FK
        uuid user_id FK
        enum type
        enum status
        enum priority
        array agents
        jsonb config
        jsonb progress
    }
    
    RESULTS {
        uuid id PK
        uuid task_id FK
        enum agent
        jsonb data
        jsonb summary
        jsonb recommendations
    }
    
    OPTIMIZATION_PLANS {
        uuid id PK
        uuid task_id FK
        enum category
        enum priority
        integer impact
        integer effort
        string title
        text description
    }
    
    KPIS {
        uuid id PK
        uuid site_id FK
        enum metric
        decimal value
        jsonb metadata
        timestamp recorded_at
    }
```

## 使用说明

这些架构图使用 Mermaid 语法编写，可以在支持 Mermaid 的环境中渲染显示：

1. **GitHub/GitLab**: 直接在 Markdown 文件中显示
2. **VS Code**: 安装 Mermaid 插件后预览
3. **在线工具**: 使用 [Mermaid Live Editor](https://mermaid-js.github.io/mermaid-live-editor/)
4. **文档工具**: Confluence、Notion 等支持 Mermaid 语法

要导出为图片格式，可以：
- 使用 Mermaid CLI: `mmdc -i input.mmd -o output.png`
- 使用在线编辑器的导出功能
- 截图保存渲染后的图表
