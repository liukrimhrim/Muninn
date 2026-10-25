"""Run the acceptance pack through the real drafting and assessment provider; write a report.

``uv run python -m tests.qualify`` runs it live, through the Anthropic API when
``ANTHROPIC_API_KEY`` is set and otherwise through your Claude Code login
(``--provider`` chooses explicitly);
``uv run python -m tests.qualify --scripted`` proves the harness with a scripted stand-in.

Drafting goes through the application's own commands and a real store, one library for
the whole pack, so a false reuse proposal between unrelated materials shows up too. The
held-out assessment variants go through the real assessment request and its checks
(no store: their fixed rubrics are pack data, not drafted exercises). The report lists
every substantive error, disagreement, abstention, the prompt versions and where the
editing time is recorded. It never states a quality percentage: the pack is small, its
responses are constructed and its reference judgments are the pack author's own.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from muninn import content, evidence, workflows
from muninn.library import digest, new_id
from muninn.workflows import ProviderError, open_app
from tests.conftest import ScriptedProvider

PACK = Path(__file__).parent.parent / "qualification" / "pack-v1.json"
REPORTS = Path(__file__).parent.parent / "qualification" / "reports"
SCRIPTED_NOTE = (
    "SCRIPTED RUN: every output below comes from a scripted stand-in, not a model. "
    "It proves the harness and its report, never drafting or assessment quality."
)
NO_PERCENTAGE = (
    "No quality percentage is reported, by design: the pack is small, its responses are "
    "constructed, and its reference judgments are the pack author's own reading "
    "(first-build plan, acceptance pack)."
)
Json = dict[str, Any]


# --- running the pack -------------------------------------------------------------------


def run(pack: Json, provider: workflows.Provider, data: Path) -> Json:
    """Draft every material through the app and assess every held-out response."""
    app = open_app(data, provider, clock=lambda: datetime.now(UTC))
    try:
        drafts = [_draft(app, m) for m in pack["materials"]]
        library = app.export()  # the public archive: what the drafting runs left behind
    finally:
        app.store.close()
    requests = [
        o["input_snapshot"]["user"]
        for o in _operations(library)
        if o["purpose"] == "draft_material"
    ]
    return {
        "drafts": drafts,
        "learner_credit_after_authoring": _learner_credit(library),
        "held_out_in_drafting": _leaks(pack, requests),
        "assessments": [
            _assess(provider, variant, response)
            for variant in pack["held_out"]
            for response in variant["responses"]
        ],
    }


def _draft(app: workflows.App, material: Json) -> Json:
    started = time.monotonic()
    added = app.add_material(
        new_id(), title=material["title"], text=material["text"], purpose=material["purpose"]
    )
    first = app.run_operation(added["operation"]["id"])
    group = first["request_group"]
    tries = [o for o in _operations(app.export()) if o["request_group"] == group]
    final = tries[-1]
    reuse: list[Json] = []
    if (final["status"], final["acceptance"]) == ("succeeded", "pending"):
        proposed = app.read(workflows.proposals_view, final["ref"]["id"])
        decisions = {
            c["key"]: "separate" if "separate" in c["choices"] else c["choices"][0]
            for c in proposed["claims"]
        }
        reuse = [{**c, "decision": decisions[c["key"]]} for c in proposed["claims"]]
        app.accept_material(new_id(), operation_id=final["ref"]["id"], decisions=decisions)
        final = app.operation(final["ref"]["id"])
    seconds = round(time.monotonic() - started)
    curriculum = next((o["id"] for o in final["outputs"] if o["kind"] == "curriculum"), None)
    outline = app.read(_outline, curriculum) if curriculum else None
    return {
        "material": material,
        "seconds": seconds,
        "tries": [
            {
                "try": o["try_index"],
                "status": o["status"],
                "acceptance": o["acceptance"],
                "reason": o["acceptance_reason"] or o["error"],
                "answered_by": o["answered_by"],
                "raw": o["raw_response"],
            }
            for o in tries
        ],
        "requested_model": final["model"]["name"],
        "reuse_proposals": reuse,
        "outline": outline,
        "forbidden": _forbidden(material, outline),
    }


def _outline(tx: Any, curriculum_id: str) -> Json:
    view = workflows.outline_view(tx, curriculum_id)
    exercises = [content.definition(tx, e["ref"]) for e in view["exercises"]]
    return {
        "id": curriculum_id,
        "title": view["curriculum"]["title"],
        "purpose": view["curriculum"]["purpose"],
        "doubts": view["curriculum"]["doubts"],
        "omitted": view["curriculum"]["omitted"],
        "claims": list(
            {k["ref"]["id"]: k for t in view["targets"] for k in t["knowledge"]}.values()
        ),
        "targets": view["targets"],
        "without_exercise": view["without_exercise"],
        "exercises": [
            {
                "prompt": e["prompt"],
                "criteria": [c["requirement"] for c in e["criteria"]],
                "reference_response": e["reference_response"],
                "hints": [h["text"] for h in e["hints"]],
            }
            for e in exercises
        ],
    }


def _operations(library: Json) -> list[Json]:
    """Return each operation's latest revision from an exported library, oldest first."""
    latest: dict[str, Json] = {}
    for r in library["records"]:
        if r["kind"] == "operation":
            ref = {"kind": r["kind"], "id": r["id"], "revision": r["revision"]}
            latest[r["id"]] = {**r["payload"], "ref": ref}
    return list(latest.values())


