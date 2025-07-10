# CornCare 后端 API 需求文档

基于前端代码分析，后端需要提供以下 API 接口。

## 🌐 API 基础信息

**基础URL**: `http://10.4.178.147:8000` (可通过环境变量 `BACKEND_URL` 配置)

**通用响应格式**:
```json
{
  "success": boolean,
  "data": any,
  "message": string,
  "error": string // 仅在失败时存在
}
```

## 📋 必需的 API 接口

### 1. 健康检查接口 ⭐ **核心**

```http
GET /api/health
```

**用途**: 检查后端服务状态，前端用于验证连接

**请求参数**: 无

**响应示例**:
```json
{
  "status": "healthy",
  "message": "CornCare Backend Service is running",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

**错误响应**:
```json
{
  "error": "Service unavailable",
  "message": "Database connection failed"
}
```

---

### 2. AI 查询接口 ⭐ **核心**

```http
POST /api/query
Content-Type: multipart/form-data
```

**用途**: 处理用户的AI查询请求，支持文本和图片输入

**请求参数**:
- `text` (string, 必需): 用户输入的文本
- `image` (file, 可选): 用户上传的图片文件 (支持 jpg, png, webp，最大5MB)

**请求示例**:
```bash
curl -X POST http://10.4.178.147:8000/api/query \
  -F "text=请帮我识别这张玉米叶片的病害" \
  -F "image=@corn_leaf.jpg"
```

**成功响应**:
```json
{
  "success": true,
  "data": "根据图片分析，这是典型的玉米叶斑病症状。建议使用苯醚甲环唑进行防治，同时注意田间通风和排水。",
  "analysis": {
    "disease": "玉米叶斑病",
    "confidence": 0.95,
    "recommendations": [
      "使用苯醚甲环唑杀菌剂",
      "改善田间通风",
      "加强排水管理"
    ]
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "图片处理失败",
  "message": "不支持的图片格式，请使用 jpg、png 或 webp 格式"
}
```

---

### 3. 根路径接口 (调试用)

```http
GET /
```

**用途**: 基本信息展示，用于调试和验证服务运行

**响应示例**:
```json
{
  "service": "CornCare AI Backend",
  "version": "1.0.0",
  "status": "running",
  "endpoints": [
    "/api/health",
    "/api/query", 
    "/api/auth/*"
  ]
}
```

---

## 🔧 可选的 API 接口

### 4. 对话历史管理 (可选实现)

```http
GET /api/conversation-history
```

**用途**: 获取用户的对话历史记录

**请求参数**:
- `user_id` (string, 可选): 用户ID
- `limit` (number, 可选): 返回条数限制，默认20
- `offset` (number, 可选): 分页偏移量，默认0

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": "conv_123",
      "name": "玉米叶斑病识别",
      "messages": [
        {
          "id": "msg_1",
          "type": "user",
          "content": "请帮我识别这张玉米叶片的病害",
          "image": "base64_image_data",
          "timestamp": "2024-01-01T12:00:00Z"
        },
        {
          "id": "msg_2", 
          "type": "ai",
          "content": "根据图片分析，这是典型的玉米叶斑病症状...",
          "timestamp": "2024-01-01T12:00:05Z"
        }
      ],
      "createdAt": "2024-01-01T12:00:00Z",
      "updatedAt": "2024-01-01T12:00:05Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

---

### 5. 用户认证接口 (可选实现)

```http
POST /api/auth/login
```

**用途**: 用户登录

**请求体**:
```json
{
  "loginMethod": "phone", // "phone" | "email"
  "phone": "13800138000", // 当 loginMethod 为 phone 时必需
  "email": "user@example.com", // 当 loginMethod 为 email 时必需
  "verificationCode": "123456", // 验证码
  "password": "password123" // 邮箱登录时的密码
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_123",
      "name": "农业专家",
      "phone": "13800138000",
      "email": "user@example.com"
    },
    "token": "jwt_token_here",
    "expiresIn": 86400
  }
}
```

```http
POST /api/auth/send-code
```

**用途**: 发送验证码

**请求体**:
```json
{
  "type": "phone", // "phone" | "email"
  "target": "13800138000" // 手机号或邮箱
}
```

```http
GET /api/auth/profile
Authorization: Bearer <token>
```

**用途**: 获取用户信息

---

## 🎯 API 实现优先级

### 第一阶段 (最小可用版本)
1. ✅ `GET /api/health` - 健康检查
2. ✅ `POST /api/query` - AI查询 (核心功能)
3. ✅ `GET /` - 基本信息

### 第二阶段 (功能完善)
4. `GET /api/conversation-history` - 对话历史
5. `POST /api/auth/login` - 用户登录
6. `POST /api/auth/send-code` - 验证码发送

### 第三阶段 (高级功能)
7. 对话CRUD操作 (增删改查)
8. 用户管理功能
9. 数据统计分析

---

## 🔒 安全要求

### 1. 数据验证
- 图片格式验证 (jpg, png, webp)
- 文件大小限制 (最大5MB)
- 文本长度限制 (建议最大10000字符)

### 2. 错误处理
- 统一的错误响应格式
- 详细的错误信息 (开发环境)
- 用户友好的错误信息 (生产环境)

### 3. 性能要求
- AI查询响应时间 < 30秒
- 健康检查响应时间 < 1秒
- 支持并发请求处理

---

## 🌐 CORS 配置

后端需要配置 CORS 以支持前端跨域请求：

```python
# FastAPI 示例
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 📝 实现建议

### 1. 推荐技术栈
- **框架**: FastAPI (Python) 或 Express.js (Node.js)
- **AI集成**: OpenAI API / Anthropic API / Google AI
- **图片处理**: PIL (Python) 或 Sharp (Node.js)
- **数据库**: PostgreSQL + Redis (可选)

### 2. 项目结构建议
```
backend/
├── app/
│   ├── api/
│   │   ├── health.py
│   │   ├── query.py
│   │   └── auth.py
│   ├── models/
│   ├── services/
│   │   ├── ai_service.py
│   │   └── image_service.py
│   └── utils/
├── requirements.txt
└── main.py
```

### 3. 环境变量
```env
# AI服务配置
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=true

# 数据库配置 (可选)
DATABASE_URL=postgresql://user:pass@localhost/corncare
REDIS_URL=redis://localhost:6379
```

---

## ✅ 测试用例

### 健康检查测试
```bash
curl -X GET http://10.4.178.147:8000/api/health
```

### AI查询测试 (纯文本)
```bash
curl -X POST http://10.4.178.147:8000/api/query \
  -F "text=玉米叶片出现黄色斑点是什么病害？"
```

### AI查询测试 (文本+图片)
```bash
curl -X POST http://10.4.178.147:8000/api/query \
  -F "text=请识别这张图片中的玉米病害" \
  -F "image=@test_image.jpg"
```

这份文档涵盖了前端代码中所有需要的后端API接口，请根据实际需求按优先级实施。 