"""
优化版 solution - 强调问题分析和验证
"""

def run_question(
    question_prompt: str,
    call_llm,
    execute_code,
    max_turns: int,
    count_tokens,
) -> str:
    """强调问题分析、边界条件和验证"""

    system_prompt = """You are a competitive programming expert.

IMPORTANT:
1. First understand the problem: What are inputs, outputs, constraints?
2. Think about edge cases: empty input, single element, maximum values
3. Design algorithm, then implement
4. Test your logic with sample input/output
5. Output ONLY the code in ```python blocks, nothing else."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question_prompt}
    ]

    response = call_llm(messages)
    result = execute_code(response)

    if result["passed"]:
        return response

    # 迭代修正
    best_response = response
    for turn in range(2, max_turns + 1):
        feedback = result["feedback"]

        # 分类反馈
        if "Runtime Error" in feedback:
            hint = "Fix: Check array bounds, division by zero, variable initialization."
        elif "Time Limit" in feedback:
            hint = "Optimize: Reduce O(n²) to O(n log n) or O(n)."
        elif "Wrong Answer" in feedback:
            hint = "Debug: Check edge cases, verify with sample I/O, trace through algorithm."
        else:
            hint = "Review the error and fix."

        messages.extend([
            {"role": "assistant", "content": response},
            {"role": "user", "content": f"Error: {feedback}\n\n{hint}\n\nProvide corrected code in ```python block."}
        ])

        response = call_llm(messages)
        result = execute_code(response)

        if result["passed"]:
            return response
        best_response = response

    return best_response
