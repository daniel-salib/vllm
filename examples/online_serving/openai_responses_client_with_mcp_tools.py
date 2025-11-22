# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
"""
Example demonstrating MCP (Model Context Protocol) tools with vLLM Responses API.

This shows how to use built-in MCP tools like code_interpreter for Python execution.

Setup:
1. Set environment variables:
   export VLLM_ENABLE_RESPONSES_API_STORE=1
   export VLLM_GPT_OSS_SYSTEM_TOOL_MCP_LABELS=code_interpreter
   export VLLM_GPT_OSS_HARMONY_SYSTEM_INSTRUCTIONS=1

2. Start vLLM server:
   vllm serve openai/gpt-oss-20b \\
       --tool-server demo \\
       --enable-auto-tool-choice \\
       --tool-call-parser gptoss

3. Run this example:
   python examples/online_serving/openai_responses_client_with_mcp_tools.py
"""

from openai import OpenAI
from utils import get_first_model


def main():
    base_url = "http://0.0.0.0:8000/v1"
    client = OpenAI(base_url=base_url, api_key="empty")
    model = get_first_model(client)

    # Example 1: Basic MCP tool usage
    print("=== Example 1: Calculate with Python ===")
    response = client.responses.create(
        model=model,
        input="Calculate 123 * 456 using Python. Print the result.",
        tools=[{"type": "mcp", "server_label": "code_interpreter"}],
        instructions="You must use the Python tool. Never simulate execution.",
    )
    print(f"Result: {response.output_text}\n")

    # Example 2: Streaming MCP calls
    print("=== Example 2: Streaming ===")
    stream = client.responses.create(
        model=model,
        input="What is 100 / 4? Use Python.",
        tools=[{"type": "mcp", "server_label": "code_interpreter"}],
        stream=True,
        instructions="You must use the Python tool. Never simulate execution.",
    )

    for event in stream:
        if "mcp_call" in event.type:
            print(f"  Event: {event.type}")


if __name__ == "__main__":
    main()
