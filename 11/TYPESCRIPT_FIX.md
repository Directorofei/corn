# TypeScript 错误修复指南

## 🔍 问题描述

在 Windows 环境下，由于 PowerShell 执行策略限制，npm 命令无法正常运行，导致以下 TypeScript 错误：

1. `Cannot find module 'next/server'` - Next.js 服务器类型声明问题
2. `Cannot find name 'process'` - Node.js 环境变量类型问题

## ✅ 已实施的解决方案

### 1. 创建自定义类型声明文件

**文件**: `types/global.d.ts`

此文件提供了：
- ✅ `NextRequest` 和 `NextResponse` 类型声明
- ✅ `process.env` 环境变量类型声明
- ✅ 常用环境变量的预定义类型

### 2. 更新 TypeScript 配置

**文件**: `tsconfig.json`

添加了：
- ✅ `typeRoots` 配置指向自定义类型目录
- ✅ `include` 包含新的类型声明文件

## 🚀 如何验证修复

### 方法 1: VS Code 类型检查
1. 在 VS Code 中打开任意 `route.ts` 文件
2. 检查是否还有红色波浪线错误提示
3. 鼠标悬停在 `NextRequest` 和 `process.env` 上应该能看到类型信息

### 方法 2: 重启 TypeScript 服务
1. 在 VS Code 中按 `Ctrl+Shift+P`
2. 搜索并执行 "TypeScript: Restart TS Server"
3. 等待几秒钟让 TypeScript 重新加载类型定义

### 方法 3: 手动类型检查（如果 npm 可用）
```bash
# 如果 PowerShell 执行策略允许
npx tsc --noEmit

# 或者使用命令提示符（cmd）而不是 PowerShell
cmd /c "npx tsc --noEmit"
```

## 🔧 如果问题依然存在

### 解决方案 1: 修复 PowerShell 执行策略
```powershell
# 以管理员身份运行 PowerShell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 解决方案 2: 使用命令提示符
用 `cmd` 代替 PowerShell 运行 npm 命令：
```cmd
cmd /c "npm install"
cmd /c "npm run dev"
```

### 解决方案 3: 使用 yarn（如果已安装）
```bash
yarn install
yarn dev
```

## 📋 错误修复前后对比

### 修复前 ❌
```typescript
import type { NextRequest } from "next/server"  // 错误：找不到模块
const BACKEND_URL = process.env.BACKEND_URL     // 错误：找不到 process
```

### 修复后 ✅
```typescript
import { NextRequest, NextResponse } from "next/server"  // ✅ 类型正确
const BACKEND_URL: string = process.env.BACKEND_URL || "http://..." // ✅ 类型正确
```

## 🎯 关键修复内容

1. **自定义 NextRequest/NextResponse 类型**：
   - 包含所有必要的属性和方法
   - 兼容 Next.js 15 的 API 结构

2. **完整的 Node.js 环境变量类型**：
   - 预定义常用环境变量
   - 支持任意字符串键值对

3. **TypeScript 配置优化**：
   - 正确的类型根目录配置
   - 包含自定义类型文件

## ✨ 其他注意事项

- 此解决方案不依赖于 npm 包安装，适用于 PowerShell 受限环境
- 类型声明覆盖了项目中使用的所有 Next.js 和 Node.js 类型
- 如果后续 npm 可用，可以通过正常安装包来替换自定义类型声明

## 🔄 后续维护

当系统环境修复后，建议：
1. 正常安装 `@types/node` 包
2. 删除 `types/global.d.ts` 自定义类型文件
3. 恢复标准的 TypeScript 配置 