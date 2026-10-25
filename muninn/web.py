"""Web Interaction: present application state and collect the learner's intentions.

A JSON API over the application commands and page views, plus one static page. The
browser never decides whether an answer was independent or how much time counted;
it sends raw observations (text, hint displays, timer spans) and renders views.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from muninn import workflows
from muninn.workflows import AnthropicProvider, App, Conflict, open_app, restore_into

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from muninn.workflows import Provider

PROTOCOL = "1"
STATIC = Path(__file__).parent / "static"


class Cmd(BaseModel):
    """Every command carries the browser's request ID, reused on retry."""

    request_id: str


class Material(Cmd):
    """New text to learn from."""

    title: str
    text: str
    purpose: str | None = None


class OutlineEdit(Cmd):
    """An organization-only outline revision."""

    base: int
    title: str
    purpose: str
    sections: list[dict[str, Any]]


class Draft(Cmd):
    """Unfinished answer text."""

    base: int
    response: str


class HintAck(Cmd):
    """The browser displayed a hint."""

    base: int
    client_at: str | None = None


class Submission(Cmd):
    """The learner's answer."""

    base: int
    response: str
    client_at: str | None = None


class AtRevision(Cmd):
    """A command on a record at an expected revision."""

    base: int
    client_at: str | None = None


class Ending(Cmd):
    """Why a session ended."""

    base: int
    reason: str


class Ratings(Cmd):
    """Optional end-of-session ratings."""

    effort: str | None = None
    usefulness: str | None = None
    note: str | None = None


class TimerClaim(Cmd):
    """A browser document asking for the timer."""

    document_run_id: str
    takeover: bool = False


class Spans(Cmd):
    """Timer spans from the browser."""

    spans: list[dict[str, Any]]


class Archive(Cmd):
    """A library archive to restore."""

    archive: str


class GoalEdit(Cmd):
    """A changed goal: action, mode, conditions and requirement wording."""

    base: int
    action: str
    mode: str
    conditions: list[str]
    requirements: list[dict[str, Any]]
    reason: str


class Flag(Cmd):
    """Why a claim looks wrong."""

    base: int
    reason: str


class ClaimEdit(Cmd):
    """A settled or corrected claim."""

    base: int
    statement: str
    scope: str
    reason: str


class Decisions(Cmd):
    """The learner's reuse decisions per drafted claim."""

    decisions: dict[str, str]


class Dispute(Cmd):
    """Why a judgment looks wrong."""

    reason: str


class Acceptance(Cmd):
    """Accept a reviewed judgment exactly as its preview showed it."""

    preview: str | None = None


