# CornCare AI聊天平台 - 完整重建提示词

## 项目概述
创建一个专业的AI驱动玉米病虫害识别平台，使用Next.js 15 + TypeScript + Tailwind CSS + shadcn/ui，具有现代化的聊天界面和完整的AI模型集成功能。

## 技术栈要求
- **框架**: Next.js 15 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS + shadcn/ui
- **AI集成**: Vercel AI SDK (@ai-sdk/openai, @ai-sdk/anthropic, @ai-sdk/google)
- **图标**: Lucide React
- **通知**: Sonner
- **Markdown**: react-markdown + react-syntax-highlighter
- **字体**: Inter (Google Fonts)

## 精确的UI设计规范

### 1. 全局配色系统
\`\`\`css
/* 在globals.css中定义 */
:root {
  --background-main: #ffffff;
  --theme-color: #d6e97a;
  --accent-color: #3a5a40;
  --text-primary: #1d1d1f;
  --text-secondary: #6e6e73;
  --border-color: #e5e7eb;
  --white: #ffffff;
  --shadow-color: rgba(0, 0, 0, 0.1);
}

/* 自定义动画 */
.animate-bounce-delay-1 {
  animation: bounce 1s infinite;
  animation-delay: 0.1s;
}

.animate-bounce-delay-2 {
  animation: bounce 1s infinite;
  animation-delay: 0.2s;
}
\`\`\`

### 2. 登录页面设计 (LoginPage)

#### 布局结构
- **整体**: `flex min-h-screen` 水平分割
- **左侧品牌区**: `hidden lg:flex lg:flex-1` 大屏显示
- **右侧登录区**: `flex-1 lg:max-w-md xl:max-w-lg`

#### 左侧品牌区域精确设计
\`\`\`typescript
// 背景渐变
background: "linear-gradient(135deg, rgba(45, 74, 58, 0.9) 0%, rgba(26, 47, 35, 0.9) 50%, rgba(15, 27, 20, 0.9) 100%)"

// 背景图片
backgroundImage: "url('/images/corn-field-bg.png')"
backgroundSize: "cover"
backgroundPosition: "center"

// Logo区域
<div className="flex items-center space-x-3 mb-8">
  <div className="w-12 h-12 rounded-xl flex items-center justify-center shadow-lg" 
       style={{ backgroundColor: "#D6E97A" }}>
    <Wheat className="w-7 h-7" style={{ color: "#3A5A40" }} />
  </div>
  <span className="text-2xl font-bold text-white">CornCare</span>
</div>

// 主标题
<h1 className="text-5xl font-bold leading-tight text-white">
  开源智能农业
  <br />
  <span style={{ color: "#D6E97A" }}>守护玉米健康成长</span>
</h1>

// 装饰点动画
<div className="absolute top-20 left-20 w-2 h-2 bg-[#D6E97A] rounded-full opacity-60 animate-pulse"></div>
\`\`\`

#### 右侧登录表单精确设计
\`\`\`typescript
// 登录方式切换按钮
<div className="flex rounded-lg p-1" style={{ backgroundColor: "#F7F9FA" }}>
  <button className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
    loginMethod === "phone" ? "bg-white shadow-sm" : "text-gray-600 hover:text-gray-900"
  }`}>
    <Smartphone className="w-4 h-4 inline mr-2" />
    手机登录
  </button>
</div>

// 主要按钮样式
<Button className="w-full h-12 text-base font-semibold rounded-xl hover:bg-[#C5D86A] transition-colors"
        style={{ backgroundColor: "#D6E97A", color: "#3A5A40" }}>
  {isLoading ? "登录中..." : "注册 / 登录"}
</Button>

