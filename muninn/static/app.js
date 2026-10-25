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
const CHOICE = { forgot: "Forgot", difficult: "Remembered with difficulty", remembered: "Remembered", easy: "Easy" };
const BUCKET = {
  QN: "Planned for later", QM: "No answer for this check", QU: "Not enough grading evidence",
  QH: "Answered with help", QX: "Does not establish this result", QS: "Correct", QE: "Incorrect",
};
const RAW = { S: "correct", E: "incorrect", H: "with help", U: "not gradable", M: "missing", N: "not yet" };
const WAITING = {
  first_check_pending: "First later check pending", after_repair_pending: "Later check after repair pending",
  unresolved: "Something is still unresolved", grading: "An answer is still being graded",
  due: "A later check is due", not_started: "Some goals are not started yet", paused: "Some goals are paused",
  held: "Some goals are on hold",
};
const DURATIONS = [[5, "5 minutes"], [10, "10 minutes"], [15, "15 minutes"], [30, "30 minutes"], [60, "an hour"], [0, "no limit"]];
const PURPOSE = {
  initial: "Practice — answer in your own words. Help is always available and is recorded.",
  clarification: "One question to tell which help fits. Your answer changes what comes next; it is not a test.",
  verification: "A fresh version of the task, to check what you just worked through. Answer in your own words.",
};
const capital = (s) => (s ? s[0].toUpperCase() + s.slice(1) : "");
const sentence = (s) => (/[.!?]$/.test(s) ? s : `${s}.`);

// What a learning concern means for the learner right now (server state, plain words).
function concernNote(c) {
  if (!c) return "";
  const causes = c.hypotheses.map((h) => h.practice);
  const focus = c.hypotheses.find((h) => h.key === c.focus);
  if (c.status === "resolved" || c.status === "superseded") return `${capital(c.resolution_reason)}.`;
  if (c.status === "paused") {
    if (c.still_uncertain) {
      return c.kind === "uncertainty"
        ? "Still uncertain: these answers don't settle it. Nothing was recorded as a mistake."
        : "Still uncertain which help fits. The earlier mistake stays recorded; nothing more is asked automatically.";
    }
    return "Paused. Its evidence is kept.";
  }
  return {
    diagnosis: `One short question will show which help fits${causes.length ? `: ${causes.join(", or ")}` : ""}.`,
    repair: {
      supported: `Next: a short explanation — ${focus?.practice}.`,
      uncertain: "Next: a worked explanation, offered as support while the cause is still uncertain.",
      direct: "Next: a short explanation of the part that went wrong.",
    }[c.help],
    verification: "Next: a fresh check of what you worked through.",
    later_check: "Shown with help on the fresh check. An independent check later will tell more; no more teaching now.",
    assessment_review: "The fresh check didn't show the repaired part either way. No new teaching starts automatically; you can pause this.",
    content_review: "These two approaches have not resolved this yet. Review the explanation or the assessment, revisit a prerequisite, or pause.",
  }[c.route] || "";
}

const KEEPALIVE_LIMIT = 60000;  // bytes; browsers refuse keepalive requests above 64 KiB

