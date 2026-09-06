import ast
import logging
import os
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.agent.state import AgentState
from app.agent.prompts import SYSTEM_PROMPT, CODE_GENERATION_PROMPT, ERROR_RECOVERY_PROMPT
from app.agent.tools import extract_code_from_response
from app.services.code_executor import DockerCodeExecutor

logger = logging.getLogger(__name__)

def retrieve_context(state: AgentState) -> dict:
    return {
        'status': 'retrieving_context',
        'status_message': 'Building context from knowledge base...'
    }

def generate_code(state: AgentState) -> dict:
    # Build prompt
    if state.get('execution_error') and state.get('generated_code'):
        prompt = ERROR_RECOVERY_PROMPT.format(
            generated_code=state['generated_code'],
            execution_error=state['execution_error']
        )
    else:
        prompt = CODE_GENERATION_PROMPT.format(
            paper_context=state.get('paper_context', ''),
            radar_context=state.get('radar_context', ''),
            data_description=state.get('data_description', ''),
            data_file_paths=state.get('data_file_paths', []),
            user_instructions=state.get('user_instructions', '')
        )
    
    # Use LangChain LLM
    llm = ChatGoogleGenerativeAI(model=os.getenv("LLM_MODEL", "gemini-1.5-pro"), temperature=0.2)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    code = extract_code_from_response(response.content)
    
    new_messages = [HumanMessage(content=prompt), AIMessage(content=response.content)]
    
    return {
        'generated_code': code,
        'status': 'generating_code',
        'status_message': 'Generating Python implementation...',
        'messages': new_messages
    }

def validate_code(state: AgentState) -> dict:
    return {
        'status': 'validating',
        'status_message': 'Validating generated code...'
    }

def execute_code(state: AgentState) -> dict:
    executor = DockerCodeExecutor(image_name="radar_sandbox")
    result = executor.execute(state.get('generated_code', ''), state.get('data_file_paths', []))
    
    return {
        'execution_output': result.stdout,
        'execution_error': result.stderr or result.error,
        'result_files': result.result_files,
        'status': 'executing'
    }

def reflect(state: AgentState) -> dict:
    error = state.get('execution_error')
    current_iter = state.get('iteration_count', 0)
    max_iter = state.get('max_iterations', 3)
    
    if not error:
        return {
            'is_complete': True,
            'status': 'complete'
        }
    else:
        if current_iter < max_iter:
            return {
                'is_complete': False,
                'iteration_count': current_iter + 1
            }
        else:
            return {
                'is_complete': True,
                'status': 'failed'
            }

def should_continue(state: AgentState) -> str:
    if state.get('is_complete', False):
        return 'finalize'
    return 'generate_code'

def is_code_valid(state: AgentState) -> str:
    code = state.get('generated_code', '')
    try:
        ast.parse(code)
        if 'os.system' in code or 'subprocess' in code:
            logger.warning("Dangerous import detected in generated code.")
        return 'execute_code'
    except SyntaxError as e:
        logger.error(f"Syntax error in generated code: {e}")
        return 'generate_code'
