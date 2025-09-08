# 前端架构设计文档

> 基于 React + TypeScript 的 SEO & GEO 优化系统前端架构设计

## 1. 架构概览

### 1.1 设计原则
- **前后端完全分离**：前端作为独立的 SPA 应用，通过 REST API 和 SSE/WebSocket 与后端通信
- **组件化设计**：UI 组件高度复用，业务逻辑与展示层分离
- **类型安全**：全面使用 TypeScript，确保类型安全和开发体验
- **响应式设计**：适配桌面、平板和移动设备
- **实时更新**：通过 SSE 实现任务进度和 Agent 状态的实时推送

### 1.2 技术栈

| 领域 | 技术选型 | 版本 | 说明 |
|------|---------|------|------|
| **核心框架** | React | 18.x | 支持 Concurrent Features 和 Suspense |
| **开发语言** | TypeScript | 5.x | 类型安全，提升开发体验 |
| **构建工具** | Vite | 5.x | 快速的开发服务器和构建性能 |
| **CSS 框架** | TailwindCSS | 3.x | 原子化 CSS，快速开发 |
| **组件库** | Headless UI | 1.x | 无样式组件，完全可定制 |
| **路由管理** | React Router | 6.x | 声明式路由 |
| **状态管理** | Zustand | 4.x | 轻量级状态管理 |
| **数据请求** | React Query | 5.x | 强大的异步状态管理 |
| **HTTP 客户端** | Axios | 1.x | 拦截器、请求取消等高级功能 |
| **表单处理** | React Hook Form | 7.x | 高性能表单方案 |
| **图表库** | Recharts | 2.x | 数据可视化 |
| **流程图** | React Flow | 11.x | Agent 工作流可视化 |
| **国际化** | react-i18next | 13.x | 多语言支持 |
| **测试框架** | Vitest + RTL | - | 单元测试和集成测试 |

## 2. 项目结构

```
frontend/
├── src/
│   ├── api/                 # API 层
│   │   ├── client.ts        # Axios 实例配置
│   │   ├── services/        # API 服务模块
│   │   │   ├── auth.service.ts
│   │   │   ├── site.service.ts
│   │   │   ├── task.service.ts
│   │   │   ├── agent.service.ts
│   │   │   └── kpi.service.ts
│   │   └── types/           # API 类型定义
│   │
│   ├── streams/             # 实时通信
│   │   ├── sse.ts          # SSE 连接管理
│   │   ├── websocket.ts    # WebSocket 备用方案
│   │   └── hooks/          # 实时通信 hooks
│   │
│   ├── stores/              # 全局状态管理
│   │   ├── auth.store.ts   # 认证状态
│   │   ├── task.store.ts   # 任务状态
│   │   ├── site.store.ts   # 站点数据
│   │   └── ui.store.ts     # UI 状态
│   │
│   ├── pages/               # 页面组件
│   │   ├── Dashboard/      # 仪表盘
│   │   ├── Analysis/       # 分析页面
│   │   ├── Results/        # 结果展示
│   │   ├── KPI/           # KPI 监控
│   │   ├── Settings/      # 设置页面
│   │   └── Auth/          # 认证页面
│   │
│   ├── features/            # 业务功能模块
│   │   ├── batch-analysis/ # 批量分析
│   │   ├── agent-flow/     # Agent 流程图
│   │   ├── optimization/   # 优化建议
│   │   └── reporting/      # 报告生成
│   │
│   ├── components/          # 通用组件
│   │   ├── ui/             # 基础 UI 组件
│   │   ├── layout/         # 布局组件
│   │   ├── charts/         # 图表组件
│   │   └── forms/          # 表单组件
│   │
│   ├── hooks/               # 自定义 Hooks
│   │   ├── useAuth.ts
│   │   ├── useSSE.ts
│   │   ├── useDebounce.ts
│   │   └── useLocalStorage.ts
│   │
│   ├── types/               # TypeScript 类型定义
│   │   ├── models/         # 数据模型
│   │   ├── api.d.ts       # API 类型
│   │   └── global.d.ts    # 全局类型
│   │
│   ├── utils/               # 工具函数
│   │   ├── format.ts
│   │   ├── validation.ts
│   │   └── helpers.ts
│   │
│   ├── styles/              # 样式文件
│   │   ├── globals.css
│   │   └── tailwind.css
│   │
│   ├── i18n/                # 国际化
│   │   ├── config.ts
│   │   └── locales/
│   │
│   ├── App.tsx              # 根组件
│   ├── main.tsx             # 入口文件
│   └── vite-env.d.ts        # Vite 类型定义
│
├── public/                  # 静态资源
├── tests/                   # 测试文件
├── .env.development        # 开发环境变量
├── .env.production         # 生产环境变量
├── vite.config.ts          # Vite 配置
├── tailwind.config.js      # Tailwind 配置
├── tsconfig.json           # TypeScript 配置
├── package.json            # 项目依赖
└── Dockerfile              # Docker 配置
```

## 3. 核心功能模块

### 3.1 Dashboard 仪表盘
- **站点概览**：显示所有监控站点的状态和基础信息
- **任务队列**：展示正在执行和等待中的分析任务
- **快速操作**：一键启动分析、查看报告等
- **KPI 卡片**：核心指标的实时展示

### 3.2 批量分析模块
- **批量导入**：支持 CSV/Excel 文件上传
- **任务配置**：选择要执行的 Agent 和分析深度
- **进度追踪**：实时显示每个任务的执行进度
- **结果导出**：批量导出分析结果

