import asyncio
import uuid
from typing import TypedDict,Annotated
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv(override=True)

class State(TypedDict):
    """State class for managing the state of the analytics agent.

    This class is used to define the structure of the state, including the messages exchanged during the interaction with the agent.
    """
    messages: Annotated[list[str], add_messages]
    user_query: str

MCP_CONFIG = {
                    "cafe24": {
                        "command": "E:/project/octpus_app/octpus_assistant/.venv/Scripts/python.exe",
                        "args": [
                            "E:/project/octpus_app/octpus_assistant/mcp_server/cafe24_mcp_tools.py"
                        ],
                        "transport": "stdio"
                    }
                }

async def cafe24_mcp_agent(state: State):
    

    llm = ChatDeepSeek(
        model="deepseek-chat",
        temperature=0.1,
    )

    client = MultiServerMCPClient(MCP_CONFIG)

    try:
        print("MCP 클라이언트 연결 시작...")
        # await client.__aenter__()
        print("MCP 클라이언트 연결 완료, 도구 조회 중...")
        tools = await client.get_tools()
        print(f"MCP 도구 {len(tools)}개 로드 완료")
    except Exception as e:
        print(f"도구 로드 실패: {e}")
        tools = []
    
    agent = create_react_agent(
        model=llm,
        tools=tools,
        checkpointer=MemorySaver(),
    )

    config=RunnableConfig( recursion_limit=10, thread_id=str(uuid.uuid4()) )

    response = await agent.ainvoke(
        {"messages": state["messages"][-1]},
        config=config
    )

    # agent.ainvoke()는 딕셔너리를 반환하므로, 메시지 내용만 추출
    ai_message = response["messages"][-1].content if response.get("messages") else str(response)
    
    return {"messages": AIMessage(content=ai_message)}

async def main():
    state = State(messages=["상품 목록을 조회해줘"])
    response = await cafe24_mcp_agent(state)
    print(f"응답: {response['messages'].content}")

if __name__ == "__main__":
    asyncio.run(main())
    