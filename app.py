"""Gradio UI and MCP server for the fintools calculators."""

import sys

import gradio as gr

from src.mortgage import (
    amortization_schedule,
    monthly_payment,
    payoff_simulation,
    refinance_breakeven,
)
from src.savings import compound_savings, emergency_fund_target, real_return

AMORTIZATION_INPUT = dict(
    choices=["annuity", "fixed_principal"], value="annuity", label="Amortization"
)

monthly_payment_tab = gr.Interface(
    fn=monthly_payment,
    inputs=[
        gr.Number(label="Principal", value=100000),
        gr.Number(label="Annual rate (%)", value=6),
        gr.Number(label="Months", value=360, precision=0),
        gr.Dropdown(**AMORTIZATION_INPUT),
    ],
    outputs=gr.JSON(label="Payment breakdown"),
    title="Monthly Payment",
)

amortization_schedule_tab = gr.Interface(
    fn=amortization_schedule,
    inputs=[
        gr.Number(label="Principal", value=100000),
        gr.Number(label="Annual rate (%)", value=6),
        gr.Number(label="Months", value=360, precision=0),
        gr.Dropdown(**AMORTIZATION_INPUT),
    ],
    outputs=gr.JSON(label="Schedule"),
    title="Amortization Schedule",
)

payoff_simulation_tab = gr.Interface(
    fn=payoff_simulation,
    inputs=[
        gr.Number(label="Principal", value=100000),
        gr.Number(label="Annual rate (%)", value=6),
        gr.Number(label="Months", value=360, precision=0),
        gr.Dropdown(**AMORTIZATION_INPUT),
        gr.Number(label="Extra monthly payment", value=100),
    ],
    outputs=gr.JSON(label="Payoff impact"),
    title="Payoff Simulation",
)

refinance_breakeven_tab = gr.Interface(
    fn=refinance_breakeven,
    inputs=[
        gr.Number(label="Current balance", value=100000),
        gr.Number(label="Current rate (%)", value=6),
        gr.Number(label="New rate (%)", value=5),
        gr.Number(label="Remaining months", value=360, precision=0),
        gr.Number(label="Closing costs", value=2000),
    ],
    outputs=gr.JSON(label="Refinance analysis"),
    title="Refinance Breakeven",
)

compound_savings_tab = gr.Interface(
    fn=compound_savings,
    inputs=[
        gr.Number(label="Monthly deposit", value=100),
        gr.Number(label="Annual rate (%)", value=4),
        gr.Number(label="Months", value=120, precision=0),
        gr.Number(label="Initial balance", value=0),
    ],
    outputs=gr.JSON(label="Projection"),
    title="Compound Savings",
)

emergency_fund_target_tab = gr.Interface(
    fn=emergency_fund_target,
    inputs=[
        gr.Number(label="Monthly expenses", value=2000),
        gr.Number(label="Months of coverage", value=6, precision=0),
        gr.Number(label="Current savings", value=0),
        gr.Number(label="Monthly contribution", value=500),
    ],
    outputs=gr.JSON(label="Fund plan"),
    title="Emergency Fund",
)

real_return_tab = gr.Interface(
    fn=real_return,
    inputs=[
        gr.Number(label="Nominal rate (%)", value=6),
        gr.Number(label="Inflation rate (%)", value=2),
    ],
    outputs=gr.JSON(label="Real return"),
    title="Real Return",
)

demo = gr.TabbedInterface(
    [
        monthly_payment_tab,
        amortization_schedule_tab,
        payoff_simulation_tab,
        refinance_breakeven_tab,
        compound_savings_tab,
        emergency_fund_target_tab,
        real_return_tab,
    ],
    [
        "Monthly Payment",
        "Amortization Schedule",
        "Payoff Simulation",
        "Refinance Breakeven",
        "Compound Savings",
        "Emergency Fund",
        "Real Return",
    ],
    title="fintools-mcp",
)

if __name__ == "__main__":
    # Gradio's MCP startup banner contains emoji, which crashes on consoles
    # that don't default to UTF-8 (e.g. cp1252 on Windows).
    if sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    demo.launch(mcp_server=True)
