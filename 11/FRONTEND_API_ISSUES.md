# 前端 API 接口问题分析与修复方案

## 🚨 发现的主要问题

### 1. **AI设置参数未被使用** ⭐ 严重问题

**问题位置**: `lib/ai-service.ts` 第84-127行

**问题描述**: 
- 用户在设置对话框中配置的 API Key、模型名称、温度等参数完全被忽略
- `generateAIResponse` 函数接收了 `settings` 参数但从未使用
- 前端直接调用 `/api/query`，不传递任何AI配置

**当前代码问题**:
```typescript
export async function generateAIResponse(
  messages: ChatMessage[],
  settings: AISettings,  // ❌ 参数被忽略
  image?: File | string,
): Promise<string> {
  // ... 只使用了 messages 和 image，settings 完全被忽略
  const response = await fetch("/api/query", {
    method: "POST",
    body: formData,  // ❌ 没有包含任何AI设置
  })
}
```

**影响**: 用户无法使用自己的API Key，无法选择不同的AI模型

---

### 2. **只发送最后一条消息** ⭐ 严重问题

**问题位置**: `lib/ai-service.ts` 第90-95行

**问题描述**: 
- 只发送最后一条用户消息，忽略对话历史
- AI无法理解对话上下文，影响回复质量

**当前代码问题**:
```typescript
// 获取最后一条用户消息作为查询文本
const lastUserMessage = messages.filter((msg) => msg.role === "user").pop()
if (!lastUserMessage) {
  throw new Error("没有找到用户消息")
}

// 构建表单数据
const formData = new FormData()
formData.append("text", lastUserMessage.content)  // ❌ 只发送最后一条消息
```

**应该发送**: 完整的对话历史数组

---

### 3. **proxy-request.ts 处理有问题** 🟡 中等问题

**问题位置**: `lib/proxy-request.ts` 第14-20行

**问题描述**: 
- 对于 multipart/form-data 请求，强制设置 Content-Type 可能导致边界丢失
- 使用 `req.blob()` 处理表单数据不正确

**当前代码问题**:
```typescript
const init: RequestInit = {
  method: req.method,
  headers: {
    "Content-Type": req.headers.get("content-type") || "application/json",  // ❌ 强制设置可能覆盖multipart边界
    Accept: req.headers.get("accept") || "*/*",
    "User-Agent": req.headers.get("user-agent") || "CornCare-Frontend",
  },
  body: ["GET", "HEAD"].includes(req.method) ? undefined : await req.blob(),  // ❌ blob()不适合处理FormData
}
```

---

### 4. **AI连接测试不准确** 🟡 中等问题

**问题位置**: `lib/ai-service.ts` 第180-211行

**问题描述**: 
- `validateAISettings` 函数只测试 `/api/health` 而不是真正的AI模型
- 无法验证用户配置的API Key是否有效

**当前代码问题**:
```typescript
export async function validateAISettings(settings: AISettings): Promise<boolean> {
  try {
    const response = await fetch("/api/health", {  // ❌ 只测试健康检查，不测试AI设置
      method: "GET",
    })
    // ... 没有使用settings参数测试真正的AI连接
  }
}
```

---

### 5. **多余的API接口** 🟢 轻微问题

**问题位置**: `lib/auth-service.ts`

**问题描述**: 
- 存在完整的认证服务但当前是演示模式
- 增加了维护复杂度

---

## 🛠️ 修复方案

### 修复1: AI设置参数传递

**方案A**: 修改前端发送完整AI设置 (推荐)
```typescript
// 修改 generateAIResponse 函数
const formData = new FormData()
formData.append("text", JSON.stringify(messages))  // 发送完整对话历史
formData.append("ai_settings", JSON.stringify(settings))  // 发送AI设置
if (image) {
  formData.append("image", processedImage)
}
```

**方案B**: 修改后端API接受AI设置参数
```http
POST /api/query
Content-Type: multipart/form-data

Body:
- messages: string (JSON格式的对话历史)
- ai_settings: string (JSON格式的AI配置)
- image: file (可选)
```

### 修复2: 发送完整对话历史

```typescript
// 修改前端发送逻辑
const formData = new FormData()
formData.append("messages", JSON.stringify(messages))  // 完整对话历史
formData.append("ai_settings", JSON.stringify(settings))
```

### 修复3: 修复proxy-request

```typescript
export async function proxyRequest(req: NextRequest, targetUrl: string) {
  try {
    const init: RequestInit = {
      method: req.method,
      headers: {
        // ✅ 不要强制覆盖 multipart/form-data 的 Content-Type
        ...(req.headers.get("content-type") 
            ? { "Content-Type": req.headers.get("content-type")! }
            : {}),
        Accept: req.headers.get("accept") || "*/*",
        "User-Agent": req.headers.get("user-agent") || "CornCare-Frontend",
      },
      // ✅ 正确处理不同类型的请求体
      body: ["GET", "HEAD"].includes(req.method) 
            ? undefined 
            : await req.arrayBuffer(),  // 使用 arrayBuffer 代替 blob
    }
    // ...
  }
}
```

### 修复4: 真正的AI测试

```typescript
export async function validateAISettings(settings: AISettings): Promise<boolean> {
  try {
    // ✅ 发送测试请求到真正的AI模型
    const response = await fetch("/api/test-ai-model", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(settings),
    })
    
    if (!response.ok) {
      throw new Error("AI模型连接失败")
    }
    
    const result = await response.json()
    return result.success
  } catch (error) {
    console.error("AI设置验证失败:", error)
    return false
  }
}
```

---

## 🎯 修复优先级

### 第一优先级 (立即修复)
1. ✅ **AI设置参数传递** - 核心功能缺失
2. ✅ **发送完整对话历史** - 影响AI回复质量

### 第二优先级 (重要修复)  
3. ✅ **修复proxy-request** - 确保API调用正确
4. ✅ **AI连接测试** - 提升用户体验

### 第三优先级 (可选优化)
5. 🔄 **清理多余接口** - 代码维护性

---

## 📝 修复后的完整API流程

### 前端 → 后端数据流
```typescript
// 1. 用户在设置中配置AI参数
const aiSettings = {
  baseUrl: "https://api.openai.com/v1",
  sdk: "openai", 
  modelName: "gpt-4",
  apiKey: "sk-xxx",
  temperature: 0.7,
  maxTokens: 2048
}

// 2. 发送完整对话和设置给后端
const formData = new FormData()
formData.append("messages", JSON.stringify(conversationHistory))
formData.append("ai_settings", JSON.stringify(aiSettings))
formData.append("image", imageFile)  // 可选

// 3. 后端使用用户配置调用AI服务
fetch("/api/query", { method: "POST", body: formData })
```

### 后端需要调整的API格式
```python
@app.post("/api/query")
async def ai_query(
    messages: str = Form(...),          # JSON格式的对话历史  
    ai_settings: str = Form(...),       # JSON格式的AI配置
    image: UploadFile = File(None)      # 可选图片
):
    messages_data = json.loads(messages)
    settings_data = json.loads(ai_settings)
    
    # 使用用户的AI设置调用相应的AI服务
    result = await call_ai_service(messages_data, settings_data, image)
    return {"success": True, "data": result}
```

---

## ✅ 验证修复效果

修复完成后，应该能够：
1. ✅ 用户可以使用自己的API Key
2. ✅ 可以选择不同的AI模型 (GPT-4, Claude, Gemini)
3. ✅ 调整温度、Token等参数生效
4. ✅ AI能理解对话上下文
5. ✅ 设置测试功能正常工作

这些修复将显著提升应用的功能完整性和用户体验。 