async function api(path, body, requestId) {
  const payload = body === undefined ? null : JSON.stringify({ request_id: requestId ?? uuid(), ...body });
  const options = payload === null ? {} : {
    method: "POST",
    // keepalive lets page-close writes finish; a restored library is far larger than that
    keepalive: new TextEncoder().encode(payload).length < KEEPALIVE_LIMIT,
    headers: { "content-type": "application/json", "x-muninn-protocol": PROTOCOL },
    body: payload,
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
// A span names its enrollment only when the session has exactly one; over several curricula
// the server keeps unattributed time as uncertain rather than guessing (cost-membership-1).
const oneEnrollment = (session) => (session.enrollments.length === 1 ? session.enrollments[0] : null);
const tag = (cls, text) => `<span class="tag ${esc(cls)}">${esc(text)}</span>`;
const go = (hash) => { if (location.hash === hash) route(); else location.hash = hash; };

// --- answer-bearing views this page opened: closed when left, so the wait can start ----

const views = {
  open: new Set(),
  async show(targets, what) {
    const { exposure } = await api("/exposures", { targets, what });
    this.open.add(exposure.id);
    return exposure.id;
  },
  track(id) { this.open.add(id); },
  close(id) {
    if (!this.open.delete(id)) return Promise.resolve();
    return api(`/exposures/${id}/close`, {}).catch(() => {});
  },
  // awaited on navigation: a view still open when the next task starts counts as help on it
  closeAll() { return Promise.all([...this.open].map((id) => this.close(id))); },
};
window.addEventListener("pagehide", () => views.closeAll());

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
  await views.closeAll();
  const [, page, id, sub] = location.hash.split("/");
  try {
    if (page === "start") await startPage(id);
    else if (page === "c" && sub === "checks") await checksPage(id);
    else if (page === "c" && sub === "track") await trackPage(id);
    else if (page === "tr") await reportPage(id);
    else if (page === "c") await outlinePage(id);
    else if (page === "t") await historyPage(id);
    else if (page === "r") await proposalsPage(id);
    else if (page === "d") await disputePage(id);
    else if (page === "rv") await reviewPage(id);
    else if (page === "s" && sub === "summary") await summaryPage(id);
    else if (page === "s" && sub === "next") await nextStep(id);
    else if (page === "s" && sub === "choose") await choosePage(id);
    else if (page === "s") await practicePage(id);
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
    if (op.status === "succeeded" && op.acceptance === "pending") {
      return `<div class="card"><strong>${esc(d.source)}</strong>
        <div class="status">The outline is ready. Some of its claims match or contradict claims you already have.</div>
        <a href="#/r/${esc(op.id)}">Review them before accepting the outline</a></div>`;
    }
    const state = live ? "Drafting your outline…" : op.acceptance === "rejected"
      ? `The draft did not pass its checks: ${op.reason}` : `Drafting stopped: ${op.reason}`;
    return `<div class="card"><strong>${esc(d.source)}</strong><div class="status">${esc(state)}</div>
      ${live ? "" : `<button type="button" class="secondary" data-retry="${esc(op.id)}">Try drafting again</button>`}</div>`;
  }).join("");
  const curricula = home.curricula.map((c) => `<div class="card">
      <a href="#/c/${esc(c.id)}"><strong>${esc(c.title)}</strong></a>
      <div class="muted small">${esc(c.purpose)}</div>
      <div class="small">${c.started} of ${c.goals} goals started · ${c.due_now ? `<strong>${c.due_now} due now</strong>` : `next check: ${esc(fmtTime(c.next_check))}`}${c.repairs ? ` · ${c.repairs} repair${c.repairs > 1 ? "s" : ""} waiting` : ""}</div>
    </div>`).join("");
  const due = home.due;
  const dueCard = due.checks || due.repairs || due.blocked ? `<div class="card"><strong>Due now:</strong>
      ${due.checks ? `${due.checks} check${due.checks > 1 ? "s" : ""}` : ""}${due.checks && due.repairs ? " and " : ""}${due.repairs ? `${due.repairs} repair${due.repairs > 1 ? "s" : ""}` : ""}
      ${due.oldest ? `<span class="muted small">· waiting since ${esc(fmtTime(due.oldest))}</span>` : ""}
      ${due.blocked ? `<div class="small">${due.blocked}${due.checks || due.repairs ? " more" : ""} cannot be offered yet; the session says why and what would let it start.</div>` : ""}
      <div class="row"><a href="#/start/${esc(due.curricula.join(","))}"><button type="button">Practice what's due</button></a></div></div>` : "";
  return `${dueCard}${drafting ? `<h2>Being drafted</h2>${drafting}` : ""}
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
  const claims = Object.fromEntries(o.targets.flatMap((t) => t.knowledge.map((k) => [k.ref.id, k])));
  const claimLine = (k) => `<div class="claim">
      <p><span class="tag">${esc(k.form)}</span>${k.status === "disputed" ? tag("error", "flagged") : ""}${esc(k.statement)}
        <span class="muted small">(${esc(k.scope)})</span></p>
      ${k.quotes.map((q) => `<blockquote>${esc(q)}</blockquote>`).join("")}
      ${k.dispute ? `<p class="small error-text">Flagged: ${esc(k.dispute.reason)}</p>` : ""}
      <div class="row">${k.status === "disputed"
        ? `<button type="button" class="secondary" data-correct="${esc(k.ref.id)}">Correct it</button>
           <button type="button" class="secondary" data-keep="${esc(k.ref.id)}">Keep it as it is</button>`
        : `<button type="button" class="secondary" data-flag="${esc(k.ref.id)}">This material is wrong</button>`}</div></div>`;
  const targetCard = (t) => `<div class="card">
      <div>${tag(t.evidence.label, LABEL[t.evidence.label])} <strong>${esc(t.action)}</strong></div>
      <div class="small muted">${esc(t.mode.replace("_", " "))}${t.conditions.length ? ` · ${esc(t.conditions.join("; "))}` : ""}
        · ${esc(t.state)}${t.schedule ? ` · ${t.schedule.type === "recall" ? "recall reviews" : "later checks"} · ${esc(NEED[t.schedule.need])}${t.schedule.due_at ? `, due ${esc(fmtTime(t.schedule.due_at))}` : ""}` : ""}</div>
      ${t.schedule?.hold_reason ? `<div class="small">${esc(capital(t.schedule.hold_reason))}.</div>` : ""}
      ${t.schedule?.next_offer ? `<div class="small muted">${t.schedule.next_offer.at
        ? `Offered again from ${esc(fmtTime(t.schedule.next_offer.at))}, 24 hours after you last saw the answer.`
        : "An earlier view of the answer may still be open; the next check waits for you to confirm it is closed."}</div>` : ""}
      ${t.hold ? `<div class="small error-text">On hold: ${esc(sentence(t.hold))}${t.schedule ? " Its evidence and due check are kept." : ""}</div>`
        : o.without_exercise.includes(t.ref.id) ? '<div class="small error-text">No exercise can check this yet.</div>' : ""}
      <details data-reveal="${esc(t.ref.id)}"><summary class="small">What this rests on <span class="muted">(shows the answer)</span></summary>
        ${t.knowledge.map(claimLine).join("")}
        <p class="small muted">An answer should show: ${t.requirements.map((r) => esc(r.statement)).join("; ")}</p>
      </details>
      <div class="row"><a class="small" href="#/t/${esc(t.ref.id)}">History and judgments</a>
        <button type="button" class="secondary" data-goal="${esc(t.ref.id)}">Edit this goal</button></div></div>`;
  const counts = o.counts;
  view.innerHTML = `
    <p><a href="#/">← Library</a></p>
    <h1>${esc(c.title)}</h1>
    <p>${esc(c.purpose)} ${c.purpose_basis === "suggested" ? '<span class="tag">suggested purpose</span>' : ""}</p>
    ${c.doubts.length ? `<div class="card"><strong>Worth checking</strong><ul>${c.doubts.map((d) => `<li>${esc(d)}</li>`).join("")}</ul></div>` : ""}
    <div class="row">
      <button type="button" id="practice">${counts.active ? "Continue practice" : "Start practice"}</button>
      <button type="button" class="secondary" id="edit">Edit titles</button>
      <a href="#/c/${esc(id)}/checks">Later checks</a> <a href="#/c/${esc(id)}/track">Follow these goals over time</a>
    </div>
    <p class="small muted">${counts.selected} goals: ${counts.unstarted} not started · ${counts.independent} correct without help ·
      ${counts.helped} with help · ${counts.errors} with a mistake · ${counts.unresolved} not settled · next check ${esc(fmtTime(o.next_check))}<br>
      Time on this curriculum, including preparation: ${esc(fmtMs(o.effort.total_ms))}</p>
    ${c.sections.map((s) => `<h2>${esc(s.title)}</h2>${s.target_ids.map((t) => targetCard(byId[t])).join("")}`).join("")}
    <h2>Exercises</h2>
    ${o.exercises.map((e) => `<div class="card">${esc(e.prompt)}<div class="small muted">${e.reviewer === "learner-review"
      ? "you confirmed it checks the edited goal" : `checked by the outline preview (${esc(e.review)})`}</div>
      ${e.hold ? `<div class="small error-text">On hold: ${esc(sentence(e.hold))}</div>
        ${e.rebindable ? `<div class="row"><button type="button" class="secondary" data-rebind="${esc(e.ref.id)}" data-base="${e.ref.revision}">It still checks the edited goal</button></div>` : ""}` : ""}</div>`).join("")}
    ${c.omitted.length ? `<details><summary>Left out of the outline</summary><ul>${c.omitted.map((m) => `<li>${esc(m.detail)} — ${esc(m.reason)}</li>`).join("")}</ul></details>` : ""}
    <details data-reveal="source"><summary>Source text <span class="muted small">(shows the answers)</span></summary><div class="card small" style="white-space:pre-wrap">${esc(o.source.text)}</div></details>`;
  timer.set(counts.active ? "progress_inspection" : "authoring", { enrollment: o.enrollment, context: [c.ref] });
  document.getElementById("practice").addEventListener("click", () => { location.hash = `#/start/${id}`; });
  // Opening answer-bearing material is exposure: a later check of those goals waits 24 h.
  view.querySelectorAll("details[data-reveal]").forEach((d) => d.addEventListener("toggle", async () => {
    if (d.open) {
      const targets = d.dataset.reveal === "source" ? o.targets.map((t) => t.ref) : [byId[d.dataset.reveal].ref];
      d.dataset.exposure = await views.show(targets, d.dataset.reveal === "source" ? "source text" : "claims");
    } else if (d.dataset.exposure) {
      views.close(d.dataset.exposure);
      delete d.dataset.exposure;
    }
  }));
  document.getElementById("edit").addEventListener("click", () => editOutline(o));
  view.querySelectorAll("[data-goal]").forEach((b) => b.addEventListener("click", () => editGoal(o, byId[b.dataset.goal])));
  view.querySelectorAll("[data-flag]").forEach((b) => b.addEventListener("click", () => flagClaim(o, claims[b.dataset.flag])));
  view.querySelectorAll("[data-correct]").forEach((b) => b.addEventListener("click", () => correctClaim(o, claims[b.dataset.correct])));
  view.querySelectorAll("[data-keep]").forEach((b) => b.addEventListener("click", async () => {
    const k = claims[b.dataset.keep];
    if (!confirm("Keep this claim as it is? What rests on it can be practised again.")) return;
    await api(`/knowledge/${k.ref.id}/revise`, { base: k.ref.revision, statement: k.statement, scope: k.scope, reason: "checked: kept as it is" });
    route();
  }));
  view.querySelectorAll("[data-rebind]").forEach((b) => b.addEventListener("click", async () => {
    if (!confirm("Does this exercise, as written, still check the edited goal? Earlier answers stay with the version they answered.")) return;
    await api(`/exercises/${b.dataset.rebind}/rebind`, { base: Number(b.dataset.base) });
    route();
  }));
}

