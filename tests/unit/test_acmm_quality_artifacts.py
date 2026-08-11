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
