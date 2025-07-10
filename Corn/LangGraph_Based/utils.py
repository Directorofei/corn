import requests
import json
from dotenv import load_dotenv
import os
import logging

load_dotenv() 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def call_dify_agent(prompt: str, chatflow_id: str, api_key: str, user_id="user_001", image_url: str = None, conversation_id: str = None) -> str:

    base_url = os.getenv("DIFY_BASE_URL", "http://192.168.163.1/v1") # 配置Dify API的基础URL，当前为测试时本机地址

    api_key = api_key or os.getenv("DIFY_API_KEY")

    url = f"{base_url}/chat-messages?chatflow_id={chatflow_id}"


    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    inputs = {
        "query": prompt
    }
    if image_url:
        inputs["image"] = image_url

    payload = {
        "inputs": inputs,
        "query": prompt,
        "response_mode": "blocking",
        "user": user_id
    }
    
    if conversation_id:
        payload["conversation_id"] = conversation_id

    try:
        # response = requests.post(url, headers=headers, json=payload, timeout=15)
        # 在关键位置添加日志
        logger.info(f"调用Dify API: {url}")
        logger.debug(f"请求参数: {payload}")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        response.raise_for_status()
        data = response.json()
        if "answer" in data:
            return data["answer"]
        elif "message" in data:
            return data["message"]
        elif "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return f"[未知格式响应] {data}"
    except Exception as e:
        return f"[Dify 调用失败] {e}"


def call_deepseek_api(prompt: str, system_prompt: str = "", model: str = None, min_tokens: int = 800, max_tokens: int = 1500) -> str:
    """
    调用DeepSeek官方API
    :param prompt: 用户输入的提示词
    :param system_prompt: 系统提示词(可选)
    :param model: 使用的模型(可选)
    :param min_tokens: 最小输出token数(默认800，约400汉字)
    :param max_tokens: 最大输出token数(默认1500，约750汉字)
    :return: API返回的响应内容
    """
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    
    if not api_key:
        return "[错误] 未配置DEEPSEEK_API_KEY环境变量"
    
    model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "min_tokens": min_tokens,
        "max_tokens": max_tokens
    }
    
    try:
        logger.info(f"调用DeepSeek API: {base_url}/chat/completions")
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"DeepSeek API调用失败: {e}")
        return f"[DeepSeek API调用失败] {e}"