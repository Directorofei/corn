# CornCare - AI驱动玉米病虫害智能识别平台

CornCare 是一个基于 Next.js 15 和 AI SDK 构建的智能农业平台，专注于玉米病虫害的识别和诊断。通过集成多种 AI 模型（OpenAI、Anthropic、Google 等），为农业专家和种植户提供专业的病虫害识别服务。

## ✨ 特性

- 🤖 **多模型支持** - 支持 OpenAI、Anthropic、Google 等多种 AI 模型
- 💬 **智能对话** - 流式 AI 对话，支持 Markdown 渲染
- 🔧 **灵活配置** - 可自定义 API 端点、模型参数等
- 📱 **响应式设计** - 适配桌面端和移动端
- 🎨 **现代 UI** - 基于 shadcn/ui 的精美界面
- 🔒 **安全可靠** - 服务端处理 API 调用，保护密钥安全

## 🚀 快速开始

### 环境要求

- Node.js 18+ 
- npm 或 pnpm

### 安装依赖

\`\`\`bash
npm install
# 或
pnpm install
\`\`\`

### 环境变量配置

在项目根目录创建 `.env.local` 文件：

\`\`\`env
# OpenAI API Key（可选，也可在应用内配置）
OPENAI_API_KEY=sk-your-openai-api-key

# 其他 AI 服务的 API Key（可选）
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
\`\`\`

### 启动开发服务器

\`\`\`bash
npm run dev
# 或
pnpm dev
\`\`\`

访问 [http://localhost:3000](http://localhost:3000) 查看应用。

### 构建生产版本

\`\`\`bash
npm run build
npm start
\`\`\`

## 📁 目录结构

\`\`\`
├── app/
│   ├── api/
│   │   └── test-ai-model/
│   │       └── route.ts          # AI 模型测试接口
│   ├── globals.css               # 全局样式
│   ├── layout.tsx                # 根布局
│   └── page.tsx                  # 首页
├── components/
│   ├── ui/                       # shadcn/ui 组件
│   ├── chat-area.tsx             # 聊天区域组件
│   ├── chat-interface.tsx        # 聊天界面主组件
│   ├── chat-sidebar.tsx          # 侧边栏组件
│   ├── login-page.tsx            # 登录页面
│   ├── markdown-renderer.tsx     # Markdown 渲染器
│   ├── settings-dialog.tsx       # 设置对话框
│   └── streaming-message.tsx     # 流式消息组件
├── lib/
│   ├── ai-service.ts             # AI 服务封装
│   └── utils.ts                  # 工具函数
├── public/
│   └── images/                   # 静态图片资源
├── DESIGN_SYSTEM.md              # 设计系统文档
└── README.md
\`\`\`

## 🔌 API 接口

### POST /api/test-ai-model

测试 AI 模型连接状态的接口。

**请求体：**

\`\`\`json
{
  "baseUrl": "https://api.openai.com/v1",
  "sdk": "openai",
  "modelName": "gpt-4",
  "apiKey": "sk-your-api-key",
  "temperature": 0.7,
  "maxTokens": 2048
}
\`\`\`

**响应示例：**

成功响应：
\`\`\`json
{
  "success": true,
  "message": "模型连接测试成功",
  "response": "Connection test successful"
}
\`\`\`

失败响应：
\`\`\`json
{
  "success": false,
  "error": "API Key 无效或已过期"
}
\`\`\`

**支持的 SDK 类型：**
- `openai` - OpenAI GPT 模型
- `anthropic` - Anthropic Claude 模型  
- `google` - Google Gemini 模型
- `custom` - 自定义兼容 OpenAI 格式的服务

## 🛠️ 技术栈

- **框架**: Next.js 15 (App Router)
- **AI SDK**: Vercel AI SDK
- **UI 组件**: shadcn/ui + Tailwind CSS
- **状态管理**: React Hooks + localStorage
- **图标**: Lucide React
- **通知**: Sonner
- **Markdown**: react-markdown + react-syntax-highlighter

## 🎨 设计系统

本项目采用了完整的设计系统，包括：

- **配色方案**: 以农业绿色为主题的专业配色
- **字体系统**: 基于 Inter 字体的层级化排版
- **组件规范**: 统一的按钮、输入框、卡片等组件样式
- **响应式布局**: 适配多种屏幕尺寸的布局系统
- **动画效果**: 流畅的过渡动画和交互反馈

详细的设计系统文档请查看 [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md)

## 📝 使用说明

1. **登录**: 使用手机号或邮箱登录系统
2. **配置 AI**: 在设置中配置你的 AI 模型参数
3. **开始对话**: 创建新对话，向 AI 咨询玉米病虫害相关问题
4. **上传图片**: 支持上传玉米病害图片进行识别
5. **历史记录**: 查看和管理历史对话记录

## 🔧 配置说明

### AI 模型配置

在应用设置中，你可以配置以下参数：

- **Base URL**: API 服务地址
- **SDK 类型**: 选择 AI 服务提供商
- **模型名称**: 具体的模型名称
- **API Key**: 你的 API 密钥
- **温度参数**: 控制回复的随机性 (0.0-2.0)
- **最大令牌数**: 限制回复长度 (1-4096)

### 支持的 AI 服务

- **OpenAI**: GPT-4, GPT-3.5-turbo 等
- **Anthropic**: Claude-3, Claude-2 等
- **Google**: Gemini Pro, Gemini Pro Vision 等
- **自定义**: 兼容 OpenAI API 格式的其他服务

## 🚀 部署

### Vercel 部署

1. Fork 本项目到你的 GitHub
2. 在 Vercel 中导入项目
3. 配置环境变量
4. 部署完成

### Docker 部署

\`\`\`bash
# 构建镜像
docker build -t corncare .

# 运行容器
docker run -p 3000:3000 -e OPENAI_API_KEY=your-key corncare
\`\`\`

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

### 开发流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 使用 TypeScript 进行类型检查
- 遵循 ESLint 和 Prettier 配置
- 组件使用 PascalCase 命名
- 文件使用 kebab-case 命名

## 📄 开源协议

本项目采用 MIT 协议开源。详见 [LICENSE](./LICENSE) 文件。

## 🙏 致谢

- [Next.js](https://nextjs.org/) - React 全栈框架
- [Vercel AI SDK](https://sdk.vercel.ai/) - AI 应用开发工具包
- [shadcn/ui](https://ui.shadcn.com/) - 现代 UI 组件库
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的 CSS 框架
- [Lucide React](https://lucide.dev/) - 精美的图标库

## 📞 联系我们

如果你有任何问题或建议，欢迎通过以下方式联系我们：

- 提交 [GitHub Issue](https://github.com/your-username/corncare/issues)
- 发送邮件至：support@corncare.com
- 访问我们的官网：https://corncare.com

---

**CornCare** - 让AI守护每一株玉米的健康成长 🌽
