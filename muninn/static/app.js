"use strict";
// Web Interaction: render application views and send the learner's intentions.
// The server decides what evidence means and how much time counted; this page only
// sends raw observations (text, hint displays, timer spans) with retry-safe request IDs.

const PROTOCOL = "1";
const view = document.getElementById("view");
const uuid = () => crypto.randomUUID();
const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const store = {
  get: (k) => { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } },
  set: (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage unavailable */ } },
  drop: (k) => { try { localStorage.removeItem(k); } catch { /* storage unavailable */ } },
};

const LABEL = {
  independent: "Correct without help",
  helped: "Correct with help",
  error: "Mistake found",
  unresolved: "Not settled yet",
  untested: "Not practiced yet",
};
const OUTCOME = { demonstrated: "Shown", error: "Mistake", not_shown: "Not shown", cannot_judge: "Couldn't judge" };
const NEED = {
  initial: "First practice",
  independent_check: "Check without help",
  repair: "Needs repair",
  clarify: "Needs clarifying",
  held: "On hold",
};

async function api(path, body, requestId) {
  const options = body === undefined ? {} : {
    method: "POST",
    keepalive: true,
    headers: { "content-type": "application/json", "x-muninn-protocol": PROTOCOL },
    body: JSON.stringify({ request_id: requestId ?? uuid(), ...body }),
  };
  const response = await fetch(`/api${path}`, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.error || response.statusText);
    error.status = response.status;
    throw error;
  }
  return data;
}

const fmtTime = (iso) => (iso ? new Date(iso).toLocaleString() : "not scheduled");
const fmtMs = (ms) => {
  if (ms === null || ms === undefined) return "not measured yet";
  const s = Math.round(ms / 1000);
  return s < 60 ? `${s} s` : `${Math.floor(s / 60)} min ${s % 60} s`;
};
const tag = (cls, text) => `<span class="tag ${esc(cls)}">${esc(text)}</span>`;

// --- timer: foreground spans, durations from the monotonic clock --------------------

const timer = {
  doc: sessionStorage.getItem("muninn.doc") || uuid(),
  run: null,
  ordinal: 0,
  open: null,
  activity: null,
  queue: store.get("muninn.spans") || [],

  async claim(takeover = false) {
    sessionStorage.setItem("muninn.doc", this.doc);
    try {
      this.run = (await api("/timer", { document_run_id: this.doc, takeover })).run.id;
      document.getElementById("timer-banner").hidden = true;
      this.resume();
    } catch (e) {
      if (e.status === 409) document.getElementById("timer-banner").hidden = false;
    }
  },
  set(category, ctx = {}) {
    this.close();
    this.activity = { category, ctx };
    this.resume();
    this.flush();
  },
  resume() {
    if (!this.run || document.hidden || !this.activity || this.open) return;
    const { session = null, enrollment = null, context = [], targets = [], hold = false } = this.activity.ctx;
    this.open = {
      id: uuid(), run_id: this.run, ordinal: ++this.ordinal, category: this.activity.category,
      monotonic_start_ms: Math.round(performance.now()), raw_wall_start: new Date().toISOString(),
      session, enrollment, context, targets,
      ...(hold ? { hold: true } : {}),
    };
  },
  close() {
    if (!this.open) return;
    const span = { ...this.open, monotonic_end_ms: Math.round(performance.now()), raw_wall_end: new Date().toISOString() };
    this.open = null;
    if (span.monotonic_end_ms > span.monotonic_start_ms) {
      this.queue.push(span);
      store.set("muninn.spans", this.queue);
    }
  },
  release(context) {
    // Held intake spans wait until we know which material they prepared.
    for (const span of [...this.queue, this.open].filter((x) => x && x.hold)) {
      span.context = [...span.context, ...context];
      delete span.hold;
    }
    store.set("muninn.spans", this.queue);
    this.flush();
  },
  async flush() {
    const batch = this.queue.filter((s) => !s.hold);
    if (!batch.length) return;
    try {
      const result = await api("/spans", { spans: batch });
      if (!result.holds_timer) this.claim();  // after a restart or restore, ask again
      const sent = new Set(batch.map((s) => s.id));
      this.queue = this.queue.filter((s) => !sent.has(s.id));
      store.set("muninn.spans", this.queue);
    } catch { /* kept for the next flush */ }
  },
};
for (const span of timer.queue) delete span.hold;  // a page closed mid-preparation: library overhead
document.getElementById("take-timer").addEventListener("click", () => timer.claim(true));
document.addEventListener("visibilitychange", () => {
  if (document.hidden) { timer.close(); timer.flush(); } else { timer.resume(); }
});
window.addEventListener("pagehide", () => { timer.close(); timer.flush(); });
setInterval(() => { if (timer.open) { timer.close(); timer.resume(); } timer.flush(); }, 30000);