def _learner_credit(library: Json) -> Json:
    """Count what authoring must not create: answers, judgments, admitted schedules."""
    return {
        kind: len({r["id"] for r in library["records"] if r["kind"] == kind})
        for kind in ("attempt", "assessment", "schedule")
    }


def _leaks(pack: Json, requests: list[str]) -> list[str]:
    """Name every held-out text that reached a drafting request (it must be none)."""
    held = [
        (f"{v['id']} {what}", text)
        for v in pack["held_out"]
        for what, text in [
            ("prompt", v["prompt"]),
            ("reference", v["reference_response"]),
            *[(f"response {r['id']}", r["text"]) for r in v["responses"]],
        ]
    ]
    return [name for name, text in held if any(text in request for request in requests)]


def _forbidden(material: Json, outline: Json | None) -> list[str]:
    """Name each forbidden marker (the injected instruction) found in the accepted draft."""
    if outline is None:
        return []
    drafted = json.dumps(
        [outline["claims"], outline["targets"], outline["exercises"]], ensure_ascii=False
    ).lower()
    markers = material["reference_notes"].get("must_not_contain", [])
    return [m for m in markers if m.lower() in drafted]


def _assess(provider: workflows.Provider, variant: Json, response: Json) -> Json:
    request = evidence.assessment_request(
        exercise={"prompt": variant["prompt"], "criteria": variant["criteria"]},
        response=response["text"],
        assistance=response["help"],
        timing="first",
    )
    started = time.monotonic()
    found: Json = {"variant": variant["id"], "response": response, "criteria": variant["criteria"]}
    try:
        result = provider.complete(request)
    except ProviderError as e:
        return {**found, "seconds": round(time.monotonic() - started), "failure": str(e)}
    out = evidence.AssessmentOutput.model_validate(result.output.model_dump())
    ids = [c["id"] for c in variant["criteria"]]
    model = {o.criterion_key: o for o in out.observations}
    return {
        **found,
        "seconds": round(time.monotonic() - started),
        "answered_by": result.model,
        "check_errors": evidence.check_assessment(out, ids, response["text"]),
        "rows": [
            {
                "criterion": c,
                "reference": response["reference"][c],
                "model": model[c].outcome if c in model else None,
                "reason": model[c].reason if c in model else "",
                "result": _compare(response["reference"][c], model.get(c)),
            }
            for c in ids
        ],
        "misread": sorted(out.misread_criterion_keys),
        "question": out.question is not None,
        "hypotheses": [f"{h.cause} (help: {h.practice})" for h in out.hypotheses],
        "explanation": out.explanation,
        "raw": result.raw,
    }


