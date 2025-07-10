"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send, Upload, User, Bot, Copy, Check, X, Trash2 } from "lucide-react"
import type { Conversation, Message } from "./chat-interface"
import { toast } from "sonner"
import StreamingMessage from "./streaming-message"
import { streamAIResponse, type AISettings, type ChatMessage } from "@/lib/ai-service"

interface ChatAreaProps {
  conversation?: Conversation
  onSendMessage: (message: Omit<Message, "id" | "timestamp">) => void
  onUpdateMessage: (messageId: string, content: string) => void
  onUpdateConversationName: (id: string, name: string) => void
  onSettingsOpen: () => void
  currentFeature: string
  aiSettings: AISettings
}

export default function ChatArea({
  conversation,
  onSendMessage,
  onUpdateMessage,
  onUpdateConversationName,
  currentFeature,
  aiSettings,
}: ChatAreaProps) {
  const [message, setMessage] = useState("")
  const [uploadedImage, setUploadedImage] = useState<File | null>(null)
  const [uploadedImagePreview, setUploadedImagePreview] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [editingTitle, setEditingTitle] = useState(false)
  const [titleValue, setTitleValue] = useState("")
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null)
  const [currentStreamingContent, setCurrentStreamingContent] = useState("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSend = async () => {
    if (!message.trim() && !uploadedImage) return

    const userMessage = {
      type: "user" as const,
      content: message,
      image: uploadedImagePreview || undefined,
    }

    onSendMessage(userMessage)
    const currentMessage = message
    const currentImage = uploadedImage

    setMessage("")
    setUploadedImage(null)
    setUploadedImagePreview(null)
    setIsLoading(true)

    try {
      // 准备对话历史
      const chatMessages: ChatMessage[] = []

      // 添加历史消息
      if (conversation?.messages) {
        conversation.messages.forEach((msg) => {
          chatMessages.push({
            role: msg.type === "user" ? "user" : "assistant",
            content: msg.content,
            image: msg.image,
          })
        })
      }

      // 添加当前用户消息
      chatMessages.push({
        role: "user",
        content: currentMessage,
        image: uploadedImagePreview || undefined,
      })

      // 创建AI消息占位符
      const aiMessageId = `${Date.now()}-ai-${Math.random().toString(36).substr(2, 9)}`
      setStreamingMessageId(aiMessageId)
      setCurrentStreamingContent("")

      // 先添加空的AI消息
      onSendMessage({
        type: "ai",
        content: "",
        id: aiMessageId,
      } as any)

      // 开始流式生成
      await streamAIResponse(
        chatMessages,
        aiSettings,
        // onChunk - 处理流式数据块
        (chunk: string) => {
          setCurrentStreamingContent((prev) => prev + chunk)
        },
        // onComplete - 流式完成
        (fullText: string) => {
          // 更新最终的AI消息内容
          onUpdateMessage(aiMessageId, fullText)
          setStreamingMessageId(null)
          setCurrentStreamingContent("")
          setIsLoading(false)
        },
        // onError - 错误处理
        (error: string) => {
          toast.error(error)
          setStreamingMessageId(null)
          setCurrentStreamingContent("")
          setIsLoading(false)
        },
        // 传递图片
        currentImage || undefined,
      )
    } catch (error) {
      console.error("AI响应失败:", error)
      toast.error("AI响应失败，请检查网络连接")
      setIsLoading(false)
      setStreamingMessageId(null)
      setCurrentStreamingContent("")
    }
  }

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error("图片大小不能超过5MB")
        return
      }

      setUploadedImage(file)

      const reader = new FileReader()
      reader.onload = (e) => {
        setUploadedImagePreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content)
    toast.success("已复制到剪贴板")
  }

  const handleEditTitle = () => {
    if (!conversation) return
    setTitleValue(conversation.name)
    setEditingTitle(true)
  }

  const handleSaveTitle = () => {
    if (!conversation || !titleValue.trim()) return
    onUpdateConversationName(conversation.id, titleValue.trim())
    setEditingTitle(false)
    toast.success("对话标题已更新")
  }

  const handleCancelEdit = () => {
    setEditingTitle(false)
    setTitleValue("")
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  // 如果没有对话或对话为空，显示欢迎界面
  const showWelcomeScreen = !conversation || conversation.messages.length === 0

  return (
    <div className="flex-1 flex flex-col min-w-0 h-screen">
      {/* Header */}
      <div className="h-14 md:h-16 bg-white px-4 md:px-6 flex items-center justify-center">
        <div className="flex items-center justify-center">
          <div className="text-center">
            {editingTitle ? (
              <div className="flex items-center space-x-2">
                <Input
                  value={titleValue}
                  onChange={(e) => setTitleValue(e.target.value)}
                  className="h-8 flex-1 focus:outline-none focus:ring-0 focus:border-[#D6E97A]"
                  style={{ borderColor: "#D6E97A" }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleSaveTitle()
                    if (e.key === "Escape") handleCancelEdit()
                  }}
                  autoFocus
                />
                <Button variant="ghost" size="sm" className="p-1" onClick={handleSaveTitle}>
                  <Check className="w-4 h-4 text-green-600" />
                </Button>
                <Button variant="ghost" size="sm" className="p-1" onClick={handleCancelEdit}>
                  <X className="w-4 h-4 text-red-600" />
                </Button>
              </div>
            ) : (
              <h1
                className="text-base md:text-lg font-semibold cursor-pointer hover:text-opacity-80"
                style={{ color: "#1D1D1F" }}
                onClick={handleEditTitle}
              >
                {conversation?.name || "CornCare AI"}
              </h1>
            )}
          </div>
        </div>
      </div>

      {/* 主内容区域 */}
      <div className="flex-1 flex flex-col">
        {showWelcomeScreen ? (
          /* 欢迎界面 - 居中布局 */
          <div className="flex-1 flex flex-col items-center justify-center px-4 md:px-6 py-8">
            <div className="max-w-2xl mx-auto text-center space-y-8">
              {/* Logo和欢迎信息 */}
              <div className="flex items-center justify-center space-x-3 mb-8">
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center"
                  style={{ backgroundColor: "#D6E97A" }}
                >
                  <Bot className="w-7 h-7" style={{ color: "#3A5A40" }} />
                </div>
                <h1 className="text-2xl md:text-3xl font-bold" style={{ color: "#1D1D1F" }}>
                  我是 CornCare AI，很高兴见到你！
                </h1>
              </div>

              <p className="text-base md:text-lg mb-8" style={{ color: "#6E6E73" }}>
                我可以帮你识别玉米病虫害，提供专业的农业建议，请把你的问题交给我吧～
              </p>

              {/* 居中的输入框 */}
              <div className="w-full max-w-3xl">
                {/* 图片预览 */}
                {uploadedImagePreview && (
                  <div className="mb-4">
                    <div className="relative inline-block">
                      <img
                        src={uploadedImagePreview || "/placeholder.svg"}
                        alt="预览"
                        className="max-w-32 max-h-32 rounded-lg shadow-sm"
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        className="absolute -top-2 -right-2 w-6 h-6 p-0 bg-red-500 hover:bg-red-600 text-white rounded-full"
                        onClick={() => {
                          setUploadedImage(null)
                          setUploadedImagePreview(null)
                        }}
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                )}

                <div className="flex items-center space-x-3 bg-white rounded-2xl border-2 border-gray-200 focus-within:border-[#D6E97A] p-4 shadow-sm">
                  <div className="flex-1">
                    <Input
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="给 CornCare 发送消息"
                      className="border-0 text-base bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 focus:outline-none p-0 h-auto"
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault()
                          handleSend()
                        }
                      }}
                    />
                  </div>

                  {/* 上传按钮 */}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-10 h-10 rounded-xl hover:text-[#3A5A40] hover:bg-[#F7F9FA]"
                    style={{ color: "#6E6E73" }}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <Upload className="w-5 h-5" />
                  </Button>

                  {/* 发送按钮 */}
                  <Button
                    className="w-10 h-10 rounded-xl hover:bg-[#C5D86A]"
                    style={{ backgroundColor: "#D6E97A", color: "#3A5A40" }}
                    onClick={handleSend}
                    disabled={!message.trim() && !uploadedImage}
                  >
                    <Send className="w-5 h-5" />
                  </Button>
                </div>

                {/* 底部提示 */}
                <div className="text-center mt-4">
                  <p className="text-xs" style={{ color: "#6E6E73" }}>
                    内容由 AI 生成，请仔细甄别
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* 有消息时的布局 */
          <>
            {/* 消息区域 */}
            <div className="flex-1 px-4 md:px-6 py-4 overflow-y-auto">
              <div className="max-w-4xl mx-auto space-y-4 md:space-y-6">
                {conversation?.messages.map((msg) => (
                  <div key={msg.id} className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"}`}>
                    <div
                      className={`flex space-x-3 max-w-[85%] md:max-w-[80%] ${msg.type === "user" ? "flex-row-reverse space-x-reverse" : ""}`}
                    >
                      {/* 头像 */}
                      <div className="w-7 h-7 md:w-8 md:h-8 flex-shrink-0 rounded-full flex items-center justify-center">
                        {msg.type === "user" ? (
                          <div
                            className="w-full h-full rounded-full flex items-center justify-center"
                            style={{ backgroundColor: "#F7F9FA" }}
                          >
                            <User className="w-4 h-4" style={{ color: "#6E6E73" }} />
                          </div>
                        ) : (
                          <div
                            className="w-full h-full rounded-full flex items-center justify-center"
                            style={{ backgroundColor: "#D6E97A" }}
                          >
                            <Bot className="w-4 h-4" style={{ color: "#3A5A40" }} />
                          </div>
                        )}
                      </div>

                      {/* 消息气泡 */}
                      <div
                        className={`rounded-2xl p-3 md:p-4 ${msg.type === "user" ? "border" : ""}`}
                        style={{
                          backgroundColor: msg.type === "user" ? "rgba(214, 233, 122, 0.2)" : "transparent",
                          borderColor: msg.type === "user" ? "rgba(214, 233, 122, 0.3)" : "transparent",
                        }}
                      >
                        {msg.image && (
                          <img
                            src={msg.image || "/placeholder.svg"}
                            alt="上传的图片"
                            className="max-h-48 md:max-h-64 rounded-lg shadow-sm mb-3"
                          />
                        )}

                        {msg.type === "ai" ? (
                          <StreamingMessage
                            content={streamingMessageId === msg.id ? currentStreamingContent : msg.content}
                            isStreaming={streamingMessageId === msg.id}
                            onStreamComplete={() => setStreamingMessageId(null)}
                          />
                        ) : (
                          <p className="text-sm md:text-base leading-relaxed" style={{ color: "#1D1D1F" }}>
                            {msg.content}
                          </p>
                        )}

                        {msg.type === "ai" && (
                          <div
                            className="border-t mt-3 pt-3 flex items-center justify-between"
                            style={{ borderColor: "#E5E7EB" }}
                          >
                            <span className="text-xs" style={{ color: "#6E6E73" }}>
                              {formatTime(msg.timestamp)}
                            </span>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="p-1 hover:text-[#3A5A40]"
                              style={{ color: "#6E6E73" }}
                              onClick={() => handleCopy(msg.content)}
                            >
                              <Copy className="w-3 h-3" />
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                {/* Loading动画 */}
                {isLoading && !streamingMessageId && (
                  <div className="flex justify-start">
                    <div className="flex space-x-3 max-w-[85%] md:max-w-[80%]">
                      <div
                        className="w-7 h-7 md:w-8 md:h-8 flex-shrink-0 rounded-full flex items-center justify-center"
                        style={{ backgroundColor: "#D6E97A" }}
                      >
                        <Bot className="w-4 h-4" style={{ color: "#3A5A40" }} />
                      </div>
                      <div
                        className="rounded-2xl p-3 md:p-4 border"
                        style={{
                          backgroundColor: "rgba(214, 233, 122, 0.2)",
                          borderColor: "rgba(214, 233, 122, 0.3)",
                        }}
                      >
                        <div className="flex space-x-1">
                          <div
                            className="w-2 h-2 rounded-full animate-bounce"
                            style={{ backgroundColor: "#3A5A40" }}
                          ></div>
                          <div
                            className="w-2 h-2 rounded-full animate-bounce animate-bounce-delay-1"
                            style={{ backgroundColor: "#3A5A40" }}
                          ></div>
                          <div
                            className="w-2 h-2 rounded-full animate-bounce animate-bounce-delay-2"
                            style={{ backgroundColor: "#3A5A40" }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* 底部输入区域 */}
            <div className="p-4 md:p-6" style={{ backgroundColor: "#FFFFFF" }}>
              <div className="max-w-4xl mx-auto">
                {/* 图片预览 */}
                {uploadedImagePreview && (
                  <div className="mb-4">
                    <div className="relative inline-block">
                      <img
                        src={uploadedImagePreview || "/placeholder.svg"}
                        alt="预览"
                        className="max-w-32 max-h-32 rounded-lg shadow-sm"
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        className="absolute -top-2 -right-2 w-6 h-6 p-0 bg-red-500 hover:bg-red-600 text-white rounded-full"
                        onClick={() => {
                          setUploadedImage(null)
                          setUploadedImagePreview(null)
                        }}
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                )}

                {/* 圆角矩形输入框 */}
                <div className="bg-gray-100 rounded-2xl border-2 border-gray-200 focus-within:border-[#D6E97A] p-4 shadow-sm">
                  <div className="flex items-center space-x-3">
                    <div className="flex-1">
                      <Input
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="给 CornCare 发送消息"
                        className="border-0 text-base bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 focus:outline-none p-0 h-auto"
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            e.preventDefault()
                            handleSend()
                          }
                        }}
                      />
                    </div>

                    {/* 上传按钮 */}
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-10 h-10 rounded-xl hover:text-[#3A5A40] hover:bg-[#F7F9FA] focus-visible:ring-0 focus-visible:ring-offset-0"
                      style={{ color: "#6E6E73" }}
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <Upload className="w-5 h-5" />
                    </Button>

                    {/* 发送按钮 */}
                    <Button
                      className="w-10 h-10 rounded-xl hover:bg-[#C5D86A] focus-visible:ring-0 focus-visible:ring-offset-0"
                      style={{ backgroundColor: "#D6E97A", color: "#3A5A40" }}
                      onClick={handleSend}
                      disabled={(!message.trim() && !uploadedImage) || isLoading}
                    >
                      <Send className="w-5 h-5" />
                    </Button>
                  </div>
                </div>

                {/* 底部提示 */}
                <div className="text-center mt-4">
                  <p className="text-xs" style={{ color: "#6E6E73" }}>
                    内容由 AI 生成，请仔细甄别
                  </p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      <input ref={fileInputRef} type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
    </div>
  )
}
