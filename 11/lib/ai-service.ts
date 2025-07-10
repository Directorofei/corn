export interface AISettings {
  baseUrl: string
  sdk: string
  modelName: string
  apiKey: string
  temperature: number
  maxTokens: number
}

export interface ChatMessage {
  role: "user" | "assistant" | "system"
  content: string
  image?: string
}

// 图片处理辅助函数
async function processImageForUpload(image: File | string): Promise<File | null> {
  try {
    if (typeof image === "string") {
      // 处理base64字符串或URL
      if (image.startsWith("data:")) {
        // base64图片
        const response = await fetch(image)
        const blob = await response.blob()
        return new File([blob], "image.jpg", { type: blob.type || "image/jpeg" })
      } else {
        // 普通URL - 尝试获取图片
        try {
          const response = await fetch(image)
          if (!response.ok) {
            throw new Error(`图片获取失败: ${response.status}`)
          }
          const blob = await response.blob()
          return new File([blob], "image.jpg", { type: blob.type || "image/jpeg" })
        } catch (fetchError) {
          console.warn("无法获取图片URL，跳过图片上传:", fetchError)
          return null
        }
      }
    } else {
      // 已经是File对象，直接返回
      return image
    }
  } catch (error) {
    console.warn("图片处理失败，跳过图片上传:", error)
    return null
  }
}

// 统一的API响应处理函数
async function processAPIResponse(response: Response): Promise<string> {
  if (!response.ok) {
    const errorText = await response.text()
    console.error("后端错误响应:", errorText)

    // 尝试解析为 JSON 错误格式
    try {
      const errorData = JSON.parse(errorText)
      const errorMessage = errorData.detail?.[0]?.msg || 
                         errorData.message || 
                         errorData.error || 
                         "后端服务器响应错误"
      throw new Error(errorMessage)
    } catch (parseError) {
      // 如果不是 JSON，直接使用文本
      throw new Error(`后端错误: ${errorText}`)
    }
  }

  // 获取响应文本
  const responseText = await response.text()
  console.log("后端响应内容:", responseText)

  if (!responseText || responseText.trim() === "") {
    throw new Error("后端返回了空响应")
  }

  // 尝试解析为 JSON，如果失败则返回原始文本
  try {
    const result = JSON.parse(responseText)
    // 如果是对象且有data字段，返回data；如果是字符串，返回字符串；否则返回整个结果
    if (typeof result === "object" && result !== null) {
      return result.data || result.message || result.response || JSON.stringify(result)
    }
    return result
  } catch (parseError) {
    // 如果不是 JSON，直接返回文本内容
    console.log("响应不是 JSON 格式，直接返回文本")
    return responseText
  }
}

// 生成AI回复 - 使用后端的 /api/query 接口
export async function generateAIResponse(
  messages: ChatMessage[],
  settings: AISettings,
  image?: File | string,
): Promise<string> {
  try {
    // 验证输入参数
    if (!messages || messages.length === 0) {
      throw new Error("没有找到对话消息")
    }

    // 构建表单数据
    const formData = new FormData()
    
    // 发送完整的对话历史，而不是只发送最后一条消息
    formData.append("messages", JSON.stringify(messages))
    
    // 传递AI设置参数，让后端知道用户想使用什么模型和配置
    formData.append("ai_settings", JSON.stringify(settings))

    // 处理图片（如果有）
    if (image) {
      const processedImage = await processImageForUpload(image)
      if (processedImage) {
        // 检查文件大小（限制5MB）
        if (processedImage.size > 5 * 1024 * 1024) {
          console.warn("图片大小超过5MB，跳过图片上传")
        } else {
          formData.append("image", processedImage)
        }
      }
    }

    console.log("发送请求到 /api/query...")
    const response = await fetch("/api/query", {
      method: "POST",
      body: formData,
    })

    console.log("响应状态:", response.status)

    // 使用统一的响应处理函数
    return await processAPIResponse(response)
  } catch (error) {
    console.error("AI生成失败:", error)
    if (error instanceof Error) {
      throw new Error(`AI服务错误: ${error.message}`)
    }
    throw new Error("AI服务暂时不可用，请检查网络连接")
  }
}

// 流式生成AI回复 - 模拟流式效果
export async function streamAIResponse(
  messages: ChatMessage[],
  settings: AISettings,
  onChunk: (chunk: string) => void,
  onComplete: (fullText: string) => void,
  onError: (error: string) => void,
  image?: File | string,
) {
  try {
    // 先获取完整响应
    const fullText = await generateAIResponse(messages, settings, image)

    if (!fullText || fullText.trim() === "") {
      onError("AI返回了空响应")
      return
    }

    // 模拟流式输出
    let currentIndex = 0
    const streamInterval = setInterval(() => {
      if (currentIndex < fullText.length) {
        // 调整块大小，中文字符优化处理
        const chunkSize = Math.floor(Math.random() * 2) + 1 // 1-2 字符
        const chunk = fullText.slice(currentIndex, currentIndex + chunkSize)
        onChunk(chunk)
        currentIndex += chunkSize
      } else {
        clearInterval(streamInterval)
        onComplete(fullText)
      }
    }, 50) // 调整为50ms，更适合中文显示
  } catch (error) {
    console.error("AI流式生成失败:", error)
    if (error instanceof Error) {
      onError(`AI服务错误: ${error.message}`)
    } else {
      onError("AI服务暂时不可用，请检查网络连接")
    }
  }
}

// 验证AI设置 - 使用专门的AI模型测试接口
export async function validateAISettings(settings: AISettings): Promise<boolean> {
  try {
    console.log("测试AI模型连接...")
    console.log("AI设置:", settings)
    
    const response = await fetch("/api/test-ai-model", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(settings),
    })

    console.log("AI模型测试响应状态:", response.status)

    if (!response.ok) {
      const errorText = await response.text()
      console.error("AI模型测试失败:", errorText)
      throw new Error(`AI模型连接失败: ${errorText}`)
    }

    const result = await response.json()
    console.log("AI模型测试响应:", result)
    
    // 检查响应中的success字段
    if (result.success === false) {
      throw new Error(result.error || "AI模型连接测试失败")
    }
    
    return true
  } catch (error) {
    console.error("AI设置验证失败:", error)
    if (error instanceof Error) {
      throw error
    }
    throw new Error("AI模型连接测试失败")
  }
}