// --- routing ------------------------------------------------------------------------

let leave = () => {};
async function route() {
  leave();
  leave = () => {};
  const [, page, id, sub] = location.hash.split("/");
  try {
    if (page === "c") await outlinePage(id);
    else if (page === "s" && sub === "summary") await summaryPage(id);
    else if (page === "s") await practicePage(id, sub === "next");
    else if (page === "a") await feedbackPage(id);
    else await homePage();
  } catch (e) {
    view.innerHTML = `<p class="error-text">${esc(e.message)}</p><p><a href="#/">Back to your library</a></p>`;
  }
  view.focus();
}
window.addEventListener("hashchange", route);

// --- home: material intake and the library -------------------------------------------

let pendingDraft = null;

function libraryLists(home) {
  const drafting = home.drafting.map((d) => {
    const op = d.operation;
    const live = op.status === "pending" || op.status === "running";
    const state = live ? "Drafting your outline…" : op.acceptance === "rejected"
      ? `The draft did not pass its checks: ${op.reason}` : `Drafting stopped: ${op.reason}`;
    return `<div class="card"><strong>${esc(d.source)}</strong><div class="status">${esc(state)}</div>
      ${live ? "" : `<button type="button" class="secondary" data-retry="${esc(op.id)}">Try drafting again</button>`}</div>`;
  }).join("");
  const curricula = home.curricula.map((c) => `<div class="card">
      <a href="#/c/${esc(c.id)}"><strong>${esc(c.title)}</strong></a>
      <div class="muted small">${esc(c.purpose)}</div>
      <div class="small">${c.started} of ${c.goals} goals started · next check: ${esc(fmtTime(c.next_check))}</div>
    </div>`).join("");
  return `${drafting ? `<h2>Being drafted</h2>${drafting}` : ""}
    <h2>Curricula</h2>${curricula || '<p class="muted">Nothing yet. Add some material below.</p>'}
    <p class="small muted">Time recorded in this library, including preparation not tied to a curriculum:
      ${esc(fmtMs(home.effort.total_ms))}</p>`;
}

async function homePage() {
  view.innerHTML = `
    <h1>Your library</h1>
    <div id="lists"></div>
    <h2>Add material</h2>
    <form id="intake" class="card">
      <label for="title">Title</label><input id="title" type="text" required>
      <label for="purpose">What do you want to be able to do with it? <span class="muted">(optional)</span></label>
      <input id="purpose" type="text" placeholder="e.g. explain why binary search is fast">
      <label for="text">Text</label><textarea id="text" required placeholder="Paste the text you want to learn from"></textarea>
      <div class="row"><button type="submit">Draft an outline</button><span class="status" id="intake-status"></span></div>
    </form>
    <h2>Library file</h2>
    <div class="card row">
      <a href="/api/export" download><button type="button" class="secondary">Export library</button></a>
      <label class="small" for="restore" style="margin:0">Restore from an exported file:</label>
      <input id="restore" type="file" accept=".json,application/json">
    </div>`;
  let poll = null;
  let preparing = false;
  const refresh = async () => {
    const home = await api("/home");
    const lists = document.getElementById("lists");
    if (!lists) return;
    lists.innerHTML = libraryLists(home);
    lists.querySelectorAll("[data-retry]").forEach((b) => b.addEventListener("click", async () => {
      await api(`/operations/${b.dataset.retry}/retry`, {});
      refresh();
    }));
    const live = home.drafting.some((d) => ["pending", "running"].includes(d.operation.status));
    if (!preparing) {
      timer.set(live && pendingDraft ? "blocked_wait" : "progress_inspection", { context: live && pendingDraft ? pendingDraft : [] });
    }
    clearTimeout(poll);
    if (live) poll = setTimeout(refresh, 2500);
  };
  leave = () => {
    clearTimeout(poll);
    timer.release([]);  // preparation that produced no material is library overhead
  };
  await refresh();
  const form = document.getElementById("intake");
  form.addEventListener("focusin", () => {
    if (!preparing) { preparing = true; timer.set("authoring", { hold: true }); }
  });
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const status = document.getElementById("intake-status");
    status.textContent = "Saving…";
    try {
      const body = { title: form.title.value, purpose: form.purpose.value || null, text: form.text.value };
      form.querySelector("button").disabled = true;
      const result = await api("/materials", body);
      pendingDraft = [result.source, result.operation];
      timer.release(pendingDraft);  // all of this preparation belongs to the new material
      form.reset();
      form.querySelector("button").disabled = false;
      status.textContent = "Saved. Drafting the outline…";
      preparing = false;
      refresh();
    } catch (e) {
      form.querySelector("button").disabled = false;
      status.innerHTML = `<span class="error-text">${esc(e.message)}</span>`;
    }
  });
  document.getElementById("restore").addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file || !confirm("Restore this file as a new library? Your current library file is kept on disk.")) return;
    try {
      await api("/restore", { archive: await file.text() });
      await timer.claim();
      route();
    } catch (e) {
      alert(`The file was not restored: ${e.message}`);
    }
  });
}