// 输入框样式
<Input className="h-11 border-gray-200 focus:border-[#D6E97A]" />
\`\`\`

### 3. 主聊天界面设计 (ChatInterface)

#### 整体布局
\`\`\`typescript
<div className="h-screen flex relative" style={{ backgroundColor: "#FFFFFF" }}>
  {/* 为侧边栏留出空间 */}
  <div className="w-20 flex-shrink-0"></div>
  
  <ChatSidebar /> {/* 固定定位侧边栏 */}
  <ChatArea />    {/* 主聊天区域 */}
</div>
\`\`\`

### 4. 侧边栏设计 (ChatSidebar)

#### 主侧边栏精确样式
\`\`\`typescript
// 容器样式
<div className="fixed left-0 top-0 z-10 flex flex-col h-screen w-20" 
     style={{ backgroundColor: "#F8F9FA" }}>

// Logo区域
<div className="w-10 h-10 rounded-lg flex items-center justify-center cursor-pointer"
     style={{ backgroundColor: "#D6E97A" }}>
  <Wheat className="w-6 h-6" style={{ color: "#3A5A40" }} />
</div>

// 功能按钮样式
<Button variant="ghost" 
        className={`w-10 h-10 p-0 rounded-xl transition-all duration-300 ease-in-out ${
          currentFeature === feature.id ? "shadow-md" : "hover:bg-[rgba(214,233,122,0.3)]"
        }`}
        style={{
          backgroundColor: currentFeature === feature.id ? "#D6E97A" : "transparent",
          color: currentFeature === feature.id ? "#3A5A40" : "#6E6E73",
        }}>
  <feature.icon className="w-5 h-5" />
</Button>

// 工具提示样式
<div className="absolute left-full ml-2 top-0 px-3 py-2 bg-gray-800 text-white text-sm rounded-lg whitespace-nowrap z-50 shadow-lg">
  {feature.name}
  <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-gray-800 rotate-45"></div>
</div>

// 底部用户信息
<Button className="w-full p-2 hover:bg-[#F7F9FA] rounded-xl flex flex-col items-center space-y-1">
  <div className="w-8 h-8 rounded-full flex items-center justify-center"
       style={{ backgroundColor: "#D6E97A", color: "#3A5A40" }}>
    <User className="w-4 h-4" />
  </div>
  <div className="text-xs font-medium truncate" style={{ color: "#1D1D1F" }}>
    农业专家
  </div>
</Button>
\`\`\`

#### 历史记录展开面板
\`\`\`typescript
// 面板容器
<div className={`fixed left-0 top-0 z-20 h-screen shadow-lg transition-all duration-300 ease-in-out ${
  isHistoryExpanded ? "w-80 opacity-100" : "w-0 opacity-0 pointer-events-none"
}`} style={{ backgroundColor: "#F8F9FA" }}>

// 新建会话按钮
<Button className="w-full h-11 rounded-xl hover:bg-[#C5D86A] justify-between"
        style={{ backgroundColor: "#D6E97A", color: "#3A5A40" }}>
  <div className="flex items-center">
    <Plus className="w-4 h-4 mr-2" />
    新建会话
  </div>
  <div className="text-xs opacity-70">Ctrl K</div>
</Button>

// 搜索框
<Input placeholder="搜索会话..." 
       className="pl-10 h-10 border-gray-200 focus:border-[#D6E97A] focus:outline-none" />

// 会话项样式
<div className={`group p-3 rounded-lg cursor-pointer transition-all duration-200 ease-in-out ${
  conversation.id === currentConversationId ? "shadow-sm" : "hover:bg-gray-50"
}`} style={{
  backgroundColor: conversation.id === currentConversationId ? "#F7F9FA" : "transparent"
}}>
\`\`\`

### 5. 聊天区域设计 (ChatArea)

#### 头部区域
\`\`\`typescript
// 头部容器
<div className="h-14 md:h-16 bg-white px-4 md:px-6 flex items-center justify-center">
  <h1 className="text-base md:text-lg font-semibold cursor-pointer hover:text-opacity-80"
      style={{ color: "#1D1D1F" }}>
    {conversation?.name || "CornCare AI"}
  </h1>
</div>
\`\`\`

#### 欢迎界面设计
\`\`\`typescript
// 欢迎界面容器
<div className="flex-1 flex flex-col items-center justify-center px-4 md:px-6 py-8">
  <div className="max-w-2xl mx-auto text-center space-y-8">
    
    // Logo和欢迎信息
    <div className="flex items-center justify-center space-x-3 mb-8">
      <div className="w-12 h-12 rounded-xl flex items-center justify-center"
           style={{ backgroundColor: "#D6E97A" }}>
        <Bot className="w-7 h-7" style={{ color: "#3A5A40" }} />
      </div>
      <h1 className="text-2xl md:text-3xl font-bold" style={{ color: "#1D1D1F" }}>
        我是 CornCare AI，很高兴见到你！
      </h1>
    </div>

    // 描述文本
    <p className="text-base md:text-lg mb-8" style={{ color: "#6E6E73" }}>
      我可以帮你识别玉米病虫害，提供专业的农业建议，请把你的问题交给我吧～
    </p>
  </div>
</div>
\`\`\`

#### 聊天输入框精确设计
\`\`\`typescript
// 输入框容器 - 圆角矩形设计
<div className="bg-gray-100 rounded-2xl border-2 border-gray-200 focus-within:border-[#D6E97A] p-4 shadow-sm">
  <div className="flex items-center space-x-3">
    
    // 输入框
    <Input placeholder="给 CornCare 发送消息"
           className="border-0 text-base bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 focus:outline-none p-0 h-auto" />
    
    // 上传按钮
    <Button variant="ghost" size="sm"
            className="w-10 h-10 rounded-xl hover:text-[#3A5A40] hover:bg-[#F7F9FA] focus-visible:ring-0"
            style={{ color: "#6E6E73" }}>
      <Upload className="w-5 h-5" />
    </Button>
    
    // 发送按钮
    <Button className="w-10 h-10 rounded-xl hover:bg-[#C5D86A] focus-visible:ring-0"
            style={{ backgroundColor: "#D6E97A", color: "#3A5A40" }}>
      <Send className="w-5 h-5" />
    </Button>
  </div>
</div>

// 底部提示
<p className="text-xs text-center mt-4" style={{ color: "#6E6E73" }}>
  内容由 AI 生成，请仔细甄别
</p>
\`\`\`

#### 消息气泡精确设计
\`\`\`typescript
// 用户消息气泡
<div className="rounded-2xl p-3 md:p-4 border"
     style={{
       backgroundColor: "rgba(214, 233, 122, 0.2)",
       borderColor: "rgba(214, 233, 122, 0.3)",
     }}>
  <p className="text-sm md:text-base leading-relaxed" style={{ color: "#1D1D1F" }}>
    {msg.content}
  </p>
</div>

// AI消息气泡
<div className="rounded-2xl p-3 md:p-4 bg-transparent">
  <StreamingMessage content={msg.content} isStreaming={streamingMessageId === msg.id} />
  
  // 底部操作栏
  <div className="border-t mt-3 pt-3 flex items-center justify-between"
       style={{ borderColor: "#E5E7EB" }}>
    <span className="text-xs" style={{ color: "#6E6E73" }}>
      {formatTime(msg.timestamp)}
    </span>
    <Button variant="ghost" size="sm"
            className="p-1 hover:text-[#3A5A40]"
            style={{ color: "#6E6E73" }}>
      <Copy className="w-3 h-3" />
    </Button>
  </div>
</div>

// 头像设计
// 用户头像
<div className="w-full h-full rounded-full flex items-center justify-center"
     style={{ backgroundColor: "#F7F9FA" }}>
  <User className="w-4 h-4" style={{ color: "#6E6E73" }} />
</div>

// AI头像
<div className="w-full h-full rounded-full flex items-center justify-center"
     style={{ backgroundColor: "#D6E97A" }}>
  <Bot className="w-4 h-4" style={{ color: "#3A5A40" }} />
</div>
\`\`\`

#### 加载动画设计
\`\`\`typescript
// 加载动画容器
<div className="rounded-2xl p-3 md:p-4 border"
     style={{
       backgroundColor: "rgba(214, 233, 122, 0.2)",
       borderColor: "rgba(214, 233, 122, 0.3)",
     }}>
  <div className="flex space-x-1">
    <div className="w-2 h-2 rounded-full animate-bounce"
         style={{ backgroundColor: "#3A5A40" }}></div>
    <div className="w-2 h-2 rounded-full animate-bounce animate-bounce-delay-1"
         style={{ backgroundColor: "#3A5A40" }}></div>
    <div className="w-2 h-2 rounded-full animate-bounce animate-bounce-delay-2"
         style={{ backgroundColor: "#3A5A40" }}></div>
  </div>
</div>
\`\`\`

### 6. 设置对话框设计 (SettingsDialog)

#### 对话框容器
\`\`\`typescript
<DialogContent className="max-w-4xl w-[90vw] max-h-[90vh] p-0 bg-white border-gray-200 overflow-hidden">
  <div className="flex h-[80vh]">
\`\`\`

#### 左侧菜单设计
\`\`\`typescript
// 菜单容器
<div className="w-64 bg-[#F8F9FA] border-r border-gray-200">
  
  // 头部
  <div className="flex items-center justify-between p-4 border-b border-gray-200">
    <h2 className="text-gray-800 text-lg font-semibold">设置</h2>
    <Button variant="ghost" size="sm"
            className="w-8 h-8 p-0 text-gray-500 hover:text-gray-700 hover:bg-gray-100">
      <X className="w-4 h-4" />
    </Button>
  </div>
  
  // 菜单项
  <button className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-left transition-colors ${
    activeTab === item.id
      ? "bg-[#D6E97A] text-[#3A5A40] shadow-sm"
      : "text-gray-600 hover:text-gray-800 hover:bg-gray-100"
  }`}>
    <item.icon className="w-4 h-4" />
    <span className="text-sm font-medium">{item.label}</span>
  </button>