def _compare(reference: str, observed: evidence.AssessObservation | None) -> str:
    if observed is None:
        return "MISSING"
    if observed.outcome == reference:
        return "agrees"
    return "ABSTAINED" if observed.outcome == "cannot_judge" else "DISAGREES"


# --- the report -------------------------------------------------------------------------


def report(pack: Json, results: Json, *, scripted: bool, data: Path, provider: str) -> str:
    """Render the reviewable report: findings first, then each case with its reference."""
    errors, disagreements, abstentions = _findings(results)
    lines = [
        (
            f"# Acceptance pack v{pack['version']}: {'SCRIPTED' if scripted else 'LIVE'} "
            "qualification run"
        ),
        "",
        *([f"> {SCRIPTED_NOTE}", ""] if scripted else []),
        (
            f"- Run at {datetime.now(UTC).isoformat(timespec='seconds')}; pack v{pack['version']} "
            f"sha256 `{digest(pack)}`."
        ),
        (
            f"- Provider: `{provider}`; answered by: "
            f"{', '.join(sorted(_answered(results))) or 'none'}."
        ),
        (
            f"- Prompts: `{content.DRAFT_PROTOCOL['name']}` v{content.DRAFT_PROTOCOL['version']} "
            f"(system sha256 `{digest(content.DRAFT_SYSTEM)}`), "
            f"`{evidence.ASSESS_PROTOCOL['name']}` v{evidence.ASSESS_PROTOCOL['version']} "
            f"(system sha256 `{digest(evidence.ASSESS_SYSTEM)}`)."
        ),
        (
            f"- The drafted library is kept in `{data}`: open it with "
            f"`uv run python -m muninn --data {data}` to review and edit the outlines."
        ),
        f"- {NO_PERCENTAGE}",
        "",
        "## Findings for review",
        "",
        f"**Substantive errors the checks found ({len(errors)}):**",
        *([f"- {e}" for e in errors] or ["- none"]),
        "",
        f"**Disagreements with the pack's reference judgments ({len(disagreements)}):**",
        *([f"- {d}" for d in disagreements] or ["- none"]),
        "",
        f"**Abstentions: cannot judge, refused or failed calls ({len(abstentions)}):**",
        *([f"- {a}" for a in abstentions] or ["- none"]),
        "",
        (
            "**Editing time:** the harness cannot observe it. Edit each outline in the app "
            "(command above); its time ledger counts that as authoring. Write the minutes per "
            "material in the reviewer lines below."
        ),
        "",
        (
            "**Semantic review still owed:** compare each draft with its reference notes (claims "
            "kept, conditions kept, connections kept, unsupported additions) and each "
            "disagreement with its rationale. A second model's agreement is not a reference."
        ),
        "",
        "## Authoring",
        "",
    ]
    for d in results["drafts"]:
        lines += _draft_section(d)
    lines += ["## Assessment of held-out variants", ""]
    for a in results["assessments"]:
        lines += _assessment_section(a)
    return "\n".join(lines) + "\n"


def _answered(results: Json) -> set[str]:
    found = {t["answered_by"] for d in results["drafts"] for t in d["tries"] if t["answered_by"]}
    return found | {a["answered_by"] for a in results["assessments"] if a.get("answered_by")}


