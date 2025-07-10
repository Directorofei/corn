# 🔧 CornCare 环境变量配置指南

## 📋 快速开始

### 1. 创建环境变量文件

在项目根目录创建 `.env.local` 文件：

```bash
# 复制示例文件
cp env.example .env.local
```

或者手动创建 `.env.local` 文件并添加以下内容：

```bash
# 在项目根目录下创建 .env.local 文件
# 注意：此文件不会被提交到Git仓库
```

---

## ⚡ 必需配置

### 后端服务地址
```env
# .env.local 文件内容
BACKEND_URL=http://10.4.178.147:8000
```

**说明**：
- 这是唯一必需的环境变量
- 指向您的后端AI服务地址
- 开发环境：`http://localhost:8000` 
- 生产环境：`https://your-backend-domain.com`

---

## 🎯 完整配置示例

### 最小配置（推荐新手）
```env
# .env.local
BACKEND_URL=http://10.4.178.147:8000
```

### 完整配置（推荐生产环境）
```env
# CornCare AI聊天平台环境变量配置

# ================================
# 🔗 后端服务配置 (必需)
# ================================
BACKEND_URL=http://10.4.178.147:8000

# ================================
# 🤖 AI模型API密钥 (可选 - 可在应用内配置)
# ================================
# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here

# Anthropic (Claude)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Google (Gemini)
GOOGLE_API_KEY=your-google-api-key-here

# ================================
# 🚀 应用配置 (可选)
# ================================
PORT=3000
NODE_ENV=development

# ================================
# 🔒 安全配置 (推荐生产环境)
# ================================
JWT_SECRET=your-super-secret-jwt-key-here
SESSION_SECRET=your-session-secret-here

# ================================
# 📁 文件上传配置 (可选)
# ================================
MAX_FILE_SIZE=5242880
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/webp

# ================================
# 📝 日志和调试 (可选)
# ================================
LOG_LEVEL=info
DEBUG=false
API_LOGGING=true

# ================================
# 🌐 部署配置 (生产环境)
# ================================
NEXT_PUBLIC_APP_URL=https://your-app-domain.com
```

---

## 📁 文件结构

```
项目根目录/
├── .env.local          # 您的环境变量文件 (需要创建)
├── env.example         # 示例文件 (已提供)
├── .gitignore          # .env.local 已被忽略
└── 其他项目文件...
```

---

## 🔧 配置步骤

### 步骤 1: 创建环境变量文件

**Windows PowerShell:**
```powershell
# 进入项目目录
cd C:\Users\86183\Desktop\11

# 创建 .env.local 文件
New-Item -ItemType File -Name ".env.local"

# 编辑文件
notepad .env.local
```

**Windows 命令提示符:**
```cmd
cd C:\Users\86183\Desktop\11
copy nul .env.local
notepad .env.local
```

**macOS/Linux:**
```bash
cd /path/to/your/project
cp env.example .env.local
vim .env.local  # 或使用其他编辑器
```

### 步骤 2: 配置必需变量

在 `.env.local` 文件中添加：
```env
BACKEND_URL=http://10.4.178.147:8000
```

### 步骤 3: 验证配置

启动项目验证配置是否正确：
```bash
npm run dev
# 或
pnpm dev
# 或  
yarn dev
```

---

## 🔍 环境变量说明

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `BACKEND_URL` | ✅ | `http://10.4.178.147:8000` | 后端API服务地址 |
| `OPENAI_API_KEY` | ❌ | 无 | OpenAI API密钥，可在应用内配置 |
| `ANTHROPIC_API_KEY` | ❌ | 无 | Claude API密钥，可在应用内配置 |
| `GOOGLE_API_KEY` | ❌ | 无 | Gemini API密钥，可在应用内配置 |
| `PORT` | ❌ | `3000` | 应用运行端口 |
| `NODE_ENV` | ❌ | `development` | 运行环境 |

---

## 🚨 常见问题

### 问题1: 环境变量不生效
**解决方案:**
1. 确保文件名为 `.env.local`（注意前面的点）
2. 重启开发服务器 (`npm run dev`)
3. 检查变量名拼写是否正确

### 问题2: 后端连接失败
**解决方案:**
1. 检查 `BACKEND_URL` 是否正确
2. 确保后端服务正在运行
3. 检查网络连接和防火墙设置

### 问题3: API密钥无法使用
**说明:**
- API密钥可以在环境变量中配置，也可以在应用的设置页面中配置
- 应用内配置会覆盖环境变量配置
- 推荐在应用内配置，更灵活安全

---

## 🔐 安全建议

### 保护环境变量
1. **永远不要提交 `.env.local` 到Git仓库**
2. **定期更换API密钥**
3. **在生产环境使用强密码**
4. **限制API密钥权限**

### API密钥获取地址
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Google**: https://makersuite.google.com/app/apikey

---

## 🌍 不同环境配置

### 开发环境
```env
NODE_ENV=development
BACKEND_URL=http://localhost:8000
DEBUG=true
```

### 生产环境
```env
NODE_ENV=production
BACKEND_URL=https://your-backend-domain.com
DEBUG=false
```

### 测试环境
```env
NODE_ENV=test
BACKEND_URL=http://test-backend:8000
```

---

## ✅ 验证配置

### 检查后端连接
1. 启动应用：`npm run dev`
2. 访问：http://localhost:3000
3. 打开设置页面
4. 点击"测试连接"按钮
5. 看到"连接成功"即表示配置正确

### 检查环境变量加载
在浏览器开发者工具的控制台中应该能看到相关日志信息，确认环境变量被正确读取。

---

## 🆘 需要帮助？

如果遇到配置问题，请检查：
1. ✅ 文件名是否为 `.env.local`
2. ✅ 文件是否在项目根目录
3. ✅ 变量格式是否正确（无空格、无引号）
4. ✅ 是否重启了开发服务器
5. ✅ 后端服务是否正常运行 