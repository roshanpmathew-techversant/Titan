from app.graph.state import TitanState

def user_input_node(state: TitanState) -> TitanState:
    
    """
        Just Normalize and pass on the user input forward
    """

    print("[user_input_node] raw query:", state["user_query"])

    user_query = state['user_query'].strip()


    return {

        **state,
        "user_query":user_query 
    }