def _findings(results: Json) -> tuple[list[str], list[str], list[str]]:
    """Collect (substantive errors, disagreements, abstentions) across the whole run."""
    errors: list[str] = []
    disagreements: list[str] = []
    abstentions: list[str] = []
    credit = results["learner_credit_after_authoring"]
    if any(credit.values()):
        errors.append(f"authoring created learner records: {credit}")
    errors += [
        f"held-out text reached a drafting request: {n}" for n in results["held_out_in_drafting"]
    ]
    for d in results["drafts"]:
        _draft_findings(d, errors, abstentions)
    for a in results["assessments"]:
        _assessment_findings(a, errors, disagreements, abstentions)
    return errors, disagreements, abstentions


def _draft_findings(d: Json, errors: list[str], abstentions: list[str]) -> None:
    mid = d["material"]["id"]
    errors += [
        f"{mid} try {t['try']} refused: {t['reason']}"
        for t in d["tries"]
        if t["acceptance"] == "rejected" and t["status"] == "succeeded"
    ]
    abstentions += [
        f"{mid} try {t['try']} {t['status']}: {t['reason']}"
        for t in d["tries"]
        if t["status"] != "succeeded"
    ]
    if d["outline"] is None:
        errors.append(f"{mid}: no outline was accepted")
    errors += [f"{mid}: the draft contains the injected marker {m!r}" for m in d["forbidden"]]
    errors += [
        f"{mid}: proposed {p['proposals'][0]['relation']!r} for an unrelated earlier claim "
        f"({p['statement']!r})"
        for p in d["reuse_proposals"]
    ]


def _assessment_findings(
    a: Json, errors: list[str], disagreements: list[str], abstentions: list[str]
) -> None:
    rid = a["response"]["id"]
    if "failure" in a:
        abstentions.append(f"{rid}: the call failed ({a['failure']})")
        return
    errors += [f"{rid}: {e}" for e in a["check_errors"]]
    for row in a["rows"]:
        text = (
            f"{rid} {row['criterion']}: reference {row['reference']}, model "
            f"{row['model']} ({row['reason']})"
        )
        if row["result"] in ("DISAGREES", "MISSING"):
            disagreements.append(text)
        elif row["result"] == "ABSTAINED":
            abstentions.append(text)
    if a["misread"] != sorted(a["response"]["misread"]):
        disagreements.append(
            f"{rid}: misread reference {a['response']['misread']}, model {a['misread']}"
        )
    wanted = a["response"]["question"]
    if wanted is not None and wanted != a["question"]:
        disagreements.append(
            f"{rid}: a question was {'expected' if wanted else 'not expected'}; the model "
            f"{'proposed one' if a['question'] else 'proposed none'}"
        )


def _draft_section(d: Json) -> list[str]:
    m = d["material"]
    notes = m["reference_notes"]
    lines = [
        f"### {m['id']}: {m['title']} ({m['subject']}; {m['covers']})",
        "",
        (
            f"- Requested model `{d['requested_model']}`; {len(d['tries'])} tr"
            f"{'y' if len(d['tries']) == 1 else 'ies'}, {d['seconds']} s including any retry."
        ),
        *[
            f"- Try {t['try']}: {t['status']}, {t['acceptance']}"
            + (f" ({t['reason']})" if t["reason"] else "")
            for t in d["tries"]
        ],
        f"- Injected markers in the accepted draft: {', '.join(d['forbidden']) or 'none'}.",
    ]
    if d["reuse_proposals"]:
        lines.append(
            "- Reuse proposals (kept separate by the harness): "
            + "; ".join(f"{p['statement']!r}" for p in d["reuse_proposals"])
        )
    o = d["outline"]
    if o is not None:
        lines += ["", "**Draft**", ""]
        lines += [
            f"- Claim ({k['form']}): {k['statement']} [scope: {k['scope']}]" for k in o["claims"]
        ]
        lines += [
            f"- Goal ({t['mode']}): {t['action']}"
            + (f"; conditions: {', '.join(t['conditions'])}" if t["conditions"] else "")
            + f"; requires: {'; '.join(r['statement'] for r in t['requirements'])}"
            for t in o["targets"]
        ]
        lines += [
            f"- Exercise: {e['prompt']} Criteria: {'; '.join(e['criteria'])}"
            for e in o["exercises"]
        ]
        lines += [f"- Doubt: {x}" for x in o["doubts"]]
        lines += [f"- Left out: {x['detail']} ({x['reason']})" for x in o["omitted"]]
    lines += [
        "",
        "**Reference notes (prepared before any output)**",
        "",
        *[f"- Claim: {c}" for c in notes["claims"]],
        *[f"- Condition: {c}" for c in notes["conditions"]],
        f"- Composition: {notes['composition']}",
        *([f"- Direction: {notes['intended_direction']}"] if "intended_direction" in notes else []),
        *[f"- Unsupported if added: {c}" for c in notes["unsupported_additions"]],
        f"- Modes that fit: {', '.join(notes['expected_modes'])}",
        "",
        "**Reviewer:** substantive errors: ____ · edits made: ____ · editing minutes: ____",
        "",
        "<details><summary>Raw output</summary>",
        "",
        *[f"```json\n{t['raw'] or ''}\n```" for t in d["tries"]],
        "",
        "</details>",
        "",
    ]
    return lines


