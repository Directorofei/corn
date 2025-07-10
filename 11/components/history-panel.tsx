"use client"

import type React from "react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { ScrollArea } from "@/components/ui/scroll-area"
import { MessageSquare, Trash2, Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { useState } from "react"
import type { Conversation } from "./chat-interface"
import { toast } from "sonner"

interface HistoryPanelProps {
  conversations: Conversation[]
  currentConversationId: string
  onConversationSelect: (id: string) => void
  onDeleteConversation: (id: string) => void
  onUpdateConversationName: (id: string, name: string) => void
  open: boolean
  onOpenChange: (open: boolean) => void
}

export default function HistoryPanel({
  conversations,
  currentConversationId,
  onConversationSelect,
  onDeleteConversation,
  open,
  onOpenChange,
}: HistoryPanelProps) {
  const [searchQuery, setSearchQuery] = useState("")

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

  const handleDeleteConversation = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    onDeleteConversation(id)
    toast.success("对话已删除")
  }

  const filteredConversations = conversations.filter((conversation) =>
    conversation.name.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  // 按日期分组
  const groupedConversations = filteredConversations.reduce(
    (groups, conversation) => {
      const date = conversation.updatedAt
      const now = new Date()
      const diff = now.getTime() - date.getTime()
      const days = Math.floor(diff / 86400000)

      let groupKey = ""
      if (days === 0) groupKey = "今天"
      else if (days === 1) groupKey = "昨天"
      else if (days < 7) groupKey = "本周"
      else if (days < 30) groupKey = "本月"
      else groupKey = "更早"

      if (!groups[groupKey]) {
        groups[groupKey] = []
      }
      groups[groupKey].push(conversation)
      return groups
    },
    {} as Record<string, Conversation[]>,
  )

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full sm:w-[400px] md:w-[480px] bg-white p-0">
        <SheetHeader className="p-4 md:p-6 border-b" style={{ borderColor: "#E5E7EB" }}>
          <SheetTitle className="text-lg md:text-xl font-bold" style={{ color: "#1D1D1F" }}>
            对话历史
          </SheetTitle>

          {/* 搜索框 */}
          <div className="relative mt-4">
            <Search
              className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4"
              style={{ color: "#6E6E73" }}
            />
            <Input
              placeholder="搜索对话..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 h-10 border-gray-200 focus:border-[#D6E97A]"
            />
          </div>
        </SheetHeader>

        <ScrollArea className="h-[calc(100vh-140px)]">
          <div className="p-4 md:p-6 space-y-6">
            {Object.entries(groupedConversations).map(([groupName, groupConversations]) => (
              <div key={groupName} className="space-y-3">
                <h3 className="text-sm font-medium sticky top-0 bg-white py-2" style={{ color: "#6E6E73" }}>
                  {groupName}
                </h3>
                <div className="space-y-2">
                  {groupConversations.map((conversation) => (
                    <div
                      key={conversation.id}
                      className={`group p-3 rounded-xl cursor-pointer transition-all duration-300 ease-in-out ${
                        conversation.id === currentConversationId ? "shadow-sm" : "hover:shadow-sm"
                      }`}
                      style={{
                        backgroundColor: conversation.id === currentConversationId ? "#F7F9FA" : "transparent",
                      }}
                      onClick={() => {
                        onConversationSelect(conversation.id)
                        onOpenChange(false)
                      }}
                    >
                      <div className="flex items-start space-x-3">
                        <MessageSquare className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: "#6E6E73" }} />
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium truncate" style={{ color: "#1D1D1F" }}>
                            {conversation.name}
                          </div>
                          <div className="text-xs mt-1" style={{ color: "#6E6E73" }}>
                            {conversation.messages.length > 0 && (
                              <span className="block truncate">
                                {conversation.messages[conversation.messages.length - 1].content}
                              </span>
                            )}
                            <span className="mt-1 block">{formatTime(conversation.updatedAt)}</span>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="opacity-0 group-hover:opacity-100 w-6 h-6 p-0 hover:bg-gray-200 flex-shrink-0"
                          onClick={(e) => handleDeleteConversation(conversation.id, e)}
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
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
      </SheetContent>
    </Sheet>
  )
}
