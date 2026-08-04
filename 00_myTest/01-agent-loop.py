#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author         : HKW
@Date           : 2025/11/19 21:07
@Description    : 
@Version        : 1.0
"""

# =================== 基本环境配置
import os
from dotenv import load_dotenv
from rich import print as rprint

load_dotenv(override=True)
BASE_URL = os.getenv("ANTHROPIC_BASE_URL")
API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL_ID = os.getenv("MODEL_ID")

# =================== 创建工具
import subprocess
from langchain_core.tools import tool

@tool(parse_docstring=True)
def run_bash(command: str) -> str:
    """
    运行一条 shell 命令

    Args:
        command: shell 命令
    """
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(command, shell=True, cwd=os.getcwd(),
                           capture_output=True, text=True, timeout=120)
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except (FileNotFoundError, OSError) as e:
        return f"Error: {e}"

# =================== 创建模型
from langchain.chat_models import init_chat_model

model = init_chat_model(
    model_provider="anthropic",
    base_url=BASE_URL,
    api_key=API_KEY,
    model=MODEL_ID,
)
# 绑定工具
model_with_tools = model.bind_tools([run_bash])

# =================== 创建提示词
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
system_prompt = SystemMessage(f"You are a coding agent at {os.getcwd()}. Use bash to solve tasks. Act, don't explain.")

# =================== 智能体主循环
def agent_loop(messages: list):
    while True:
        response = model_with_tools.invoke(messages)
        messages.append(response)




if __name__ == "__main__":
    print("s01: Agent Loop")
    print("输入问题，回车发送。输入 q 退出。\n")

    history = []
    history.append(system_prompt)
    while True:
        try:
            query = input("\033[36ms01 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append(HumanMessage(query))
        agent_loop(history)
        # Print the model's final text response
        response = history[-1]
        if isinstance(response, AIMessage):
            response.pretty_print()
        print()



