// --- changing what is learned ----------------------------------------------------------

function changeForm(o, title, intro, fields, submit) {
  view.innerHTML = `<p><a href="#/c/${esc(o.curriculum.ref.id)}">← Outline</a></p><h1>${esc(title)}</h1>
    <p class="muted">${esc(intro)}</p>
    <form id="change" class="card">${fields}
      <label for="reason">Why</label><input id="reason" type="text" required>
      <div class="row"><button type="submit">Save</button><span class="status" id="change-status"></span></div>
    </form>`;
  timer.set("authoring", { enrollment: o.enrollment, context: [o.curriculum.ref] });
  document.getElementById("change").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await submit(document.getElementById("reason").value);
      go(`#/c/${o.curriculum.ref.id}`);
    } catch (e) {
      document.getElementById("change-status").innerHTML = `<span class="error-text">${esc(e.message)}</span>`;
    }
  });
}

const MODES = ["recognition", "recall", "explain", "reconstruct", "select", "describe_procedure", "execute"];

function editGoal(o, t) {
  changeForm(o, "Edit this goal",
    "This makes a new version of the goal. Its earlier evidence and due check stay with the old version, and exercises written for it wait for your review.",
    `<label for="g-action">What you want to be able to do</label><input id="g-action" type="text" value="${esc(t.action)}" required>
     <label for="g-mode">Kind of performance</label><select id="g-mode">${MODES.map((m) => `<option ${m === t.mode ? "selected" : ""}>${m}</option>`).join("")}</select>
     <label for="g-conditions">Conditions (one per line)</label><textarea id="g-conditions">${esc(t.conditions.join("\n"))}</textarea>
     ${t.requirements.map((r, i) => `<label for="g-r${i}">An answer should show (${i + 1})</label><input id="g-r${i}" type="text" value="${esc(r.statement)}">`).join("")}`,
    (reason) => api(`/targets/${t.ref.id}/revise`, {
      base: t.ref.revision,
      action: document.getElementById("g-action").value,
      mode: document.getElementById("g-mode").value,
      conditions: document.getElementById("g-conditions").value.split("\n"),
      requirements: t.requirements.map((r, i) => ({ id: r.id, statement: document.getElementById(`g-r${i}`).value })),
      reason,
    }));
}

function flagClaim(o, k) {
  changeForm(o, "This material is wrong",
    `“${k.statement}” will be flagged. Goals and exercises resting on it wait until you correct it or keep it; everything else continues.`,
    "", (reason) => api(`/knowledge/${k.ref.id}/flag`, { base: k.ref.revision, reason }));
}

function correctClaim(o, k) {
  changeForm(o, "Correct this claim",
    "A corrected claim changes the goals that rest on it: they get new versions, and earlier evidence stays with the old ones.",
    `${k.dispute ? `<p class="small error-text">Flagged: ${esc(k.dispute.reason)}</p>` : ""}
     <label for="k-statement">Claim</label><textarea id="k-statement">${esc(k.statement)}</textarea>
     <label for="k-scope">Scope</label><input id="k-scope" type="text" value="${esc(k.scope)}">`,
    (reason) => api(`/knowledge/${k.ref.id}/revise`, {
      base: k.ref.revision,
      statement: document.getElementById("k-statement").value,
      scope: document.getElementById("k-scope").value,
      reason,
    }));
}

// --- history: old definitions, every judgment and its corrections ------------------------

const judgmentCard = (j) => `<div class="small">
    ${j.results.map((r) => `<div>${tag(r.outcome, OUTCOME[r.outcome])} ${esc(r.requirement)} <span class="muted">— ${esc(r.reason)}</span></div>`).join("")}
    <div class="muted">${j.interpretation === "supported_misread" ? "Read as a misread of the task. " : ""}Judged by ${esc(j.assessor)}${j.revision_reason ? ` · corrected after: “${esc(j.revision_reason)}”` : ""}</div></div>`;

function reviewLink(review) {
  if (!review) return "";
  if (["pending", "running"].includes(review.status)) return `<a class="small" href="#/rv/${esc(review.id)}">A review of this judgment is running</a>`;
  if (review.status === "succeeded" && review.acceptance === "pending") return `<a class="small" href="#/rv/${esc(review.id)}">The review is ready for your decision</a>`;
  return "";
}

async function historyPage(targetId) {
  const h = await api(`/targets/${targetId}/history`);
  const revisions = [...h.revisions].reverse();
  view.innerHTML = `<p><button type="button" class="secondary" id="back">← Back</button></p>
    <h1>${esc(h.revisions.at(-1).action)}</h1>
    <p class="muted small">Every version of this goal keeps its own answers, judgments and due checks. Answers are folded away; opening one shows what you wrote and how it was judged.</p>
    ${revisions.map((r) => `<div class="card">
      <div><strong>Version ${r.ref.revision}</strong> ${r.current ? tag("independent", "current") : tag("untested", "replaced")}
        ${tag(r.evidence.label, LABEL[r.evidence.label])}</div>
      <div>${esc(r.action)}</div>
      <div class="small muted">${esc(r.mode.replace("_", " "))}${r.conditions.length ? ` · ${esc(r.conditions.join("; "))}` : ""}</div>
      <div class="small muted">An answer should show: ${r.requirements.map((q) => esc(q.statement)).join("; ")}</div>
      ${r.mapping ? `<div class="small">Changed from the previous version: ${esc(r.mapping.reason)}</div>` : ""}
      ${r.hold && r.current ? `<div class="small error-text">On hold: ${esc(r.hold)}</div>` : ""}
      ${r.answers.map((a) => {
        const current = a.judgments.at(-1);
        const earlier = a.judgments.slice(0, -1);
        return `<div class="card small">
          <div>${esc(fmtTime(a.submitted_at))} · ${a.label ? tag(a.label, LABEL[a.label]) : "not graded yet"} ${esc(a.prompt)}</div>
          <details><summary>Answer and judgment</summary><blockquote>${esc(a.response)}</blockquote>
            ${current ? judgmentCard(current) : ""}
            ${earlier.length ? `<details><summary>Earlier judgment${earlier.length > 1 ? "s" : ""} (kept)</summary>${earlier.map(judgmentCard).join("<hr>")}</details>` : ""}
          </details>
          <div class="row">${a.disputable
            ? `<a href="#/d/${esc(a.attempt.id)}">This judgment is wrong</a>` : ""} ${reviewLink(a.review)}</div></div>`;
      }).join("")}
      ${r.schedule.length ? `<details><summary class="small">Check decisions</summary><ul class="small">${r.schedule.map((s) => `<li>${s.obligation.status === "open"
        ? `${esc(NEED[s.need])}${s.due_at ? `, due ${esc(fmtTime(s.due_at))}` : ""}`
        : `${s.obligation.kind === "initial" ? "First" : "Later"} check ${esc(DISPOSITION[s.obligation.status])}`}: ${esc(s.reason)}
        ${s.resolution_rule ? " (recomputed after a correction)" : ""}</li>`).join("")}</ul></details>` : ""}
    </div>`).join("")}`;
  timer.set("progress_inspection", { context: [] });
  document.getElementById("back").addEventListener("click", () => history.back());
}

