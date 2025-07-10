import { NextRequest, NextResponse } from "next/server"

const BACKEND_BASE_URL: string = process.env.BACKEND_URL || "https://api.deepseek.com"

export async function GET() {
  try {
    // 测试根路径
    const rootResponse = await fetch(`${BACKEND_BASE_URL}/`, {
      method: "GET",
    })
    const rootText = await rootResponse.text()

    // 测试健康检查
    const healthResponse = await fetch(`${BACKEND_BASE_URL}/api/health`, {
      method: "GET",
    })
    const healthText = await healthResponse.text()

    return NextResponse.json({
      backend_url: BACKEND_BASE_URL,
      root_endpoint: {
        status: rootResponse.status,
        response: rootText.substring(0, 200), // 只显示前200字符
      },
      health_endpoint: {
        status: healthResponse.status,
        response: healthText.substring(0, 200),
      },
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    return NextResponse.json(
      {
        error: "调试测试失败",
        message: error instanceof Error ? error.message : "未知错误",
        backend_url: BACKEND_BASE_URL,
      },
      { status: 500 },
    )
  }
}
