# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个提示词工程考试项目（2026年春），目标是通过 prompt engineering 设计策略，让 LLM 解决编程问题。系统会调用 Qwen3-8B 模型生成代码，并在沙箱环境中执行测试。

## 考试要求

### 提交内容
1. **solution.py**: 实现 `run_question()` 函数（唯一需要编辑的文件）
2. **探索报告.pdf**: 记录不同提示词策略的尝试、效果和分析

### 评分标准
- 客观得分（80%）：私有测试集上的 pass@1 平均准确率，排名赋分
- 主观得分（20%）：提示词的创新性、合理性、可解释性

### 约束条件
- 最大 LLM 调用轮数：3 次（max_turns=3）
- 单次 prompt 长度限制：16k tokens（Qwen3-8B tokenizer）
- 模型参数固定：temperature=1.0, top_p=1, max_tokens=8192
- 不允许 import 第三方库，仅可使用 Python 标准库
- 禁止硬编码测试集答案

## 核心架构

### 文件职责

- **solution.py**: 唯一需要编辑的文件，实现 prompt 策略
- **run.py**: 评测运行脚本，加载题目、调用 solution、计算分数
- **llm_client.py**: LLM 调用封装（模型参数已固定）
- **code_reward.py**: 代码执行沙箱和测试评分系统
- **data/dev.jsonl**: 验证集数据（每行一个编程题）

### 数据格式

dev.jsonl 中每行包含：
- `id`: 题目编号
- `prompt`: OpenAI Message 格式的题目描述
- `tests`: 输入输出测试用例字典

### 工作流程

1. `run.py` 从 `data/dev.jsonl` 加载题目
2. 调用 `solution.run_question()` 并传入工具函数：
   - `call_llm(messages)`: 调用 LLM，返回回复文本
   - `execute_code(response)`: 提取代码并运行测试，返回 `{"passed": bool, "feedback": str}`
   - `count_tokens(text)`: 计算 token 数量
3. `solution.run_question()` 设计 prompt 策略，可多轮调用（最多3次）
4. 最终返回包含 ```python 代码块的回复文本
5. `code_reward.py` 在沙箱中执行代码并评分（pass@1）

### 沙箱限制

代码在受限环境中执行：
- 禁用文件 I/O、进程操作、网络访问
- 允许的模块：math, itertools, collections, numpy, re, json 等标准库
- 超时限制：默认 1 秒/测试用例
- 内存限制：1GB

## 常用命令

### 运行单个题目（开发调试）
```bash
cd code
python run.py --question-index 0
```

### 运行所有题目（完整评测）
```bash
python run.py --all
```

### 指定最大 LLM 调用轮数
```bash
python run.py --question-index 0 --max-turns 3
```

### 并行评测（多样本，模拟正式评分）
```bash
python run.py --all --samples 16 --workers 80 --max-turns 3
```

### 自定义 API 配置
```bash
python run.py --all --api-base http://localhost:8001/v1 --api-key EMPTY
```

### 查看单题详细输出
```bash
python run.py --question-index 0 --max-turns 3 --run-name debug
cat outputs/debug/q0-s0.json
```

## 开发策略指南

### solution.py 实现要点

1. **单轮策略（baseline）**
   - 直接调用 LLM 生成代码
   - 适合简单题目，但准确率有限

2. **多轮迭代策略（推荐）**
   - 第1轮：生成初始代码
   - 第2轮：根据 `execute_code` 的 feedback 修正错误
   - 第3轮：进一步优化（如果还有错误）
   - 注意：max_turns=3 的硬性限制

3. **Prompt 设计技巧**
   - 明确指令：要求输出完整可运行的代码
   - 思维链引导：让模型先分析问题再编码
   - 错误反馈：将测试失败信息清晰传递给模型
   - 格式约束：强调代码必须在 ```python 代码块中

4. **Token 管理**
   - 使用 `count_tokens()` 监控上下文长度
   - 单次 prompt 不超过 16k tokens
   - 多轮对话时注意累积的 message 长度

### 提示词策略探索方向

1. **指令优化**
   - 系统提示词设计（system message）
   - 问题重述与澄清
   - 输出格式约束

2. **思维链技术**
   - Chain-of-Thought (CoT)
   - Step-by-step reasoning
   - Self-consistency

3. **错误修正机制**
   - 反馈解析与理解
   - 针对性修正提示
   - 边界条件处理

4. **Few-shot 示例**
   - 提供类似题目的解题示例
   - 注意 token 预算

### 测试类型

题目支持三种测试类型（在 tests JSON 中定义）：
- `functional`: 函数调用测试，比较返回值
- `stdin`: 标准输入输出测试
- `code`: 执行测试代码块

## 配置参数

默认配置（在 `run.py` 中）：
- API_BASE: `http://localhost:8001/v1`
- MODEL: `Qwen3-8B`（在 `llm_client.py` 中）
- MAX_TURNS: 3（考试限制）
- SAMPLES: 16（每题采样数，模拟正式评分）
- WORKERS: 80（并行进程数）

正式评分模型参数（固定）：
- temperature: 1.0
- top_p: 1
- max_tokens: 8192
- enable_thinking: False（不开思考模式）

## 输出结果

结果保存在 `outputs/` 目录：
- 单次运行：`outputs/<run_name>/q<index>-s<sample_id>.json`
- 汇总报告：`outputs/<run_name>/summary.json`

汇总报告包含：
- 每题的 pass@1 成功率
- 平均 pass@1（这是最终客观得分的基础）
- 每个样本的详细结果

## 探索报告撰写建议

探索报告应包含：

1. **策略设计思路**
   - 为什么选择这种 prompt 策略
   - 如何利用多轮交互能力
   - Token 预算如何分配

2. **实验对比**
   - 不同策略的 pass@1 对比
   - 典型成功/失败案例分析
   - 错误类型统计（语法错误、逻辑错误、超时等）

3. **创新点**
   - 与 baseline 的差异
   - 独特的 prompt 技巧
   - 针对特定题型的优化

4. **反思与改进**
   - 当前方案的局限性
   - 未来可能的改进方向

## 开发工作流

1. **理解题目**：先手动查看 dev.jsonl 中的题目类型
2. **设计策略**：在 solution.py 中实现 prompt 策略
3. **单题调试**：用 `--question-index` 测试单个题目
4. **完整评测**：用 `--all --samples 16` 模拟正式评分
5. **分析结果**：查看 summary.json，找出失败题目
6. **迭代优化**：针对失败案例改进 prompt
7. **撰写报告**：记录探索过程和实验结果

## 注意事项

- solution.py 中只能包含 `run_question` 函数
- 不能修改其他文件（run.py, llm_client.py, code_reward.py）
- 需要自备 LLM API（可用公开平台或自行部署 vllm/sglang）
- 最终评分在私有测试集上进行，dev.jsonl 仅供开发调试
- 禁止硬编码测试集答案，会被人工复核
