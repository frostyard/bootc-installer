"""Structural regression tests for repository quality and safety artifacts."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_level_three_quality_artifacts_exist():
    required = (
        "docs/metrics.md",
        "docs/review-rubric.md",
        "docs/quality.md",
        ".github/workflows/ci.yml",
        ".claude/settings.json",
        ".claude/session-summary.md",
    )

    missing = [path for path in required if not (ROOT / path).is_file()]
    assert not missing, f"missing ACMM quality artifacts: {missing}"


def test_claude_settings_mechanically_enforce_safety_boundaries():
    settings = json.loads((ROOT / ".claude/settings.json").read_text())
    permissions = settings["permissions"]

    assert permissions["disableBypassPermissionsMode"] == "disable"
    assert permissions["disableAutoMode"] == "disable"

    denied = set(permissions["deny"])
    assert "Bash(rm -rf *)" in denied
    assert "Bash(git reset --hard *)" in denied
    assert "Bash(git push --force*)" in denied
    assert "Bash(sudo fisherman *)" in denied
    assert "Read(./.env)" in denied

    approval_required = set(permissions["ask"])
    assert "Bash(git push *)" in approval_required
    assert "Bash(gh pr merge *)" in approval_required
    assert "Bash(sudo *)" in approval_required


def test_ci_workflow_keeps_supported_python_matrix():
    workflow = (ROOT / ".github/workflows/ci.yml").read_text()

    assert "matrix:" in workflow
    assert '"3.11"' in workflow
    assert '"3.12"' in workflow
    assert "ruff check bootc_installer tests" in workflow


def test_level_four_security_aware_artifacts_exist():
    required = (
        ".github/auto-qa-tuning.json",
        ".github/workflows/ai-fix.yml",
        ".github/workflows/triage.yml",
        "docs/risk-tiers.md",
        "docs/security/SECURITY-AI.md",
        "docs/reflections/README.md",
    )

    missing = [path for path in required if not (ROOT / path).is_file()]
    assert not missing, f"missing ACMM security-aware artifacts: {missing}"


def test_auto_qa_tuning_cannot_relax_safety_gates():
    tuning = json.loads((ROOT / ".github/auto-qa-tuning.json").read_text())

    assert tuning["metrics"]["pythonCoverage"]["minimum"] >= 51
    assert tuning["metrics"]["pythonCoverage"]["decreaseAutomatically"] is False
    assert tuning["guardrails"]["requireHumanApproval"] is True
    assert tuning["guardrails"]["openProposalInsteadOfDirectChange"] is True
    assert tuning["guardrails"]["neverRelaxSafetyGates"] is True
    assert tuning["guardrails"]["installationPathRequiresE2E"] is True


def test_automation_uses_scoped_permissions_and_human_review():
    ai_fix = (ROOT / ".github/workflows/ai-fix.yml").read_text()
    triage = (ROOT / ".github/workflows/triage.yml").read_text()
    security_policy = (ROOT / "docs/security/SECURITY-AI.md").read_text()
    normalized_policy = " ".join(security_policy.lower().split())

    assert "contents: read" in ai_fix
    assert "issues: write" in ai_fix
    assert "pull-requests: write" not in ai_fix
    assert "human review" in ai_fix
    assert "contents: read" in triage
    assert "issues: write" in triage
    assert "pull requests" in normalized_policy
    assert "complete installation" in normalized_policy