### 3.3 Agent Flow 可视化
- **流程图展示**：使用 React Flow 展示 Agent 工作流
- **状态监控**：实时显示每个 Agent 的执行状态
- **日志查看**：查看每个 Agent 的详细执行日志
- **性能分析**：展示各 Agent 的执行时间和资源消耗

### 3.4 优化建议展示
- **分类展示**：按 Agent 类型分类显示优化建议
- **优先级排序**：根据 Impact/Effort 矩阵排序
- **详细说明**：每个建议的详细实施步骤
- **进度跟踪**：标记已实施的优化项

### 3.5 KPI 监控
- **趋势图表**：使用 Recharts 展示 KPI 趋势
- **对比分析**：不同时期、不同站点的对比
- **自定义指标**：支持自定义 KPI 指标
- **告警设置**：KPI 异常时的告警通知

## 4. API 交互设计

### 4.1 RESTful API 封装

```typescript
// api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = authStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      authStore.getState().logout();
    }
    return Promise.reject(error);
  }
);
```

### 4.2 实时通信 (SSE)

```typescript
// streams/hooks/useSSE.ts
export function useSSE(url: string) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource(url);

    eventSource.onopen = () => setIsConnected(true);
    
    eventSource.onmessage = (event) => {
      const parsedData = JSON.parse(event.data);
      setData(parsedData);
      
      // 更新任务状态
      if (parsedData.task_id) {
        taskStore.getState().updateProgress(parsedData);
      }
    };

    eventSource.onerror = (error) => {
      setError(error);
      setIsConnected(false);
    };

    return () => eventSource.close();
  }, [url]);

  return { data, error, isConnected };
}
```

## 5. 状态管理策略

### 5.1 Zustand Store 设计

```typescript
// stores/task.store.ts
interface TaskState {
  tasks: Task[];
  currentTask: Task | null;
  progress: Record<string, TaskProgress>;
  
  // Actions
  createTask: (task: CreateTaskDto) => Promise<void>;
  updateProgress: (progress: TaskProgress) => void;
  selectTask: (taskId: string) => void;
}

export const useTaskStore = create<TaskState>((set, get) => ({
  tasks: [],
  currentTask: null,
  progress: {},
  
  createTask: async (dto) => {
    const task = await taskService.create(dto);
    set((state) => ({
      tasks: [...state.tasks, task],
      currentTask: task,
    }));
  },
  
  updateProgress: (progress) => {
    set((state) => ({
      progress: {
        ...state.progress,
        [progress.task_id]: progress,
      },
    }));
  },
  
  selectTask: (taskId) => {
    const task = get().tasks.find((t) => t.id === taskId);
    set({ currentTask: task });
  },
}));
```

### 5.2 React Query 集成

```typescript
// hooks/useSites.ts
export function useSites() {
  return useQuery({
    queryKey: ['sites'],
    queryFn: siteService.getAll,
    staleTime: 5 * 60 * 1000, // 5 分钟
    cacheTime: 10 * 60 * 1000, // 10 分钟
  });
}

export function useCreateSite() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: siteService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['sites']);
    },
  });
}
```

## 6. 部署方案

### 6.1 Docker 多阶段构建

```dockerfile
# Dockerfile
# 构建阶段
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 6.2 Nginx 配置

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # SPA 路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # SSE 支持
    location /events {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_buffering off;
        proxy_cache off;
    }
}
```

## 7. 开发流程

### 7.1 开发环境设置

```bash
# 克隆项目
git clone <repository>
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 运行测试
npm run test

# 构建生产版本
npm run build
```

### 7.2 Git 工作流

- **main**: 生产环境分支
- **develop**: 开发分支
- **feature/***: 功能分支
- **hotfix/***: 紧急修复分支

### 7.3 代码规范

- ESLint + Prettier 自动格式化
- Husky + lint-staged 提交前检查
- 组件命名：PascalCase
- 文件命名：kebab-case
- 提交信息：遵循 Conventional Commits

## 8. 性能优化

### 8.1 代码分割
- 路由级别的懒加载
- 大型库的动态导入
- 图片和资源的懒加载

### 8.2 缓存策略
- React Query 的查询缓存
- 静态资源的 CDN 缓存
- Service Worker 离线缓存

### 8.3 渲染优化
- React.memo 避免不必要的重渲染
- useMemo/useCallback 优化计算和函数
- 虚拟滚动处理大列表

## 9. 安全考虑

- XSS 防护：React 默认转义
- CSRF 防护：Token 验证
- 敏感信息：环境变量管理
- HTTPS：生产环境强制使用
- CSP：内容安全策略配置

## 10. 监控与日志

- Sentry：错误监控和性能追踪
- Google Analytics：用户行为分析
- 自定义日志：关键操作记录
- 性能监控：Web Vitals 指标

## 11. 里程碑计划

| 阶段 | 时间 | 交付内容 |
|------|------|----------|
| M1 | Week 1 | 项目初始化、技术栈搭建、API 对接 |
| M2 | Week 2 | Dashboard、基础组件库、认证流程 |
| M3 | Week 3 | 批量分析、实时通信（SSE） |
| M4 | Week 4 | Agent Flow 可视化、结果展示 |
| M5 | Week 5 | KPI 监控、数据导出、测试覆盖 |
| M6 | Week 6 | 性能优化、部署配置、文档完善 |

---

> 本文档将随项目进展持续更新，确保架构设计与实际实现保持一致。
