# 前后端 API 接口规范

> SEO & GEO 优化系统 API 接口定义文档

## 1. 基础约定

### 1.1 请求格式
- **Base URL**: `https://api.seo-geo.com/v1`
- **Content-Type**: `application/json`
- **字符编码**: UTF-8
- **时间格式**: ISO 8601 (e.g., `2024-01-01T00:00:00Z`)

### 1.2 认证方式
```http
Authorization: Bearer <JWT_TOKEN>
```

### 1.3 响应格式

#### 成功响应
```json
{
  "success": true,
  "data": {
    // 业务数据
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "uuid-v4"
  }
}
```

#### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "人类可读的错误信息",
    "details": {
      // 额外的错误详情
    }
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "uuid-v4"
  }
}
```

### 1.4 HTTP 状态码
- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `204 No Content`: 删除成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证
- `403 Forbidden`: 无权限
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 业务逻辑错误
- `429 Too Many Requests`: 请求过于频繁
- `500 Internal Server Error`: 服务器内部错误

## 2. 认证接口

### 2.1 用户登录
```http
POST /auth/login
```

**请求体**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**
```json
{
  "success": true,
  "data": {
    "token": "jwt_token_here",
    "refresh_token": "refresh_token_here",
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "admin",
      "permissions": ["read", "write", "delete"]
    },
    "expires_in": 3600
  }
}
```

### 2.2 刷新 Token
```http
POST /auth/refresh
```

**请求体**
```json
{
  "refresh_token": "refresh_token_here"
}
```

### 2.3 用户登出
```http
POST /auth/logout
```

## 3. 站点管理接口

### 3.1 获取站点列表
```http
GET /sites?page=1&limit=20&status=active&search=example
```

**查询参数**
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 20, 最大: 100)
- `status`: 状态过滤 (active|inactive|all)
- `search`: 搜索关键词
- `sort`: 排序字段 (created_at|updated_at|name)
- `order`: 排序方向 (asc|desc)

**响应**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "site_123",
        "url": "https://example.com",
        "name": "Example Site",
        "status": "active",
        "last_analysis": "2024-01-01T00:00:00Z",
        "metrics": {
          "domain_authority": 45,
          "page_speed": 85,
          "seo_score": 78
        },
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

### 3.2 创建站点
```http
POST /sites
```

**请求体**
```json
{
  "url": "https://example.com",
  "name": "Example Site",
  "crawl_config": {
    "depth": 3,
    "max_pages": 100,
    "follow_external": false
  },
  "analysis_config": {
    "agents": ["keyword", "content", "technical", "geo", "link"],
    "frequency": "weekly"
  }
}
```

### 3.3 获取站点详情
```http
GET /sites/{site_id}
```

### 3.4 更新站点
```http
PUT /sites/{site_id}
```

### 3.5 删除站点
```http
DELETE /sites/{site_id}
```

## 4. 分析任务接口

### 4.1 创建分析任务
```http
POST /tasks
```

**请求体**
```json
{
  "site_id": "site_123",
  "type": "full_analysis",
  "agents": ["keyword", "content", "technical", "geo", "link"],
  "priority": "high",
  "config": {
    "depth": 3,
    "include_competitors": true,
    "competitor_urls": ["https://competitor1.com", "https://competitor2.com"]
  }
}
```

**响应**
```json
{
  "success": true,
  "data": {
    "task_id": "task_456",
    "status": "queued",
    "estimated_time": 300,
    "queue_position": 5,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 4.2 获取任务状态
```http
GET /tasks/{task_id}
```

**响应**
```json
{
  "success": true,
  "data": {
    "task_id": "task_456",
    "site_id": "site_123",
    "status": "running",
    "progress": {
      "overall": 0.45,
      "agents": {
        "keyword": {
          "status": "completed",
          "progress": 1.0,
          "started_at": "2024-01-01T00:00:00Z",
          "completed_at": "2024-01-01T00:05:00Z"
        },
        "content": {
          "status": "running",
          "progress": 0.6,
          "started_at": "2024-01-01T00:05:00Z"
        },
        "technical": {
          "status": "queued",
          "progress": 0
        },
        "geo": {
          "status": "queued",
          "progress": 0
        },
        "link": {
          "status": "queued",
          "progress": 0
        }
      }
    },
    "logs": [
      {
        "timestamp": "2024-01-01T00:00:00Z",
        "level": "info",
        "agent": "keyword",
        "message": "Starting keyword analysis..."
      }
    ]
  }
}
```

### 4.3 获取任务列表
```http
GET /tasks?site_id=site_123&status=running&page=1&limit=20
```

### 4.4 取消任务
```http
POST /tasks/{task_id}/cancel
```

### 4.5 批量创建任务
```http
POST /tasks/batch
```

**请求体**
```json
{
  "sites": [
    {"site_id": "site_123", "config": {...}},
    {"site_id": "site_456", "config": {...}}
  ],
  "default_config": {
    "agents": ["keyword", "content"],
    "priority": "normal"
  }
}
```

## 5. 分析结果接口

### 5.1 获取分析结果
```http
GET /results/{task_id}
```

**响应**
```json
{
  "success": true,
  "data": {
    "task_id": "task_456",
    "site_id": "site_123",
    "completed_at": "2024-01-01T00:30:00Z",
    "summary": {
      "seo_score": 78,
      "issues_found": 23,
      "opportunities": 45,
      "critical_issues": 3
    },
    "agents": {
      "keyword": {
        "keywords_analyzed": 150,
        "opportunities": [
          {
            "keyword": "example keyword",
            "search_volume": 5000,
            "difficulty": 45,
            "current_rank": null,
            "potential_traffic": 1500,
            "recommendation": "Target this keyword with dedicated content"
          }
        ],
        "gaps": [...],
        "competitors": [...]
      },
      "content": {
        "pages_analyzed": 50,
        "issues": [
          {
            "type": "missing_meta_description",
            "severity": "medium",
            "pages": ["page1.html", "page2.html"],
            "impact": "Reduced CTR in search results",
            "solution": "Add unique meta descriptions"
          }
        ],
        "recommendations": [...]
      },
      "technical": {
        "performance": {
          "page_speed_score": 85,
          "core_web_vitals": {
            "lcp": 2.5,
            "fid": 100,
            "cls": 0.1
          }
        },
        "issues": [...],
        "sitemap_status": "valid",
        "robots_txt_status": "valid"
      },
      "geo": {
        "local_visibility_score": 65,
        "gmb_status": "claimed",
        "nap_consistency": 0.95,
        "local_keywords": [...],
        "citations": [...]
      },
      "link": {
        "total_backlinks": 1500,
        "referring_domains": 120,
        "domain_authority": 45,
        "toxic_links": 5,
        "link_opportunities": [...]
      }
    },
    "optimization_plan": [
      {
        "id": "opt_1",
        "category": "content",
        "priority": "high",
        "impact": 5,
        "effort": 2,
        "title": "Optimize meta descriptions",
        "description": "Add unique meta descriptions to 23 pages",
        "estimated_improvement": "+15% CTR",
        "implementation_guide": "..."
      }
    ]
  }
}
```

### 5.2 导出结果
```http
GET /results/{task_id}/export?format=pdf
```

**查询参数**
- `format`: 导出格式 (pdf|csv|json|html)

## 6. KPI 监控接口

### 6.1 获取 KPI 数据
```http
GET /kpis?site_id=site_123&metric=organic_traffic&period=30d&granularity=daily
```

**查询参数**
- `site_id`: 站点 ID (必需)
- `metric`: 指标类型 (organic_traffic|rankings|backlinks|page_speed)
- `period`: 时间范围 (7d|30d|90d|1y|custom)
- `start_date`: 自定义开始日期
- `end_date`: 自定义结束日期
- `granularity`: 数据粒度 (hourly|daily|weekly|monthly)

**响应**
```json
{
  "success": true,
  "data": {
    "metric": "organic_traffic",
    "period": {
      "start": "2023-12-01T00:00:00Z",
      "end": "2024-01-01T00:00:00Z"
    },
    "summary": {
      "total": 45000,
      "average": 1500,
      "growth": 0.15,
      "trend": "increasing"
    },
    "data_points": [
      {
        "timestamp": "2023-12-01T00:00:00Z",
        "value": 1200,
        "change": 0.05
      }
    ],
    "comparison": {
      "previous_period": {
        "total": 39000,
        "average": 1300
      },
      "year_over_year": {
        "total": 35000,
        "average": 1166
      }
    }
  }
}
```

### 6.2 获取 KPI 仪表盘
```http
GET /kpis/dashboard?site_id=site_123
```

## 7. 实时通信 (SSE)

### 7.1 任务进度推送
```http
GET /events/tasks/{task_id}
```

**SSE 事件格式**
```
event: task_progress
data: {"task_id":"task_456","agent":"keyword","status":"running","progress":0.45,"message":"Analyzing keywords..."}

event: agent_completed
data: {"task_id":"task_456","agent":"keyword","duration":300,"results_preview":{...}}

event: task_completed
data: {"task_id":"task_456","status":"completed","total_duration":1800,"summary":{...}}

event: task_error
data: {"task_id":"task_456","agent":"technical","error":"Connection timeout","retry_count":1}
```

### 7.2 批量任务监控
```http
GET /events/batch/{batch_id}
```

**SSE 事件格式**
```
event: batch_progress
data: {"batch_id":"batch_789","total":10,"completed":3,"running":2,"queued":5,"failed":0}

event: task_update
data: {"batch_id":"batch_789","task_id":"task_456","status":"completed"}
```

## 8. WebSocket 备用方案

### 8.1 连接建立
```javascript
ws://api.seo-geo.com/ws?token=<JWT_TOKEN>
```

### 8.2 消息格式

**客户端订阅**
```json
{
  "type": "subscribe",
  "channel": "task",
  "id": "task_456"
}
```

**服务器推送**
```json
{
  "type": "task_progress",
  "data": {
    "task_id": "task_456",
    "agent": "keyword",
    "progress": 0.45
  }
}
```

## 9. 错误码定义

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| AUTH_INVALID_CREDENTIALS | 无效的登录凭据 | 401 |
| AUTH_TOKEN_EXPIRED | Token 已过期 | 401 |
| AUTH_INSUFFICIENT_PERMISSIONS | 权限不足 | 403 |
| RESOURCE_NOT_FOUND | 资源不存在 | 404 |
| VALIDATION_ERROR | 参数验证失败 | 400 |
| RATE_LIMIT_EXCEEDED | 超过请求频率限制 | 429 |
| TASK_ALREADY_RUNNING | 任务已在运行中 | 422 |
| SITE_LIMIT_REACHED | 达到站点数量限制 | 422 |
| INTERNAL_SERVER_ERROR | 服务器内部错误 | 500 |

## 10. 限流策略

- **全局限流**: 1000 请求/分钟
- **单用户限流**: 100 请求/分钟
- **任务创建限流**: 10 任务/小时
- **批量操作限流**: 1 批量/分钟

限流响应头：
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704067200
```

## 11. 分页约定

所有列表接口均支持分页，使用统一的分页参数和响应格式：

**请求参数**
- `page`: 页码，从 1 开始
- `limit`: 每页数量，默认 20，最大 100

**响应格式**
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## 12. 版本管理

API 版本通过 URL 路径指定：
- v1: `https://api.seo-geo.com/v1`
- v2: `https://api.seo-geo.com/v2`

版本废弃策略：
1. 新版本发布后，旧版本继续维护 6 个月
2. 废弃前 3 个月发送废弃通知
3. 响应头包含废弃警告：`X-API-Deprecation-Warning`

---

> 本文档定义了前后端交互的完整接口规范，所有开发必须严格遵循此规范。
