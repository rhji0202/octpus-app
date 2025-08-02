
from ..states import State
from langchain_core.messages import AIMessage

def delivery(state: State):
    """
    This function is a placeholder for the delivery process in the analytics agent.
    It currently does not perform any operations but can be extended in the future.
    
    Args:
        state: The current state of the analytics agent.
    """
    response_msg = f"""
    Delivery process is not implemented yet.
    User query: {state['user_query']}
    """
    return { "messages": [AIMessage(content=response_msg)] }