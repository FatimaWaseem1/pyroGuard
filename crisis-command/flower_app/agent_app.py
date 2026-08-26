[5:24 PM]from __future__ import annotations

import os

from flwr.agentapp import AgentApp, AgentSession
from flwr.app import Context

from main import execute_pipeline



app = AgentApp()



@app.main()
def main(agent: AgentSession, context: Context) -> None:
    """
    Flower entry point for Crisis Command.

    Runs the existing multi-agent emergency dispatch pipeline.
    """

    raw_input = context.run_config.get(
        "agent.input",
        (
            "Severe flooding reported in Sector 4.\n"
            "Approximately 200 civilians are isolated.\n"
            "Ground access is unavailable.\n"
            "Emergency water and trauma supplies required.\n"
            "Runway is flooded. Helicopter landing area remains accessible."
        ),
    )

    if not isinstance(raw_input, str) or not raw_input.strip():
        raise ValueError(
            "agent.input must be a non-empty string"
        )

    demo_mode = context.run_config.get(
        "crisis.demo",
        True,
    )

    os.environ["CRISIS_DEMO_MODE"] = (
        "true" if demo_mode else "false"
    )

    reports = [
        line.strip()
        for line in raw_input.splitlines()
        if line.strip()
    ]

    success = execute_pipeline(reports)

    if not success:
        raise RuntimeError(
            "Crisis Command blocked dispatch because "
            "safety requirements were not satisfied."
        )

    print(
        "CRISIS COMMAND: "
        "MISSION CLEARED FOR DISPATCH"
    )