// --- outline ------------------------------------------------------------------------

async function outlinePage(id) {
  const o = await api(`/curricula/${id}`);
  const c = o.curriculum;
  const byId = Object.fromEntries(o.targets.map((t) => [t.ref.id, t]));
  const targetCard = (t) => `<div class="card">
      <div>${tag(t.evidence.label, LABEL[t.evidence.label])} <strong>${esc(t.action)}</strong></div>
      <div class="small muted">${esc(t.mode.replace("_", " "))}${t.conditions.length ? ` · ${esc(t.conditions.join("; "))}` : ""}
        · ${esc(t.state)}${t.schedule ? ` · ${esc(NEED[t.schedule.need])}${t.schedule.due_at ? `, due ${esc(fmtTime(t.schedule.due_at))}` : ""}` : ""}</div>
      ${o.without_exercise.includes(t.ref.id) ? '<div class="small error-text">No exercise can check this yet.</div>' : ""}
      <details><summary class="small">What this rests on</summary>
        ${t.knowledge.map((k) => `<p><span class="tag">${esc(k.form)}</span>${esc(k.statement)} <span class="muted small">(${esc(k.scope)})</span></p>
          ${k.quotes.map((q) => `<blockquote>${esc(q)}</blockquote>`).join("")}`).join("")}
        <p class="small muted">An answer should show: ${t.requirements.map((r) => esc(r.statement)).join("; ")}</p>
      </details></div>`;
  const counts = o.counts;
  view.innerHTML = `
    <p><a href="#/">← Library</a></p>
    <h1>${esc(c.title)}</h1>
    <p>${esc(c.purpose)} ${c.purpose_basis === "suggested" ? '<span class="tag">suggested purpose</span>' : ""}</p>
    ${c.doubts.length ? `<div class="card"><strong>Worth checking</strong><ul>${c.doubts.map((d) => `<li>${esc(d)}</li>`).join("")}</ul></div>` : ""}
    <div class="row">
      <button type="button" id="practice">${counts.active ? "Continue practice" : "Start practice"}</button>
      <button type="button" class="secondary" id="edit">Edit titles</button>
    </div>
    <p class="small muted">${counts.selected} goals: ${counts.unstarted} not started · ${counts.independent} correct without help ·
      ${counts.helped} with help · ${counts.errors} with a mistake · ${counts.unresolved} not settled · next check ${esc(fmtTime(o.next_check))}<br>
      Time on this curriculum, including preparation: ${esc(fmtMs(o.effort.total_ms))}</p>
    ${c.sections.map((s) => `<h2>${esc(s.title)}</h2>${s.target_ids.map((t) => targetCard(byId[t])).join("")}`).join("")}
    <h2>Exercises</h2>
    ${o.exercises.map((e) => `<div class="card">${esc(e.prompt)}<div class="small muted">checked by the outline preview (${esc(e.review)})</div></div>`).join("")}
    ${c.omitted.length ? `<details><summary>Left out of the outline</summary><ul>${c.omitted.map((m) => `<li>${esc(m.detail)} — ${esc(m.reason)}</li>`).join("")}</ul></details>` : ""}
    <details><summary>Source text</summary><div class="card small" style="white-space:pre-wrap">${esc(o.source.text)}</div></details>`;
  timer.set(counts.active ? "progress_inspection" : "authoring", { enrollment: o.enrollment, context: [c.ref] });
  document.getElementById("practice").addEventListener("click", async () => {
    const { session } = await api(`/curricula/${id}/sessions`, {});
    location.hash = `#/s/${session.id}`;
  });
  document.getElementById("edit").addEventListener("click", () => editOutline(o));
}

