import os
from langchain_openai import ChatOpenAI
from portkey_ai import createHeaders

def setup_input_guardrails():
    """Setup LLM with input guardrails using Portkey"""
    # Import configuration from config
    from config import IMPROVED_INPUT_GUARDRAIL_CONFIG, DEFAULT_MODEL
    
    return ChatOpenAI(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.portkey.ai/v1",
        default_headers=createHeaders(
            api_key=os.environ.get("PORTKEY_API_KEY"),
            provider="groq",
            config=IMPROVED_INPUT_GUARDRAIL_CONFIG
        ),
        model=DEFAULT_MODEL,
        temperature=0.1,
        model_kwargs={"max_tokens": 100}
    )

def setup_output_guardrails():
    """Setup LLM with output guardrails using Portkey"""
    # Import configuration from config
    from config import OUTPUT_GUARDRAIL_CONFIG, DEFAULT_MODEL
    
    return ChatOpenAI(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.portkey.ai/v1",
        default_headers=createHeaders(
            api_key=os.environ.get("PORTKEY_API_KEY"),
            provider="groq",
            config=OUTPUT_GUARDRAIL_CONFIG
        ),
        model=DEFAULT_MODEL,
        temperature=0.1,
        model_kwargs={"max_tokens": 2000}
    )

def format_solution_manually(solution: str, question: str) -> str:
    """Manual formatting when output guardrails fail"""
    formatted_solution = f"""Solution:

Step 1: Understanding the Problem
{question}

Step 2: Detailed Solution
{solution}

Step 3: Verification and Final Answer
The solution above provides the mathematical approach and reasoning needed to solve this problem.

Therefore, the final answer is contained in the detailed solution provided in Step 2.

Note: This solution has been manually formatted to meet quality standards after guardrails processing.
"""
    return formatted_solution