// --- "this judgment is wrong" ---------------------------------------------------------------

const DISPUTE_REASONS = ["I misread it", "My answer is valid", "The question is unclear"];
const DISPOSITION = { consumed: "met", replaced: "replaced", invalidated: "no longer applies" };

async function disputePage(attemptId) {
  const f = await api(`/attempts/${attemptId}`);
  view.innerHTML = `<p><a href="#/a/${esc(attemptId)}">← Feedback</a></p><h1>Question this judgment</h1>
    <p class="muted">${esc(f.prompt)}</p>
    <div class="card"><strong>Your answer</strong><p>${esc(f.attempt.response)}</p>
      ${f.criteria.map((c) => `<div class="small">${tag(c.outcome, OUTCOME[c.outcome])} ${esc(c.requirement)}</div>`).join("")}</div>
    <form id="dispute" class="card">
      <fieldset><legend>What looks wrong?</legend>
        ${DISPUTE_REASONS.map((r, i) => `<label class="choice"><input type="radio" name="why" value="${esc(r)}" ${i === 1 ? "checked" : ""}> ${esc(r)}</label>`).join("")}
        <label class="choice"><input type="radio" name="why" value=""> Something else</label></fieldset>
      <label for="detail">In your words <span class="muted">(optional)</span></label><textarea id="detail"></textarea>
      <p class="small muted">The assessor checks the same answer again against the same rubric. Your reason is a claim to check, not a pass. Nothing changes until you accept the result.</p>
      <div class="row"><button type="submit">Ask for a review</button><span class="status" id="dispute-status"></span></div>
    </form>`;
  timer.set("assessment_correction", { session: f.session, context: [f.attempt.ref] });
  document.getElementById("dispute").addEventListener("submit", async (event) => {
    event.preventDefault();
    const picked = view.querySelector("input[name=why]:checked").value;
    const detail = document.getElementById("detail").value.trim();
    const reason = [picked, detail].filter(Boolean).join(": ");
    try {
      const { operation } = await api(`/attempts/${attemptId}/dispute`, { reason });
      location.hash = `#/rv/${operation.id}`;
    } catch (e) {
      document.getElementById("dispute-status").innerHTML = `<span class="error-text">${esc(e.message)}</span>`;
    }
  });
}

function changeRows(rows, show) {
  return rows.filter((r) => JSON.stringify(r.before) !== JSON.stringify(r.after))
    .map((r) => `<li>${show(r)}</li>`).join("");
}

async function reviewPage(opId) {
  const op = await api(`/operations/${opId}`);
  const attemptId = op.input_snapshot.context.attempt.id;
  const back = `<p><a href="#/a/${esc(attemptId)}">← Feedback</a></p>`;
  timer.set("blocked_wait", { context: [op.ref] });
  if (["pending", "running"].includes(op.status)) {
    view.innerHTML = `${back}<h1>Reviewing your answer…</h1><p class="status">The same answer is being checked again against the same rubric.</p>`;
    const poll = setTimeout(route, 2000);
    leave = () => clearTimeout(poll);
    return;
  }
  if (op.acceptance === "accepted" || op.acceptance === "cancelled") {
    view.innerHTML = `${back}<h1>${op.acceptance === "accepted" ? "The corrected judgment is in place" : "The original judgment stays"}</h1>
      <p><a href="#/a/${esc(attemptId)}">See the feedback</a></p>`;
    return;
  }
  if (op.status !== "succeeded" || op.acceptance !== "pending") {
    view.innerHTML = `${back}<h1>The review did not finish</h1><p>${esc(op.acceptance_reason || op.error || "")}</p>
      <p class="muted">Nothing about your answer or its judgment changed.</p>
      <div class="row"><button type="button" id="retry">Try the review again</button></div>`;
    document.getElementById("retry").addEventListener("click", async () => {
      const { operation } = await api(`/operations/${opId}/retry`, {});
      location.hash = `#/rv/${operation.id}`;
    });
    return;
  }
  const p = await api(`/operations/${opId}/correction`);
  timer.set("assessment_correction", { context: [op.ref] });
  const decide = async (action) => {
    try {
      await api(`/operations/${opId}/correction/${action}`, action === "accept" ? { preview: p.digest } : {});
      location.hash = `#/a/${attemptId}`;
    } catch (e) {
      if (e.status !== 409) throw e;
      alert(e.message);  // the effect changed since this preview: show the new one
      route();
    }
  };
  if (!p.changes) {
    view.innerHTML = `${back}<h1>The review kept the original judgment</h1>
      <div class="card"><p>${esc(p.explanation)}</p></div>
      <div class="row"><button type="button" id="keep">Back to the feedback</button></div>`;
    document.getElementById("keep").addEventListener("click", () => decide("keep"));
    return;
  }
  view.innerHTML = `${back}<h1>The review suggests a different judgment</h1>
    <div class="card"><p>${esc(p.explanation)}</p></div>
    <h2>What accepting changes</h2>
    <p class="small muted">This changes the earlier judgment; no new answer is added. Dates are worked out from when you answered, not from today.</p>
    <ul>${changeRows(p.criteria, (c) => `${esc(c.requirement)}: ${tag(c.before.outcome, OUTCOME[c.before.outcome])} → ${tag(c.after.outcome, OUTCOME[c.after.outcome])}${c.after.misread ? " (a misread, not counted as a mistake)" : ""}`)}
      ${changeRows(p.targets, (t) => `${esc(t.action)}: ${tag(t.before.label, LABEL[t.before.label])} → ${tag(t.after.label, LABEL[t.after.label])}${t.after.schedule
        ? ` · next: ${esc(NEED[t.after.schedule.need])}${t.after.schedule.due_at ? `, due ${esc(fmtTime(t.after.schedule.due_at))}` : ""}` : ""}`)}
      ${p.concerns.map((c) => `<li>${esc(concernNote(c.after))}</li>`).join("")}</ul>
    <div class="row"><button type="button" id="accept">Accept the corrected judgment</button>
      <button type="button" class="secondary" id="keep">Keep the original</button></div>`;
  document.getElementById("accept").addEventListener("click", () => decide("accept"));
  document.getElementById("keep").addEventListener("click", () => decide("keep"));
}

// --- new material that repeats or contradicts what you have ----------------------------------

