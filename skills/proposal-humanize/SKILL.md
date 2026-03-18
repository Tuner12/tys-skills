---
name: proposal-humanize
description: "Rewrite, polish, and humanize business proposals by using a reference proposal, brief, DOC/DOCX/PDF text extraction, or pasted sample as a style model. Use when Codex needs to: (1) imitate the structure, tone, and rhetorical flow of a reference proposal, (2) make a draft sound more natural, persuasive, and human-written, (3) reduce generic or AI-sounding phrasing, (4) tighten executive/business writing while preserving the user's facts, scope, and claims, or (5) produce a client-ready proposal in English or Chinese from rough material."
---

# Proposal Humanize

## Overview

Use this skill to transform a draft proposal into a cleaner, more convincing, more human-sounding version while preserving the user's actual commitments and constraints.

Treat the reference proposal as a style source, not as content to copy. Extract its structure, pacing, persuasive moves, and level of specificity, then rewrite the target proposal with original wording.

## Workflow

1. Identify the inputs.
   - Reference proposal or proposal excerpt
   - Target proposal to rewrite
   - Optional audience, region, tone, or response constraints
2. Determine the task shape.
   - If the user wants style transfer, first infer the reference document's structure and writing habits.
   - If the user wants humanization only, diagnose where the draft sounds generic, repetitive, padded, or mechanically formal.
   - If the user wants both, do style extraction first and humanization second.
3. Preserve meaning before improving expression.
   - Keep factual scope, deliverables, timelines, pricing logic, and risk statements unless the user asks to change them.
   - Do not invent certifications, metrics, clients, case studies, or legal promises.
4. Rewrite for business credibility.
   - Prefer concrete claims over inflated adjectives.
   - Prefer smooth transitions over abrupt bullet dumping.
   - Prefer selective emphasis over constant sales language.
5. Deliver the best useful output for the context.
   - Full rewritten proposal
   - Section-by-section rewrite
   - Side-by-side "before vs after" when comparison helps
   - Short rationale only when the user asks or when important constraints required interpretation

## Reference Extraction

When a reference proposal is provided, extract only the reusable writing pattern:

- Opening strategy: direct, relational, strategic, technical, or consultative
- Structural order: problem, objectives, solution, scope, differentiators, timeline, pricing, close
- Paragraph rhythm: short and punchy, medium and executive, or long and formal
- Evidence style: proof points, process detail, outcomes, or reassurance language
- Sales temperature: restrained, moderate, or assertive
- Level of formality: boardroom, procurement, founder-to-founder, agency, or partnership tone

Then apply that pattern to the user's proposal without mirroring distinctive phrases too closely.

## Humanization Rules

Humanization means removing signals of generic machine-written prose while keeping professionalism.

- Cut padded transitions such as empty "moreover", "furthermore", and "in today's dynamic landscape" phrasing unless they genuinely help flow.
- Replace abstract claims with specific business meaning.
- Vary sentence length and cadence. Avoid every sentence sounding equally balanced or equally polished.
- Break up repetitive triads and stacked buzzwords.
- Keep some plainspoken sentences. Not every line needs to sound elevated.
- Remove fake certainty. Use measured wording where the draft overclaims.
- Preserve natural emphasis: one strong point per sentence or paragraph is often enough.
- Prefer verbs over noun-heavy abstractions.
- Keep lists parallel, but avoid making all prose read like templated list copy.

Read [rewriting-checklist.md](./references/rewriting-checklist.md) when you need a more detailed pass.

## Output Standard

Default to polished client-facing prose unless the user asks for marked edits.

If the source is rough, silently fix:

- grammar
- redundancy
- awkward transitions
- mixed tone
- overexplaining
- obvious AI-style filler

If the source contains sensitive proposal language, preserve:

- contractual boundaries
- scope limitations
- dependencies and assumptions
- pricing qualifiers
- legal or operational caveats

## Working Style

When the user provides both reference and draft:

1. Infer the reference style in a short internal summary.
2. Rewrite the draft fully.
3. Run one more pass specifically for human cadence and non-generic wording.
4. Return the improved proposal directly unless the user asked for commentary.

When the user provides only a draft:

1. Infer the likely target tone from the draft and request context only if absolutely necessary.
2. Rewrite toward a credible business proposal voice.
3. Humanize aggressively enough to remove template-like phrasing, but do not make it casual unless requested.

## Boundaries

- Do not claim the text is "100% human" or promise detector outcomes.
- Do not imitate a named person's proprietary writing too closely.
- Do not preserve weak wording just because it appears in the reference.
- Do not add unsupported numbers, delivery promises, or compliance claims.