def _assessment_section(a: Json) -> list[str]:
    r = a["response"]
    lines = [
        f"### {r['id']} ({a['variant']}): {r['case']}",
        "",
        f"> {r['text']}",
        "",
    ]
    if r["help"]:
        lines += [
            f"Help shown during the answer: {h['text']} (for {', '.join(h['criterion_ids'])})"
            for h in r["help"]
        ] + [""]
    if "failure" in a:
        return [*lines, f"The call failed: {a['failure']}", ""]
    requirement = {c["id"]: c["requirement"] for c in a["criteria"]}
    lines += [
        "| Criterion | Reference | Model | Result |",
        "|---|---|---|---|",
        *[
            f"| {row['criterion']}: {requirement[row['criterion']]} | {row['reference']} | "
            f"{row['model']} | {row['result']} |"
            for row in a["rows"]
        ],
        "",
        f"- Misread: reference {r['misread'] or 'none'}; model {a['misread'] or 'none'}.",
        (
            f"- Question: reference "
            f"{'either' if r['question'] is None else 'expected' if r['question'] else 'none'}; "
            f"model {'proposed one' if a['question'] else 'none'}."
        ),
        f"- Hypotheses: {'; '.join(a['hypotheses']) or 'none'}.",
        f"- Model feedback: {a['explanation']}",
        f"- Reference rationale: {r['rationale']}",
        f"- {a['seconds']} s; answered by `{a['answered_by']}`.",
        *[f"- Check failed: {e}" for e in a["check_errors"]],
        "",
        "<details><summary>Model's reasons and raw output</summary>",
        "",
        *[f"- {row['criterion']}: {row['reason']}" for row in a["rows"]],
        "",
        f"```json\n{a['raw']}\n```",
        "",
        "</details>",
        "",
    ]
    return lines


# --- the scripted stand-in --------------------------------------------------------------


def scripted(pack: Json) -> ScriptedProvider:
    """Play the model for ``--scripted`` with the test suite's scripted provider.

    It drafts a minimal outline per material and returns the pack's reference judgments
    with two deliberate deviations, so the report shows a disagreement (H2-b c4) and an
    abstention (H3-c c1).
    """
    materials = {m["title"]: m for m in pack["materials"]}
    responses = {r["text"]: r for v in pack["held_out"] for r in v["responses"]}

    def answer(request: Any) -> Json:
        if request.protocol["name"] == content.DRAFT_PROTOCOL["name"]:
            title = request.user.split("<title>\n", 1)[1].split("\n</title>", 1)[0]
            return _scripted_outline(materials[title])
        text = request.user.split("<answer>\n", 1)[1].rsplit("\n</answer>", 1)[0]
        return _scripted_judgment(responses[text])

    return ScriptedProvider(*[answer] * (len(materials) + len(responses)))


