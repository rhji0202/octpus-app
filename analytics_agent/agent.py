import asyncio
import logging
from typing import Annotated, Literal, TypedDict
from langchain_core.messages import AnyMessage, ToolMessage, AIMessage, HumanMessage, BaseMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek  # Anthropic 또는 OpenAI 사용 가능
from langchain_core.tools import BaseTool, ToolException
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables.config import RunnableConfig
from dotenv import load_dotenv
import os
import uuid
from prompt import SYSTEM_PROMPT
# 비동기 종료 관련 경고 무시

load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── 상태 스키마 정의 ───────────────────────────
class State(TypedDict, total=False):
    messages: Annotated[list, add_messages]  # 반드시 존재하는 key
    tools: Annotated[list, 'mcp_tools' ]  # MCP tools
    last_error: Annotated[str, 'last error']

# ─── 1) MCP 도구 초기화 로직 ─────────────────────
async def init_client():

    # 더 간단한 방식으로 MultiServerMCPClient 사용
    config = {
      "cafe24": {
        "command": "/Users/ho/Sites/octpus-app/.venv/bin/python",
        "args": ["/Users/ho/Sites/octpus-app/mcp_server/cafe24_mcp_tools.py"],
        "transport": "stdio"
      }
    }

    try:
        # 도구만 로드하고 클라이언트는 반환하지 않음
        client = MultiServerMCPClient(config)
        tools = await client.get_tools()
        logger.info(f"MCP 도구 {len(tools)}개 로드 완료")
        
        # 클라이언트 객체는 반환하지 않음 (가비지 컬렉터가 정리하도록 함)
        return tools

    except Exception as e:
        logger.error(f"[MCP ERROR] {e}")
        return []

model = ChatDeepSeek(model="deepseek-chat", temperature=0.7)
# ─── 2) 모델 호출 노드 ───────────────────────────
async def llm_node(state: State) -> State:
    global model
    model_with_tools = model.bind_tools(state.get("tools", []))
    
    # 메시지를 직접 전달
    resp = await model_with_tools.ainvoke(state["messages"], config = RunnableConfig(recursion_limit=10,thread_id=uuid.uuid4(),max_retries=3))
    
    # 안전하게 처리
    return {"messages": [resp]}

# ─── 3) 도구 실행 노드 (기본 오류 처리 활성화) ───
def tool_node(tools):
    return ToolNode(tools, handle_tool_errors=True, messages_key="messages")

def should_continue(state: State) -> Literal["tools", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]
    if (
      last_message.tool_calls
    ):
        return "tools"
    else:
        return "__end__"
    

# ─── 5) StateGraph 설계 ───────────────────────────
def make_graph(tools):
    builder = StateGraph(State)
    builder.add_node("assistant", llm_node)
    builder.add_node("tools", tool_node(tools))

    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", should_continue,{
        "tools": "tools",
        "__end__": END
    })
    builder.add_edge("tools", "assistant")

    # 체크포인터에 thread_id 제공
    memory = InMemorySaver()
    return builder.compile(checkpointer=memory)

# ─── 6) 실행 진입점 ───────────────
async def main():
    
    # 문자열 대신 HumanMessage 객체 사용
    init_state = {"messages": [SystemMessage(content=SYSTEM_PROMPT),HumanMessage(content="안녕")]}
    

    graph = make_graph()

    # 그래프를 이미지로 저장
    graph_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workflow_graph.png")
    mermaid_syntax = graph.get_graph().draw_mermaid()
    from langchain_core.runnables.graph_mermaid import draw_mermaid_png
    draw_mermaid_png(mermaid_syntax, output_file_path=graph_path)
    print(f"그래프 이미지가 저장되었습니다: {graph_path}")

    try:
        # thread_id를 포함한 RunnableConfig 사용
        config = RunnableConfig(recursion_limit=10,thread_id=str(uuid.uuid4()), max_retries=3)
        # result = await graph.ainvoke(init_state, config=config)
        # print(result.pretty_print())
        # print("AI:", result["messages"][-1].content)
        async for chunk in graph.astream(init_state, config=config, stream_mode="values"):
            print(chunk["messages"][-1].pretty_print())
    except Exception as e:
        print("[GRAPH ERROR]", e)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"예상치 못한 오류: {e}")