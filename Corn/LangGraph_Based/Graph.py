from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
# from Agents import pest_detection_agent, qa_agent, decision_agent
from Agents_Dify import imitate_pest_detection_agent, pest_detection_agent, qa_agent, decision_agent, refine_agent, intention_agent

# print("Graph.py 正在被加载...")

# 定义共享状态
class AgentState(TypedDict):
    question: Optional[str]
    image_path: Optional[str]
    detection_result: Optional[str]
    image_description: Optional[str]
    answer: Optional[str]
    need_medication: Optional[bool]
    decision: Optional[str]

def log_agent(name, func):
    def wrapper(state):
        print(f"🤖 当前正在调用：{name}")
        return func(state)
    return wrapper

# 构建流程图
def build_graph():
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("route", route_controller)

    graph.add_node("detect", log_agent("图像识别 Agent", imitate_pest_detection_agent))
    # graph.add_node("detect", log_agent("图像识别 Agent", pest_detection_agent))
    graph.add_node("qa", log_agent("问答 Agent", qa_agent))
    graph.add_node("refine", log_agent("精炼 Agent", refine_agent))
    graph.add_node("intention", log_agent("意图识别 Agent", intention_agent))
    graph.add_node("decision", log_agent("农药决策 Agent", decision_agent))

    # 条件控制：输入内容决定路线
    def router(state: AgentState) -> str:
        has_image = bool(state.get("image_path"))
        has_text = bool(state.get("question"))

        if has_image and has_text:
            return "detect_then_qa"
        elif has_image:
            return "detect_only"
        elif has_text:
            return "qa_only"
        else:
            return END

    graph.add_conditional_edges("route", router, {
        "detect_then_qa": "detect",
        "detect_only": "detect",
        "qa_only": "qa"
    })

    # 如果有图像，先识别再问答
    graph.add_conditional_edges("detect", lambda s: "qa" if s.get("question") else "refine", {
        "qa": "qa",
        "refine": "refine"
    })

    # 问答后进入精炼
    graph.add_edge("qa", "refine")
    
    # 精炼后进入意图识别
    graph.add_edge("refine", "intention")
    
    # 意图识别后决定是否进入决策智能体
    def confirm_decision(state: AgentState) -> str:
        return "decision" if state.get("need_medication") else END

    graph.add_conditional_edges("intention", confirm_decision, {
        "decision": "decision",
        END: END
    })

    graph.add_edge("decision", END)

    graph.set_entry_point("route")
    return graph.compile()

# 空路由节点，仅用作入口
def route_controller(state: AgentState):
    return state

