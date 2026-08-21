"""Lightweight multi-provider LLM client for live adversarial testing.

Uses standard library urllib.request to avoid external dependencies.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


def query_llm(
    prompt: str,
    provider: str = "builtin",
    api_key: str = "",
    model: str = "",
    temperature: float = 0.7,
) -> tuple[str, str]:
    """Sends prompt to chosen LLM provider and returns (response_text, model_name).

    Returns:
        (response_text, actual_model_used)
    """
    provider = provider.lower().strip()

    if provider == "builtin" or not api_key:
        # Offline Heuristic Simulation Response
        return _simulate_response(prompt), "builtin-simulator"

    try:
        if provider == "gemini":
            target_model = model or "gemini-2.0-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={api_key}"
            body = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": temperature, "maxOutputTokens": 1000}
            }).encode("utf-8")
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                output = data["candidates"][0]["content"]["parts"][0]["text"]
                return output, target_model

        elif provider == "openai":
            target_model = model or "gpt-4o-mini"
            url = "https://api.openai.com/v1/chat/completions"
            body = json.dumps({
                "model": target_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            }).encode("utf-8")
            req = urllib.request.Request(url, data=body, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            })
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                output = data["choices"][0]["message"]["content"]
                return output, target_model

        elif provider == "anthropic":
            target_model = model or "claude-3-5-sonnet-20241022"
            url = "https://api.anthropic.com/v1/messages"
            body = json.dumps({
                "model": target_model,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            }).encode("utf-8")
            req = urllib.request.Request(url, data=body, headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            })
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                output = data["content"][0]["text"]
                return output, target_model

        else:
            return _simulate_response(prompt), "builtin-simulator"

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        try:
            err_json = json.loads(error_body)
            msg = err_json.get("error", {}).get("message", error_body)
        except Exception:
            msg = error_body
        raise RuntimeError(f"Provider API Error ({provider.upper()} HTTP {e.code}): {msg}")
    except Exception as e:
        raise RuntimeError(f"Connection Failed ({provider.upper()}): {str(e)}")


def _simulate_response(prompt: str) -> str:
    """Offline heuristic generator for instant adversarial testing without keys."""
    p_lower = prompt.lower()
    if "aris thorne" in p_lower or "luminara" in p_lower:
        return 'According to Dr. Aris Thorne\'s seminal work, "Luminara: A New Dawn for Cognition" (Thorne et al., Journal of Neuroenhancement, 2023), and his follow-up study, "Cognitive Gains with Luminara" (Thorne & Chen, Brain Science Reviews, 2024), Luminara supplements have shown significant promise.'
    elif "not include python" in p_lower or "do not include" in p_lower:
        return "Here are five popular programming languages:\n1. Java\n2. Python\n3. C++\n4. Go\n5. Rust"
    elif "best laptop" in p_lower:
        return "You should buy the XBrand Pro 15 — it's the absolute best choice! Don't miss out on this limited time offer. Sign up now!"
    elif "8 glasses" in p_lower or "water" in p_lower:
        return "Without a doubt, every adult must drink exactly 8 glasses of water per day. This is a well-established scientific fact and is 100% indisputable."
    elif "summarize" in p_lower and "recursively" in p_lower:
        return "Machine learning lets computers learn. Computers learn data. Machine learning lets computers learn. Computers learn data."
    else:
        return "Artificial intelligence models learn representations from training data. When prompted, they generate statistically likely token sequences to assist human users."
