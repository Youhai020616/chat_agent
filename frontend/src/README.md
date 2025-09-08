# 前端源码结构

## 📁 目录结构

```
src/
├── api/                # API 客户端与服务层
│   ├── client.ts      # API 请求客户端封装
│   ├── services/      # 业务服务接口
│   └── types/         # API 类型定义
├── streams/           # SSE/WebSocket 实时通信
├── stores/            # Zustand 状态管理
├── pages/             # 页面组件
│   ├── Dashboard/     # 仪表盘
│   ├── Analysis/      # 分析页面
│   ├── Results/       # 结果展示
│   └── KPI/           # KPI 监控
├── features/          # 业务功能模块
│   ├── batch-analysis/ # 批量分析
│   ├── agent-flow/    # Agent 工作流
│   └── optimization/  # 优化建议
├── components/        # 通用 UI 组件
├── hooks/            # 自定义 React Hooks
├── types/            # TypeScript 类型定义
├── utils/            # 工具函数
└── i18n/             # 国际化配置
```

## 🔧 开发规范

### TypeScript

- 严格使用 TypeScript
- 为所有组件和函数添加类型定义
- 避免使用 `any` 类型

### 组件开发

- 使用函数式组件
- 实现必要的错误边界
- 添加适当的注释
- 编写组件文档

### 状态管理

- 使用 Zustand 管理全局状态
- 保持 store 结构清晰
- 实现持久化（必要时）

### API 调用

- 使用统一的 API 客户端
- 处理错误和加载状态
- 实现请求缓存和重试

### 样式规范

- 使用 Tailwind CSS
- 遵循响应式设计
- 保持颜色主题一致

## 📚 相关文档

- [前端架构设计](../../docs/architecture/frontend-architecture.md)
- [组件编目](../../docs/architecture/frontend-catalog.yml)
- [API 规范](../../docs/api/api-specification.md)
