# 开发工具集合

该目录包含开发和维护项目所需的各种工具。

## 📁 工具分类

### 🔧 代码生成工具
- `generators/` - 代码生成器
  - `agent_generator.py` - Agent 代码生成
  - `api_generator.py` - API 接口生成
  - `component_generator.js` - React 组件生成

### 📊 数据工具
- `data/` - 数据处理工具
  - `migrate_data.py` - 数据迁移工具
  - `export_data.py` - 数据导出工具
  - `validate_data.py` - 数据验证工具

### 🧪 测试工具
- `testing/` - 测试辅助工具
  - `mock_generator.py` - Mock 数据生成
  - `test_runner.sh` - 测试运行器
  - `coverage_reporter.py` - 覆盖率报告

### 📈 分析工具
- `analysis/` - 代码分析工具
  - `dependency_analyzer.py` - 依赖分析
  - `performance_profiler.py` - 性能分析
  - `security_scanner.py` - 安全扫描

### 🚀 部署工具
- `deployment/` - 部署相关工具
  - `health_checker.py` - 健康检查
  - `log_analyzer.py` - 日志分析
  - `metrics_collector.py` - 指标收集

## 使用说明

```bash
# 生成新的 Agent
python tools/generators/agent_generator.py --name NewAgent

# 运行数据迁移
python tools/data/migrate_data.py --from v1 --to v2

# 执行安全扫描
python tools/analysis/security_scanner.py --target backend/
```
