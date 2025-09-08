# 端到端测试

该目录包含跨服务的集成测试和端到端测试。

## 📁 测试分类

### 🔄 集成测试
- `integration/` - 服务间集成测试
  - `api_integration/` - API 集成测试
  - `database_integration/` - 数据库集成测试
  - `agent_integration/` - Agent 协作测试

### 🎯 端到端测试
- `e2e/` - 完整业务流程测试
  - `seo_workflow/` - SEO 优化流程测试
  - `geo_workflow/` - GEO 优化流程测试
  - `user_journey/` - 用户体验测试

### 📊 性能测试
- `performance/` - 性能和负载测试
  - `load_tests/` - 负载测试
  - `stress_tests/` - 压力测试
  - `benchmark/` - 基准测试

### 🔒 安全测试
- `security/` - 安全测试
  - `auth_tests/` - 认证测试
  - `injection_tests/` - 注入攻击测试
  - `vulnerability_scans/` - 漏洞扫描

## 运行测试

```bash
# 运行所有集成测试
npm run test:integration

# 运行端到端测试
npm run test:e2e

# 运行性能测试
npm run test:performance
```
