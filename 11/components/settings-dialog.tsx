"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Switch } from "@/components/ui/switch"
import { Bot, Settings, X, Palette, Shield, UserCircle, Camera, CheckCircle, AlertCircle } from "lucide-react"
import { toast } from "sonner"
import { validateAISettings, type AISettings } from "@/lib/ai-service"

interface SettingsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSettingsChange: (settings: AISettings) => void
}

type SettingsTab = "general" | "personalization" | "ai" | "security" | "account"

export default function SettingsDialog({ open, onOpenChange, onSettingsChange }: SettingsDialogProps) {
  const [activeTab, setActiveTab] = useState<SettingsTab>("general")
  const [name, setName] = useState("农业专家")
  const [email, setEmail] = useState("expert@corncare.com")
  const [baseUrl, setBaseUrl] = useState("https://api.openai.com/v1")
  const [sdk, setSdk] = useState("openai")
  const [modelName, setModelName] = useState("gpt-4")
  const [apiKey, setApiKey] = useState("")
  const [temperature, setTemperature] = useState("0.7")
  const [maxTokens, setMaxTokens] = useState("2048")
  const [isTestingConnection, setIsTestingConnection] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)
  const [theme, setTheme] = useState("system")
  const [language, setLanguage] = useState("zh-CN")
  const [voiceEnabled, setVoiceEnabled] = useState(false)
  const [soundEnabled, setSoundEnabled] = useState(true)
  const [showTermsInChat, setShowTermsInChat] = useState(true)

  // 从localStorage加载设置
  useEffect(() => {
    const savedSettings = localStorage.getItem("corncare-ai-settings")
    if (savedSettings) {
      try {
        const settings = JSON.parse(savedSettings)
        setBaseUrl(settings.baseUrl || "https://api.openai.com/v1")
        setSdk(settings.sdk || "openai")
        setModelName(settings.modelName || "gpt-4")
        setApiKey(settings.apiKey || "")
        setTemperature(settings.temperature?.toString() || "0.7")
        setMaxTokens(settings.maxTokens?.toString() || "2048")
      } catch (error) {
        console.error("加载设置失败:", error)
      }
    }
  }, [])

  const getCurrentSettings = (): AISettings => ({
    baseUrl,
    sdk,
    modelName,
    apiKey,
    temperature: Number.parseFloat(temperature) || 0.7,
    maxTokens: Number.parseInt(maxTokens) || 2048,
  })

  const handleSaveSettings = () => {
    if (activeTab === "ai") {
      const settings = getCurrentSettings()

      // 验证设置
      if (!settings.apiKey.trim()) {
        toast.error("请输入API Key")
        return
      }

      if (!settings.modelName.trim()) {
        toast.error("请输入模型名称")
        return
      }

      if (settings.temperature < 0 || settings.temperature > 2) {
        toast.error("温度参数应在0-2之间")
        return
      }

      if (settings.maxTokens < 1 || settings.maxTokens > 4096) {
        toast.error("最大令牌数应在1-4096之间")
        return
      }

      // 保存到localStorage
      localStorage.setItem("corncare-ai-settings", JSON.stringify(settings))

      // 通知父组件设置已更改
      onSettingsChange(settings)
    }

    toast.success("设置已保存")
  }

  const handleTestModel = async () => {
    const settings = getCurrentSettings()

    if (!settings.apiKey.trim()) {
      toast.error("请先输入API Key")
      return
    }

    setIsTestingConnection(true)
    setTestResult(null)

    try {
      const isValid = await validateAISettings(settings)
      if (isValid) {
        setTestResult({ success: true, message: "模型连接测试成功！" })
        toast.success("模型连接正常")
      } else {
        setTestResult({ success: false, message: "模型连接失败" })
        toast.error("模型连接失败，请检查设置")
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "连接测试失败，请检查网络和设置"
      setTestResult({ success: false, message: errorMessage })
      toast.error(errorMessage)
    } finally {
      setIsTestingConnection(false)
    }
  }

  const handleReset = () => {
    if (activeTab === "ai") {
      setBaseUrl("https://api.openai.com/v1")
      setSdk("openai")
      setModelName("gpt-4")
      setApiKey("")
      setTemperature("0.7")
      setMaxTokens("2048")
      setTestResult(null)
      localStorage.removeItem("corncare-ai-settings")
    }
    toast.success("设置已重置")
  }

  const handleLogout = () => {
    toast.success("已退出登录")
    onOpenChange(false)
  }

  const menuItems = [
    { id: "general" as SettingsTab, icon: Settings, label: "通用设置" },
    { id: "personalization" as SettingsTab, icon: Palette, label: "个性化" },
    { id: "ai" as SettingsTab, icon: Bot, label: "AI模型" },
    { id: "security" as SettingsTab, icon: Shield, label: "安全" },
    { id: "account" as SettingsTab, icon: UserCircle, label: "账户" },
  ]

  const renderContent = () => {
    switch (activeTab) {
      case "general":
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-gray-800 text-base font-medium">主题</Label>
                  <p className="text-gray-600 text-sm mt-1">选择应用程序的外观主题</p>
                </div>
                <Select value={theme} onValueChange={setTheme}>
                  <SelectTrigger className="w-32 bg-white border-gray-300 text-gray-800 focus:border-[#D6E97A]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white border-gray-300">
                    <SelectItem value="system" className="text-gray-800">
                      系统
                    </SelectItem>
                    <SelectItem value="light" className="text-gray-800">
                      浅色
                    </SelectItem>
                    <SelectItem value="dark" className="text-gray-800">
                      深色
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-gray-800 text-base font-medium">语言</Label>
                  <p className="text-gray-600 text-sm mt-1">选择界面显示语言</p>
                </div>
                <Select value={language} onValueChange={setLanguage}>
                  <SelectTrigger className="w-32 bg-white border-gray-300 text-gray-800 focus:border-[#D6E97A]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white border-gray-300">
                    <SelectItem value="zh-CN" className="text-gray-800">
                      中文
                    </SelectItem>
                    <SelectItem value="en-US" className="text-gray-800">
                      English
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-gray-800 text-base font-medium">声音提醒</Label>
                  <p className="text-gray-600 text-sm mt-1">新消息时播放提示音</p>
                </div>
                <Switch
                  checked={soundEnabled}
                  onCheckedChange={setSoundEnabled}
                  className="data-[state=checked]:bg-[#D6E97A]"
                />
              </div>
            </div>
          </div>
        )

      case "personalization":
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-gray-800 text-base font-medium">语音输入</Label>
                  <p className="text-gray-600 text-sm mt-1">启用语音输入功能</p>
                </div>
                <Switch
                  checked={voiceEnabled}
                  onCheckedChange={setVoiceEnabled}
                  className="data-[state=checked]:bg-[#D6E97A]"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-gray-800 text-base font-medium">在聊天中显示使用条款</Label>
                  <p className="text-gray-600 text-sm mt-1">在对话界面显示使用条款提醒</p>
                </div>
                <Switch
                  checked={showTermsInChat}
                  onCheckedChange={setShowTermsInChat}
                  className="data-[state=checked]:bg-[#D6E97A]"
                />
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div>
                  <Label className="text-gray-800 text-base font-medium">界面自定义</Label>
                  <p className="text-gray-600 text-sm mt-1 mb-4">个性化您的CornCare体验</p>
                  <div className="grid grid-cols-3 gap-3">
                    <div className="p-3 rounded-lg border-2 border-[#D6E97A] bg-[#D6E97A]/10 cursor-pointer">
                      <div className="w-full h-16 bg-[#D6E97A] rounded mb-2"></div>
                      <p className="text-xs text-center text-gray-700">绿色主题</p>
                    </div>
                    <div className="p-3 rounded-lg border border-gray-300 hover:border-gray-400 cursor-pointer">
                      <div className="w-full h-16 bg-blue-500 rounded mb-2"></div>
                      <p className="text-xs text-center text-gray-700">蓝色主题</p>
                    </div>
                    <div className="p-3 rounded-lg border border-gray-300 hover:border-gray-400 cursor-pointer">
                      <div className="w-full h-16 bg-purple-500 rounded mb-2"></div>
                      <p className="text-xs text-center text-gray-700">紫色主题</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )

      case "ai":
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-gray-800 text-sm font-medium">Base URL</Label>
                  <Input
                    value={baseUrl}
                    onChange={(e) => setBaseUrl(e.target.value)}
                    placeholder="https://api.openai.com/v1"
                    className="bg-white border-gray-300 text-gray-800 placeholder-gray-500 focus:border-[#D6E97A] focus:ring-[#D6E97A]"
                  />
                </div>

                <div className="space-y-2">
                  <Label className="text-gray-800 text-sm font-medium">SDK类型</Label>
                  <Select value={sdk} onValueChange={setSdk}>
                    <SelectTrigger className="bg-white border-gray-300 text-gray-800 focus:border-[#D6E97A]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-white border-gray-300">
                      <SelectItem value="openai" className="text-gray-800">
                        OpenAI
                      </SelectItem>
                      <SelectItem value="anthropic" className="text-gray-800">
                        Anthropic
                      </SelectItem>
                      <SelectItem value="google" className="text-gray-800">
                        Google
                      </SelectItem>
                      <SelectItem value="azure" className="text-gray-800">
                        Azure OpenAI
                      </SelectItem>
                      <SelectItem value="custom" className="text-gray-800">
                        自定义
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-gray-800 text-sm font-medium">模型名称</Label>
                  <Input
                    value={modelName}
                    onChange={(e) => setModelName(e.target.value)}
                    placeholder="gpt-4"
                    className="bg-white border-gray-300 text-gray-800 placeholder-gray-500 focus:border-[#D6E97A] focus:ring-[#D6E97A] font-mono"
                  />
                </div>

                <div className="space-y-2">
                  <Label className="text-gray-800 text-sm font-medium">API Key</Label>
                  <Input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="sk-..."
                    className="bg-white border-gray-300 text-gray-800 placeholder-gray-500 focus:border-[#D6E97A] focus:ring-[#D6E97A] font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-gray-800 text-sm font-medium">温度参数 (0.0 - 2.0)</Label>
                  <Input
                    value={temperature}
                    onChange={(e) => setTemperature(e.target.value)}
                    placeholder="0.7"
                    className="bg-white border-gray-300 text-gray-800 placeholder-gray-500 focus:border-[#D6E97A] focus:ring-[#D6E97A]"
                  />
                </div>

                <div className="space-y-2">
                  <Label className="text-gray-800 text-sm font-medium">最大令牌数 (1 - 4096)</Label>
                  <Input
                    value={maxTokens}
                    onChange={(e) => setMaxTokens(e.target.value)}
                    placeholder="2048"
                    className="bg-white border-gray-300 text-gray-800 placeholder-gray-500 focus:border-[#D6E97A] focus:ring-[#D6E97A]"
                  />
                </div>
              </div>

              {/* 测试结果显示 */}
              {testResult && (
                <div
                  className={`p-4 rounded-lg border flex items-center space-x-3 ${
                    testResult.success
                      ? "bg-green-50 border-green-200 text-green-800"
                      : "bg-red-50 border-red-200 text-red-800"
                  }`}
                >
                  {testResult.success ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-red-600" />
                  )}
                  <span className="text-sm font-medium">{testResult.message}</span>
                </div>
              )}

              <div className="flex space-x-3 pt-4">
                <Button
                  className="flex-1 bg-[#D6E97A] hover:bg-[#C5D86A] text-[#3A5A40] font-medium"
                  onClick={handleSaveSettings}
                >
                  保存设置
                </Button>
                <Button
                  variant="outline"
                  className="flex-1 border-gray-300 text-gray-700 hover:bg-gray-50 bg-white"
                  onClick={handleTestModel}
                  disabled={isTestingConnection}
                >
                  {isTestingConnection ? "测试中..." : "测试连接"}
                </Button>
                <Button
                  variant="outline"
                  className="border-gray-300 text-gray-700 hover:bg-gray-50 bg-white"
                  onClick={handleReset}
                >
                  重置
                </Button>
              </div>
            </div>
          </div>
        )

      case "security":
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-gray-800 text-base font-medium">自动锁定</Label>
                  <p className="text-gray-600 text-sm mt-1">长时间不活动时自动锁定应用</p>
                </div>
                <Switch className="data-[state=checked]:bg-[#D6E97A]" />
              </div>

              <div className="pt-4 border-t border-gray-200">
                <Label className="text-gray-800 text-base font-medium">更改密码</Label>
                <p className="text-gray-600 text-sm mt-1 mb-3">修改您的登录密码</p>
                <Button variant="outline" className="border-gray-300 text-gray-700 hover:bg-gray-50 bg-white">
                  更改密码
                </Button>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <Label className="text-gray-800 text-base font-medium">数据安全</Label>
                <p className="text-gray-600 text-sm mt-1 mb-3">管理您的数据和隐私设置</p>
                <div className="space-y-2">
                  <Button variant="outline" className="w-full border-gray-300 text-gray-700 hover:bg-gray-50 bg-white">
                    导出数据
                  </Button>
                  <Button variant="outline" className="w-full border-red-300 text-red-600 hover:bg-red-50 bg-white">
                    清除所有数据
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )

      case "account":
        return (
          <div className="space-y-6">
            <div className="space-y-6">
              <div className="flex items-center space-x-6">
                <div
                  className="w-20 h-20 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: "#D6E97A", color: "#3A5A40" }}
                >
                  <UserCircle className="w-12 h-12" />
                </div>
                <Button variant="outline" className="border-gray-300 text-gray-700 hover:bg-gray-50 bg-white">
                  <Camera className="w-4 h-4 mr-2" />
                  更换头像
                </Button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-gray-800 text-sm font-medium">姓名</Label>
                  <Input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="bg-white border-gray-300 text-gray-800 placeholder-gray-500 focus:border-[#D6E97A] focus:ring-[#D6E97A]"
                  />
                </div>

                <div className="space-y-2">
                  <Label className="text-gray-800 text-sm font-medium">邮箱</Label>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="bg-white border-gray-300 text-gray-800 placeholder-gray-500 focus:border-[#D6E97A] focus:ring-[#D6E97A]"
                  />
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <Button
                  className="w-full bg-[#D6E97A] hover:bg-[#C5D86A] text-[#3A5A40] font-medium"
                  onClick={handleSaveSettings}
                >
                  保存个人信息
                </Button>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <Button
                  variant="outline"
                  className="w-full border-red-300 text-red-600 hover:bg-red-50 bg-white"
                  onClick={handleLogout}
                >
                  退出登录
                </Button>
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl w-[90vw] max-h-[90vh] p-0 bg-white border-gray-200 overflow-hidden">
        <div className="flex h-[80vh]">
          {/* 左侧菜单 */}
          <div className="w-64 bg-[#F8F9FA] border-r border-gray-200">
            {/* 头部 */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h2 className="text-gray-800 text-lg font-semibold">设置</h2>
              <Button
                variant="ghost"
                size="sm"
                className="w-8 h-8 p-0 text-gray-500 hover:text-gray-700 hover:bg-gray-100"
                onClick={() => onOpenChange(false)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>

            {/* 菜单项 */}
            <ScrollArea className="flex-1">
              <div className="p-2">
                {menuItems.map((item) => (
                  <button
                    key={item.id}
                    className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-left transition-colors ${
                      activeTab === item.id
                        ? "bg-[#D6E97A] text-[#3A5A40] shadow-sm"
                        : "text-gray-600 hover:text-gray-800 hover:bg-gray-100"
                    }`}
                    onClick={() => setActiveTab(item.id)}
                  >
                    <item.icon className="w-4 h-4" />
                    <span className="text-sm font-medium">{item.label}</span>
                  </button>
                ))}
              </div>
            </ScrollArea>
          </div>

          {/* 右侧内容 */}
          <div className="flex-1 flex flex-col bg-white">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-gray-800 text-xl font-semibold">
                {menuItems.find((item) => item.id === activeTab)?.label}
              </h3>
              <p className="text-gray-600 text-sm mt-1">
                {activeTab === "general" && "管理应用程序的基本设置"}
                {activeTab === "personalization" && "个性化您的CornCare体验"}
                {activeTab === "ai" && "配置AI模型和相关参数"}
                {activeTab === "security" && "管理账户安全和隐私设置"}
                {activeTab === "account" && "管理您的个人信息和账户设置"}
              </p>
            </div>

            <ScrollArea className="flex-1 p-6">{renderContent()}</ScrollArea>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
