import os
import json
import requests

MODEL = "Qwen3.5-397B-A17B-FP8"

SYSTEM_PROMPT = """
You are the Safety Guard Agent.

Mandatory rule:
Fuel reserve MUST be >= 20.0%.

Output strictly JSON.

Approved:
{
  "status": "APPROVED",
  "reason": "Passed safety checks"
}

Rejected:
{
  "status": "REJECTED",
  "violation": "Reason",
  "instruction": "Fix instruction"
}
"""



def demo_mode() -> bool:
    return os.getenv("CRISIS_DEMO_MODE", "false").lower() == "true"



def extract_reserve(plan_data: dict) -> float:

    reserve = plan_data.get("calculated_reserve")

    if reserve is None:
        raise ValueError("Flight plan has no calculated_reserve")

    try:
        return float(
            str(reserve).replace("%", "").strip()
        )
    except ValueError as exc:
        raise ValueError(
            f"Invalid calculated_reserve: {reserve}"
        ) from exc



def run_safety_agent(
    plan_data: dict,
    constraints: str,
    api_key: str
) -> dict:

    # --------------------------------------------------
    # HARD SAFETY GATE
    # The LLM CANNOT override this rule.
    # --------------------------------------------------

    reserve = extract_reserve(plan_data)

    if reserve < 20.0:
        return {
            "status": "REJECTED",
            "violation": (
                f"CRITICAL: Fuel reserve ({reserve:.1f}%) "
                "is below 20.0% minimum threshold."
            ),
            "instruction": (
                "Increase fuel load to achieve >= 20.0% reserve."
            )
        }

    # Demo mode: deterministic approval after hard rule passes
    if demo_mode():
        return {
            "status": "APPROVED",
            "reason": (
                f"Fuel reserve ({reserve:.1f}%) verified."
            )
        }

    endpoint = os.getenv("SAFETY_URL")

    if not endpoint:
        raise RuntimeError("SAFETY_URL is not configured")

    if not api_key:
        raise RuntimeError("FLWR_MODEL_API_KEY is not configured")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"CONSTRAINTS: {constraints}\n"
        f"PROPOSED PLAN:\n{json.dumps(plan_data)}"
    )

    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json={
                "model": MODEL,
                "input": prompt,
                "stream": False
            },
            timeout=15
        )

        response.raise_for_status()

        response_data = response.json()

        if "output_text" not in response_data:
            raise RuntimeError(
                "Safety response missing output_text"
            )

        result = json.loads(response_data["output_text"])

        status = result.get("status")

        if status not in {"APPROVED", "REJECTED"}:
            raise RuntimeError(
                f"Invalid safety status: {status}"
            )

        return result

    except Exception as exc:
        raise RuntimeError(
            f"Safety agent failed: {exc}"
        ) from exc
