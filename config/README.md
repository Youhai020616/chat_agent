# 配置文件集合

该目录包含项目的各种配置文件。

## 📁 配置分类

### 🐳 Docker 配置
- `docker/` - Docker 相关配置
  - `nginx.conf` - Nginx 配置
  - `postgres.conf` - PostgreSQL 配置
  - `redis.conf` - Redis 配置

### 🔧 环境配置
- `environments/` - 不同环境的配置
  - `development.yml` - 开发环境配置
  - `staging.yml` - 测试环境配置  
  - `production.yml` - 生产环境配置

### 📊 监控配置
- `monitoring/` - 监控和日志配置
  - `prometheus.yml` - Prometheus 配置
  - `grafana/` - Grafana 仪表板
  - `loki.yml` - 日志聚合配置

### 🚀 CI/CD 配置
- `ci/` - 持续集成配置
  - `github-actions/` - GitHub Actions 工作流
  - `jenkins/` - Jenkins 管道配置

## 使用说明

配置文件按环境和用途分类存放，方便管理和维护。