function editOutline(o) {
  const c = o.curriculum;
  view.innerHTML = `<p><a href="#/c/${esc(c.ref.id)}">← Outline</a></p><h1>Edit titles</h1>
    <form id="edit-form" class="card">
      <label for="e-title">Title</label><input id="e-title" type="text" value="${esc(c.title)}" required>
      <label for="e-purpose">Purpose</label><input id="e-purpose" type="text" value="${esc(c.purpose)}">
      ${c.sections.map((s, i) => `<label for="s-${i}">Section ${i + 1}</label><input id="s-${i}" type="text" value="${esc(s.title)}">`).join("")}
      <div class="row"><button type="submit">Save</button><span class="status" id="edit-status"></span></div>
    </form>`;
  document.getElementById("edit-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await api(`/curricula/${c.ref.id}/edit`, {
        base: c.ref.revision,
        title: document.getElementById("e-title").value,
        purpose: document.getElementById("e-purpose").value,
        sections: c.sections.map((s, i) => ({ id: s.id, title: document.getElementById(`s-${i}`).value, target_ids: s.target_ids })),
      });
      location.hash = `#/c/${c.ref.id}`;
    } catch (e) {
      document.getElementById("edit-status").innerHTML = `<span class="error-text">${esc(e.message)}</span>`;
    }
  });
}

// --- practice -------------------------------------------------------------------------

async function practicePage(sessionId, wantNext) {
  let p = await api(`/sessions/${sessionId}`);
  if (!p.attempt || (wantNext && p.attempt.status === "submitted" && p.attempt.feedback_ready)) {
    const next = await api(`/sessions/${sessionId}/next`, {});
    if (!next.attempt) {
      view.innerHTML = `<h1>Nothing more to practice right now</h1>
        <p>Every exercise in this curriculum has an answer. Later checks appear when they are due.</p>
        <button type="button" id="finish">See this session's summary</button>`;
      document.getElementById("finish").addEventListener("click", () => finish(p.session));
      timer.set("progress_inspection", { session: p.session.ref, enrollment: p.session.enrollments[0] });
      return;
    }
    p = await api(`/sessions/${sessionId}`);
  }
  const a = p.attempt;
  const ctx = { session: p.session.ref, enrollment: p.session.enrollments[0], context: [a.ref] };
  if (a.status === "submitted") return waitForFeedback(sessionId, a, ctx);
  const backupKey = `muninn.draft.${a.ref.id}`;
  const backup = store.get(backupKey);
  const restored = backup && backup !== a.response;
  let base = a.ref.revision;
  view.innerHTML = `
    <p class="small muted">Practice — answer in your own words. Help is always available and is recorded.</p>
    <h1>${esc(a.prompt)}</h1>
    <label for="answer">Your answer</label>
    <textarea id="answer" class="answer">${esc(restored ? backup : a.response)}</textarea>
    <div class="status" id="draft-status">${restored ? "Restored text that had not been saved yet." : ""}</div>
    <div id="hints">${a.hints.map((h, i) => h.text
      ? `<div class="card small"><strong>Hint ${i + 1}:</strong> ${esc(h.text)}</div>`
      : `<button type="button" class="secondary" data-hint="${esc(h.id)}">Show hint ${i + 1}</button> `).join("")}</div>
    <div class="row"><button type="button" id="submit">Submit answer</button>
      <button type="button" class="secondary" id="stop">Stop for now</button></div>`;
  timer.set("answer", ctx);
  const box = document.getElementById("answer");
  const status = document.getElementById("draft-status");
  let saving = Promise.resolve();
  let timeout = null;
  const save = () => {
    saving = saving.then(async () => {
      try {
        base = (await api(`/attempts/${a.ref.id}/draft`, { base, response: box.value })).attempt.revision;
        store.drop(backupKey);
        status.textContent = "Draft saved.";
      } catch (e) {
        status.innerHTML = `<span class="error-text">Not saved yet (${esc(e.message)}). Your text is kept here.</span>`;
      }
    });
    return saving;
  };
  box.addEventListener("input", () => {
    store.set(backupKey, box.value);
    status.textContent = "Typing…";
    clearTimeout(timeout);
    timeout = setTimeout(save, 1200);
  });
  leave = () => clearTimeout(timeout);
  view.querySelectorAll("[data-hint]").forEach((button) => button.addEventListener("click", async () => {
    await saving;
    const { hint } = await api(`/attempts/${a.ref.id}/hints/${button.dataset.hint}/reveal`, {});
    const card = document.createElement("div");
    card.className = "card small";
    card.innerHTML = `<strong>Hint:</strong> ${esc(hint.text)}`;
    button.replaceWith(card);
    requestAnimationFrame(async () => {
      base = (await api(`/attempts/${a.ref.id}/hints/${hint.id}/ack`, { base, client_at: new Date().toISOString() })).attempt.revision;
    });
  }));
  document.getElementById("submit").addEventListener("click", async () => {
    clearTimeout(timeout);
    await saving;
    if (!box.value.trim()) { status.textContent = "Write an answer first."; return; }
    const pending = store.get(`muninn.submit.${a.ref.id}`);
    const requestId = pending && pending.response === box.value ? pending.id : uuid();
    store.set(`muninn.submit.${a.ref.id}`, { id: requestId, response: box.value });
    try {
      await api(`/attempts/${a.ref.id}/submit`, { base, response: box.value, client_at: new Date().toISOString() }, requestId);
      store.drop(backupKey);
      store.drop(`muninn.submit.${a.ref.id}`);
      route();
    } catch (e) {
      status.innerHTML = `<span class="error-text">Not submitted (${esc(e.message)}). Your answer is kept; try again.</span>`;
    }
  });
  document.getElementById("stop").addEventListener("click", async () => {
    clearTimeout(timeout);
    await save();
    finish(p.session);
  });
}

