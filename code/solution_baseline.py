"""
Baseline 版本 - 只用 1 轮调用，不做迭代修正
用于对比测试
"""

def run_question(
    question_prompt: str,
    call_llm,
    execute_code,
    max_turns: int,
    count_tokens,
) -> str:
    """单轮 baseline"""

    system_prompt = """You are an expert competitive programmer. Write clean, efficient Python code to solve the problem.

Requirements:
1. Read the problem carefully
2. Consider edge cases
3. Write complete, runnable code
4. Output in ```python code block"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question_prompt}
    ]

    response = call_llm(messages)
    return response
