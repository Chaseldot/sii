#!/usr/bin/env python3
"""
快速测试脚本 - 测试部分题目并生成报告
"""
import json
import subprocess
import time
from pathlib import Path

# 测试配置
TEST_QUESTIONS = [0, 1, 2, 5, 10, 15, 19]  # 选择几个题目测试
MAX_TURNS = 3
RUN_NAME = "quick_test"

def run_single_test(question_index):
    """运行单个题目测试"""
    print(f"Testing question {question_index}...", flush=True)
    start_time = time.time()

    cmd = [
        "python", "run.py",
        "--question-index", str(question_index),
        "--max-turns", str(MAX_TURNS),
        "--run-name", RUN_NAME
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        elapsed = time.time() - start_time

        # 解析输出
        output = result.stdout + result.stderr
        if "PASS" in output:
            status = "PASS"
        elif "FAIL" in output:
            status = "FAIL"
        else:
            status = "UNKNOWN"

        print(f"  Q{question_index}: {status} ({elapsed:.1f}s)")
        return {
            "question": question_index,
            "status": status,
            "elapsed": elapsed
        }
    except subprocess.TimeoutExpired:
        print(f"  Q{question_index}: TIMEOUT")
        return {
            "question": question_index,
            "status": "TIMEOUT",
            "elapsed": 300
        }
    except Exception as e:
        print(f"  Q{question_index}: ERROR - {e}")
        return {
            "question": question_index,
            "status": "ERROR",
            "elapsed": 0
        }

def analyze_results():
    """分析测试结果"""
    output_dir = Path("outputs") / RUN_NAME
    if not output_dir.exists():
        print("No results found")
        return

    results = []
    for json_file in output_dir.glob("q*.json"):
        with open(json_file) as f:
            data = json.load(f)
            results.append(data)

    if not results:
        print("No results to analyze")
        return

    # 统计
    total = len(results)
    passed = sum(1 for r in results if r.get("passed", False))
    failed = total - passed
    avg_time = sum(r.get("elapsed_seconds", 0) for r in results) / total if total > 0 else 0

    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    print(f"总题目数: {total}")
    print(f"通过: {passed} ({passed/total*100:.1f}%)")
    print(f"失败: {failed} ({failed/total*100:.1f}%)")
    print(f"平均耗时: {avg_time:.1f}秒")
    print()

    print("详细结果:")
    for r in sorted(results, key=lambda x: x["question_index"]):
        status = "✓ PASS" if r["passed"] else "✗ FAIL"
        print(f"  Q{r['question_index']:2d} ({r['question_id']:>6s}): {status}  "
              f"reward={r['final_reward']:.2f}  {r['elapsed_seconds']:.1f}s")
    print("="*60)

if __name__ == "__main__":
    print(f"开始测试 {len(TEST_QUESTIONS)} 个题目...")
    print(f"配置: max_turns={MAX_TURNS}, run_name={RUN_NAME}")
    print()

    # 运行测试
    test_results = []
    for q_idx in TEST_QUESTIONS:
        result = run_single_test(q_idx)
        test_results.append(result)
        time.sleep(1)  # 避免过快

    # 等待所有测试完成
    print("\n等待测试完成...")
    time.sleep(5)

    # 分析结果
    analyze_results()
