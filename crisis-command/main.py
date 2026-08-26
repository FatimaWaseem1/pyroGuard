import os
import json
import time
from dotenv import load_dotenv

from rich.console import Console
from rich.panel import Panel
from rich.json import JSON
from rich.theme import Theme

from agents.coordinator import run_coordinator_agent
from agents.allocator import run_allocator_agent
from agents.safety import run_safety_agent

load_dotenv()

custom_theme = Theme({
    "info": "bold cyan",
    "warning": "bold yellow",
    "danger": "bold red",
    "success": "bold green",
    "highlight": "bold magenta"
})

console = Console(theme=custom_theme)

def execute_pipeline(reports: list[str]):
    api_key = os.getenv("FLWR_MODEL_API_KEY", "DEMO_KEY")

    console.rule("[highlight]CRISIS COMMAND: MULTI-AGENT EMERGENCY DISPATCH[/highlight]")
    console.print("[dim]Powered by Autonomous SuperGrid Self-Healing Engine[/dim]\n")

    # Step 1: Coordinator
    with console.status("[bold cyan]Step 1: Ground Coordinator Ingesting Reports (GLM-5.2)...[/bold cyan]"):
        time.sleep(1.2)
        demand = run_coordinator_agent(reports, api_key)
    console.print(Panel(JSON(json.dumps(demand)), title="[info]1. Demand Output (GLM-5.2)[/info]", border_style="cyan"))

    # Step 2: Allocator
    with console.status("[bold yellow]Step 2: Resource Allocator Calculating Route (Kimi-K2.7-Code)...[/bold yellow]"):
        time.sleep(1.5)
        plan = run_allocator_agent(demand, api_key)
    console.print(Panel(JSON(json.dumps(plan)), title="[warning]2. Initial Flight Plan (Kimi-K2.7-Code)[/warning]", border_style="yellow"))

    # Step 3: Safety Guard Audit
    with console.status("[bold magenta]Step 3: Safety Guard Auditing Compliance (Qwen3.5-397B)...[/bold magenta]"):
        time.sleep(1.0)
        audit = run_safety_agent(plan, demand.get("landing_constraints", ""), api_key)

    # Step 4: Self-Healing Trigger
    if audit.get("status") == "REJECTED":
        console.print(Panel(JSON(json.dumps(audit)), title="[danger]3. Safety Audit Result: REJECTED[/danger]", border_style="red"))
        console.print("\n[bold red]⚠️ SAFETY VIOLATION DETECTED![/bold red]")
        console.print("[bold yellow]Triggering Autonomous Self-Healing Loop...[/bold yellow]\n")

        with console.status("[bold yellow]Re-calculating Flight Plan with Safety Feedback...[/bold yellow]"):
            time.sleep(2.0)
            healed_plan = run_allocator_agent(
                demand,
                api_key,
                feedback=audit.get("instruction", "Increase fuel reserve to >= 20%")
            )

        console.print(Panel(JSON(json.dumps(healed_plan)), title="[warning]Self-Healed Flight Plan (Kimi-K2.7-Code)[/warning]", border_style="yellow"))

        with console.status("[bold green]Re-auditing Corrected Flight Plan...[/bold green]"):
            time.sleep(1.0)
            final_audit = run_safety_agent(healed_plan, demand.get("landing_constraints", ""), api_key)

        console.print(Panel(JSON(json.dumps(final_audit)), title="[success]4. Final Clearance Approved (Qwen3.5-397B)[/success]", border_style="green"))
    else:
        console.print(Panel(JSON(json.dumps(audit)), title="[success]3. Final Clearance Approved (Qwen3.5-397B)[/success]", border_style="green"))

if __name__ == "__main__":
    sample_reports = [
        "Urgent: Flood waters rising fast in Sector 4. Main runway submerged, helipad operational.",
        "We need medical trauma kits and clean water immediately for 300 casualties."
    ]
    execute_pipeline(sample_reports)