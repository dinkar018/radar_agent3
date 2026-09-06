from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import retrieve_context, generate_code, validate_code, execute_code, reflect, is_code_valid, should_continue

def build_agent_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node('retrieve_context', retrieve_context)
    graph.add_node('generate_code', generate_code)
    graph.add_node('validate_code', validate_code)
    graph.add_node('execute_code', execute_code)
    graph.add_node('reflect', reflect)
    
    graph.set_entry_point('retrieve_context')
    graph.add_edge('retrieve_context', 'generate_code')
    graph.add_conditional_edges('validate_code', is_code_valid, {'execute_code': 'execute_code', 'generate_code': 'generate_code'})
    graph.add_edge('generate_code', 'validate_code') 
    graph.add_edge('execute_code', 'reflect')
    graph.add_conditional_edges('reflect', should_continue, {'finalize': END, 'generate_code': 'generate_code'})
    
    return graph.compile()