async function proposalsPage(opId) {
  const p = await api(`/operations/${opId}/proposals`);
  const relation = { same: "the same claim as", conflicts: "contradicts" };
  view.innerHTML = `<p><a href="#/">← Library</a></p><h1>${esc(p.title)}</h1>
    <p>Some claims drafted from “${esc(p.source)}” match or contradict claims you already have. Nothing is merged without your decision.</p>
    <form id="decide">${p.claims.map((c) => `<div class="card">
      <p><strong>${esc(c.statement)}</strong> <span class="muted small">(${esc(c.scope)})</span></p>
      ${c.quotes.map((q) => `<blockquote>${esc(q)}</blockquote>`).join("")}
      ${c.proposals.map((x) => `<div class="small">Proposed: ${esc(relation[x.relation])}
        <strong>${esc(x.existing.statement)}</strong> <span class="muted">(${esc(x.existing.scope)})</span> — ${esc(x.why)}
        ${x.existing.status === "disputed" ? `<div class="error-text">You flagged that claim: ${esc(x.existing.dispute.reason)}</div>` : ""}</div>`).join("")}
      ${c.choices.includes("reuse")
        ? `<label class="choice"><input type="radio" name="${esc(c.key)}" value="reuse" required> Use the claim I already have (this source is added to it)</label>
           <label class="choice"><input type="radio" name="${esc(c.key)}" value="separate"> Keep it as a separate claim</label>`
        : c.choices.includes("hold")
          ? '<p class="small error-text">Kept as a separate claim and put on hold until you settle it; a flag cannot be cleared by reusing it.</p>'
          : '<p class="small">That claim was reworded after this outline was drafted, so this one stays a separate claim.</p>'}
    </div>`).join("")}
      <div class="row"><button type="submit">Accept the outline</button><span class="status" id="decide-status"></span></div></form>`;
  timer.set("authoring", { context: [] });
  document.getElementById("decide").addEventListener("submit", async (event) => {
    event.preventDefault();
    const decisions = Object.fromEntries([...view.querySelectorAll("input[type=radio]:checked")].map((i) => [i.name, i.value]));
    try {
      const { curriculum } = await api(`/operations/${opId}/accept`, { decisions });
      location.hash = `#/c/${curriculum.id}`;
    } catch (e) {
      document.getElementById("decide-status").innerHTML = `<span class="error-text">${esc(e.message)}</span>`;
    }
  });
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
      go(`#/c/${c.ref.id}`);
    } catch (e) {
      document.getElementById("edit-status").innerHTML = `<span class="error-text">${esc(e.message)}</span>`;
    }
  });
}

// --- practice -------------------------------------------------------------------------

// The session's next step: the server decides; this page shows it.
async function nextStep(sessionId) {
  const p = await api(`/sessions/${sessionId}`);
  const step = await api(`/sessions/${sessionId}/next`, {});
  const ctx = { session: p.session.ref, enrollment: oneEnrollment(p.session), context: [] };
  const finishButton = '<button type="button" class="secondary" id="finish">Finish session</button>';
  const onFinish = () => document.getElementById("finish")?.addEventListener("click", () => finish(p.session));
  const c = step.concern;
  if (["exercise", "clarification", "verification", "pending"].includes(step.kind)) return go(`#/s/${sessionId}`);
  if (step.kind === "study") return studyPage(p.session, step.study.id);
  if (step.kind === "preparing") {
    view.innerHTML = `<h1>${c?.route === "verification" ? "Preparing a fresh question…" : "Preparing a short explanation…"}</h1>
      <p class="status">It is written for what your answer showed and checked before you see it.</p>`;
    timer.set("blocked_wait", { ...ctx, context: c ? [c.ref] : [] });
    const poll = setTimeout(route, 2000);
    leave = () => clearTimeout(poll);
    return;
  }
  if (step.kind === "not_ready") {
    const what = c?.route === "verification" ? "fresh question" : "explanation";
    view.innerHTML = `<h1>This ${what} isn't ready</h1>
      <p>${esc(step.operation.reason || "The model did not answer.")}</p><p class="muted">Nothing you did was lost.</p>
      <div class="row"><button type="button" id="retry">Try again</button>
        <button type="button" class="secondary" id="skip">Skip it for now</button>${finishButton}</div>`;
    timer.set("progress_inspection", ctx);
    document.getElementById("retry").addEventListener("click", async () => {
      await api(`/operations/${step.operation.id}/retry`, {});
      route();
    });
    document.getElementById("skip").addEventListener("click", async () => {
      await api(`/concerns/${c.ref.id}/pause`, { base: c.ref.revision });
      route();
    });
    return onFinish();
  }
  if (step.kind === "stopped") {
    view.innerHTML = `<h1>Let's stop repairing this automatically</h1>
      <div class="card">${esc(concernNote(c))}</div>
      <p class="muted small">Your answers, the explanations and the time spent are all kept.</p>
      <div class="row"><button type="button" id="pause">Pause it and continue</button>${finishButton}</div>`;
    timer.set("progress_inspection", ctx);
    document.getElementById("pause").addEventListener("click", async () => {
      await api(`/concerns/${c.ref.id}/pause`, { base: c.ref.revision });
      route();
    });
    return onFinish();
  }
  const leftList = step.left?.length ? `<ul class="plain">${step.left.map((x) => `<li class="card small">${esc(x.action)}
      <div class="muted">${esc(capital(x.reason))}.</div>
      ${x.confirm_closed ? `<button type="button" class="secondary" data-closed="${esc(JSON.stringify(x.target))}">It's closed now — start a later check from here</button>` : ""}</li>`).join("")}</ul>` : "";
  const more = `<button type="button" class="secondary" id="more">Add 10 minutes</button>`;
  const choose = `<a href="#/s/${esc(sessionId)}/choose">Choose something to practise anyway</a>`;
  if (step.kind === "budget_spent") {
    view.innerHTML = `<h1>This session's time is used</h1>
      <p>Your answers and feedback are kept. These are still waiting, with their original times:</p>${leftList}
      <div class="row">${more}${finishButton}</div>`;
  } else if (step.kind === "nothing_fits") {
    view.innerHTML = `<h1>Nothing fits in the time left</h1>
      <p>Nothing was skipped or marked done; each need keeps its waiting time.${step.new_material_waits ? " New material is available but takes longer than the time left." : ""}</p>${leftList}
      <div class="row">${more}${finishButton} ${choose}</div>`;
  } else {
    view.innerHTML = `<h1>Nothing more to practise right now</h1>
      <p>${step.upcoming?.length ? `The next check is offered from ${esc(fmtTime(step.upcoming[0]))}.` : "Later checks appear here when they are due."}</p>
      ${leftList ? `<h2>Waiting</h2>${leftList}` : ""}
      <div class="row"><button type="button" id="finish">See this session's summary</button> ${choose}</div>`;
  }
  timer.set("progress_inspection", ctx);
  document.getElementById("more")?.addEventListener("click", async () => {
    const budget = (p.session.budget_seconds || 0) + 600;
    await api(`/sessions/${sessionId}/budget`, { base: p.session.ref.revision, budget_seconds: budget });
    route();
  });
  view.querySelectorAll("[data-closed]").forEach((b) => b.addEventListener("click", async () => {
    await api("/closed", { targets: [JSON.parse(b.dataset.closed)] });
    route();
  }));
  onFinish();
}

// --- the learner's own choice of what to practise (a recorded override) ---------------------

