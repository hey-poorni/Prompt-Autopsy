import os
import sys
from pathlib import Path
from collections import Counter

# Add project root to sys.path
_repo_root = Path(__file__).parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import google.generativeai as genai # type: ignore


def rank_issues(evaluation_results: list[dict]) -> list[tuple[str, int]]:
    """
    Counts and ranks the most common issues across all evaluation results.

    Args:
        evaluation_results: List of dicts, each with an 'issues' key.

    Returns:
        A list of (issue, count) tuples sorted by frequency (descending).
    """
    all_issues: list[str] = []
    for result in evaluation_results:
        issues = result.get("issues", [])
        all_issues.extend(issues)
    return Counter(all_issues).most_common()


def generate_improvement_suggestions(
    system_prompt: str,
    ranked_issues: list[tuple[str, int]],
    api_key: str | None = None
) -> str:
    """
    Uses Gemini LLM to suggest improvements to the system prompt based on detected issues.

    Args:
        system_prompt: The current system prompt text.
        ranked_issues: List of (issue, count) tuples ranked by frequency.
        api_key: Optional Google API key. Falls back to env var or .env file.

    Returns:
        A markdown-formatted string with structured improvement suggestions.
    """
    # Resolve API key
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        env_path = _repo_root / ".env"
        if env_path.exists():
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("GOOGLE_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break

    if not api_key:
        return "ERROR: GOOGLE_API_KEY not found. Cannot generate suggestions."

    genai.configure(api_key=api_key)

    # Dynamically pick best available model
    available_models = [
        m.name for m in genai.list_models()
        if 'generateContent' in m.supported_generation_methods
    ]
    preference = [
        'models/gemini-1.5-flash',
        'models/gemini-1.5-flash-latest',
        'models/gemini-2.0-flash',
        'models/gemini-2.0-flash-001',
        'models/gemini-flash-latest'
    ]
    target_model = next((m for m in preference if m in available_models), None)
    if not target_model:
        flash_models = [m for m in available_models if 'flash' in m]
        target_model = flash_models[0] if flash_models else 'models/gemini-pro'

    # Format the issues for the prompt
    issues_summary = "\n".join(
        f"- {issue} (detected {count} time{'s' if count > 1 else ''})"
        for issue, count in ranked_issues
    )

    meta_prompt = f"""You are an expert in designing AI voice agent system prompts for debt collection calls.

Below is the CURRENT SYSTEM PROMPT used by the AI agent:

---
{system_prompt}
---

After evaluating multiple call transcripts, the following issues were detected in agent behavior (ranked by frequency):

{issues_summary}

Based on these issues, suggest specific, actionable improvements to the system prompt.

Format your response as a structured markdown document with:
1. A brief summary of the key problems found
2. A numbered list of specific improvements to add or change in the system prompt
3. For each improvement, write the exact instruction text that should be added to the prompt

Be concise, practical, and specific. Focus on the most frequent issues first.
"""

    model = genai.GenerativeModel(target_model)
    response = model.generate_content(meta_prompt)
    return response.text.strip()


def build_improvements_report(
    system_prompt: str,
    evaluation_results: list[dict]
) -> tuple[str, list[tuple[str, int]]]:
    """
    Full pipeline: ranks issues and generates LLM-based improvements.

    Returns:
        (markdown_report_text, ranked_issues)
    """
    ranked_issues = rank_issues(evaluation_results)

    if not ranked_issues:
        no_issues_msg = "# Prompt Improvement Suggestions\n\nNo issues detected across all evaluated transcripts. The prompt appears to be performing well!"
        return no_issues_msg, ranked_issues

    suggestions = generate_improvement_suggestions(system_prompt, ranked_issues)

    report = f"""# Prompt Improvement Suggestions

## Most Common Issues Detected

| Issue | Frequency |
|-------|-----------|
"""
    for issue, count in ranked_issues:
        report += f"| {issue} | {count} |\n"

    report += f"""
---

## LLM-Generated Improvement Suggestions

{suggestions}
"""
    return report, ranked_issues
