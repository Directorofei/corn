"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Plus,
  Wheat,
  MessageSquare,
  Scan,
  FileText,
  BarChart3,
  BookOpen,
  Search,
  Trash2,
  Clock,
  User,
} from "lucide-react"
import { toast } from "sonner"
import type { Conversation } from "./chat-interface"

interface ChatSidebarProps {
  conversations: Conversation[]
  currentConversationId: string
  onConversationSelect: (id: string) => void
  onNewConversation: () => void
  onDeleteConversation: (id: string) => void
  currentFeature: string
  onFeatureChange: (feature: string) => void
  onSettingsOpen: () => void
}

export default function ChatSidebar({
  conversations,
  currentConversationId,
  onConversationSelect,
  onNewConversation,
  onDeleteConversation,
  currentFeature,
  onFeatureChange,
  onSettingsOpen,
}: ChatSidebarProps) {
  const [isHistoryExpanded, setIsHistoryExpanded] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [hoveredConversation, setHoveredConversation] = useState<string | null>(null)
  const [hoveredFeature, setHoveredFeature] = useState<string | null>(null)

  const handleFeatureClick = (featureId: string, featureName: string) => {
    onFeatureChange(featureId)
    if (featureId !== "chat") {
      toast.info(`${featureName}功能开发中...`)
    }
  }

  const handleNewConversation = () => {
    onNewConversation()
    toast.success("新对话已创建")
  }

  const handleDeleteConversation = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    onDeleteConversation(id)
    toast.success("对话已删除")
  }

  const formatTime = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return "刚刚"
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`
    return date.toLocaleDateString()
  }

  const features = [
    { id: "chat", icon: MessageSquare, name: "智能对话", description: "AI智能对话" },
    { id: "scan", icon: Scan, name: "智能识别", description: "AI病虫害识别" },
    { id: "report", icon: FileText, name: "诊断报告", description: "生成详细报告" },
    { id: "analysis", icon: BarChart3, name: "数据分析", description: "病害趋势分析" },
    { id: "knowledge", icon: BookOpen, name: "知识库", description: "病虫害百科" },
  ]

  const filteredConversations = conversations.filter((conversation) =>
    conversation.name.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  // 鼠标进入左侧边缘时展开历史记录
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (currentFeature === "chat") {
        if (e.clientX <= 10) {
          setIsHistoryExpanded(true)
        } else if (e.clientX > 320) {
          setIsHistoryExpanded(false)
        }
      }
    }

    window.addEventListener("mousemove", handleMouseMove)
    return () => window.removeEventListener("mousemove", handleMouseMove)
  }, [currentFeature])

  return (
    <div className="relative">
      {/* 历史记录展开面板 - 提高z-index，确保在主侧边栏之上 */}
      {currentFeature === "chat" && (
        <div
          className={`fixed left-0 top-0 z-20 h-screen shadow-lg transition-all duration-300 ease-in-out ${
            isHistoryExpanded ? "w-80 opacity-100" : "w-0 opacity-0 pointer-events-none"
          }`}
          style={{ backgroundColor: "#F8F9FA" }}
          onMouseEnter={() => setIsHistoryExpanded(true)}
          onMouseLeave={() => setIsHistoryExpanded(false)}
        >
          <div className="flex flex-col h-full">
            {/* 历史记录头部 */}
            <div className="p-4 space-y-4">
              {/* Logo */}
              <div className="flex items-center space-x-3">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: "#D6E97A" }}
                >
                  <Wheat className="w-5 h-5" style={{ color: "#3A5A40" }} />
                </div>
                <h1 className="text-lg font-bold" style={{ color: "#1D1D1F" }}>
                  CornCare
                </h1>
              </div>

              {/* 新建会话按钮 */}
              <Button
                className="w-full h-11 rounded-xl hover:bg-[#C5D86A] justify-between"
                style={{ backgroundColor: "#D6E97A", color: "#3A5A40" }}
                onClick={handleNewConversation}
              >
                <div className="flex items-center">
                  <Plus className="w-4 h-4 mr-2" />
                  新建会话
                </div>
                <div className="text-xs opacity-70">Ctrl K</div>
              </Button>

              {/* 搜索框 */}
              <div className="relative">
                <Search
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4"
                  style={{ color: "#6E6E73" }}
                />
                <Input
                  placeholder="搜索会话..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 h-10 border-gray-200 focus:border-[#D6E97A] focus:outline-none"
                />
              </div>
            </div>

            {/* 历史会话标题 */}
            <div className="px-4 py-3">
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4" style={{ color: "#6E6E73" }} />
                <h2 className="text-sm font-medium" style={{ color: "#6E6E73" }}>
                  历史会话
                </h2>
              </div>
            </div>

            {/* 会话列表 */}
            <ScrollArea className="flex-1">
              <div className="p-2 space-y-1">
                {filteredConversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    className={`group p-3 rounded-lg cursor-pointer transition-all duration-200 ease-in-out ${
                      conversation.id === currentConversationId
                        ? "shadow-sm"
                        : hoveredConversation === conversation.id
                          ? "shadow-sm"
                          : "hover:bg-gray-50"
                    }`}
                    style={{
                      backgroundColor:
                        conversation.id === currentConversationId
                          ? "#F7F9FA"
                          : hoveredConversation === conversation.id
                            ? "#F7F9FA"
                            : "transparent",
                    }}
                    onClick={() => onConversationSelect(conversation.id)}
                    onMouseEnter={() => setHoveredConversation(conversation.id)}
                    onMouseLeave={() => setHoveredConversation(null)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate mb-1" style={{ color: "#1D1D1F" }}>
                          {conversation.name}
                        </div>
                        <div className="text-xs" style={{ color: "#6E6E73" }}>
                          {formatTime(conversation.updatedAt)}
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className={`w-6 h-6 p-0 hover:bg-red-100 transition-opacity duration-200 ${
                          hoveredConversation === conversation.id ? "opacity-100" : "opacity-0"
                        }`}
                        onClick={(e) => handleDeleteConversation(conversation.id, e)}
                      >
                        <Trash2 className="w-3 h-3 text-red-500" />
                      </Button>
                    </div>
                  </div>
                ))}

                {filteredConversations.length === 0 && (
                  <div className="text-center py-8">
                    <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-30" style={{ color: "#6E6E73" }} />
                    <p className="text-sm" style={{ color: "#6E6E73" }}>
                      {searchQuery ? "未找到匹配的对话" : "暂无对话历史"}
                    </p>
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* 查看全部 */}
            <div className="p-4">
              <Button variant="ghost" className="w-full text-sm hover:bg-[#F7F9FA]" style={{ color: "#6E6E73" }}>
                查看全部
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* 主侧边栏 - 降低z-index，确保在历史记录面板之下 */}
      <div
        className={`fixed left-0 top-0 z-10 flex flex-col transition-all duration-300 ease-in-out h-screen ${
          isHistoryExpanded && currentFeature === "chat" ? "w-20" : "w-20"
        }`}
        style={{ backgroundColor: "#F8F9FA" }}
      >
        {/* Header */}
        <div className="p-4 flex flex-col items-center space-y-4">
          <div
            className="relative w-10 h-10 rounded-lg flex items-center justify-center cursor-pointer"
            style={{ backgroundColor: "#D6E97A" }}
            onMouseEnter={() => setHoveredFeature("logo")}
            onMouseLeave={() => setHoveredFeature(null)}
          >
            <Wheat className="w-6 h-6" style={{ color: "#3A5A40" }} />

            {/* 悬停提示 */}
            {hoveredFeature === "logo" && (
              <div className="absolute left-full ml-2 top-0 px-3 py-2 bg-gray-800 text-white text-sm rounded-lg whitespace-nowrap z-50 shadow-lg">
                CornCare
                <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-gray-800 rotate-45"></div>
              </div>
            )}
          </div>
        </div>

        {/* 功能列表 */}
        <div className="flex-1 flex flex-col justify-between p-4">
          <div className="space-y-2">
            {features.map((feature) => (
              <div
                key={feature.id}
                className="relative"
                onMouseEnter={() => setHoveredFeature(feature.id)}
                onMouseLeave={() => setHoveredFeature(null)}
              >
                <Button
                  variant="ghost"
                  className={`w-10 h-10 p-0 rounded-xl transition-all duration-300 ease-in-out ${
                    currentFeature === feature.id ? "shadow-md" : "hover:bg-[rgba(214,233,122,0.3)]"
                  }`}
                  style={{
                    backgroundColor: currentFeature === feature.id ? "#D6E97A" : "transparent",
                    color: currentFeature === feature.id ? "#3A5A40" : "#6E6E73",
                  }}
                  onClick={() => handleFeatureClick(feature.id, feature.name)}
                >
                  <feature.icon className="w-5 h-5" />
                </Button>

                {/* 悬停提示 */}
                {hoveredFeature === feature.id && (
                  <div className="absolute left-full ml-2 top-0 px-3 py-2 bg-gray-800 text-white text-sm rounded-lg whitespace-nowrap z-50 shadow-lg">
                    {feature.name}
                    <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-gray-800 rotate-45"></div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* 底部用户信息 */}
          <div className="pt-4">
            <Button
              variant="ghost"
              className="w-full p-2 hover:bg-[#F7F9FA] rounded-xl flex flex-col items-center space-y-1"
              onClick={onSettingsOpen}
            >
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center"
                style={{ backgroundColor: "#D6E97A", color: "#3A5A40" }}
              >
                <User className="w-4 h-4" />
              </div>
              <div className="text-xs font-medium truncate" style={{ color: "#1D1D1F" }}>
                农业专家
              </div>
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
