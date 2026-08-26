import os
import json
import requests

MODEL = "glm-5.2-fp8"

SYSTEM_PROMPT = """
You are the Ground Coordinator Agent for Crisis Command.
Convert raw emergency field reports into a clean JSON demand payload.

Output strictly JSON:
{
  "zone_id": "Sector 4 Flood",
  "urgency": "CRITICAL",
  "required_supplies": {
    "clean_water_kg": 400,
    "trauma_kits_kg": 200
  },
  "total_weight_kg": 600,
  "landing_constraints": "flooded_runway_helipad_only"
}
"""



def demo_mode() -> bool:
    return os.getenv("CRISIS_DEMO_MODE", "false").lower() == "true"



def run_coordinator_agent(raw_reports: list[str], api_key: str) -> dict:

    # EXPLICIT demo data — never silently used in production
    if demo_mode():
        return {
            "zone_id": "Sector 4 Flood Zone",
            "urgency": "CRITICAL",
            "required_supplies": {
                "clean_water_kg": 400,
                "trauma_kits_kg": 200
            },
            "total_weight_kg": 600,
            "landing_constraints": "flooded_runway_helipad_only"
        }

    endpoint = os.getenv("COORDINATOR_URL")

    if not endpoint:
        raise RuntimeError("COORDINATOR_URL is not configured")

    if not api_key:
        raise RuntimeError("FLWR_MODEL_API_KEY is not configured")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = (
        f"{SYSTEM_PROMPT}\n\nRAW FIELD REPORTS:\n"
        + "\n".join(raw_reports)
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
                "Coordinator response missing output_text"
            )

        demand = json.loads(response_data["output_text"])

        required_fields = {
            "zone_id",
            "urgency",
            "required_supplies",
            "total_weight_kg",
            "landing_constraints"
        }

        missing = required_fields - demand.keys()

        if missing:
            raise RuntimeError(
                f"Coordinator output missing fields: {missing}"
            )

        return demand

    except Exception as exc:
        raise RuntimeError(
            f"Coordinator agent failed: {exc}"
        ) from exc