</div>
\`\`\`

#### AI设置表单设计
\`\`\`typescript
// 输入框样式
<Input className="bg-white border-gray-300 text-gray-800 placeholder-gray-500 focus:border-[#D6E97A] focus:ring-[#D6E97A]" />

// 选择框样式
<SelectTrigger className="bg-white border-gray-300 text-gray-800 focus:border-[#D6E97A]">

// 按钮组
<div className="flex space-x-3 pt-4">
  <Button className="flex-1 bg-[#D6E97A] hover:bg-[#C5D86A] text-[#3A5A40] font-medium">
    保存设置
  </Button>
  <Button variant="outline" 
          className="flex-1 border-gray-300 text-gray-700 hover:bg-gray-50 bg-white">
    测试连接
  </Button>
  <Button variant="outline"
          className="border-gray-300 text-gray-700 hover:bg-gray-50 bg-white">
    重置
  </Button>
</div>

// 测试结果显示
<div className={`p-4 rounded-lg border flex items-center space-x-3 ${
  testResult.success
    ? "bg-green-50 border-green-200 text-green-800"
    : "bg-red-50 border-red-200 text-red-800"
}`}>
  {testResult.success ? (
    <CheckCircle className="w-5 h-5 text-green-600" />
  ) : (
    <AlertCircle className="w-5 h-5 text-red-600" />
  )}
  <span className="text-sm font-medium">{testResult.message}</span>
</div>
\`\`\`

### 7. Markdown渲染器设计 (MarkdownRenderer)

\`\`\`typescript
// 代码块样式
<SyntaxHighlighter style={oneDark} language={match[1]} PreTag="div" 
                   className="rounded-lg text-sm">

// 行内代码样式
<code className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-sm font-mono">

// 标题样式
h1: ({ children }) => (
  <h1 className="text-xl font-bold mb-3 mt-4 text-gray-900 flex items-center">{children}</h1>
),

// 列表样式
ul: ({ children }) => <ul className="list-disc list-inside space-y-1 my-2 ml-2">{children}</ul>,

// 引用样式
blockquote: ({ children }) => (
  <blockquote className="border-l-4 border-gray-300 pl-4 py-2 my-2 bg-gray-50 rounded-r">{children}</blockquote>
),
\`\`\`

### 8. 流式消息组件 (StreamingMessage)

\`\`\`typescript
// 流式光标
{isStreaming && currentIndex < content.length && (
  <span className="inline-block w-2 h-4 bg-gray-400 animate-pulse ml-1" />
)}
\`\`\`

## 功能要求

### 1. 核心功能
- **登录系统**: 手机号/邮箱登录，验证码功能
- **AI聊天**: 支持文本和图片输入，流式回复
- **多模型支持**: OpenAI、Anthropic、Google等
- **历史记录**: 对话保存、搜索、删除
- **设置管理**: AI模型配置、个人信息设置

### 2. 交互功能
- **键盘快捷键**: Ctrl+K 新建对话
- **鼠标悬停**: 侧边栏工具提示
- **响应式设计**: 适配移动端和桌面端
- **实时反馈**: 加载状态、错误提示

### 3. 数据管理
- **本地存储**: 使用localStorage保存设置和对话
- **状态管理**: React Hooks管理应用状态
- **API集成**: 服务端API调用和错误处理

## 文件结构要求

\`\`\`
├── app/
│   ├── api/test-ai-model/route.ts
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/ (shadcn/ui组件)
│   ├── chat-area.tsx
│   ├── chat-interface.tsx
│   ├── chat-sidebar.tsx
│   ├── history-panel.tsx
│   ├── login-page.tsx
│   ├── markdown-renderer.tsx
│   ├── settings-dialog.tsx
│   └── streaming-message.tsx
├── lib/
│   ├── ai-service.ts
│   └── utils.ts
├── public/images/
└── tailwind.config.ts
\`\`\`

## 特殊要求

1. **精确颜色匹配**: 严格按照提供的颜色值实现
2. **动画效果**: 包含所有过渡动画和悬停效果
3. **响应式设计**: 完整的移动端适配
4. **无障碍支持**: 适当的ARIA标签和键盘导航
5. **性能优化**: 合理的组件拆分和状态管理
6. **错误处理**: 完整的错误边界和用户反馈

使用这个提示词应该能够完全重现CornCare平台的所有视觉效果和功能特性。
