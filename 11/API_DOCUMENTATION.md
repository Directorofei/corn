# API 接口文档

## 概述

本项目是一个基于 Next.js 的前端应用，通过代理模式将前端请求转发到后端服务。后端服务地址默认为 `http://10.4.178.147:8000`，可通过环境变量 `BACKEND_URL` 进行配置。

## 通用配置

- **后端基础URL**: `http://10.4.178.147:8000` (可通过 `BACKEND_URL` 环境变量配置)
- **默认Content-Type**: `application/json`
- **跨域支持**: 已配置 CORS 头部
- **缓存策略**: `no-store` (避免缓存)

---

## API 接口列表

### 1. 认证接口 (Authentication)

#### 通用认证代理
- **路径**: `/api/auth/*`
- **说明**: 通用认证代理，支持所有 `/api/auth/` 下的子路径
- **代理目标**: `{BACKEND_URL}/api/auth/*`
- **支持方法**: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`
- **实现**: 动态路由 `[...slug]`，支持任意深度的认证相关路径

**示例用法**:
```
GET  /api/auth/login     => http://10.4.178.147:8000/api/auth/login
POST /api/auth/register  => http://10.4.178.147:8000/api/auth/register
GET  /api/auth/user/info => http://10.4.178.147:8000/api/auth/user/info
```

**特点**:
- 自动复制原始请求的所有头部和请求体
- 支持 GET/HEAD 请求（无请求体）和其他方法的请求体转发
- 保持原始响应状态码和响应头

---

### 2. 对话历史接口 (Conversation History)

#### 获取对话历史
- **路径**: `/api/conversation-history`
- **方法**: `GET`
- **功能**: 获取用户的对话历史记录
- **代理目标**: `{BACKEND_URL}/api/conversation-history`

**请求格式**:
```http
GET /api/conversation-history
```

**响应**: 代理后端响应，通常包含对话历史数据

---

### 3. 查询接口 (Query)

#### AI 查询处理
- **路径**: `/api/query`
- **方法**: `POST`
- **功能**: 处理AI查询请求，与AI模型进行交互
- **代理目标**: `{BACKEND_URL}/api/query`

**请求格式**:
```http
POST /api/query
Content-Type: application/json

{
  "message": "用户查询内容",
  "context": "上下文信息"
}
```

**响应**: 代理后端AI服务的响应

---

### 4. 健康检查接口 (Health Check)

#### 服务健康状态
- **路径**: `/api/health`
- **方法**: `GET`
- **功能**: 检查后端服务健康状态
- **代理目标**: `{BACKEND_URL}/api/health`

**请求格式**:
```http
GET /api/health
```

**响应**: 后端服务健康状态信息

---

### 5. 调试接口 (Debug)

#### 系统调试信息
- **路径**: `/api/debug`
- **方法**: `GET`
- **功能**: 获取系统调试信息，测试后端连接状态

**请求格式**:
```http
GET /api/debug
```

**响应格式**:
```json
{
  "backend_url": "http://10.4.178.147:8000",
  "root_endpoint": {
    "status": 200,
    "response": "根路径响应内容（前200字符）"
  },
  "health_endpoint": {
    "status": 200,
    "response": "健康检查响应内容（前200字符）"
  },
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

**错误响应**:
```json
{
  "error": "调试测试失败",
  "message": "具体错误信息",
  "backend_url": "http://10.4.178.147:8000"
}
```

---

### 6. AI模型测试接口 (Test AI Model)

#### 测试后端AI模型连接
- **路径**: `/api/test-ai-model`
- **方法**: `POST`
- **功能**: 测试与后端AI服务的连接状态

**请求格式**:
```http
POST /api/test-ai-model
Content-Type: application/json

{}
```

**成功响应**:
```json
{
  "success": true,
  "message": "后端服务器连接正常",
  "response": "后端健康检查的响应数据",
  "backend_url": "http://10.4.178.147:8000"
}
```

**失败响应**:
```json
{
  "success": false,
  "error": "后端服务器连接失败",
  "status": 500,
  "response": "错误响应内容",
  "backend_url": "http://10.4.178.147:8000"
}
```

---

## 代理工具库 (Proxy Request Utility)

### proxyRequest 函数
位于 `lib/proxy-request.ts`，为多个API接口提供统一的代理功能。

**特性**:
- 智能处理各种请求类型（GET、POST、PUT、DELETE等）
- 自动保留重要的HTTP头部信息
- 支持二进制数据和文件上传
- 错误处理和日志记录
- CORS 头部自动添加

**使用方式**:
```typescript
import { proxyRequest } from "@/lib/proxy-request"

export async function GET(req: NextRequest) {
  return proxyRequest(req, `${BACKEND_URL}/api/target-endpoint`)
}
```

---

## 错误处理

所有接口都包含统一的错误处理机制：

1. **网络错误**: 当无法连接到后端服务时返回 500 状态码
2. **代理错误**: 详细的错误信息包含在响应体中
3. **日志记录**: 控制台输出详细的请求和响应日志

**通用错误响应格式**:
```json
{
  "error": "错误类型",
  "message": "具体错误信息",
  "target": "目标URL（如适用）"
}
```

---

## 环境配置

### 必需的环境变量
- `BACKEND_URL`: 后端服务基础URL（可选，默认: `http://10.4.178.147:8000`）

### 配置示例
```bash
# .env.local
BACKEND_URL=http://your-backend-server.com:8000
```

---

## 注意事项

1. **安全性**: 当前配置允许所有跨域请求，生产环境需要限制CORS设置
2. **缓存**: 所有代理请求都设置了 `no-store` 以避免缓存问题
3. **文件上传**: 支持 multipart/form-data 格式的文件上传
4. **日志**: 开发环境会输出详细的请求/响应日志
5. **认证**: 认证相关的token和会话信息会自动转发到后端

---

## 更新历史

- **版本 1.0**: 初始版本，包含基础代理功能
- **当前版本**: 支持认证、查询、健康检查、调试等完整功能 