import requests
import os
api_key = os.getenv("AGENT_API_KEY")

def call_dify_agent(base_url, api_key, chatflow_id, user_input, user_id="user-123"):
    url = f"{base_url}/chat-messages"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": {},  # 预设为空，如果你的 chatflow 用到了结构化 input 可以填
        "query": user_input,
        "response_mode": "blocking",
        "chatflow_id": chatflow_id,
        "user": user_id
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        return res.json().get("answer")
    except Exception as e:
        return f"请求出错: {str(e)}"


from langchain.agents import Tool

BASE_URL = "http://192.168.163.1/v1"
API_KEY = "app-YRqDrxrIoSEeZdCe4cGEzAjM"

# 假设你有 3 个 chatflow
AGENT_A_ID = "dgwDnRc6UgpK01z0"  # 识别病害
AGENT_B_ID = "xxxxx123456"       # 问诊分析
AGENT_C_ID = "CQOpi0xo0y9Z26EH"       # 农药推荐

tools = [
    Tool(
        name="病害识别助手",
        func=lambda x: call_dify_agent(BASE_URL, API_KEY, AGENT_A_ID, x),
        description="用于分析图片或文字中玉米的病虫害类型"
    ),
    Tool(
        name="问诊分析助手",
        func=lambda x: call_dify_agent(BASE_URL, API_KEY, AGENT_B_ID, x),
        description="用于根据症状描述进行玉米病情诊断"
    ),
    Tool(
        name="农药推荐助手",
        func=lambda x: call_dify_agent(BASE_URL, API_KEY, AGENT_C_ID, x),
        description="用于根据诊断结果推荐合适农药"
    )
]
