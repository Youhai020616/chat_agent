# 项目脚本集合

该目录包含项目级别的实用脚本。

## 📁 脚本分类

### 🚀 部署脚本
- `deploy.sh` - 生产环境部署
- `deploy-dev.sh` - 开发环境部署
- `rollback.sh` - 版本回滚

### 🔧 开发脚本  
- `setup.sh` - 项目初始化
- `dev.sh` - 启动开发环境
- `build.sh` - 构建所有服务

### 📊 数据脚本
- `seed-data.sh` - 初始化测试数据
- `backup-db.sh` - 数据库备份
- `restore-db.sh` - 数据库恢复

### 🧹 维护脚本
- `cleanup.sh` - 清理临时文件
- `update-deps.sh` - 更新依赖
- `health-check.sh` - 健康检查

## 使用说明

所有脚本都应该从项目根目录执行：

```bash
# 项目初始化
./scripts/setup.sh

# 启动开发环境
./scripts/dev.sh

# 部署到生产环境
./scripts/deploy.sh
```
