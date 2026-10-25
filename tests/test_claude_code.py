"""The Claude Code provider, run against a stand-in ``claude`` executable."""

import json
import stat
import sys
import textwrap
from pathlib import Path

import pytest

from muninn import evidence
from muninn.workflows import ClaudeCodeProvider, ProviderError, choose_provider
from tests.drafts import assessment

GRADED = assessment({"c1": "not_shown"})


def stand_in(tmp_path, *, result=None, stdout=None, sleep=0):
    """Write a fake ``claude`` that records its call and prints a canned result."""
    record = tmp_path / "call.json"
    printed = stdout if stdout is not None else json.dumps(result)
    script = tmp_path / "claude"
    script.write_text(
        textwrap.dedent(
            f"""\
            #!{sys.executable}
            import json, os, sys, time
            json.dump(
                {{"argv": sys.argv[1:], "stdin": sys.stdin.read(), "cwd": os.getcwd(),
                  "env": sorted(os.environ)}},
                open({str(record)!r}, "w"),
            )
            time.sleep({sleep})
            sys.stdout.write({printed!r})
            """
        )
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return script, record


def ok(structured, model="claude-opus-5-5"):
    return {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "result": "",
        "structured_output": structured,
        "modelUsage": {model: {"outputTokens": 10}},
    }


def request():
    exercise = {
        "prompt": "Why?",
        "criteria": [{"id": "c1", "requirement": "Says why"}],
        "targets": [],
    }
    return evidence.assessment_request(
        exercise=exercise, response="Because.", assistance=[], timing="first"
    )


def test_a_structured_result_is_validated_and_attributed_to_the_model_that_answered(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "must-not-reach-claude")
    monkeypatch.setenv("CLAUDECODE", "1")
    script, record = stand_in(tmp_path, result=ok(GRADED, model="claude-opus-5-5"))
    result = ClaudeCodeProvider(executable=str(script)).complete(request())
    assert isinstance(result.output, evidence.AssessmentOutput)
    assert result.model == "claude-opus-5-5"
    assert json.loads(result.raw) == GRADED
    call = json.loads(record.read_text())
    assert call["stdin"] == request().user  # learner text goes in as data on stdin
    # isolated from the user's own Claude Code setup and credentials
    assert "ANTHROPIC_API_KEY" not in call["env"]
    assert not any(name.startswith("CLAUDE") for name in call["env"])
    assert Path(call["cwd"]).resolve() != Path.cwd().resolve()
    argv = call["argv"]
    for flag in (
        "--tools",
        "--setting-sources",
        "--strict-mcp-config",
        "--disable-slash-commands",
        "--no-session-persistence",
    ):
        assert flag in argv
    assert argv[argv.index("--system-prompt") + 1] == request().system
    assert argv[argv.index("--model") + 1] == "claude-opus-5-5"
    schema = json.loads(argv[argv.index("--json-schema") + 1])
    assert "observations" in schema["properties"]


def test_an_expired_login_is_unavailable_with_a_sign_in_hint(tmp_path):
    failed = {
        "type": "result",
        "subtype": "success",
        "is_error": True,
        "result": "Failed to authenticate: OAuth session expired and could not be refreshed",
    }
    script, _ = stand_in(tmp_path, result=failed)
    with pytest.raises(ProviderError) as e:
        ClaudeCodeProvider(executable=str(script)).complete(request())
    assert e.value.kind == "unavailable"
    assert "claude" in e.value.detail
    assert "/login" in e.value.detail


@pytest.mark.parametrize(
    "result",
    [
        ok(None),
        ok({"observations": "not a list"}),
        {"type": "result", "is_error": False, "result": "plain text"},
    ],
    ids=["no-structured-output", "schema-mismatch", "text-only"],
)
def test_output_that_does_not_fit_the_schema_is_malformed(tmp_path, result):
    script, _ = stand_in(tmp_path, result=result)
    with pytest.raises(ProviderError) as e:
        ClaudeCodeProvider(executable=str(script)).complete(request())
    assert e.value.kind == "malformed"


def test_unreadable_output_and_a_missing_cli_are_unavailable(tmp_path):
    script, _ = stand_in(tmp_path, stdout="crashed before printing json")
    with pytest.raises(ProviderError) as e:
        ClaudeCodeProvider(executable=str(script)).complete(request())
    assert e.value.kind == "unavailable"
    with pytest.raises(ProviderError) as e:
        ClaudeCodeProvider(executable=str(tmp_path / "no-such-claude")).complete(request())
    assert e.value.kind == "unavailable"


def test_a_slow_call_times_out(tmp_path):
    script, _ = stand_in(tmp_path, result=ok(GRADED), sleep=5)
    with pytest.raises(ProviderError) as e:
        ClaudeCodeProvider(executable=str(script), timeout_s=1).complete(request())
    assert e.value.kind == "timeout"


def test_the_provider_follows_the_setting_or_the_available_credential(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert isinstance(choose_provider(None), ClaudeCodeProvider)
    assert isinstance(choose_provider("claude-code"), ClaudeCodeProvider)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    assert not isinstance(choose_provider(None), ClaudeCodeProvider)
    with pytest.raises(ValueError, match="unknown provider"):
        choose_provider("openai")