def create_app(  # noqa: C901, PLR0915 - one route table
    data_dir: Path,
    *,
    provider: Provider | None = None,
    clock: Callable[[], datetime] | None = None,
) -> FastAPI:
    """Build the web application over the active store in ``data_dir``."""
    tick = clock or (lambda: datetime.now(UTC))
    core: App = open_app(data_dir, provider or AnthropicProvider(), clock=tick)
    api = FastAPI(title="Muninn")
    api.state.core = core

    @api.middleware("http")
    async def require_protocol(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.method == "POST" and request.headers.get("x-muninn-protocol") != PROTOCOL:
            return JSONResponse(
                {"error": "This page is out of date. Refresh it; your text is kept."},
                status_code=409,
            )
        return await call_next(request)

    @api.exception_handler(Conflict)
    async def conflict(_: Request, e: Conflict) -> JSONResponse:
        return JSONResponse({"error": str(e)}, status_code=409)

    @api.exception_handler(LookupError)
    async def missing(_: Request, e: LookupError) -> JSONResponse:
        return JSONResponse({"error": str(e)}, status_code=404)

    @api.exception_handler(ValueError)
    async def refused(_: Request, e: ValueError) -> JSONResponse:
        return JSONResponse({"error": str(e)}, status_code=422)

    def read(view: Callable[..., Any], *args: Any) -> Any:  # noqa: ANN401
        return core.read(view, *args)

    @api.get("/api/home")
    def home() -> Any:  # noqa: ANN401
        return read(workflows.home_view)

    @api.get("/api/curricula/{curriculum_id}")
    def outline(curriculum_id: str) -> Any:  # noqa: ANN401
        return read(workflows.outline_view, curriculum_id)

    @api.get("/api/sessions/{session_id}")
    def practice(session_id: str) -> Any:  # noqa: ANN401
        return read(workflows.practice_view, session_id)

    @api.get("/api/sessions/{session_id}/summary")
    def summary(session_id: str) -> Any:  # noqa: ANN401
        return read(workflows.summary_view, session_id)

    @api.get("/api/attempts/{attempt_id}")
    def feedback(attempt_id: str) -> Any:  # noqa: ANN401
        return read(workflows.feedback_view, attempt_id)

    @api.get("/api/studies/{study_id}")
    def study(study_id: str) -> Any:  # noqa: ANN401
        return read(workflows.study_page_view, study_id)

    @api.get("/api/operations/{operation_id}")
    def operation(operation_id: str) -> Any:  # noqa: ANN401
        return core.operation(operation_id)

    @api.get("/api/operations/{operation_id}/proposals")
    def proposals(operation_id: str) -> Any:  # noqa: ANN401
        return read(workflows.proposals_view, operation_id)

    @api.get("/api/operations/{operation_id}/correction")
    def correction(operation_id: str) -> Any:  # noqa: ANN401
        return core.correction_preview(operation_id)

    @api.get("/api/targets/{target_id}/history")
    def target_history(target_id: str) -> Any:  # noqa: ANN401
        return read(workflows.target_history_view, target_id)

    @api.post("/api/materials")
    def add_material(body: Material, background: BackgroundTasks) -> Any:  # noqa: ANN401
        result = core.add_material(
            body.request_id, title=body.title, text=body.text, purpose=body.purpose
        )
        background.add_task(core.run_operation, result["operation"]["id"])
        return result

    @api.post("/api/operations/{operation_id}/retry")
    def retry(operation_id: str, body: Cmd, background: BackgroundTasks) -> Any:  # noqa: ANN401
        result = core.retry_operation(body.request_id, operation_id)
        background.add_task(core.run_operation, result["operation"]["id"])
        return result

    @api.post("/api/curricula/{curriculum_id}/edit")
    def edit(curriculum_id: str, body: OutlineEdit) -> Any:  # noqa: ANN401
        return core.edit_outline(
            body.request_id,
            curriculum_id=curriculum_id,
            base=body.base,
            title=body.title,
            purpose=body.purpose,
            sections=body.sections,
        )

    @api.post("/api/operations/{operation_id}/accept")
    def accept_material(operation_id: str, body: Decisions) -> Any:  # noqa: ANN401
        return core.accept_material(
            body.request_id, operation_id=operation_id, decisions=body.decisions
        )

    @api.post("/api/targets/{target_id}/revise")
    def revise_target(target_id: str, body: GoalEdit) -> Any:  # noqa: ANN401
        return core.revise_target(
            body.request_id,
            target_id=target_id,
            base=body.base,
            action=body.action,
            mode=body.mode,
            conditions=body.conditions,
            requirements=body.requirements,
            reason=body.reason,
        )

    @api.post("/api/knowledge/{knowledge_id}/flag")
    def flag(knowledge_id: str, body: Flag) -> Any:  # noqa: ANN401
        return core.flag_material(
            body.request_id, knowledge_id=knowledge_id, base=body.base, reason=body.reason
        )

    @api.post("/api/knowledge/{knowledge_id}/revise")
    def revise_claim(knowledge_id: str, body: ClaimEdit) -> Any:  # noqa: ANN401
        return core.revise_material(
            body.request_id,
            knowledge_id=knowledge_id,
            base=body.base,
            statement=body.statement,
            scope=body.scope,
            reason=body.reason,
        )

    @api.post("/api/exercises/{exercise_id}/rebind")
    def rebind(exercise_id: str, body: AtRevision) -> Any:  # noqa: ANN401
        return core.rebind_exercise(body.request_id, exercise_id=exercise_id, base=body.base)

    @api.post("/api/attempts/{attempt_id}/dispute")
    def dispute(attempt_id: str, body: Dispute, background: BackgroundTasks) -> Any:  # noqa: ANN401
        result = core.dispute_judgment(body.request_id, attempt_id=attempt_id, reason=body.reason)
        background.add_task(core.run_operation, result["operation"]["id"])
        return result

    @api.post("/api/operations/{operation_id}/correction/accept")
    def accept_correction(operation_id: str, body: Acceptance) -> Any:  # noqa: ANN401
        return core.accept_correction(
            body.request_id, operation_id=operation_id, preview=body.preview
        )

    @api.post("/api/operations/{operation_id}/correction/keep")
    def keep(operation_id: str, body: Cmd) -> Any:  # noqa: ANN401
        return core.keep_judgment(body.request_id, operation_id=operation_id)

    @api.post("/api/curricula/{curriculum_id}/sessions")
    def start(curriculum_id: str, body: Cmd) -> Any:  # noqa: ANN401
        return core.start_session(body.request_id, curriculum_id=curriculum_id)

    @api.post("/api/sessions/{session_id}/next")
    def next_exercise(session_id: str, body: Cmd, background: BackgroundTasks) -> Any:  # noqa: ANN401
        result = core.next_exercise(body.request_id, session_id=session_id)
        if result["kind"] == "preparing" and result["operation"]["status"] == "pending":
            background.add_task(core.run_operation, result["operation"]["id"])
        return result

    @api.post("/api/studies/{study_id}/complete")
    def complete(study_id: str, body: AtRevision) -> Any:  # noqa: ANN401
        return core.complete_study(
            body.request_id, study_id=study_id, base=body.base, client_at=body.client_at
        )

    @api.post("/api/concerns/{concern_id}/pause")
    def pause(concern_id: str, body: AtRevision) -> Any:  # noqa: ANN401
        return core.pause_concern(body.request_id, concern_id=concern_id, base=body.base)

    @api.post("/api/sessions/{session_id}/end")
    def end(session_id: str, body: Ending) -> Any:  # noqa: ANN401
        return core.end_session(
            body.request_id, session_id=session_id, base=body.base, reason=body.reason
        )

    @api.post("/api/sessions/{session_id}/feedback")
    def rate(session_id: str, body: Ratings) -> Any:  # noqa: ANN401
        return core.session_feedback(
            body.request_id,
            session_id=session_id,
            effort=body.effort,
            usefulness=body.usefulness,
            note=body.note,
        )

    @api.post("/api/attempts/{attempt_id}/draft")
    def save_draft(attempt_id: str, body: Draft) -> Any:  # noqa: ANN401
        return core.save_draft(
            body.request_id, attempt_id=attempt_id, base=body.base, response=body.response
        )

    @api.post("/api/attempts/{attempt_id}/hints/{hint_id}/reveal")
    def reveal(attempt_id: str, hint_id: str, body: Cmd) -> Any:  # noqa: ANN401
        return core.reveal_hint(body.request_id, attempt_id=attempt_id, hint_id=hint_id)

    @api.post("/api/attempts/{attempt_id}/hints/{hint_id}/ack")
    def acknowledge(attempt_id: str, hint_id: str, body: HintAck) -> Any:  # noqa: ANN401
        return core.acknowledge_hint(
            body.request_id,
            attempt_id=attempt_id,
            base=body.base,
            hint_id=hint_id,
            client_at=body.client_at,
        )

    @api.post("/api/attempts/{attempt_id}/submit")
    def submit(attempt_id: str, body: Submission, background: BackgroundTasks) -> Any:  # noqa: ANN401
        result = core.submit_answer(
            body.request_id,
            attempt_id=attempt_id,
            base=body.base,
            response=body.response,
            client_at=body.client_at,
        )
        background.add_task(core.run_operation, result["operation"]["id"])
        return result

    @api.post("/api/attempts/{attempt_id}/feedback-viewed")
    def viewed(attempt_id: str, body: Cmd) -> Any:  # noqa: ANN401
        return core.view_feedback(body.request_id, attempt_id=attempt_id)

    @api.post("/api/timer")
    def timer(body: TimerClaim) -> Any:  # noqa: ANN401
        return core.open_timer(
            body.request_id, document_run_id=body.document_run_id, takeover=body.takeover
        )

    @api.post("/api/spans")
    def spans(body: Spans) -> Any:  # noqa: ANN401
        return core.record_spans(body.request_id, spans=body.spans)

    @api.get("/api/export")
    def export() -> Response:
        archive = core.export()
        name = f"library-{archive['library_id']}-{archive['export_id']}.learning.json"
        return JSONResponse(
            archive, headers={"content-disposition": f'attachment; filename="{name}"'}
        )

    @api.post("/api/restore")
    def restore(body: Archive) -> Any:  # noqa: ANN401
        restore_into(core, data_dir, body.archive, clock=tick)
        return {"library_id": core.library_id}

    api.mount("/", StaticFiles(directory=STATIC, html=True), name="static")
    return api
