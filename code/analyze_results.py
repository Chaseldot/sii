#!/usr/bin/env python3
"""
分析现有测试结果
"""
import json
from pathlib import Path

def analyze_all_results():
    """分析所有输出目录中的结果"""
    output_base = Path("outputs")

    if not output_base.exists():
        print("outputs 目录不存在")
        return

    # 查找所有结果文件
    all_results = []
    for json_file in output_base.rglob("q*.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)
                all_results.append(data)
        except Exception as e:
            print(f"读取 {json_file} 失败: {e}")

    if not all_results:
        print("没有找到测试结果")
        return

    # 按 run_name 分组
    by_run = {}
    for r in all_results:
        run_name = r.get("run_name") or "default"
        if run_name not in by_run:
            by_run[run_name] = []
        by_run[run_name].append(r)

    # 显示每个 run 的结果
    for run_name, results in by_run.items():
        print("\n" + "="*70)
        print(f"Run: {run_name}")
        print("="*70)

        total = len(results)
        passed = sum(1 for r in results if r.get("passed", False))
        failed = total - passed
        avg_time = sum(r.get("elapsed_seconds", 0) for r in results) / total if total > 0 else 0

        print(f"总题目数: {total}")
        print(f"通过: {passed} ({passed/total*100:.1f}%)")
        print(f"失败: {failed} ({failed/total*100:.1f}%)")
        print(f"平均耗时: {avg_time:.1f}秒")
        print()

        print("详细结果:")
        for r in sorted(results, key=lambda x: x.get("question_index", 0)):
            status = "✓ PASS" if r.get("passed", False) else "✗ FAIL"
            q_idx = r.get("question_index", "?")
            q_id = r.get("question_id", "?")
            reward = r.get("final_reward", 0)
            elapsed = r.get("elapsed_seconds", 0)
            print(f"  Q{q_idx:2} (ID:{q_id:>6s}): {status}  reward={reward:.2f}  {elapsed:.1f}s")

if __name__ == "__main__":
    analyze_all_results()