async function choosePage(sessionId) {
  const c = await api(`/sessions/${sessionId}/choices`);
  view.innerHTML = `<p><a href="#/s/${esc(sessionId)}/next">← Back</a></p><h1>Choose what to practise</h1>
    <p class="muted small">Your choice is recorded as yours. A goal whose check is not due counts as extra practice: its scheduled check stays as it is.</p>
    ${c.exercises.map((e) => `<div class="card">${esc(e.prompt)}
      <div class="small muted">about ${Math.round(e.seconds / 60) || 1} min</div>
      <ul class="small">${e.targets.map((t) => `<li>${esc(t.action)} — ${t.role === "owner" ? "its scheduled check" : "extra practice"}${t.blocked ? ` (${esc(t.blocked)})` : ""}</li>`).join("")}</ul>
      <button type="button" data-pick="${esc(e.exercise.id)}">Practise this</button></div>`).join("") || '<p class="muted">No exercise can be practised now.</p>'}
    <div class="row"><button type="button" class="secondary" id="fresh">Start new material instead</button></div>`;
  timer.set("progress_inspection", { session: c.session.ref });
  const pick = async (body) => {
    try {
      const step = await api(`/sessions/${sessionId}/next`, body);
      go(step.kind === "exercise" || step.resumed ? `#/s/${sessionId}` : `#/s/${sessionId}/next`);
    } catch (e) {
      alert(e.message);
    }
  };
  view.querySelectorAll("[data-pick]").forEach((b) => b.addEventListener("click", () => pick({ exercise_id: b.dataset.pick })));
  document.getElementById("fresh").addEventListener("click", () => pick({ new_material: true }));
}

// --- starting a session: a short proposal and a duration choice ----------------------------

function proposalText(p, minutes) {
  if (!p.ready && !p.repairs) {
    return `${p.new_material ? "Nothing is due. New material is available." : "Nothing is due and there is no new material."}${p.upcoming.length ? ` The next check is offered from ${fmtTime(p.upcoming[0])}.` : ""}`;
  }
  const head = minutes ? `${minutes} minutes.` : "No time limit.";
  const first = p.first ? ` Start with ${p.first.overdue ? "an overdue check" : "a due check"}: ${p.first.action}.` : " Nothing due fits this time.";
  const others = p.fits > 1 ? ` ${p.fits - 1} other check${p.fits > 2 ? "s" : ""} may fit.` : "";
  const repairs = p.repairs ? ` ${p.repairs} repair${p.repairs > 1 ? "s" : ""} waiting.` : "";
  const fresh = p.new_material ? " New material remains available; it adds future checks." : "";
  return `${head}${first}${others}${repairs}${fresh}`;
}

async function startPage(ids) {
  const curricula = ids.split(",");
  const saved = store.get("muninn.minutes");
  let minutes = Number.isInteger(saved) ? saved : 10;
  view.innerHTML = `<p><a href="#/">← Library</a></p><h1>Start a session</h1>
    <label for="minutes">How long do you have?</label>
    <select id="minutes">${DURATIONS.map(([m, label]) => `<option value="${m}" ${m === minutes ? "selected" : ""}>${label}</option>`).join("")}</select>
    <div class="card" id="proposal">…</div>
    <div class="row"><button type="button" id="go">Start</button></div>`;
  timer.set("progress_inspection", { context: [] });
  const show = async () => {
    const budget = minutes ? `&budget=${minutes * 60}` : "";
    const p = await api(`/proposal?curricula=${encodeURIComponent(ids)}${budget}`);
    document.getElementById("proposal").innerHTML = `<p>${esc(proposalText(p, minutes))}</p>
      ${p.blocked.length ? `<p class="small muted">${p.blocked.length} check${p.blocked.length > 1 ? "s" : ""} cannot be offered yet; the session will say why.</p>` : ""}`;
  };
  document.getElementById("minutes").addEventListener("change", (e) => {
    minutes = Number(e.target.value);
    store.set("muninn.minutes", minutes);
    show();
  });
  document.getElementById("go").addEventListener("click", async () => {
    const { session } = await api("/sessions", { curricula, budget_seconds: minutes ? minutes * 60 : null });
    location.hash = `#/s/${session.id}`;
  });
  await show();
}

async function studyPage(session, studyId) {
  const s = await api(`/studies/${studyId}`);
  view.innerHTML = `
    <p class="small muted">Focused help${s.uncertain ? ", offered as support while the cause is still uncertain" : ""}.
      Working through it is recorded as study, not as a test.</p>
    <h1>${esc(s.targets.join("; "))}</h1>
    <div class="card"><p class="teaching">${esc(s.content)}</p>
      ${s.derivation ? `<p class="small"><strong>Why:</strong> ${esc(s.derivation)}</p>` : ""}
      ${s.quotes.map((q) => `<blockquote>${esc(q)}</blockquote>`).join("")}
      <div class="small muted">Approach: ${esc(s.approach)}</div></div>
    <div class="row"><button type="button" id="done">I've worked through this</button>
      <button type="button" class="secondary" id="stop">Stop for now</button></div>`;
  timer.set("study", { session: session.ref, enrollment: oneEnrollment(session), context: [s.ref] });
  document.getElementById("done").addEventListener("click", async () => {
    await api(`/studies/${studyId}/complete`, { base: s.ref.revision, client_at: new Date().toISOString() });
    route();
  });
  document.getElementById("stop").addEventListener("click", () => finish(session));
}

