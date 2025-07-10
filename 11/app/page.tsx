"use client"

import { useState } from "react"
import LoginPage from "@/components/login-page"
import ChatInterface from "@/components/chat-interface"

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  if (!isLoggedIn) {
    return <LoginPage onLogin={() => setIsLoggedIn(true)} />
  }

  return <ChatInterface />
}
