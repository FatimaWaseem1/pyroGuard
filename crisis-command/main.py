def execute_pipeline(reports: list[str]):

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
        # 1. COORDINATOR
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
        # 2. ALLOCATOR
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

        audit = run_safety_agent(
            plan,
            demand.get("landing_constraints", ""),
            api_key
        )

        # APPROVED FIRST TIME
        if audit.get("status") == "APPROVED":

            console.print(
                Panel(
                    JSON(json.dumps(audit)),
                    title="3. SAFETY CLEARANCE: APPROVED",
                    border_style="green"
                )
            )

            return True

        # -------------------------------------------------
        # REJECTED → SELF HEAL
        # -------------------------------------------------

        if audit.get("status") != "REJECTED":
            raise RuntimeError(
                f"Unknown safety decision: {audit}"
            )

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
        # 4. RE-PLAN
        # -------------------------------------------------

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
        # 5. RE-AUDIT
        # -------------------------------------------------

        final_audit = run_safety_agent(
            healed_plan,
            demand.get("landing_constraints", ""),
            api_key
        )

        # THIS CHECK WAS MISSING
        if final_audit.get("status") == "APPROVED":

            console.print(
                Panel(
                    JSON(json.dumps(final_audit)),
                    title="5. FINAL CLEARANCE: APPROVED",
                    border_style="green"
                )
            )

            return True

        # FAIL CLOSED
        console.print(
            Panel(
                JSON(json.dumps(final_audit)),
                title="5. FINAL CLEARANCE: BLOCKED",
                border_style="red"
            )
        )

        console.print(
            "[bold red]"
            "MISSION BLOCKED — safety requirements "
            "still not satisfied."
            "[/bold red]"
        )

        return False

    except Exception as exc:

        console.print(
            Panel(
                str(exc),
                title="SYSTEM FAILURE — DISPATCH BLOCKED",
                border_style="red"
            )
        )

        return False
