import requests
from utils import call_dify_agent, call_deepseek_api
from config import  DETECTION_CHATFLOW_ID, DETECTION_API_KEY,QA_CHATFLOW_ID, QA_API_KEY, DECISION_CHATFLOW_ID, DECISION_API_KEY

# 模拟识别
def imitate_pest_detection_agent(state):
    # 模拟返回识别结果
    result = "发现玉米叶片有红蜘蛛和叶斑病症状。"
    print("[图像识别 Agent 输出]", result)
    state["image_description"] = result
    state["detection_result"] = result
    return state

# 识别智能体
def pest_detection_agent(state):
    # prompt = f"""
    # 请根据图像描述识别图像中的作物类型和疾病：
    # 图像描述：{state.get('image_description', '')}
    # 识别结果：
    # """
    prompt = "请识别图像中的病害和作物。"
    image_url = state.get("image_path", None)

    # 调用 Dify 识别智能体
    response = call_dify_agent(
        prompt.strip(),
        chatflow_id=DETECTION_CHATFLOW_ID,
        api_key=DETECTION_API_KEY,
        image_url=image_url
    )
    print("[识别 Agent 输出]", response)
    state["detection_result"] = response
    return state

# 问答智能体
def qa_agent(state):
    # 获取识别结果和用户问题
    detection_result = state.get("detection_result", "")
    question = state.get("question", "")
    
    prompt = f"""
你是一名农业植保专家，请基于以下信息回答用户问题：

【图像识别结果】
{detection_result}

【用户问题】
{question}

请提供专业的农业诊断和建议，包括：
1. 病害/虫害分析
2. 危害程度评估
3. 防治建议
4. 预防措施

要求回答详细、专业、可操作。
"""
    # 调用 Dify 问答智能体
    response = call_dify_agent(
        prompt=prompt.strip(),
        chatflow_id=QA_CHATFLOW_ID,
        api_key=QA_API_KEY,
    )
    print("[问答 Agent 输出]", response)
    state["answer"] = response
    return state

# 决策智能体
def decision_agent(state):
    # 获取识别和问答的结果
    detection_result = state.get("detection_result", "")
    answer = state.get("answer", "")
    question = state.get("question", "")
    
    prompt = f"""
你是一名农业植保专家，需要基于以下信息制定农药使用建议：

【图像识别结果】
{detection_result}

【专家问答分析】
{answer}

【用户问题】
{question}

请基于以上识别结果和专家分析，制定针对性的农药使用建议。要求：
1. 明确防治对象（具体病害/虫害）
2. 推荐具体药剂（通用名+剂型）
3. 使用方法和用量
4. 安全注意事项
5. 防治时机建议

输出格式：
农药推荐：<具体建议>
"""
    # 调用 Dify 决策智能体
    response = call_dify_agent(
        prompt.strip(),
        chatflow_id=DECISION_CHATFLOW_ID,
        api_key=DECISION_API_KEY,
    )
    print("[决策 Agent 输出]", response)
    state["decision"] = response
    return state

# 精炼智能体
def refine_agent(state):
    full_answer = state.get("answer", "")

    prompt = f"""
你是一名农业问诊助手，以下是系统生成的详细问答内容：

{full_answer}

请你基于以上内容，总结一句清晰明了的建议，便于农民快速理解和采取行动。

要求：
1. 输出长度控制在150-200字
2. 包含关键防治措施
3. 语言简洁易懂
4. 突出最重要的行动建议

输出格式：
简明建议：100-200字的总结建议>
"""

    summary = call_deepseek_api(prompt)
    print("[精炼 Agent 输出]", summary)

    # 可选：保留原始内容
    state["original_answer"] = full_answer
    state["answer"] = summary
    return state

# 意图识别智能体
def intention_agent(state):
    user_input = state.get("question", "")
    detection_result = state.get("detection_result", "")
    answer = state.get("answer", "")
    
    # 如果用户提供了具体症状描述，更倾向于推荐农药
    has_symptoms = any(keyword in user_input.lower() for keyword in [
        "叶片", "茎秆", "根部", "斑点", "锈粉", "穿孔", "蛀孔", "瘤状", "腐烂",
        "铁锈", "病斑", "症状", "发病", "感染", "危害"
    ])
    
    prompt = f"""
你是一个农业问诊系统中的意图识别助手。请分析以下信息：

【用户问题】
"{user_input}"

【识别结果】
{detection_result}

【专家分析】
{answer}

请判断用户是否希望获得农药推荐，仅回答 `yes` 或 `no`。

判断标准：
- 如果用户明确表示希望知道该用什么药、推荐农药、怎么治疗、想治、要治等，回答 `yes`
- 如果用户提供了具体的病害症状描述（如叶片斑点、茎秆症状等），回答 `yes`
- 如果只是表达病害、咨询诊断，未表示想用药且无具体症状，回答 `no`
- 如果专家分析中提到了防治建议或用药方案，回答 `yes`
"""

    answer = call_deepseek_api(prompt).lower()
    print("[意图识别 Agent 输出]", answer)

    # 如果用户提供了症状描述，更倾向于推荐农药
    if "yes" in answer or has_symptoms:
        state["need_medication"] = True
    else:
        state["need_medication"] = False

    return state
