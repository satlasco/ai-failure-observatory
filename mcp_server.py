"""AI Failure Observatory — FastMCP Server & Dual-Mode CLI Entry Point.

Run directly for MCP stdio mode (Claude Desktop, Cursor, Antigravity):
    python mcp_server.py
    uvx ai-failure-observatory

Run with --web to launch the Web Observatory Dashboard:
    python mcp_server.py --web
    ai-failure-observatory --web
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from typing import Any, Optional

# Ensure UTF-8 output on Windows consoles
if sys.platform.startswith("win"):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

from mcp.server.fastmcp import FastMCP
from src import mcp_tools

# Initialize FastMCP Server
mcp = FastMCP(
    "ai-failure-observatory",
    instructions="AI Safety, Red-Teaming, Vulnerability Probing & Product-Risk Auditing platform for detecting hallucinations, fake confidence, context loss, instruction drift, persuasive manipulation, and reasoning collapse in LLMs."
)


@mcp.tool()
def audit_prompt_response(prompt: str, response: str, model: str = "custom") -> str:
    """Audit any LLM prompt-response pair for 6 behavioral failure modes: hallucinations (invented citations/facts), fake confidence (epistemic arrogance), context loss (amnesia), instruction drift (negative constraint violations), manipulation (urgency/steering), and recursive reasoning collapse (circular logic). Returns structured verdict, confidence scores, evidence, and mitigations."""
    res = mcp_tools.audit_prompt_response(prompt=prompt, response=response, model=model)
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def get_failure_taxonomy(failure_type: Optional[str] = None) -> str:
    """Retrieve the formal AI Failure Taxonomy definitions, severity scores (1-10), product risk implications, and concrete engineering mitigations. Pass optional failure_type ('hallucinations', 'fake_confidence', 'context_loss', 'instruction_drift', 'manipulation', 'recursive_reasoning_collapse') or leave empty for full taxonomy."""
    res = mcp_tools.get_failure_taxonomy(failure_type=failure_type)
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def get_risk_report() -> str:
    """Generate the real-time AI product risk scorecard, incident distribution across failure categories, aggregate vulnerability score, and top compliance risk areas."""
    res = mcp_tools.get_risk_report()
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def log_safety_incident(
    model_name: str,
    prompt: str,
    response: str,
    failure_type: str,
    severity: str = "medium",
    notes: str = ""
) -> str:
    """Record a detected AI safety or behavioral failure incident into the persistent observatory database for compliance tracking and risk index calculation. Failure types: 'hallucinations', 'fake_confidence', 'context_loss', 'instruction_drift', 'manipulation', 'recursive_reasoning_collapse'."""
    res = mcp_tools.log_safety_incident(
        model_name=model_name,
        prompt=prompt,
        response=response,
        failure_type=failure_type,
        severity=severity,
        notes=notes
    )
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def scan_multi_turn_conversation(turns_json: str) -> str:
    """Scan a multi-turn conversation dialogue (JSON array of {role: 'user'|'assistant', content: '...'}) to detect working memory context degradation, conversational amnesia, and progressive instruction drift."""
    try:
        turns = json.loads(turns_json)
        if not isinstance(turns, list):
            return json.dumps({"error": "turns_json must be a JSON array of turn objects"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Invalid JSON: {e}"}, indent=2)

    res = mcp_tools.scan_multi_turn_conversation(turns)
    return json.dumps(res, indent=2, ensure_ascii=False)


@mcp.tool()
def run_benchmark_evaluations() -> str:
    """Execute the automated reproducible evaluation benchmark suite across all 6 AI failure modes and return detailed pass/fail test results."""
    res = mcp_tools.run_benchmark_evaluations()
    return json.dumps(res, indent=2, ensure_ascii=False)


def main() -> None:
    """CLI Entry Point: default is MCP stdio server; if --web passed, launches HTTP dashboard."""
    parser = argparse.ArgumentParser(description="AI Failure Observatory — Behavioral Safety & MCP Server")
    parser.add_argument("--web", action="store_true", help="Launch the Web Observatory Dashboard on localhost:5089")
    parser.add_argument("--port", type=int, default=5089, help="Port for the web server (default: 5089)")
    args, unknown = parser.parse_known_args()

    if args.web:
        from server import run_server
        print(f"🛡️ Starting AI Failure Observatory Web Dashboard on http://localhost:{args.port}")
        run_server(port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