async function waitForFeedback(sessionId, a, ctx) {
  const op = a.assessment;
  const live = op && ["pending", "running"].includes(op.status);
  if (a.feedback_ready) { location.hash = `#/a/${a.ref.id}`; return; }
  view.innerHTML = `<h1>${esc(a.prompt)}</h1>
    <div class="card"><strong>Your answer is saved.</strong><blockquote>${esc(a.response)}</blockquote></div>
    <p class="status">${live ? "Assessment pending — checking your answer against each criterion…"
      : `The assessment did not finish (${esc(op?.reason || "interrupted")}). Nothing about your answer was lost.`}</p>
    ${live ? "" : '<button type="button" id="retry">Try the assessment again</button>'}`;
  timer.set(live ? "blocked_wait" : "progress_inspection", ctx);
  if (live) {
    const poll = setTimeout(route, 2000);
    leave = () => clearTimeout(poll);
  } else {
    document.getElementById("retry").addEventListener("click", async () => {
      await api(`/operations/${op.id}/retry`, {});
      route();
    });
  }
}

// --- feedback ------------------------------------------------------------------------

function highlight(text, quotes) {
  let html = esc(text);
  for (const q of quotes) html = html.replace(esc(q), `<mark>${esc(q)}</mark>`);
  return html;
}

async function feedbackPage(attemptId) {
  const f = await api(`/attempts/${attemptId}`);
  await api(`/attempts/${attemptId}/feedback-viewed`, {});
  const quotes = f.criteria.flatMap((c) => c.quotes);
  view.innerHTML = `
    <h1>Feedback</h1>
    <p class="muted">${esc(f.prompt)}</p>
    <div class="card"><strong>Your answer</strong><p>${highlight(f.attempt.response, quotes)}</p></div>
    <div class="card"><p>${esc(f.explanation)}</p></div>
    <h2>Each part of the answer</h2>
    ${f.criteria.map((c) => `<div class="card">
        ${tag(c.outcome, OUTCOME[c.outcome])}${c.help === "shown" ? tag("helped", "hint used") : c.help === "unconfirmed" ? tag("unresolved", "hint sent, display not confirmed") : ""} ${esc(c.requirement)}
        ${c.quotes.map((q) => `<blockquote>${esc(q)}</blockquote>`).join("")}
        <div class="small muted">${esc(c.reason)}</div></div>`).join("")}
    <h2>What this shows</h2>
    <ul class="plain">${f.targets.map((t) => `<li>${tag(t.label, LABEL[t.label])} ${esc(t.action)}
      <div class="small muted">${esc(t.reasons.join("; "))}</div></li>`).join("")}</ul>
    <details><summary>Show the reference answer</summary><div class="card">${esc(f.reference_response)}</div>
      <p class="small muted">Seeing this answer counts as practice, not as a later check.</p></details>
    <p class="small muted">Judged by ${esc(f.assessor?.name)} under protocol ${esc(f.assessor?.protocol_version)}.</p>
    <div class="row"><button type="button" id="next">Next exercise</button>
      <button type="button" class="secondary" id="finish">Finish session</button></div>`;
  const session = await api(`/sessions/${f.session.id}`);
  timer.set("feedback", { session: f.session, enrollment: session.session.enrollments[0], context: [f.attempt.ref] });
  document.getElementById("next").addEventListener("click", () => { location.hash = `#/s/${f.session.id}/next`; });
  document.getElementById("finish").addEventListener("click", () => finish(session.session));
}

