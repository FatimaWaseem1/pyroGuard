pyroguard is a multi-agent emergency dispatch prototype that turns raw crisis reports into a resource plan, validates that plan against hard safety rules, and automatically requests a corrected plan when safety requirements are violated.
The project currently uses three backend agents:

Ground Coordinator — GLM-5.2
Resource Allocator — Kimi-K2.7-Code
Safety Guard — Qwen3.5-397B-A17B-FP8
The core demo shows an unsafe initial plan being rejected, corrected, and re-audited before dispatch clearance.
Architecture
Emergency Reports
      ↓
Ground Coordinator
GLM-5.2
      ↓
Structured Demand
      ↓
Resource Allocator
Kimi-K2.7-Code
      ↓
Proposed Plan
      ↓
Hard Safety Gate
Fuel reserve >= 20%
      ↓
   SAFE?
   /   \
 NO     YES
 ↓       ↓
Feedback Approval
 ↓
Re-plan
 ↓
Re-audit
 ↓
APPROVE or BLOCKCritical Safety Rule
Fuel reserve MUST be >= 20%This rule is enforced directly in Python.
The LLM cannot override it.
UNKNOWN != SAFE
ERROR   != APPROVEDAny failed safety re-check blocks the mission.
Demo Mode
For the hackathon demo:
export CRISIS_DEMO_MODE=true
python main.pyDemo mode intentionally uses deterministic data so endpoint/network failures cannot break the presentation.
The demo flow is:
Initial plan
15% reserve
    ↓
REJECTED
    ↓
Safety feedback
    ↓
Allocator replans
    ↓
25% reserve
    ↓
Re-audit
    ↓
APPROVEDLive Mode
export CRISIS_DEMO_MODE=falseConfigure:
FLWR_MODEL_API_KEY=YOUR_PROVIDED_KEY

COORDINATOR_URL=YOUR_PROVIDED_GLM_ENDPOINT
ALLOCATOR_URL=YOUR_PROVIDED_KIMI_ENDPOINT
SAFETY_URL=YOUR_PROVIDED_QWEN_ENDPOINTUse only the model endpoints supplied by the hackathon infrastructure.
Do not guess or invent endpoints.
In live mode, model/network/parsing failures block execution instead of silently generating fake mission data.
Models
AgentModelJobGround Coordinatorglm-5.2-fp8Understand emergency reportsResource AllocatorKimi-K2.7-CodeGenerate and revise mission planSafety GuardQwen3.5-397B-A17B-FP8Model-assisted safety review
Project Structure
pyroGuard/
├── README.md
└── crisis-command/
    ├── index.html
    ├── main.py
    ├── pyproject.toml
    ├── test_endpoints.py
    └── agents/
        ├── __init__.py
        ├── coordinator.py
        ├── allocator.py
        └── safety.pyInstallation
Requires Python 3.10+.
cd crisis-command

python -m venv .venv
source .venv/bin/activate

pip install -e .Then:
export CRISIS_DEMO_MODE=true
python main.pyFailure Policy
Crisis Command must never convert these failures into approval:

endpoint unavailable
authentication failure
timeout
malformed model response
invalid JSON
missing required fields
invalid fuel reserve
unknown safety decision
second safety rejection
missing configuration
The system fails closed:
APPROVED → continue

REJECTED → block/replan

ERROR → blockCurrent Scope
Implemented:

Ground Coordinator
Resource Allocator
Safety Guard
safety rejection
feedback to allocator
autonomous replanning
second safety validation
deterministic 20% reserve rule
explicit demo mode
fail-closed behavior
The visual index.html currently contains additional conceptual agents such as Voice Intake, Vision AI and Dispatcher.
Those are not yet equivalent backend Python agents, and the frontend is currently separate from the Python pipeline.
Demo Explanation
An emergency report comes in. The coordinator determines what is needed. The allocator creates a mission plan. Before the plan can receive clearance, the safety boundary checks it. The initial plan leaves only 15% fuel reserve, so it is rejected. The reason is returned to the allocator, which replans with 25% reserve. The corrected plan is then checked again before final clearance.The key idea:
AI proposes.
Safety decides.
Unsafe execution is blocked.
The system corrects and retries.Status
Crisis Command is a hackathon prototype demonstrating multi-agent crisis planning, deterministic safety enforcement, rejection feedback and autonomous replanning.
It is not a production emergency-response system.
:::
