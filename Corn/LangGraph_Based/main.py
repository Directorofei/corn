import time
import sys
import threading
from Graph import build_graph, AgentState
from fastapi import FastAPI, Query
import uvicorn
import uuid
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# 全局初始化graph，避免重复构建
graph_app = build_graph()

# Pydantic模型定义
class AskRequest(BaseModel):
    question: Optional[str] = None
    image_path: Optional[str] = None

class AskResponse(BaseModel):
    answer: Optional[str] = None
    detection_result: Optional[str] = None
    decision: Optional[str] = None

# 流式输出函数
def stream_print(text, prefix="", delay=0.03):
    """
    模拟打字机效果，一个字一个字地输出
    """
    print(f"{prefix}", end="", flush=True)
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()  # 换行

def stream_agent_output(agent_name, output_text, delay=0.02, use_streaming=False):
    """
    流式输出智能体结果
    """
    if not output_text:
        return
    
    print(f"\n🤖 {agent_name} 正在思考...", end="", flush=True)
    time.sleep(0.5)  # 模拟思考时间
    print("\r", end="", flush=True)  # 清除"正在思考"
    
    if use_streaming:
        # 流式输出（可能有重复风险）
        lines = output_text.split('\n')
        for i, line in enumerate(lines):
            if line.strip():  # 跳过空行
                if i == 0:
                    stream_print(line, f"🤖 {agent_name}: ", delay)
                else:
                    stream_print(line, "    ", delay)
            else:
                print()  # 空行直接换行
    else:
        # 直接输出完整文本（推荐，避免重复）
        print(f"🤖 {agent_name}: {output_text}")

# API路由
@app.post("/api/ask", response_model=AskResponse)
async def ask(data: AskRequest):
    state: AgentState = {
        "question": data.question,
        "image_path": data.image_path,
        "image_description": None,
        "detection_result": None,
        "answer": None,
        "need_medication": None,
        "decision": None
    }
    result = graph_app.invoke(state)
    return AskResponse(
        answer=result.get("answer"),
        detection_result=result.get("detection_result"),
        decision=result.get("decision")
    )

@app.get("/api/chat")
async def chat_endpoint(question: str = Query(None), image_url: str = Query(None)):
    state: AgentState = {
        "question": question,
        "image_path": image_url,
        "image_description": None,
        "detection_result": None,
        "answer": None,
        "need_medication": None,
        "decision": None
    }
    result = graph_app.invoke(state)
    return result

@app.get("/api/chat/stream")
async def chat_stream_endpoint(question: str = Query(None), image_url: str = Query(None)):
    state: AgentState = {
        "question": question,
        "image_path": image_url,
        "image_description": None,
        "detection_result": None,
        "answer": None,
        "need_medication": None,
        "decision": None
    }
    
    def event_stream():
        for step in graph_app.stream(state, stream_mode="updates"):
            yield f"data: {step}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")

def main():
    print("🌽 智能系统开始：支持图像路径 + 问题文字输入")
    print("💡 提示：系统将模拟真实对话，一个字一个字地输出回答\n")
    
    # 询问用户是否使用流式输出
    use_streaming = input("🎬 是否使用流式输出效果？(y/n，默认n): ").strip().lower() == 'y'
    if use_streaming:
        print("⚠️  注意：流式输出可能在某些情况下出现重复文本")
    print()

    # 初始化对话状态，保持上下文连续性
    conversation_state: AgentState = {
        "question": None,
        "image_path": None,
        "image_description": None,
        "detection_result": None,
        "answer": None,
        "need_medication": None,
        "decision": None
    }

    while True:
        img = input("🖼️ 输入图像路径（可留空）：\n> ").strip()
        if img.lower() in ["", "无", "无图", "none", "no", "n"]:
            img = None

        txt = input("📝 输入问题（可留空）：\n> ").strip()
        if not txt or txt.lower() in ["", "无", "无图", "none", "no", "n"]:
            txt = None
            if not img:
                print("请至少提供图像或文本输入。")
                continue

        if txt and txt.lower() in ["退出", "exit", "quit"]:
            print("再见！感谢使用玉米智能系统！")
            break

        if not img and not txt:
            print("请至少提供图像或文本输入。")
            continue

        # 更新对话状态，保持上下文连续性
        if img:
            conversation_state["image_path"] = img
        if txt:
            conversation_state["question"] = txt
        
        print(f"\n🧠 正在分析您的问题：{txt}")
        time.sleep(0.5)
        
        # 调用智能体推理
        result = graph_app.invoke(conversation_state)

        # 更新对话状态，保存推理结果供后续对话使用
        for key, value in result.items():
            if key in conversation_state:
                conversation_state[key] = value

        # 流式输出结果
        if result.get("detection_result"):
            stream_agent_output("图像识别", result.get("detection_result"), use_streaming=use_streaming)
        
        if result.get("answer"):
            stream_agent_output("农业专家", result.get("answer"), use_streaming=use_streaming)
        
        if result.get("decision"):
            stream_agent_output("农药专家", result.get("decision"), use_streaming=use_streaming)

        # 多轮对话循环
        while True:
            followup = input("\n👴🏻 继续对话（输入新问题，或输入'退出'结束）：\n> ").strip()
            if followup and followup.lower() in ["退出", "exit", "quit", "结束"]:
                break
            
            if followup:
                print(f"\n🧠 正在分析您的问题：{followup}")
                time.sleep(0.5)
                
                # 更新问题，但保持其他上下文信息
                conversation_state["question"] = followup
                conversation_state["need_medication"] = None  # 重置决策标志
                
                # 继续推理，传入完整的上下文状态
                result = graph_app.invoke(conversation_state)
                
                # 更新对话状态，保存推理结果供后续对话使用
                for key, value in result.items():
                    if key in conversation_state:
                        conversation_state[key] = value
                
                # 流式输出结果
                if result.get("detection_result"):
                    stream_agent_output("图像识别", result.get("detection_result"), use_streaming=use_streaming)
                
                if result.get("answer"):
                    stream_agent_output("农业专家", result.get("answer"), use_streaming=use_streaming)
                
                if result.get("decision"):
                    stream_agent_output("农药专家", result.get("decision"), use_streaming=use_streaming)
            else:
                break

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        print("🚀 启动FastAPI服务...")
        print("📡 API接口：")
        print("   POST /api/ask - 问答接口")
        print("   GET  /api/chat - 普通问答接口")
        print("   GET  /api/chat/stream - 流式问答接口")
        print("🌐 访问地址：http://localhost:8000")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        main()