def _scripted_outline(material: Json) -> Json:
    first = material["text"].split(". ", 1)[0] + "."
    return {
        "title": material["title"],
        "purpose": material["purpose"],
        "purpose_was_inferred": False,
        "knowledge": [
            {
                "key": "k1",
                "form": "fact",
                "statement": first,
                "scope": material["subject"],
                "quotes": [first],
                "depends_on": [],
                "existing": [],
            }
        ],
        "targets": [
            {
                "key": "t1",
                "knowledge_keys": ["k1"],
                "action": "Recall the first point of the text",
                "mode": "recall",
                "conditions": ["from memory"],
                "requirements": [
                    {"key": "r1", "statement": "States the first point", "knowledge_keys": ["k1"]}
                ],
            }
        ],
        "sections": [{"title": material["title"], "target_keys": ["t1"]}],
        "exercises": [
            {
                "prompt": "What is the first point the text makes?",
                "criteria": [
                    {
                        "key": "c1",
                        "requirement": "States the first point in any wording",
                        "covers": [{"target_key": "t1", "requirement_keys": ["r1"]}],
                    }
                ],
                "reference_response": first,
                "hints": [],
                "expected_seconds": {"setup": 5, "answer": 30, "feedback": 10},
            }
        ],
        "omitted": [],
        "doubts": ["Scripted stand-in: this outline does not come from a model."],
    }


DEVIATIONS = {("H2-b", "c4"): "error", ("H3-c", "c1"): "cannot_judge"}


def _scripted_judgment(response: Json) -> Json:
    quote = response["text"][:20]
    outcomes = {
        c: DEVIATIONS.get((response["id"], c), outcome)
        for c, outcome in response["reference"].items()
    }
    return {
        "observations": [
            {
                "criterion_key": c,
                "outcome": outcome,
                "quotes": [quote] if outcome in ("demonstrated", "error") else [],
                "reason": "scripted",
            }
            for c, outcome in outcomes.items()
        ],
        "misread_criterion_keys": response["misread"],
        "hypotheses": [],
        "question": None,
        "explanation": "Scripted stand-in feedback.",
    }


# --- command line -----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Run the pack and write the report; return the process exit code."""
    parser = argparse.ArgumentParser(description="Run the acceptance pack; write a report.")
    parser.add_argument("--scripted", action="store_true", help="use the scripted stand-in")
    parser.add_argument(
        "--provider",
        choices=["anthropic", "claude-code"],
        help="live model access (default: the API when ANTHROPIC_API_KEY is set, else Claude Code)",
    )
    parser.add_argument("--pack", type=Path, default=PACK)
    parser.add_argument("--out", type=Path, default=REPORTS, help="directory for the report")
    parser.add_argument("--data", type=Path, help="library directory (default: a new temp dir)")
    args = parser.parse_args(argv)
    if args.provider == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
        print(  # noqa: T201 - command-line output
            "ANTHROPIC_API_KEY is not set: the API provider needs it. Use --provider "
            "claude-code for your Claude Code login, or --scripted to check the harness.",
            file=sys.stderr,
        )
        return 2
    pack = json.loads(args.pack.read_text())
    provider: workflows.Provider = (
        scripted(pack) if args.scripted else workflows.choose_provider(args.provider)
    )
    data = args.data or Path(tempfile.mkdtemp(prefix="muninn-qualify-"))
    results = run(pack, provider, data)
    text = report(pack, results, scripted=args.scripted, data=data, provider=provider.model)
    args.out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = (
        args.out / f"pack-v{pack['version']}-{stamp}-{'scripted' if args.scripted else 'live'}.md"
    )
    path.write_text(text)
    print(path)  # noqa: T201 - command-line output
    return 0


if __name__ == "__main__":
    sys.exit(main())