async function practicePage(sessionId) {
  const p = await api(`/sessions/${sessionId}`);
  if (!p.attempt) return go(`#/s/${sessionId}/next`);
  const a = p.attempt;
  const ctx = { session: p.session.ref, enrollment: oneEnrollment(p.session), context: [a.ref] };
  if (a.status === "submitted") return waitForFeedback(sessionId, a, ctx);
  const backupKey = `muninn.draft.${a.ref.id}`;
  const backup = store.get(backupKey);
  const restored = backup && backup !== a.response;
  let base = a.ref.revision;
  view.innerHTML = `
    <p class="small muted">${esc(PURPOSE[a.purpose] || PURPOSE.initial)}</p>
    ${a.counts_as_practice ? '<p class="small">Earlier history changed after this was offered: your draft is kept, and this answer now counts as practice, not as a scheduled check.</p>' : ""}
    ${a.purpose === "initial" && a.roles.some((r) => r.role === "extra") ? `<p class="small">Extra practice for: ${esc(a.roles.filter((r) => r.role === "extra").map((r) => r.action).join("; "))}. Its scheduled check stays as it is.</p>` : ""}
    <h1>${esc(a.prompt)}</h1>
    <label for="answer">Your answer</label>
    <textarea id="answer" class="answer">${esc(restored ? backup : a.response)}</textarea>
    <div class="status" id="draft-status">${restored ? "Restored text that had not been saved yet." : ""}</div>
    <div id="hints">${a.hints.map((h, i) => h.text
      ? `<div class="card small"><strong>Hint ${i + 1}:</strong> ${esc(h.text)}</div>`
      : `<button type="button" class="secondary" data-hint="${esc(h.id)}">Show hint ${i + 1}</button> `).join("")}</div>
    <div class="row"><button type="button" id="submit">Submit answer</button>
      <button type="button" class="secondary" id="stop">Stop for now</button>
      ${a.purpose === "initial" ? `<a href="#/s/${esc(sessionId)}/choose">Practise something else</a>` : ""}</div>`;
  timer.set(a.purpose === "clarification" ? "diagnosis" : "answer", ctx);
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
  const { exposure } = await api(`/attempts/${attemptId}/feedback-viewed`, {});
  views.track(exposure.id);
  const quotes = f.criteria.flatMap((c) => c.quotes);
  const misread = f.criteria.some((c) => c.misread);
  const note = concernNote(f.concern);
  view.innerHTML = `
    <h1>${f.attempt.purpose === "clarification" ? "What your answer showed" : "Feedback"}</h1>
    <p class="muted">${esc(f.prompt)}</p>
    <div class="card"><strong>Your answer</strong><p>${highlight(f.attempt.response, quotes)}</p></div>
    <div class="card"><p>${esc(f.explanation)}</p></div>
    ${misread ? '<div class="card"><strong>This looks like a misread of the task, not a gap in what you know.</strong> Nothing more to practise here; it is not counted as a mistake.</div>' : ""}
    ${f.earlier_judgments.length ? `<div class="card"><strong>This judgment was corrected</strong> after: “${esc(f.revision_reason)}”. No new answer was added.
      <details><summary class="small">The earlier judgment (kept)</summary>${f.earlier_judgments.map(judgmentCard).join("<hr>")}</details></div>` : ""}
    ${reviewLink(f.review) ? `<div class="card">${reviewLink(f.review)}</div>` : ""}
    ${note ? `<div class="card"><strong>What happens next.</strong> ${esc(note)}</div>` : ""}
    ${f.ratings.map((r, i) => `<div class="card" id="rating-${i}"><strong>How well did you remember: ${esc(r.action)}?</strong>
      <div class="row">${r.choices.map((c) => `<button type="button" class="${r.choice === c ? "" : "secondary"}" data-rate="${i}" data-choice="${c}">${esc(CHOICE[c])}</button>`).join("")}</div>
      <p class="small muted" id="rated-${i}">${r.choices.length === 1 ? "The answer had a mistake, so this review counts as forgotten. " : "Rate your own recall, not the grade. "}${r.choice ? `Rated: ${esc(CHOICE[r.choice])}.` : "This review is saved only when you choose."}</p></div>`).join("")}
    <h2>Each part of the answer</h2>
    ${f.criteria.map((c) => `<div class="card">
        ${tag(c.outcome, OUTCOME[c.outcome])}${c.misread ? tag("unresolved", "probably a misread") : ""}${c.help === "shown" ? tag("helped", "hint used") : c.help === "unconfirmed" ? tag("unresolved", "hint sent, display not confirmed") : ""} ${esc(c.requirement)}
        ${c.quotes.map((q) => `<blockquote>${esc(q)}</blockquote>`).join("")}
        <div class="small muted">${esc(c.reason)}</div></div>`).join("")}
    <h2>${f.attempt.purpose === "clarification" ? "Where things stand (a focused question does not change this)" : "What this shows"}</h2>
    <ul class="plain">${f.targets.map((t) => `<li>${tag(t.label, LABEL[t.label])} ${esc(t.action)}
      <div class="small muted">${esc(t.reasons.join("; "))}</div></li>`).join("")}</ul>
    <details><summary>Show the reference answer</summary><div class="card">${esc(f.reference_response)}</div>
      <p class="small muted">Seeing this answer counts as practice, not as a later check.</p></details>
    <p class="small muted">Judged by ${esc(f.assessor?.name)} under protocol ${esc(f.assessor?.protocol_version)}.</p>
    <div class="row"><button type="button" id="next">Continue</button>
      <button type="button" class="secondary" id="finish">Finish session</button>
      ${f.disputable ? `<a href="#/d/${esc(attemptId)}">This judgment is wrong</a>` : ""}</div>`;
  const session = await api(`/sessions/${f.session.id}`);
  timer.set("feedback", { session: f.session, enrollment: oneEnrollment(session.session), context: [f.attempt.ref] });
  const unrated = new Set(f.ratings.map((r, i) => (r.choice ? null : i)).filter((i) => i !== null));
  const next = document.getElementById("next");
  const gate = () => {
    next.disabled = unrated.size > 0;
    next.title = unrated.size ? "Rate your recall first (or finish; you can rate it later)" : "";
  };
  gate();
  view.querySelectorAll("[data-rate]").forEach((b) => b.addEventListener("click", async () => {
    const r = f.ratings[Number(b.dataset.rate)];
    await api(`/attempts/${attemptId}/rate`, { target: r.target, choice: b.dataset.choice });
    document.querySelectorAll(`[data-rate="${b.dataset.rate}"]`).forEach((x) => { x.className = x === b ? "" : "secondary"; });
    document.getElementById(`rated-${b.dataset.rate}`).textContent = `Rated: ${CHOICE[b.dataset.choice]}. The next review is set from this rating.`;
    unrated.delete(Number(b.dataset.rate));
    gate();
  }));
  next.addEventListener("click", () => { location.hash = `#/s/${f.session.id}/next`; });
  document.getElementById("finish").addEventListener("click", () => finish(session.session));
}

async function finish(session) {
  await views.closeAll();  // leaving this page: its views are closed before the unmet needs are saved
  if (session.status !== "ended") {
    await api(`/sessions/${session.ref.id}/end`, { base: session.ref.revision, reason: "learner finished" }).catch(() => {});
  }
  timer.close();
  await timer.flush();
  location.hash = `#/s/${session.ref.id}/summary`;
}

// --- later checks: every check kept, and whether you are caught up -------------------------

const CHECK_STATUS = { consumed: "met on time", replaced: "replaced after teaching", invalidated: "no longer applies" };

function caughtUpText(c) {
  if (c.state === "caught_up") {
    return `Caught up on later checks as of ${fmtTime(c.as_of)}${c.scope === "active" ? " (started goals only; some selected goals are not started, paused or on hold)" : ""}.`;
  }
  return `${WAITING[c.state] || "Not caught up yet"}.`;
}

async function checksPage(id) {
  const v = await api(`/curricula/${id}/checks`);
  const k = v.counts;
  view.innerHTML = `<p><a href="#/c/${esc(id)}">← Outline</a></p><h1>Later checks: ${esc(v.curriculum.title)}</h1>
    <div class="card"><strong>${esc(caughtUpText(v.caught_up))}</strong>
      ${v.caught_up.pending.length ? `<ul class="small">${v.caught_up.pending.map((p) => `<li>${esc(p.action)}: ${esc(p.reason)}</li>`).join("")}</ul>` : ""}
      <p class="small muted">A statement about now: later checks keep coming, and earlier unmet checks stay in the history.</p></div>
    <p class="small">${k.met_on_time} met on time${k.reviewed_as_forgotten ? ` · ${k.reviewed_as_forgotten} reviewed as forgotten` : ""} · ${k.replaced_after_teaching} replaced after teaching · ${k.overdue} due now · ${k.upcoming} upcoming
      · answers: ${k.with_errors} with a mistake, ${k.answered_with_help} with help, ${k.unresolved_answers} unsettled, ${k.too_soon} too soon after seeing the answer</p>
    ${v.targets.map((t) => `<div class="card"><strong>${esc(t.action)}</strong> <span class="small muted">${t.type === "recall" ? "recall reviews (FSRS)" : t.type ? "capability checks (24 h, then 7 days)" : "not started"}</span>
      ${t.checks.length ? `<ul class="small">${t.checks.map((c) => `<li>Due ${esc(fmtTime(c.due_at))} — ${c.status === "open"
        ? (c.due_at && c.due_at <= v.caught_up.as_of ? "due now" : "upcoming") + (c.next_offer ? (c.next_offer.at ? `, offered from ${esc(fmtTime(c.next_offer.at))}` : ", waiting for an open view to be closed") : "")
        : c.status === "consumed" && t.type === "recall" ? "reviewed" : esc(CHECK_STATUS[c.status])}
        ${c.answers.map((a) => `<div class="muted">${esc(fmtTime(a.at))}: ${a.role === "owner" ? "the check" : "extra practice"}, ${a.label ? esc(LABEL[a.label]) : "not graded yet"}${a.effect ? ` (${esc(a.effect)})` : ""}</div>`).join("")}</li>`).join("")}</ul>`
        : '<p class="small muted">No later check yet.</p>'}</div>`).join("")}`;
  timer.set("progress_inspection", { context: [v.curriculum.ref] });
}

