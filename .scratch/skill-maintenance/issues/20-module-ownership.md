# Which modules own the learning rules and shared transactions?

Type: task
Label: wayfinder:task
Status: resolved
Mode: AFK
Assignee: Codex
Parent: ../map.md
Blocked by: none

## Question

Assess the existing modularization against the user's requirement for high internal cohesion and low coupling. Produce a concrete proposed module/interface design: responsibility and record ownership, allowed dependencies, shared-rule ownership, atomic workflows, external adapters, evolution constraints and verification obligations. Ground the choices in the current contracts and named audit cases. Do not implement the application or claim architecture quality from a diagram alone.

## Comments

2026-10-15 review follow-up: the user pointed to another agent's comments. The [original audit](../module-design-audit.md) is preserved; the [response](../module-design-review-response.md) evaluates all eighteen findings against the actual contracts and records the revisions and qualified disagreements. Record-kind coverage alone missed nested semantic ownership and recovery gaps. This remains a resolved design proposal with implementation checks outstanding, not a claim of proven low coupling.

2026-10-15: The user asks how modular the current design is and states that the system should use cohesive, decoupled modules. Codex claims the bounded assessment and design continuation. Baseline `0127a4f` has a four-module outline, strong behavioral/data contracts and atomicity requirements, but no complete ownership/dependency/interface contract. Preserve web delivery, the general learning scope, saved-progress compatibility and the design-only restriction. This task completes a reviewable proposal; broader human release/policy choices remain open.

## Answer

The [module/interface proposal](../module-design.md) defines Content, Evidence, Practice and Measurement as domain modules, supported by Web Interaction, Application Workflows and Library. It assigns all 27 current domain record kinds one owner, keeps shared interpretation rules with one semantic owner, specifies allowed dependencies and read/write interfaces, and traces atomic cross-module commands without giving the coordinator educational policy. Budget input and prospective endpoint assignment avoid a Practice–Measurement cycle; authoring packets avoid a Content–Evidence cycle.

The main spec, build plan, compatibility contract and observability plan/readiness notes now reference these constraints. Ten interface/integration obligations cover encapsulation, atomic correction, shared qualification, prospective assignment, historical context, budgets, external failures, migration and change locality. Document verification checked local links/anchors, record-owner coverage and the declared acyclic graph. This resolves the requested design assessment/proposal, not implementation, proven maintainability or the broader first-release decision. Context: `codex/research/observability-campaign`, baseline `0127a4f`.
