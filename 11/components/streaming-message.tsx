"use client"

import { useState, useEffect } from "react"
import MarkdownRenderer from "./markdown-renderer"

interface StreamingMessageProps {
  content: string
  isStreaming: boolean
  onStreamComplete?: () => void
}

export default function StreamingMessage({ content, isStreaming, onStreamComplete }: StreamingMessageProps) {
  const [displayedContent, setDisplayedContent] = useState("")
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    if (!isStreaming) {
      setDisplayedContent(content)
      return
    }

    if (currentIndex < content.length) {
      const timer = setTimeout(() => {
        setDisplayedContent(content.slice(0, currentIndex + 1))
        setCurrentIndex(currentIndex + 1)
      }, 20) // 调整速度

      return () => clearTimeout(timer)
    } else if (onStreamComplete) {
      onStreamComplete()
    }
  }, [content, currentIndex, isStreaming, onStreamComplete])

  return (
    <div className="relative">
      <MarkdownRenderer content={displayedContent} />
      {isStreaming && currentIndex < content.length && (
        <span className="inline-block w-2 h-4 bg-gray-400 animate-pulse ml-1" />
      )}
    </div>
  )
}
