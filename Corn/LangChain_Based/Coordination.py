import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent
from Agents import tools

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    # 移除不支持的language参数
    temperature=0.7  # 可以添加这个常用参数
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type="zero-shot-react-description",
    verbose=True
)