// --- following the same goals over time (routine-tracking-1) -------------------------------

async function trackPage(id) {
  const p = await api(`/curricula/${id}/tracking`);
  const running = p.plans.find((x) => x.lifecycle === "active");
  if (running) return go(`#/tr/${running.id}`);
  view.innerHTML = `<p><a href="#/c/${esc(id)}">← Outline</a></p><h1>Follow the same goals over time</h1>
    <p>This records a fixed comparison using your normal reviews: three one-week windows from now. It adds no extra questions and changes no due dates. Some windows may have no check.</p>
    ${p.population.length ? `<div class="card"><strong>Tracked (${p.population.length})</strong><ul class="small">${p.population.map((m) => `<li>${esc(m.action)} — baseline: ${m.baseline.state === "selected" ? "your last answer so far" : m.baseline.state === "missing" ? "none yet" : "two answers at the same moment"}${m.hold ? ` · on hold: ${esc(m.hold)}` : ""}${m.authoring_unavailable ? " · no exercise yet" : ""}</li>`).join("")}</ul></div>` : '<p class="error-text">Nothing is started yet. Start practice first; tracking follows practised goals.</p>'}
    ${p.outside.length ? `<p class="small muted">Not tracked: ${p.outside.map((o) => `${esc(o.action)} (${esc(o.reason)})`).join("; ")}</p>` : ""}
    <p class="small">Windows: ${p.windows.map((w) => `${esc(fmtTime(w.start))} – ${esc(fmtTime(w.end))}`).join("; ")}</p>
    ${p.population.length ? '<div class="row"><button type="button" id="start">Start tracking</button></div>' : ""}
    ${p.plans.length ? `<h2>Earlier plans</h2><ul>${p.plans.map((x) => `<li><a href="#/tr/${esc(x.id)}">${esc(fmtTime(x.frozen_at))}</a> (${esc(x.lifecycle)})</li>`).join("")}</ul>` : ""}`;
  timer.set("progress_inspection", { context: [] });
  document.getElementById("start")?.addEventListener("click", async () => {
    const { cohort } = await api(`/curricula/${id}/tracking`, {});
    location.hash = `#/tr/${cohort.id}`;
  });
}

const fraction = ([n, d]) => (d ? `${n} of ${d}` : "not available yet");

async function reportPage(id) {
  const r = await api(`/tracking/${id}`);
  view.innerHTML = `<p><a href="#/c/${esc(r.curriculum.id)}">← Outline</a></p><h1>Following the same goals</h1>
    <p class="small muted">Started ${esc(fmtTime(r.frozen_at))} · ${r.lifecycle === "stopped" ? `<strong>stopped</strong> ${esc(fmtTime(r.stopped_at))}` : r.lifecycle}
      · ${r.population.length} goals, fixed when tracking began. Intervening practice is allowed, so this is not retention without rehearsal.</p>
    ${r.windows.map((w) => `<div class="card"><strong>Window ${w.index + 1}</strong> <span class="small muted">${esc(fmtTime(w.start))} – ${esc(fmtTime(w.end))}${w.mature ? "" : " · still open"}</span>
      <ul class="small">${w.endpoints.map((e) => `<li>${esc(r.actions[e.target.id])}: ${esc(BUCKET[e.claims.performance.bucket])}${e.raw !== "N" ? ` (raw: ${esc(RAW[e.raw])})` : ""}
        ${e.reason ? `<span class="muted">— ${esc(e.reason)}</span>` : ""}${w.mature && ["QS", "QE", "QX"].includes(e.claims.performance.bucket) ? `<span class="muted"> · as a later check: ${esc(BUCKET[e.claims.later_check.bucket])}</span>` : ""}
        ${e.claims.performance.reasons.filter((x) => x.result !== "eligible").map((x) => `<span class="muted"> · ${esc(x.code.replace("_", " "))}: ${esc(x.result)}</span>`).join("")}</li>`).join("")}</ul>
      ${w.mature ? `<p class="small">Correct among graded answers: ${fraction(w.counts.formulas.raw_correct)} · planned checks that established the result: ${fraction(w.counts.formulas.qualified_coverage)} · answered: ${fraction(w.counts.formulas.checked)}</p>` : ""}</div>`).join("")}
    <p class="small">Time on this curriculum since tracking began: ${esc(fmtMs(r.cost.period.total_ms))}${r.cost.uncertain_spans ? ` (plus ${esc(fmtMs(r.cost.uncertain_known_ms))} that may belong to it)` : ""} · before tracking: ${esc(fmtMs(r.cost.before_tracking.total_ms))}</p>
    ${r.added.length ? `<p class="small muted">Added since tracking began (not in this comparison): ${r.added.map((a) => esc(a.action)).join("; ")}</p>` : ""}
    ${r.lifecycle === "active" ? '<div class="row"><button type="button" class="secondary" id="stop">Stop tracking</button></div>' : ""}`;
  timer.set("progress_inspection", { context: [] });
  document.getElementById("stop")?.addEventListener("click", async () => {
    if (!confirm("Stop tracking? Checks already assigned keep their results; later windows will show as missing.")) return;
    await api(`/tracking/${id}/stop`, { base: r.ref.revision, reason: "stopped by the learner" });
    route();
  });
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
    ${s.help.length ? `<h2>Help</h2><ul class="plain">${s.help.map((h) => `<li class="card">${esc(capital(h.approach))}
      <div class="small muted">${esc(h.targets.join("; "))} · ${h.status === "completed" ? "worked through" : "started, not finished"}</div></li>`).join("")}</ul>` : ""}
    ${s.concerns.length || s.clarifications ? `<h2>Follow-up</h2>
      <p class="small muted">Clarifying requests used this session: ${s.clarifications} of at most ${s.clarification_limit}.</p>
      <ul class="plain">${s.concerns.map((c) => `<li class="card">${esc(concernNote(c))}</li>`).join("")}</ul>` : ""}
    <p>Next check: ${esc(fmtTime(s.next_check))}</p>
    ${s.unmet.length ? `<h2>Still waiting</h2><p class="small muted">Nothing here was marked done or failed; each keeps its original waiting time.</p>
      <ul class="plain">${s.unmet.map((u) => `<li class="card small">${esc(u.action)}<div class="muted">${esc(capital(u.reason))}${u.waiting_since ? ` · waiting since ${esc(fmtTime(u.waiting_since))}` : ""}</div></li>`).join("")}</ul>` : ""}
    ${s.session.budget_seconds ? `<p class="small muted">Chosen time: ${esc(fmtMs(s.session.budget_seconds * 1000))}.</p>` : ""}
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
  timer.set("progress_inspection", { session: s.session.ref, enrollment: oneEnrollment(s.session) });
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
