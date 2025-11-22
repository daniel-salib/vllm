# MCP Tools Update for vLLM Recipes - GPT-OSS.md

This content should be added to: https://github.com/vllm-project/recipes/blob/main/OpenAI/GPT-OSS.md

---

## Add this new section after "Tool Calling" section:

### MCP Tool Calling

vLLM supports MCP (Model Context Protocol) tools through the Responses API, allowing models to call external services and execute code.

#### Setup

1. **Set environment variables**:
```bash
export VLLM_ENABLE_RESPONSES_API_STORE=1
export VLLM_GPT_OSS_SYSTEM_TOOL_MCP_LABELS=code_interpreter
export VLLM_RESPONSES_API_USE_MCP_TYPES=1
export VLLM_GPT_OSS_HARMONY_SYSTEM_INSTRUCTIONS=1
```

2. **Start vLLM server**:
```bash
vllm serve openai/gpt-oss-20b \
    --tool-server demo \
    --enable-auto-tool-choice \
    --tool-call-parser gptoss
```

#### Built-in MCP Tools

| Tool | Description | Server Label |
|------|-------------|--------------|
| Python Execution | Execute Python code | `code_interpreter` |
| Container | Run commands in containers | `container` |
| Web Search | Search and retrieve web content | `web_search_preview` |

#### Example Usage

**Basic MCP Tool Call:**
```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="empty")

response = client.responses.create(
    model="openai/gpt-oss-20b",
    input="Calculate 123 * 456 using Python",
    tools=[{"type": "mcp", "server_label": "code_interpreter"}],
    instructions="You must use the Python tool. Never simulate execution.",
)

print(response.output_text)
```

**Streaming MCP Events:**
```python
stream = client.responses.create(
    model="openai/gpt-oss-20b",
    input="What is 100 / 4? Use Python.",
    tools=[{"type": "mcp", "server_label": "code_interpreter"}],
    stream=True,
)

for event in stream:
    if "mcp_call" in event.type:
        print(f"Event: {event.type}")
        # Events: response.mcp_call.in_progress
        #         response.mcp_call_arguments.delta
        #         response.mcp_call_arguments.done
        #         response.mcp_call.completed
```

**Filter Specific Tools:**
```python
response = client.responses.create(
    model="openai/gpt-oss-20b",
    input="Add 10 and 20",
    tools=[{
        "type": "mcp",
        "server_label": "calculator",
        "allowed_tools": ["add"]  # Only allow specific tools
    }],
)
```

#### Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `VLLM_ENABLE_RESPONSES_API_STORE` | Enable response storage | `0` |
| `VLLM_GPT_OSS_SYSTEM_TOOL_MCP_LABELS` | Comma-separated MCP server labels | `""` |
| `VLLM_RESPONSES_API_USE_MCP_TYPES` | Enable MCP type system | `0` |
| `VLLM_GPT_OSS_HARMONY_SYSTEM_INSTRUCTIONS` | Enable harmony instructions | `0` |

#### Example Code

See `examples/online_serving/openai_responses_client_with_mcp_tools.py` for a complete working example.

---

## Add this note to the existing "Tool Calling" section:

> **Note**: For MCP (Model Context Protocol) tools that call external services, see the [MCP Tool Calling](#mcp-tool-calling) section below.
