import { NextRequest, NextResponse } from "next/server"

const BACKEND_BASE_URL: string = process.env.BACKEND_URL || "https://api.deepseek.com"

export async function POST(request: NextRequest) {
  try {
    console.log("测试后端连接:", BACKEND_BASE_URL)

    // 测试后端健康检查接口
    const response = await fetch(`${BACKEND_BASE_URL}/api/health`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "User-Agent": "CornCare-Test",
      },
    })

    console.log("后端响应状态:", response.status)
    console.log("后端响应头:", Object.fromEntries(response.headers.entries()))

    const responseText = await response.text()
    console.log("后端响应内容:", responseText)

    if (!response.ok) {
      return NextResponse.json(
        {
          success: false,
          error: "后端服务器连接失败",
          status: response.status,
          response: responseText,
        },
        { status: response.status },
      )
    }

    // 尝试解析为 JSON
    let result
    try {
      result = JSON.parse(responseText)
    } catch (parseError) {
      // 如果不是 JSON，直接使用文本
      result = responseText
    }

    return NextResponse.json({
      success: true,
      message: "后端服务器连接正常",
      response: result,
      backend_url: BACKEND_BASE_URL,
    })
  } catch (error) {
    console.error("后端连接测试失败:", error)

    let errorMessage = "无法连接到后端服务器"

    if (error instanceof Error) {
      if (error.message.includes("fetch")) {
        errorMessage = "后端服务器连接失败，请检查服务器状态"
      } else {
        errorMessage = `连接失败: ${error.message}`
      }
    }

    return NextResponse.json(
      {
        success: false,
        error: errorMessage,
        backend_url: BACKEND_BASE_URL,
      },
      { status: 500 },
    )
  }
}
