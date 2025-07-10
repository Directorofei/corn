# from langchain_core.messages import HumanMessage
# from langchain_openai import ChatOpenAI
# from config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME

# # 初始化通用 LLM
# llm = ChatOpenAI(
#     api_key=OPENAI_API_KEY,
#     base_url=OPENAI_BASE_URL,
#     model=MODEL_NAME,
#     temperature=0.3
# )

# def pest_detection_agent(state):
#     # 模拟图像识别结果
#     result = "发现玉米叶片有红蜘蛛和叶斑病症状。"
#     print("[图像识别 Agent 输出]", result)
#     state["image_description"] = result
#     state["detection_result"] = result
#     return state

# def qa_agent(state):
#     prompt = f"""
#         图像描述：{state['image_description']}
#         问题：{state['question']}
#         请结合图像描述回答问题：
#         """
#     response = llm.invoke([HumanMessage(content=prompt)])
#     print("[问答 Agent 输出]", response.content)
#     state["answer"] = response.content
#     return state

# def decision_agent(state):
#     prompt = f"""
#         基于以下图像识别结果和回答内容，请生成农药建议：
#         图像识别结果：{state['detection_result']}
#         问题回答：{state['answer']}
#         输出格式：建议内容 + 农药推荐
#         """
#     response = llm.invoke([HumanMessage(content=prompt)])
#     print("[决策 Agent 输出]", response.content)
#     state["decision"] = response.content
#     return state


from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME

# 初始化通用 LLM
llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
    model=MODEL_NAME,
    temperature=0.3
)

# 图像识别智能体
def pest_detection_agent(state):
    # 模拟图像识别（可替换为真实模型）
    result = "发现玉米叶片有红蜘蛛和叶斑病症状。"
    print("🔬 [图像识别 Agent 输出]", result)

    state["image_description"] = result
    state["detection_result"] = result
    return state

# 问答智能体
def qa_agent(state):
    image_desc = state.get("image_description", "无图像信息")
    question = state.get("question", "")

    prompt = f"""
图像描述：{image_desc}
用户提问：{question}

请结合图像和问题，提供专业、简洁、可执行的病虫害管理建议。
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    print("🧠 [问答 Agent 输出]", response.content)

    state["answer"] = response.content
    return state

# 农药决策智能体
def decision_agent(state):
    detection = state.get("detection_result", "无识别信息")
    answer = state.get("answer", "无问答内容")

    prompt = f"""
你是一名农业植保专家。

根据以下诊断信息和问答内容，请制定针对性的农药使用建议：

图像识别结果：{detection}
专家回答内容：{answer}

请明确列出：
1. 防治对象
2. 药剂名称（通用名+剂型）
3. 使用浓度或用量（亩/次）
4. 安全间隔期
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    print("💊 [决策 Agent 输出]", response.content)

    state["decision"] = response.content
    return state
