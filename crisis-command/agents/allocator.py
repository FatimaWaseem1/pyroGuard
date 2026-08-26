import os
import json
import requests

MODEL = "Kimi-K2.7-Code"

SYSTEM_PROMPT = """
You are the Resource Allocator Agent.

Generate a flight plan.

Output strictly JSON:
{
  "vehicle": "CH-47 Helicopter",
  "payload_kg": 600,
  "distance_km": 120,
  "fuel_allocated_liters": 240,
  "calculated_reserve": "15.0%"
}
"""



def demo_mode() -> bool:
    return os.getenv("CRISIS_DEMO_MODE", "false").lower() == "true"



def run_allocator_agent(
    demand_data: dict,
    api_key: str,
    feedback: str = ""
) -> dict:

    # Explicit deterministic demo
    if demo_mode():

        if feedback:
            return {
                "vehicle": "CH-47 Helicopter",
                "payload_kg": demand_data.get("total_weight_kg", 600),
                "distance_km": 120,
                "fuel_allocated_liters": 310,
                "calculated_reserve": "25.0%"
            }

        return {
            "vehicle": "CH-47 Helicopter",
            "payload_kg": demand_data.get("total_weight_kg", 600),
            "distance_km": 120,
            "fuel_allocated_liters": 240,
            "calculated_reserve": "15.0%"
        }

    endpoint = os.getenv("ALLOCATOR_URL")

    if not endpoint:
        raise RuntimeError("ALLOCATOR_URL is not configured")

    if not api_key:
        raise RuntimeError("FLWR_MODEL_API_KEY is not configured")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"DEMAND DATA:\n{json.dumps(demand_data)}"
    )

    if feedback:
        prompt += (
            f"\n\nSAFETY FEEDBACK TO FIX:\n{feedback}"
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
                "Allocator response missing output_text"
            )

        plan = json.loads(response_data["output_text"])

        required_fields = {
            "vehicle",
            "payload_kg",
            "distance_km",
            "fuel_allocated_liters",
            "calculated_reserve"
        }

        missing = required_fields - plan.keys()

        if missing:
            raise RuntimeError(
                f"Allocator output missing fields: {missing}"
            )

        return plan

    except Exception as exc:
        raise RuntimeError(
            f"Allocator agent failed: {exc}"
        ) from exc
