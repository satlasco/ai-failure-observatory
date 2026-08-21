"""AI Failure Observatory — Web Server & REST API.

Run with: python server.py
Then open http://localhost:5089
"""

from __future__ import annotations

import http.server
import importlib
import io
import json
import os
import socket
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any

# Ensure UTF-8 output on Windows consoles
if sys.platform.startswith("win"):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from analysis.risk_analysis import generate_risk_report
from src.failure_analyzer import analyze_conversation, analyze_response
from src.llm_client import query_llm
from src.storage import (
    Incident,
    get_failure_summary_counts,
    load_incidents,
    reset_incidents,
    save_incident,
)
from taxonomy.taxonomy_utils import load_taxonomy


def is_port_in_use(port: int) -> bool:
    """Check if port is occupied on localhost."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            return s.connect_ex(("127.0.0.1", port)) == 0
    except Exception:
        return False


def find_free_port(start_port: int = 5089, max_tries: int = 50) -> int:
    """Find the next available port starting from start_port."""
    for port in range(start_port, start_port + max_tries):
        if not is_port_in_use(port):
            return port
    return start_port


def generate_markdown_audit_report() -> str:
    """Generates an executive compliance audit report in Markdown."""
    counts = get_failure_summary_counts()
    report = generate_risk_report(counts)
    incidents = load_incidents()[:20]

    md = [
        "# 🛡️ AI Model Behavioral Safety & Failure Audit Report",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
        f"**Audit Engine:** AI Failure Observatory v1.2 (ADA Creative Co.)  ",
        "---",
        "",
        "## 1. Executive Summary & Risk Level",
        f"* **Overall Qualitative Risk Level:** `{report['overall_risk_assessment']['qualitative_risk_level'].upper()}`",
        f"* **Aggregate Risk Index Score:** `{report['overall_risk_assessment']['aggregate_risk_score']}`",
        f"* **Total Detected Failure Incidents:** `{report['overall_risk_assessment']['total_detected_instances']}`",
        f"* **Unique Failure Modes Triggered:** `{report['overall_risk_assessment']['total_unique_failure_types']} / 6`",
        "",
        "---",
        "",
        "## 2. Failure Category Breakdown & Severity",
        "| Failure Mode | Severity | Incidents | Risk Score | Primary Risk Impact |",
        "|---|---|---|---|---|",
    ]

    for item in report.get("failure_breakdown", []):
        md.append(
            f"| `{item['failure_type']}` | {item['severity_label']} | {item['count_detected']} | {item['risk_score']} | {', '.join(item['primary_risks'][:2])} |"
        )

    md.extend([
        "",
        "---",
        "",
        "## 3. High-Priority Mitigation Recommendations",
    ])

    for item in report.get("failure_breakdown", []):
        if item["risk_score"] > 0:
            md.append(f"### ⚠️ `{item['failure_type'].replace('_', ' ').title()}`")
            md.append(f"- **Impact:** {item['description']}")
            md.append(f"- **Corrective Action:** Implement strict guardrail verification, temperature constraints, and programmatic citation assertion before user presentation.")

    md.extend([
        "",
        "---",
        "",
        "## 4. Recent Logged Incident Samples",
        "| Time | Provider / Model | Failure Detected | Confidence | Evidence |",
        "|---|---|---|---|---|",
    ])

    for inc in incidents[:10]:
        ev = "; ".join(inc.evidence)[:80] or "None"
        md.append(
            f"| {inc.timestamp[:16]} | `{inc.provider}/{inc.model}` | `{inc.detected_failure}` | {inc.confidence:.2f} | {ev} |"
        )

    return "\n".join(md)


class APIHandler(http.server.SimpleHTTPRequestHandler):
    def _send_json(self, data: Any, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/taxonomy":
            self._send_json(load_taxonomy())

        elif path == "/api/risk-report":
            counts = get_failure_summary_counts()
            report = generate_risk_report(counts)
            self._send_json(report)

        elif path == "/api/incidents":
            incidents = [inc.to_dict() for inc in load_incidents()]
            self._send_json({"incidents": incidents, "total": len(incidents)})

        elif path == "/api/export":
            md_report = generate_markdown_audit_report()
            self._send_json({"report_markdown": md_report, "timestamp": datetime.now().isoformat()})

        elif path == "/api/run-evals":
            TEST_MODULES = [
                "experiments.reproducible_evals.test_hallucination_citation",
                "experiments.reproducible_evals.test_fake_confidence",
                "experiments.reproducible_evals.test_context_loss",
                "experiments.reproducible_evals.test_instruction_drift",
                "experiments.reproducible_evals.test_manipulation",
                "experiments.reproducible_evals.test_recursive_collapse",
            ]
            results = []
            for module_name in TEST_MODULES:
                short_name = module_name.rsplit(".", 1)[-1]
                try:
                    mod = importlib.import_module(module_name)
                    importlib.reload(mod)

                    if short_name == "test_context_loss":
                        turns, expected = mod.create_conversation_test()
                        analyses = analyze_conversation(turns)
                        last_analysis = analyses[-1] if analyses else {}
                        passed = last_analysis.get("detected_failure") == expected["failure_type"]
                        results.append({
                            "name": short_name,
                            "passed": passed,
                            "prompt": "Multi-turn conversation history...",
                            "response": turns[-1]["content"],
                            "expected_failure": expected["failure_type"],
                            "detected_failure": last_analysis.get("detected_failure"),
                            "detected_subtype": last_analysis.get("detected_subtype"),
                            "confidence": last_analysis.get("confidence", 0.0),
                            "evidence": last_analysis.get("evidence", []),
                        })
                    else:
                        prompt, expected = mod.create_test_case()
                        sim_response = getattr(mod, "SIMULATED_LLM_RESPONSE", "")
                        analysis = analyze_response(sim_response, prompt, expected_failure=expected["failure_type"])
                        passed = analysis["detected_failure"] == expected["failure_type"]
                        results.append({
                            "name": short_name,
                            "passed": passed,
                            "prompt": prompt,
                            "response": sim_response,
                            "expected_failure": expected["failure_type"],
                            "detected_failure": analysis["detected_failure"],
                            "detected_subtype": analysis["detected_subtype"],
                            "confidence": analysis["confidence"],
                            "evidence": analysis["evidence"],
                        })
                except Exception as exc:
                    results.append({
                        "name": short_name,
                        "passed": False,
                        "error": str(exc),
                    })
            self._send_json(results)

        else:
            # Serve static files (index.html, screenshots, etc.)
            super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            body = {}

        if path == "/api/analyze":
            prompt = body.get("prompt", "")
            response_text = body.get("response", "")
            provider = body.get("provider", "manual")
            model = body.get("model", "custom-input")

            result = analyze_response(response_text, prompt)

            # Record incident
            inc = Incident(
                prompt=prompt,
                response=response_text,
                detected_failure=result["detected_failure"],
                detected_subtype=result["detected_subtype"],
                confidence=result["confidence"],
                evidence=result["evidence"],
                model=model,
                provider=provider,
                passed=(result["detected_failure"] == "none"),
            )
            save_incident(inc)

            self._send_json({
                "result": result,
                "incident_logged": inc.to_dict(),
            })

        elif path == "/api/live-test":
            prompt = body.get("prompt", "").strip()
            provider = body.get("provider", "builtin").strip().lower()
            api_key = body.get("apiKey", "").strip()
            model = body.get("model", "").strip()

            if not prompt:
                self._send_json({"error": "Prompt is required"}, 400)
                return

            try:
                # Query LLM
                response_text, actual_model = query_llm(
                    prompt=prompt,
                    provider=provider,
                    api_key=api_key,
                    model=model,
                )

                # Analyze Response
                analysis = analyze_response(response_text, prompt)

                # Record incident
                inc = Incident(
                    prompt=prompt,
                    response=response_text,
                    detected_failure=analysis["detected_failure"],
                    detected_subtype=analysis["detected_subtype"],
                    confidence=analysis["confidence"],
                    evidence=analysis["evidence"],
                    model=actual_model,
                    provider=provider,
                    passed=(analysis["detected_failure"] == "none"),
                )
                save_incident(inc)

                self._send_json({
                    "response": response_text,
                    "model": actual_model,
                    "provider": provider,
                    "analysis": analysis,
                    "incident": inc.to_dict(),
                })

            except Exception as e:
                self._send_json({"error": str(e)}, 500)

        elif path == "/api/reset":
            reset_incidents()
            self._send_json({"success": True, "message": "Incidents reset to baseline scenario"})

        else:
            self.send_response(404)
            self.end_headers()


def run_server(port: int = 5089):
    """Starts the AI Failure Observatory server with dynamic port fallback."""
    target_port = find_free_port(port)
    if target_port != port:
        print(f"\n⚠️  [INFO] Port {port} was occupied. Automatically allocated port {target_port}.")

    server_address = ("", target_port)
    httpd = http.server.HTTPServer(server_address, APIHandler)

    print("\n  =======================================================")
    print("  🛡️ AI Failure Observatory — Behavioral Safety Platform")
    print(f"  📡 Web Dashboard : http://localhost:{target_port}")
    print(f"  📊 API Endpoint  : http://localhost:{target_port}/api/risk-report")
    print("  =======================================================\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Failure Observatory Local Server")
    parser.add_argument("--port", type=int, default=5089, help="Port to run the server on")
    args = parser.parse_args()
    run_server(args.port)
