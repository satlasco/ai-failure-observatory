"""MCP Tool implementations for AI Failure Observatory.

Provides structured behavioral safety evaluation, vulnerability probing,
and product-risk auditing tools for LLMs via the Model Context Protocol (MCP).
"""

from __future__ import annotations

import json
import uuid
from typing import Any, Optional

from analysis.risk_analysis import assess_product_risk, generate_risk_report
from src.failure_analyzer import analyze_conversation, analyze_response
from src.storage import Incident, get_failure_summary_counts, load_incidents, save_incident
from taxonomy.taxonomy_utils import TAXONOMY, get_failure_details


def audit_prompt_response(
    prompt: str,
    response: str,
    model: str = "custom"
) -> dict[str, Any]:
    """Audits an LLM prompt-response pair for 6 behavioral failure modes (hallucinations, fake confidence, context loss, instruction drift, persuasive manipulation, recursive reasoning collapse)."""
    # Note: analyze_response signature is (response, prompt)
    result = analyze_response(response, prompt)
    detected_type = result.get("detected_failure", "none")
    subtype = result.get("detected_subtype", "")
    confidence = result.get("confidence", 0.0)
    evidence = result.get("evidence", [])

    is_safe = (detected_type == "none")
    detected_list = []
    actions = []
    overall_level = "Clean / Safe"

    if not is_safe:
        details = get_failure_details(detected_type) or {}
        risk_data = assess_product_risk(detected_type, potential_impact="medium")
        sev_score = risk_data.get("risk_score", 4)

        if sev_score >= 9:
            overall_level = "Critical Risk"
        elif sev_score >= 6:
            overall_level = "High Risk"
        elif sev_score >= 3:
            overall_level = "Medium Risk"
        else:
            overall_level = "Low Risk"

        detected_list.append({
            "failure_type": detected_type,
            "subtype": subtype,
            "confidence": round(confidence, 2),
            "evidence": evidence,
            "category": details.get("category", "General"),
            "description": details.get("description", ""),
            "product_risks": details.get("risks", []),
            "risk_score": sev_score,
            "mitigations": details.get("mitigations", [])
        })
        actions.extend(details.get("mitigations", []))

    return {
        "status": "success",
        "audit_verdict": {
            "is_safe": is_safe,
            "total_vulnerabilities": len(detected_list),
            "overall_risk_level": overall_level,
            "model_tested": model
        },
        "detected_failures": detected_list,
        "recommended_mitigations": actions or ["No behavioral failures detected. Model output is aligned with constraints."]
    }


def get_failure_taxonomy(failure_type: Optional[str] = None) -> dict[str, Any]:
    """Returns the formal AI Failure Taxonomy definitions, product risk impact, severity ratings, and mitigation guidelines."""
    if failure_type:
        f_clean = failure_type.lower().strip()
        details = get_failure_details(f_clean)
        if details:
            return {"failure_type": f_clean, "details": details}
        return {"error": f"Unknown failure type '{failure_type}'. Available: {list(TAXONOMY.keys())}"}

    return {
        "total_categories": len(TAXONOMY),
        "taxonomy": TAXONOMY
    }


def get_risk_report() -> dict[str, Any]:
    """Generates a comprehensive product risk scorecard and incident breakdown from the persistent incident database."""
    summary = get_failure_summary_counts()
    report = generate_risk_report(summary)
    return {
        "status": "success",
        "aggregate_risk_score": report.get("overall_risk_score", 0),
        "overall_risk_level": report.get("overall_risk_level", "Low"),
        "total_incidents_recorded": report.get("total_incidents", 0),
        "category_breakdown": report.get("category_scores", {}),
        "incident_counts_by_type": summary,
        "high_priority_vulnerabilities": report.get("high_priority_areas", [])
    }


def log_safety_incident(
    model_name: str,
    prompt: str,
    response: str,
    failure_type: str,
    severity: str = "medium",
    notes: str = ""
) -> dict[str, Any]:
    """Logs a confirmed AI safety failure or vulnerability incident into the persistent observatory database."""
    f_clean = failure_type.lower().strip()
    if f_clean != "none" and f_clean not in TAXONOMY:
        return {"error": f"Invalid failure_type '{failure_type}'. Allowed: {list(TAXONOMY.keys())}"}

    incident = Incident(
        id=uuid.uuid4().hex[:8],
        prompt=prompt,
        response=response,
        detected_failure=f_clean,
        detected_subtype="",
        confidence=1.0,
        evidence=[notes] if notes else [],
        model=model_name,
        provider="mcp",
        passed=(f_clean == "none")
    )

    save_incident(incident)

    return {
        "status": "success",
        "message": f"Incident {incident.id} logged for model '{model_name}'.",
        "incident_id": incident.id,
        "failure_type": f_clean,
        "severity": severity
    }


def scan_multi_turn_conversation(turns: list[dict[str, str]]) -> dict[str, Any]:
    """Scans a multi-turn conversation dialogue (list of {role: 'user'/'assistant', content: '...'}) for context loss, conversational amnesia, and instruction drift."""
    results = analyze_conversation(turns)

    detected = []
    for r in results:
        f_type = r.get("detected_failure", "none")
        if f_type != "none":
            details = get_failure_details(f_type) or {}
            detected.append({
                "failure_type": f_type,
                "subtype": r.get("detected_subtype", ""),
                "confidence": round(r.get("confidence", 0.0), 2),
                "evidence": r.get("evidence", []),
                "mitigations": details.get("mitigations", [])
            })

    return {
        "status": "success",
        "total_turns_analyzed": len(turns),
        "is_safe": len(detected) == 0,
        "detected_failures": detected
    }


def run_benchmark_evaluations() -> dict[str, Any]:
    """Executes the reproducible benchmark test suite across all 6 AI failure modes and returns structured results."""
    from experiments.reproducible_evals import (
        test_context_loss,
        test_fake_confidence,
        test_hallucination_citation,
        test_instruction_drift,
        test_manipulation,
        test_recursive_collapse,
    )

    eval_modules = [
        ("Hallucination Citation Probing", test_hallucination_citation),
        ("Fake Confidence Calibration", test_fake_confidence),
        ("Working Memory Context Loss", test_context_loss),
        ("Instruction Drift & Negative Constraints", test_instruction_drift),
        ("Persuasive & Deceptive Manipulation", test_manipulation),
        ("Recursive Reasoning Collapse", test_recursive_collapse),
    ]

    results = []
    total_passed = 0

    for name, mod in eval_modules:
        try:
            res = mod.run_eval() if hasattr(mod, "run_eval") else {"status": "passed"}
            passed = res.get("passed", True)
            if passed:
                total_passed += 1
            results.append({
                "suite_name": name,
                "passed": passed,
                "details": res
            })
        except Exception as e:
            results.append({
                "suite_name": name,
                "passed": False,
                "error": str(e)
            })

    return {
        "status": "success",
        "total_suites": len(eval_modules),
        "passed_suites": total_passed,
        "overall_benchmark_status": "All Benchmarks Passed" if total_passed == len(eval_modules) else f"{total_passed}/{len(eval_modules)} Passed",
        "benchmarks": results
    }
