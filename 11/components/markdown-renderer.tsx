"use client"

import ReactMarkdown from "react-markdown"
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism"

interface MarkdownRendererProps {
  content: string
}

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <div className="prose prose-sm max-w-none">
      <ReactMarkdown
        components={{
        // 自定义代码块渲染
        code({ children, className, ...props }: any) {
          const match = /language-(\w+)/.exec(className || "")
          const inline = !match
          return !inline && match ? (
            <SyntaxHighlighter
              style={oneDark as any}
              language={match[1]}
              PreTag="div"
              className="rounded-lg text-sm"
              {...props}
            >
              {String(children).replace(/\n$/, "")}
            </SyntaxHighlighter>
          ) : (
            <code className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
              {children}
            </code>
          )
        },
        // 自定义标题渲染
        h1: ({ children }) => (
          <h1 className="text-xl font-bold mb-3 mt-4 text-gray-900 flex items-center">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-lg font-semibold mb-2 mt-3 text-gray-800 flex items-center">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-base font-medium mb-2 mt-2 text-gray-700 flex items-center">{children}</h3>
        ),
        // 自定义列表渲染
        ul: ({ children }) => <ul className="list-disc list-inside space-y-1 my-2 ml-2">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 my-2 ml-2">{children}</ol>,
        li: ({ children }) => <li className="text-gray-700 leading-relaxed">{children}</li>,
        // 自定义段落渲染
        p: ({ children }) => <p className="mb-2 leading-relaxed text-gray-700">{children}</p>,
        // 自定义强调渲染
        strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
        // 自定义链接渲染
        a: ({ href, children }) => (
          <a
            href={href}
            className="text-blue-600 hover:text-blue-800 underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            {children}
          </a>
        ),
        // 自定义引用渲染
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-gray-300 pl-4 py-2 my-2 bg-gray-50 rounded-r">{children}</blockquote>
        ),
      }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
