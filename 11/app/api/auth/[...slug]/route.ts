/**
 * 通用 Auth 代理：
 * /api/auth/*  =>  http://10.4.178.147:8000/api/auth/*
 */
import { NextRequest, NextResponse } from "next/server"

const BACKEND_BASE_URL: string = process.env.BACKEND_URL || "https://api.deepseek.com"

async function proxy(req: NextRequest, slug: string[]) {
  // 组装目标 URL
  const target = `${BACKEND_BASE_URL}/api/auth/${slug.join("/")}`

  // 复制原始请求
  const init: RequestInit = {
    method: req.method,
    headers: { "Content-Type": req.headers.get("content-type") || "application/json" },
    // 对于 GET/HEAD 没有 body
    body: ["GET", "HEAD"].includes(req.method) ? undefined : await req.text(),
    // 避免缓存
    cache: "no-store",
  }

  const res = await fetch(target, init)

  const data = await res.text() // 直接转发文本，可为 JSON
  return new NextResponse(data, {
    status: res.status,
    headers: { "Content-Type": res.headers.get("content-type") || "application/json" },
  })
}

// 为所有常用 HTTP 方法暴露同一个处理器
export async function GET(req: NextRequest, { params }: { params: { slug: string[] } }) {
  return proxy(req, params.slug)
}
export const POST = GET
export const PUT = GET
export const DELETE = GET
export const PATCH = GET
