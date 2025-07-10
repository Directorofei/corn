import type { NextRequest } from "next/server"

/**
 * 将入站 Next.js Request 转发到目标后端
 * @param req  NextRequest
 * @param targetUrl  完整后端 URL
 */
export async function proxyRequest(req: NextRequest, targetUrl: string) {
  try {
    console.log(`代理请求: ${req.method} ${targetUrl}`)

    const init: RequestInit = {
      method: req.method,
      // 保留重要的 headers，特别注意不要覆盖 multipart/form-data 的边界
      headers: {
        // 只有在原请求没有 Content-Type 时才设置默认值
        ...(req.headers.get("content-type") 
            ? { "Content-Type": req.headers.get("content-type")! }
            : { "Content-Type": "application/json" }),
        Accept: req.headers.get("accept") || "*/*",
        "User-Agent": req.headers.get("user-agent") || "CornCare-Frontend",
      },
      // GET/HEAD 没有 body，其他方法使用 arrayBuffer 更好地处理各种数据类型
      body: ["GET", "HEAD"].includes(req.method) ? undefined : await req.arrayBuffer(),
      cache: "no-store",
      redirect: "manual",
    }

    const resp = await fetch(targetUrl, init)
    console.log(`后端响应: ${resp.status} ${resp.statusText}`)

    // 获取响应内容
    const body = await resp.arrayBuffer()

    // 创建响应，保留原始状态码和重要头部
    return new Response(body, {
      status: resp.status,
      statusText: resp.statusText,
      headers: {
        "Content-Type": resp.headers.get("content-type") || "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
      },
    })
  } catch (error) {
    console.error(`代理请求失败 ${targetUrl}:`, error)

    return new Response(
      JSON.stringify({
        error: "代理请求失败",
        message: error instanceof Error ? error.message : "未知错误",
        target: targetUrl,
      }),
      {
        status: 500,
        headers: {
          "Content-Type": "application/json",
        },
      },
    )
  }
}
