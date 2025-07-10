// 改为调用同源 API，实际由 Route Handler 代理到后端
const API_PREFIX = "/api/auth"

export interface LoginCredentials {
  method: "phone" | "email"
  phone?: string
  email?: string
  verificationCode?: string
  password?: string
}

export interface AuthResponse {
  success: boolean
  token?: string
  user?: {
    id: string
    name: string
    email?: string
    phone?: string
  }
  error?: string
}

// 发送验证码
export async function sendVerificationCode(method: "phone" | "email", contact: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_PREFIX}/send-code`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        method,
        [method]: contact,
      }),
    })

    const result = await response.json()
    return result.success
  } catch (error) {
    console.error("发送验证码失败:", error)
    return false
  }
}

// 用户登录
export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  try {
    const response = await fetch(`${API_PREFIX}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentials),
    })

    const result = await response.json()

    if (result.success && result.token) {
      // 保存 token 到 localStorage
      localStorage.setItem("corncare-auth-token", result.token)
      localStorage.setItem("corncare-user", JSON.stringify(result.user))
    }

    return result
  } catch (error) {
    console.error("登录失败:", error)
    return {
      success: false,
      error: "网络连接失败，请检查网络设置",
    }
  }
}

// 用户注册
export async function register(userInfo: {
  name: string
  method: "phone" | "email"
  phone?: string
  email?: string
  verificationCode: string
  password?: string
}): Promise<AuthResponse> {
  try {
    const response = await fetch(`${API_PREFIX}/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userInfo),
    })

    const result = await response.json()

    if (result.success && result.token) {
      localStorage.setItem("corncare-auth-token", result.token)
      localStorage.setItem("corncare-user", JSON.stringify(result.user))
    }

    return result
  } catch (error) {
    console.error("注册失败:", error)
    return {
      success: false,
      error: "网络连接失败，请检查网络设置",
    }
  }
}

// 退出登录
export async function logout(): Promise<void> {
  try {
    const token = localStorage.getItem("corncare-auth-token")

    if (token) {
      await fetch(`${API_PREFIX}/logout`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      })
    }
  } catch (error) {
    console.error("退出登录失败:", error)
  } finally {
    // 清除本地存储
    localStorage.removeItem("corncare-auth-token")
    localStorage.removeItem("corncare-user")
  }
}

// 获取当前用户信息
export function getCurrentUser() {
  try {
    const userStr = localStorage.getItem("corncare-user")
    return userStr ? JSON.parse(userStr) : null
  } catch (error) {
    console.error("获取用户信息失败:", error)
    return null
  }
}

// 获取认证 token
export function getAuthToken(): string | null {
  return localStorage.getItem("corncare-auth-token")
}

// 检查是否已登录
export function isAuthenticated(): boolean {
  const token = getAuthToken()
  const user = getCurrentUser()
  return !!(token && user)
}
