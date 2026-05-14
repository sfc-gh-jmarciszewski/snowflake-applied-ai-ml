# Cortex Code Agent SDK Quickstart

[Cortex Code Agent SDK quickstart | Snowflake Documentation](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/quickstart)

## Setup

### 1. Install Cortex Code CLI

```bash
curl -LsS https://ai.snowflake.com/static/cc-scripts/install.sh | sh
```

verify install

```bash
cortex --version
```

### 2. Setup project directory

```bash
cd cortex-code-agent-sdk/01-quick-start
```


### 3. Install SDK

```bash
uv venv && source .venv/bin/activate
uv pip install cortex-code-agent-sdk
```

## Create a data pipeline script that needs fixing

```bash
cat > report.py << 'EOF'
import json

def load_results(rows):
    """Load query results into a list of campaign dicts."""
    return [
        {
            "campaign": row["campaign_name"],
            "impressions": row["impressions"],
            "clicks": row["clicks"],
            "conversions": row["conversions"],
        }
        for row in rows
    ]

def compute_conversion_rate(results):
    """Add conversion_rate (conversions / clicks) to each campaign."""
    for row in results:
        row["conversion_rate"] = row["conversions"] / row["clicks"]  # Bug: ZeroDivisionError when clicks is 0
    return results

def format_report(results):
    """Return a JSON summary with total conversions and the top campaign."""
    total = sum(r["conversions"] for r in results)
    top = max(results, key=lambda r: r["conversion_rate"])  # Bug: crashes on empty list
    return json.dumps({"total_conversions": total, "top_campaign": top["campaign"]})
EOF
```

Issues with code:

This code has two issues:

1. computeConversionRate / compute_conversion_rate divides by clicks without checking for zero, returning NaN or Infinity (TypeScript) or raising a ZeroDivisionError (Python) for campaigns with no clicks.
2. formatReport / format_report calls max / reduce on the results list without checking whether it is empty, which raises a ValueError (Python) or TypeError (TypeScript) when there are no rows.



## Build agent to fix the code 


https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/python-reference

```bash 
cat > agent.py << 'EOF'
# agent.py
import asyncio
from cortex_code_agent_sdk import query, AssistantMessage, ResultMessage, CortexCodeAgentOptions

async def main():
    # Agentic loop: streams messages as the agent works
    async for message in query(
        prompt="Review report.py for bugs in the data pipeline. Fix any issues you find.",
        options=CortexCodeAgentOptions(
            cwd=".",
            connection="my-connection",              # Snowflake CLI connection name
            allowed_tools=["Read", "Edit", "Bash"],  # Auto-approve these tools without prompting
        ),
    ):
        # Print human-readable output
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text, end="")  # Agent's reasoning
                elif hasattr(block, "name"):
                    print(f"Tool: {block.name}")  # Tool being called
        elif isinstance(message, ResultMessage):
            print(f"\nDone: {message.subtype}")  # Final result

asyncio.run(main())
EOF
```

### Run agent

```bash
# which python
python agent.py 
```

#### sample response

```txt 
✓ Updated successfully!
Launching updated version...

Tool: glob
Tool: bash
Tool: read
I found two bugs in `report.py`. Let me fix them.

**Bug 1** (`compute_conversion_rate`, line 18): Division by zero when `clicks` is 0.

**Bug 2** (`format_report`, line 24): `max()` on an empty list raises `ValueError`.Tool: edit
Tool: edit
Fixed both bugs:

1. **`compute_conversion_rate` (line 18)** — Added a guard so that when `clicks` is 0, `conversion_rate` defaults to `0.0` instead of raising `ZeroDivisionError`.

2. **`format_report` (lines 23-24)** — Added an early return when `results` is empty, returning a safe JSON response with `total_conversions: 0` and `top_campaign: null` instead of crashing on `max()` with an empty sequence.
Done: success
```

## References 

* https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/cortex-code-agent-sdk - overview docs page