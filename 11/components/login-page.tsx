"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Wheat, Smartphone, Mail } from "lucide-react"
import { toast } from "sonner"

interface LoginPageProps {
  onLogin: () => void
}

export default function LoginPage({ onLogin }: LoginPageProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [mode, setMode] = useState<"login" | "register">("login")
  const [loginMethod, setLoginMethod] = useState<"phone" | "email">("phone")
  const [phoneNumber, setPhoneNumber] = useState("")
  const [email, setEmail] = useState("")
  const [verificationCode, setVerificationCode] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [userName, setUserName] = useState("")
  const [stayLoggedIn, setStayLoggedIn] = useState(false)
  const [countdown, setCountdown] = useState(0)

  const handleSendCode = () => {
    if (loginMethod === "phone" && !phoneNumber.trim()) {
      toast.error("请输入手机号")
      return
    }
    if (loginMethod === "email" && !email.trim()) {
      toast.error("请输入邮箱")
      return
    }

    setCountdown(60)
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          return 0
        }
        return prev - 1
      })
    }, 1000)

    toast.success("验证码已发送（演示模式）")
  }

  // 获取本地存储的用户数据
  const getStoredUsers = () => {
    try {
      const users = localStorage.getItem("corncare-registered-users")
      return users ? JSON.parse(users) : []
    } catch (error) {
      return []
    }
  }

  // 保存用户到本地存储
  const saveUserToStorage = (user: any) => {
    const users = getStoredUsers()
    users.push(user)
    localStorage.setItem("corncare-registered-users", JSON.stringify(users))
  }

  // 查找用户
  const findUser = (method: "phone" | "email", contact: string) => {
    const users = getStoredUsers()
    return users.find((user: any) => 
      method === "phone" ? user.phone === contact : user.email === contact
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    // 模拟网络延迟
    setTimeout(() => {
      setIsLoading(false)

      if (mode === "register") {
        // 注册逻辑
        if (loginMethod === "phone") {
          if (!phoneNumber || !verificationCode || !userName) {
            toast.error("请填写完整的注册信息")
            return
          }
          
          // 检查用户是否已存在
          if (findUser("phone", phoneNumber)) {
            toast.error("该手机号已注册，请直接登录")
            return
          }

          // 验证码校验（演示模式固定为123456）
          if (verificationCode !== "123456") {
            toast.error("验证码错误，演示模式请输入：123456")
            return
          }

          // 创建新用户
          const newUser = {
            id: `user-${Date.now()}`,
            name: userName,
            phone: phoneNumber,
            registeredAt: new Date().toISOString(),
            loginTime: new Date().toISOString(),
          }

          saveUserToStorage(newUser)
          localStorage.setItem("corncare-user", JSON.stringify(newUser))
          toast.success("注册成功！欢迎使用CornCare")
          onLogin()

        } else {
          // 邮箱注册
          if (!email || !password || !confirmPassword || !userName) {
            toast.error("请填写完整的注册信息")
            return
          }

          if (password !== confirmPassword) {
            toast.error("两次输入的密码不一致")
            return
          }

          if (password.length < 6) {
            toast.error("密码长度至少6位")
            return
          }

          // 检查用户是否已存在
          if (findUser("email", email)) {
            toast.error("该邮箱已注册，请直接登录")
            return
          }

          // 创建新用户
          const newUser = {
            id: `user-${Date.now()}`,
            name: userName,
            email: email,
            password: password, // 实际项目中应该加密
            registeredAt: new Date().toISOString(),
            loginTime: new Date().toISOString(),
          }

          saveUserToStorage(newUser)
          localStorage.setItem("corncare-user", JSON.stringify(newUser))
          toast.success("注册成功！欢迎使用CornCare")
          onLogin()
        }

      } else {
        // 登录逻辑
        if (loginMethod === "phone") {
          if (!phoneNumber || !verificationCode) {
            toast.error("请填写完整的登录信息")
            return
          }

          const user = findUser("phone", phoneNumber)
          if (!user) {
            toast.error("该手机号未注册，请先注册")
            return
          }

          // 验证码校验（演示模式固定为123456）
          if (verificationCode !== "123456") {
            toast.error("验证码错误，演示模式请输入：123456")
            return
          }

          // 更新登录时间
          user.loginTime = new Date().toISOString()
          localStorage.setItem("corncare-user", JSON.stringify(user))
          toast.success("登录成功！")
          onLogin()

        } else {
          // 邮箱登录
          if (!email || !password) {
            toast.error("请填写完整的登录信息")
            return
          }

          const user = findUser("email", email)
          if (!user) {
            toast.error("该邮箱未注册，请先注册")
            return
          }

          if (user.password !== password) {
            toast.error("密码错误")
            return
          }

          // 更新登录时间
          user.loginTime = new Date().toISOString()
          localStorage.setItem("corncare-user", JSON.stringify(user))
          toast.success("登录成功！")
          onLogin()
        }
      }
    }, 1500)
  }

  return (
    <div className="flex min-h-screen">
      {/* 左侧品牌展示区域 */}
      <div
        className="hidden lg:flex lg:flex-1 relative overflow-hidden"
        style={{
          background:
            "linear-gradient(135deg, rgba(45, 74, 58, 0.9) 0%, rgba(26, 47, 35, 0.9) 50%, rgba(15, 27, 20, 0.9) 100%)",
        }}
      >
        {/* 背景图片 */}
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: "url('/images/corn-field-bg.png')",
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        />

        {/* 渐变遮罩 */}
        <div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(135deg, rgba(45, 74, 58, 0.8) 0%, rgba(26, 47, 35, 0.8) 50%, rgba(15, 27, 20, 0.8) 100%)",
          }}
        />

        {/* 装饰元素 */}
        <div className="absolute inset-0">
          <div className="absolute top-20 left-20 w-2 h-2 bg-[#D6E97A] rounded-full opacity-60 animate-pulse"></div>
          <div
            className="absolute top-40 right-32 w-3 h-3 bg-[#D6E97A] rounded-full opacity-40 animate-pulse"
            style={{ animationDelay: "1s" }}
          ></div>
          <div
            className="absolute bottom-32 left-16 w-1 h-1 bg-[#D6E97A] rounded-full opacity-80 animate-pulse"
            style={{ animationDelay: "2s" }}
          ></div>
          <div
            className="absolute bottom-20 right-20 w-2 h-2 bg-[#D6E97A] rounded-full opacity-50 animate-pulse"
            style={{ animationDelay: "0.5s" }}
          ></div>
        </div>

        <div className="relative z-10 flex flex-col justify-center p-12 text-white">
          {/* Logo */}
          <div className="flex items-center space-x-3 mb-8">
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center shadow-lg"
              style={{ backgroundColor: "#D6E97A" }}
            >
              <Wheat className="w-7 h-7" style={{ color: "#3A5A40" }} />
            </div>
            <span className="text-2xl font-bold">CornCare</span>
          </div>

          {/* 主标题 */}
          <div className="space-y-6 mb-12">
            <h1 className="text-5xl font-bold leading-tight">
              开源智能农业
              <br />
              <span style={{ color: "#D6E97A" }}>守护玉米健康成长</span>
            </h1>
            <p className="text-xl text-gray-200 leading-relaxed">
              基于开源AI技术，免费提供玉米病虫害识别服务
              <br />
              智能诊断 · 精准识别 · 科学防治 · 数据分析
            </p>
          </div>

          {/* 项目介绍 */}
          <div className="space-y-6">
            <h2 className="text-3xl font-bold">
              CornCare —<span style={{ color: "#D6E97A" }}>开源农业AI平台</span>
            </h2>
            <div className="space-y-3 text-lg">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-[#D6E97A] rounded-full"></div>
                <span>完全免费，永久开源</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-[#D6E97A] rounded-full"></div>
                <span>AI驱动，精准识别</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-[#D6E97A] rounded-full"></div>
                <span>社区驱动，持续改进</span>
              </div>
            </div>
            <Button
              className="px-8 py-3 text-lg font-semibold rounded-xl hover:bg-[#C5D86A] transition-colors shadow-lg"
              style={{ backgroundColor: "#D6E97A", color: "#3A5A40" }}
            >
              开始使用 →
            </Button>
          </div>

          {/* 底部提示 */}
          <div className="mt-12 text-sm text-gray-300">
            <span className="inline-flex items-center">
              <Wheat className="w-4 h-4 mr-2" />
              开源项目，欢迎贡献代码和反馈建议
            </span>
          </div>
        </div>
      </div>

      {/* 右侧登录表单 */}
      <div className="flex-1 lg:max-w-md xl:max-w-lg flex items-center justify-center bg-white p-8">
        <div className="w-full max-w-sm space-y-8">
          {/* 表单标题 */}
          <div className="text-center space-y-2">
            <h2 className="text-2xl font-bold" style={{ color: "#1D1D1F" }}>
              欢迎使用 CornCare
            </h2>
            <div className="flex items-center justify-center space-x-1 text-sm" style={{ color: "#6E6E73" }}>
              <span>语言</span>
              <Select defaultValue="zh">
                <SelectTrigger className="w-16 h-6 border-0 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="zh">中文</SelectItem>
                  <SelectItem value="en">EN</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* 登录方式切换 */}
          <div className="flex rounded-lg p-1" style={{ backgroundColor: "#F7F9FA" }}>
            <button
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                loginMethod === "phone" ? "bg-white shadow-sm" : "text-gray-600 hover:text-gray-900"
              }`}
              onClick={() => setLoginMethod("phone")}
            >
              <Smartphone className="w-4 h-4 inline mr-2" />
              手机登录
            </button>
            <button
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                loginMethod === "email" ? "bg-white shadow-sm" : "text-gray-600 hover:text-gray-900"
              }`}
              onClick={() => setLoginMethod("email")}
            >
              <Mail className="w-4 h-4 inline mr-2" />
              邮箱登录
            </button>
          </div>

          {/* 登录/注册模式切换 */}
          <div className="flex rounded-lg p-1 mb-6" style={{ backgroundColor: "#F7F9FA" }}>
            <button
              type="button"
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                mode === "login" ? "bg-white shadow-sm" : "text-gray-600 hover:text-gray-900"
              }`}
              onClick={() => setMode("login")}
            >
              登录
            </button>
            <button
              type="button"
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                mode === "register" ? "bg-white shadow-sm" : "text-gray-600 hover:text-gray-900"
              }`}
              onClick={() => setMode("register")}
            >
              注册
            </button>
          </div>

          {/* 登录/注册表单 */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* 注册模式下的用户名字段 */}
            {mode === "register" && (
              <div className="space-y-2">
                <Label htmlFor="userName" className="text-sm font-medium">
                  用户名
                </Label>
                <Input
                  id="userName"
                  type="text"
                  placeholder="请输入用户名"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                  className="h-11 border-gray-200 focus:border-[#D6E97A]"
                  required
                />
              </div>
            )}

            {loginMethod === "phone" ? (
              <div className="space-y-2">
                <Label htmlFor="phone" className="text-sm font-medium">
                  手机号
                </Label>
                <div className="flex space-x-2">
                  <Select defaultValue="+86">
                    <SelectTrigger className="w-20">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="+86">+86</SelectItem>
                      <SelectItem value="+1">+1</SelectItem>
                      <SelectItem value="+44">+44</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input
                    id="phone"
                    type="tel"
                    placeholder="请输入手机号"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="flex-1 h-11 border-gray-200 focus:border-[#D6E97A]"
                    required
                  />
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium">
                  邮箱
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="请输入邮箱"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="h-11 border-gray-200 focus:border-[#D6E97A]"
                  required
                />
              </div>
            )}

            {loginMethod === "phone" ? (
              <div className="space-y-2">
                <Label htmlFor="code" className="text-sm font-medium">
                  验证码
                </Label>
                <div className="flex space-x-2">
                  <Input
                    id="code"
                    type="text"
                    placeholder="请输入验证码"
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value)}
                    className="flex-1 h-11 border-gray-200 focus:border-[#D6E97A]"
                    required
                  />
                  <Button
                    type="button"
                    variant="outline"
                    className="px-4 h-11 whitespace-nowrap bg-transparent"
                    onClick={handleSendCode}
                    disabled={countdown > 0}
                  >
                    {countdown > 0 ? `${countdown}s` : "获取验证码"}
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium">
                  密码
                </Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="请输入密码"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="h-11 border-gray-200 focus:border-[#D6E97A]"
                  required
                />
              </div>
            )}

            {/* 注册模式下的确认密码字段（仅邮箱注册） */}
            {mode === "register" && loginMethod === "email" && (
              <div className="space-y-2">
                <Label htmlFor="confirmPassword" className="text-sm font-medium">
                  确认密码
                </Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="请再次输入密码"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="h-11 border-gray-200 focus:border-[#D6E97A]"
                  required
                />
              </div>
            )}

            <Button
              type="submit"
              className="w-full h-12 text-base font-semibold rounded-xl hover:bg-[#C5D86A] transition-colors"
              style={{ backgroundColor: "#D6E97A", color: "#3A5A40" }}
              disabled={isLoading}
            >
              {isLoading 
                ? (mode === "register" ? "注册中..." : "登录中...") 
                : (mode === "register" ? "注册" : "登录")
              }
            </Button>

            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="stay-logged"
                  checked={stayLoggedIn}
                  onCheckedChange={(checked) => setStayLoggedIn(checked as boolean)}
                />
                <Label htmlFor="stay-logged" className="text-sm" style={{ color: "#6E6E73" }}>
                  30天内保持登录
                </Label>
              </div>
              <button type="button" className="text-sm hover:underline" style={{ color: "#D6E97A" }}>
                忘记密码
              </button>
            </div>
          </form>

          {/* 底部链接 */}
          <div className="text-center text-xs space-x-4" style={{ color: "#6E6E73" }}>
            <span>使用即表示同意</span>
            <a href="#" className="hover:underline" style={{ color: "#D6E97A" }}>
              开源协议
            </a>
            <span>和</span>
            <a href="#" className="hover:underline" style={{ color: "#D6E97A" }}>
              使用条款
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
