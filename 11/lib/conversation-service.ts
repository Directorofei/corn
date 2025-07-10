import type { Conversation } from "@/components/chat-interface"

// 由于后端API尚未完全实现对话CRUD操作，暂时统一使用本地存储
// 后续可以根据后端API实现情况进行调整

// 获取用户的所有对话历史 - 从本地存储获取
export async function getConversations(): Promise<Conversation[]> {
  try {
    return getLocalConversations()
  } catch (error) {
    console.error("获取对话历史失败:", error)
    return []
  }
}

// 保存对话到本地存储
export async function saveConversation(conversation: Conversation): Promise<boolean> {
  try {
    const conversations = getLocalConversations()
    const existingIndex = conversations.findIndex((c: Conversation) => c.id === conversation.id)

    if (existingIndex >= 0) {
      conversations[existingIndex] = conversation
    } else {
      conversations.unshift(conversation)
    }

    localStorage.setItem("corncare-conversations", JSON.stringify(conversations))
    return true
  } catch (error) {
    console.error("保存对话失败:", error)
    return false
  }
}

// 更新对话
export async function updateConversation(conversationId: string, updates: Partial<Conversation>): Promise<boolean> {
  try {
    const conversations = getLocalConversations()
    const index = conversations.findIndex((c: Conversation) => c.id === conversationId)

    if (index >= 0) {
      conversations[index] = { ...conversations[index], ...updates }
      localStorage.setItem("corncare-conversations", JSON.stringify(conversations))
      return true
    }

    return false
  } catch (error) {
    console.error("更新对话失败:", error)
    return false
  }
}

// 删除对话
export async function deleteConversation(conversationId: string): Promise<boolean> {
  try {
    const conversations = getLocalConversations()
    const filtered = conversations.filter((c: Conversation) => c.id !== conversationId)
    localStorage.setItem("corncare-conversations", JSON.stringify(filtered))
    return true
  } catch (error) {
    console.error("删除对话失败:", error)
    return false
  }
}

// 搜索对话
export async function searchConversations(query: string): Promise<Conversation[]> {
  try {
    const conversations = getLocalConversations()
    return conversations.filter(
      (c: Conversation) =>
        c.name.toLowerCase().includes(query.toLowerCase()) ||
        c.messages.some((m) => m.content.toLowerCase().includes(query.toLowerCase())),
    )
  } catch (error) {
    console.error("搜索对话失败:", error)
    return []
  }
}

// 从本地存储获取对话列表
export function getLocalConversations(): Conversation[] {
  try {
    if (typeof window === 'undefined') {
      return [] // 服务器端渲染时返回空数组
    }
    return JSON.parse(localStorage.getItem("corncare-conversations") || "[]")
  } catch (error) {
    console.error("获取本地对话失败:", error)
    return []
  }
}

// 备份对话到后端（可选功能，当后端API完善时使用）
export async function backupConversationsToBackend(): Promise<boolean> {
  try {
    const conversations = getLocalConversations()
    // TODO: 当后端API实现后，可以在这里调用后端API进行备份
    console.log("对话备份功能待后端API实现")
    return true
  } catch (error) {
    console.error("备份对话失败:", error)
    return false
  }
}

// 从后端恢复对话（可选功能，当后端API完善时使用）
export async function restoreConversationsFromBackend(): Promise<boolean> {
  try {
    // TODO: 当后端API实现后，可以在这里调用后端API进行恢复
    console.log("对话恢复功能待后端API实现")
    return true
  } catch (error) {
    console.error("恢复对话失败:", error)
    return false
  }
}
