from Agents import tools
from Coordination import agent

if __name__ == "__main__":
    user_input = input()
    result = agent.invoke({
        "input": "我的玉米叶子有锈斑，是什么病？",
        "handle_parsing_errors": True
    })
    print(result)
