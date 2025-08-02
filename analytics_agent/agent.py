import asyncio
from typing import Annotated, List, TypedDict
from langgraph.prebuilt import create_react_agent
from langchain_deepseek import ChatDeepSeek
from nodes.cafe24_mcp_agent import cafe24_mcp_agent
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
import uuid

load_dotenv(override=True)

class State(TypedDict):
    messages: Annotated[List[str], add_messages]

llm = ChatDeepSeek(
        model="deepseek-chat",
        temperature=0.1,
    )

workflow  = StateGraph(State)

workflow.add_node("cafe24_mcp_agent", cafe24_mcp_agent)
workflow.add_edge(START, "cafe24_mcp_agent")
workflow.add_edge("cafe24_mcp_agent", END)

memory_saver = InMemorySaver()
chain = workflow.compile(checkpointer=memory_saver)

# Example usage
async def main():
    while True:
        user_input = input("User: ")
        if user_input.lower() in ['exit', 'quit', 'q']:
            break

        response = await chain.ainvoke({ "messages": user_input }, config=RunnableConfig(recursion_limit=10, thread_id=str(uuid.uuid4())))
        print(f"응답: {response['messages'][-1].content if response['messages'] else 'No response'}")
    
if __name__ == "__main__":
    asyncio.run(main())

