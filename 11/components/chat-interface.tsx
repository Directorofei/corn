"use client"

import { useState, useEffect } from "react"
import ChatSidebar from "./chat-sidebar"
import ChatArea from "./chat-area"
import SettingsDialog from "./settings-dialog"
import type { AISettings } from "@/lib/ai-service"

export interface Message {
  id: string
  type: "user" | "ai"
  content: string
  image?: string
  timestamp: Date
}

export interface Conversation {
  id: string
  name: string
  messages: Message[]
  createdAt: Date
  updatedAt: Date
}

export default function ChatInterface() {
  const [conversations, setConversations] = useState<Conversation[]>([
    {
      id: "1",
      name: "玉米叶斑病识别",
      messages: [
        {
          id: "1",
          type: "user",
          content: "请帮我识别这张玉米叶片的病害",
          timestamp: new Date(Date.now() - 3600000),
        },
        {
          id: "2",
          type: "ai",
          content: "根据图片分析，这是典型的玉米叶斑病症状。建议使用苯醚甲环唑进行防治，同时注意田间通风和排水。",
          timestamp: new Date(Date.now() - 3500000),
        },
      ],
      createdAt: new Date(Date.now() - 3600000),
      updatedAt: new Date(Date.now() - 3500000),
    },
    {
      id: "2",
      name: "设计系统概览: 风格、配色方案优化",
      messages: [],
      createdAt: new Date(Date.now() - 7200000),
      updatedAt: new Date(Date.now() - 7200000),
    },
    {
      id: "3",
      name: "设计系统配置文件",
      messages: [],
      createdAt: new Date(Date.now() - 10800000),
      updatedAt: new Date(Date.now() - 10800000),
    },
    {
      id: "4",
      name: "解决 'next' 命令未识别问题",
      messages: [],
      createdAt: new Date(Date.now() - 14400000),
      updatedAt: new Date(Date.now() - 14400000),
    },
    {
      id: "5",
      name: "RDB: 关系型数据库与Redis缓存",
      messages: [],
      createdAt: new Date(Date.now() - 18000000),
      updatedAt: new Date(Date.now() - 18000000),
    },
    {
      id: "6",
      name: "2025年MSI在加拿大温哥华举办",
      messages: [],
      createdAt: new Date(Date.now() - 86400000),
      updatedAt: new Date(Date.now() - 86400000),
    },
  ])

  // 默认创建新会话
  const [currentConversationId, setCurrentConversationId] = useState<string>("")
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [currentFeature, setCurrentFeature] = useState<string>("chat")
  const [aiSettings, setAiSettings] = useState<AISettings>({
    baseUrl: "https://api.openai.com/v1",
    sdk: "openai",
    modelName: "gpt-4",
    apiKey: "",
    temperature: 0.7,
    maxTokens: 2048,
  })

  // 初始化时创建新会话和加载AI设置
  useEffect(() => {
    if (!currentConversationId) {
      createNewConversation()
    }

    // 加载AI设置
    const savedSettings = localStorage.getItem("corncare-ai-settings")
    if (savedSettings) {
      try {
        const settings = JSON.parse(savedSettings)
        setAiSettings(settings)
      } catch (error) {
        console.error("加载AI设置失败:", error)
      }
    }
  }, [])

  const currentConversation = conversations.find((c) => c.id === currentConversationId)

  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: "新对话",
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    setConversations((prev) => [newConversation, ...prev])
    setCurrentConversationId(newConversation.id)
    setCurrentFeature("chat") // Ensure we're in chat mode
  }

  const deleteConversation = (id: string) => {
    setConversations((prev) => prev.filter((c) => c.id !== id))
    if (currentConversationId === id) {
      const remaining = conversations.filter((c) => c.id !== id)
      if (remaining.length > 0) {
        setCurrentConversationId(remaining[0].id)
      } else {
        // 如果没有剩余对话，创建新对话
        createNewConversation()
      }
    }
  }

  const updateConversationName = (id: string, name: string) => {
    setConversations((prev) => prev.map((c) => (c.id === id ? { ...c, name, updatedAt: new Date() } : c)))
  }

  const addMessage = (message: Omit<Message, "id" | "timestamp">) => {
    const newMessage: Message = {
      ...message,
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
    }

    setConversations((prev) =>
      prev.map((c) =>
        c.id === currentConversationId
          ? {
              ...c,
              messages: [...c.messages, newMessage],
              updatedAt: new Date(),
              // 如果是第一条消息且对话名称是"新对话"，则更新对话名称
              name:
                c.messages.length === 0 && c.name === "新对话"
                  ? message.content.slice(0, 20) + (message.content.length > 20 ? "..." : "")
                  : c.name,
            }
          : c,
      ),
    )
  }

  const updateMessage = (messageId: string, content: string) => {
    setConversations((prev) =>
      prev.map((c) =>
        c.id === currentConversationId
          ? {
              ...c,
              messages: c.messages.map((m) => (m.id === messageId ? { ...m, content } : m)),
              updatedAt: new Date(),
            }
          : c,
      ),
    )
  }

  const handleSettingsChange = (settings: AISettings) => {
    setAiSettings(settings)
  }

  // 键盘快捷键
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === "k") {
        e.preventDefault()
        createNewConversation()
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])

  return (
    <div className="h-screen flex relative" style={{ backgroundColor: "#FFFFFF" }}>
      {/* 为侧边栏留出空间 */}
      <div className="w-20 flex-shrink-0"></div>

      <ChatSidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onConversationSelect={setCurrentConversationId}
        onNewConversation={createNewConversation}
        onDeleteConversation={deleteConversation}
        currentFeature={currentFeature}
        onFeatureChange={setCurrentFeature}
        onSettingsOpen={() => setSettingsOpen(true)}
      />

      <ChatArea
        conversation={currentConversation}
        onSendMessage={addMessage}
        onUpdateMessage={updateMessage}
        onUpdateConversationName={updateConversationName}
        onSettingsOpen={() => setSettingsOpen(true)}
        currentFeature={currentFeature}
        aiSettings={aiSettings}
      />

      <SettingsDialog open={settingsOpen} onOpenChange={setSettingsOpen} onSettingsChange={handleSettingsChange} />
    </div>
  )
}
