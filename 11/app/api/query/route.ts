import { NextRequest, NextResponse } from "next/server"
import { proxyRequest } from "@/lib/proxy-request"

// 明确声明环境变量类型
const BACKEND_BASE_URL: string = process.env.BACKEND_URL || "https://api.deepseek.com"

export async function POST(req: NextRequest) {
  return proxyRequest(req, `${BACKEND_BASE_URL}/api/query`)
}
