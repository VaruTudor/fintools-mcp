---
title: Fintools MCP
emoji: 🧮
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "6.19.0"
app_file: app.py
pinned: false
---

# fintools-mcp

**Live demo:** https://huggingface.co/spaces/varutudor/fintools-mcp

Personal finance calculators exposed as an MCP server with a Gradio UI, deployable to Hugging Face Spaces.

## Tools

- **monthly_payment** — mortgage payment for annuity or fixed-principal loans
- **amortization_schedule** — month-by-month payment/principal/interest breakdown
- **payoff_simulation** — months and interest saved by paying extra each month
- **refinance_breakeven** — monthly savings, breakeven month, and net savings of a refinance
- **compound_savings** — end balance of monthly deposits with compound interest
- **emergency_fund_target** — target amount, gap, and months to reach it
- **real_return** — inflation-adjusted return (Fisher equation, exact and approximate)

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

## Run tests

```bash
pytest
```

## Use as an MCP server

Claude Code:

```bash
claude mcp add --transport http --scope user fintools https://varutudor-fintools-mcp.hf.space/gradio_api/mcp/
```

Generic config (SSE endpoint):

```json
{
  "mcpServers": {
    "fintools": {
      "url": "https://varutudor-fintools-mcp.hf.space/gradio_api/mcp/sse"
    }
  }
}
```

Note: the free Space sleeps after inactivity — the first request may take ~30s while it wakes up.
