from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class State(TypedDict):
    """State class for managing the state of the analytics agent.

    This class is used to define the structure of the state, including the messages exchanged during the interaction with the agent.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str