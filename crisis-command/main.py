import os
import json

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON
from rich.theme import Theme

from agents.coordinator import run_coordinator_agent
from agents.allocator import run_allocator_agent
from agents.safety import run_safety_agent



# ---------------------------------------------------------
# SETUP
# ---------------------------------------------------------

load_dotenv()

custom_theme = Theme(
    {
        "highlight": "bold cyan",
    }
)

console = Console(theme=custom_theme)



# ---------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------

def execute_pipeline(reports: list[str]) -> bool:

    demo = os.getenv(
        "CRISIS_DEMO_MODE",
        "false"
    ).lower() == "true"

    api_key = os.getenv("FLWR_MODEL_API_KEY")

    console.rule(
        "[highlight]CRISIS COMMAND: "
        "MULTI-AGENT EMERGENCY DISPATCH[/highlight]"
    )

    if demo:
        console.print(
            "[bold yellow]"
            "DEMO MODE — deterministic simulation"
            "[/bold yellow]\n"
        )

    try:

        # -------------------------------------------------
        # 1. GROUND COORDINATOR
        # -------------------------------------------------

        with console.status(
            "[bold cyan]"
            "Ground Coordinator analysing incident..."
            "[/bold cyan]"
        ):
            demand = run_coordinator_agent(
                reports,
                api_key
            )

        console.print(
            Panel(
                JSON(json.dumps(demand)),
                title="1. Ground Coordinator",
                border_style="cyan"
            )
        )

        # -------------------------------------------------
        # 2. RESOURCE ALLOCATOR
        # -------------------------------------------------

        with console.status(
            "[bold yellow]"
            "Resource Allocator generating plan..."
            "[/bold yellow]"
        ):
            plan = run_allocator_agent(
                demand,
                api_key
            )

        console.print(
            Panel(
                JSON(json.dumps(plan)),
                title="2. Initial Resource Plan",
                border_style="yellow"
            )
        )

        # -------------------------------------------------
        # 3. SAFETY GATE
        # -------------------------------------------------

        with console.status(
            "[bold magenta]"
            "Safety Guard auditing plan..."
            "[/bold magenta]"
        ):
            audit = run_safety_agent(
                plan,
                demand.get("landing_constraints", ""),
                api_key
            )

        # -------------------------------------------------
        # APPROVED FIRST TIME
        # -------------------------------------------------

        if audit.get("status") == "APPROVED":

            console.print(
                Panel(
                    JSON(json.dumps(audit)),
                    title="3. SAFETY CLEARANCE: APPROVED",
                    border_style="green"
                )
            )

            console.print(
                "\n[bold green]"
                "MISSION CLEARED FOR DISPATCH"
                "[/bold green]"
            )

            return True

        # -------------------------------------------------
        # UNKNOWN RESPONSE → FAIL CLOSED
        # -------------------------------------------------

        if audit.get("status") != "REJECTED":

            raise RuntimeError(
                f"Unknown safety decision: {audit}"
            )

        # -------------------------------------------------
        # SAFETY REJECTION
        # -------------------------------------------------

        console.print(
            Panel(
                JSON(json.dumps(audit)),
                title="3. SAFETY GATE: REJECTED",
                border_style="red"
            )
        )

        console.print(
            "\n[bold red]"
            ":warning: SAFETY VIOLATION DETECTED"
            "[/bold red]"
        )

        console.print(
            "[bold yellow]"
            "Re-planning with safety feedback..."
            "[/bold yellow]\n"
        )

        # -------------------------------------------------
        # 4. SELF-HEAL / RE-PLAN
        # -------------------------------------------------

        with console.status(
            "[bold yellow]"
            "Resource Allocator correcting plan..."
            "[/bold yellow]"
        ):
            healed_plan = run_allocator_agent(
                demand,
                api_key,
                feedback=audit.get(
                    "instruction",
                    "Correct safety violation"
                )
            )

        console.print(
            Panel(
                JSON(json.dumps(healed_plan)),
                title="4. Corrected Resource Plan",
                border_style="yellow"
            )
        )

        # -------------------------------------------------
        # 5. FINAL SAFETY RE-AUDIT
        # -------------------------------------------------

        with console.status(
            "[bold magenta]"
            "Safety Guard re-auditing corrected plan..."
            "[/bold magenta]"
        ):
            final_audit = run_safety_agent(
                healed_plan,
                demand.get("landing_constraints", ""),
                api_key
            )

        # -------------------------------------------------
        # FINAL APPROVAL
        # -------------------------------------------------

        if final_audit.get("status") == "APPROVED":

            console.print(
                Panel(
                    JSON(json.dumps(final_audit)),
                    title="5. FINAL CLEARANCE: APPROVED",
                    border_style="green"
                )
            )

            console.print(
                "\n[bold green]"
                "MISSION CLEARED FOR DISPATCH"
                "[/bold green]"
            )

            return True

        # -------------------------------------------------
        # FINAL REJECTION → FAIL CLOSED
        # -------------------------------------------------

        console.print(
            Panel(
                JSON(json.dumps(final_audit)),
                title="5. FINAL CLEARANCE: BLOCKED",
                border_style="red"
            )
        )

        console.print(
            "\n[bold red]"
            "MISSION BLOCKED — safety requirements "
            "still not satisfied."
            "[/bold red]"
        )

        return False

    # -----------------------------------------------------
    # SYSTEM FAILURE → FAIL CLOSED
    # -----------------------------------------------------

    except Exception as exc:

        console.print(
            Panel(
                str(exc),
                title="SYSTEM FAILURE — DISPATCH BLOCKED",
                border_style="red"
            )
        )

        return False



# ---------------------------------------------------------
# RUN DEMO
# ---------------------------------------------------------

if __name__ == "__main__":

    sample_reports = [
        (
            "Severe flooding reported in Sector 4. "
            "Approximately 200 civilians are isolated."
        ),
        (
            "Ground access is unavailable. "
            "Emergency water and trauma supplies required."
        ),
        (
            "Runway is flooded. "
            "Helicopter landing area remains accessible."
        )
    ]

    success = execute_pipeline(sample_reports)

    if success:
        raise SystemExit(0)

    raise SystemExit(1)