async function finish(session) {
  if (session.status !== "ended") {
    await api(`/sessions/${session.ref.id}/end`, { base: session.ref.revision, reason: "learner finished" }).catch(() => {});
  }
  timer.close();
  await timer.flush();
  location.hash = `#/s/${session.ref.id}/summary`;
}

// --- summary ----------------------------------------------------------------------------

async function summaryPage(sessionId) {
  const s = await api(`/sessions/${sessionId}/summary`);
  const e = s.effort;
  const groups = e.groups || {};
  view.innerHTML = `
    <h1>Session summary</h1>
    <p>${esc(s.headline)}</p>
    <ul class="plain">${s.targets.map((t) => `<li class="card">${tag(t.label, LABEL[t.label])} ${esc(t.action)}
      <div class="small muted">${esc(t.reasons.join("; "))} · <a href="#/a/${esc(t.attempt)}">see the answer and feedback</a></div></li>`).join("")
      || '<li class="muted">No answers in this session.</li>'}</ul>
    ${s.pending_assessments ? `<p>${s.pending_assessments} answer(s) not graded yet.</p>` : ""}
    <p>Next check: ${esc(fmtTime(s.next_check))}</p>
    <h2>Time</h2>
    <dl class="time">
      <dt>Learning work</dt><dd>${esc(fmtMs(groups.learning ?? null))}</dd>
      <dt>Waiting for the app</dt><dd>${esc(fmtMs(groups.waiting ?? null))}</dd>
      <dt>Overhead</dt><dd>${esc(fmtMs(groups.overhead ?? null))}</dd>
      <dt>Total accounted</dt><dd>${esc(fmtMs(e.total_ms))}</dd>
      <dt>Session length, breaks included</dt><dd>${esc(fmtMs(s.elapsed_ms))}</dd>
    </dl>
    ${e.unknown_tails || e.stale_spans || e.unplaced_known_ms || e.disputed_ms ? `<p class="small muted">Not counted:
      ${e.unknown_tails} gap(s) of unknown length, ${e.stale_spans} span(s) from another tab,
      ${esc(fmtMs(e.unplaced_known_ms))} that could not be placed, ${esc(fmtMs(e.disputed_ms))} overlapping a break.</p>` : ""}
    <details><summary>How did this session feel? (optional)</summary>
      <form id="ratings" class="card">
        <label for="effort">Effort</label><select id="effort"><option value="">—</option><option>easy</option><option>moderate</option><option>hard</option></select>
        <label for="useful">Usefulness</label><select id="useful"><option value="">—</option><option value="useful">useful</option><option value="mixed">mixed</option><option value="not_useful">not useful</option></select>
        <div class="row"><button type="submit">Save</button><span class="status" id="ratings-status"></span></div>
      </form></details>
    <p><a href="#/">Back to your library</a></p>`;
  timer.set("progress_inspection", { session: s.session.ref, enrollment: s.session.enrollments[0] });
  document.getElementById("ratings").addEventListener("submit", async (event) => {
    event.preventDefault();
    await api(`/sessions/${sessionId}/feedback`, {
      effort: document.getElementById("effort").value || null,
      usefulness: document.getElementById("useful").value || null,
      note: null,
    });
    document.getElementById("ratings-status").textContent = "Saved.";
  });
}

timer.claim().then(route);
