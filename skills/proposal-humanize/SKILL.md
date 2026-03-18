---
name: proposal-humanize
description: "Rewrite, polish, and humanize business proposals by using a reference proposal, brief, DOC/DOCX/PDF text extraction, or pasted sample as a style model. Use when Codex needs to: (1) imitate the structure, tone, and rhetorical flow of a reference proposal, (2) make a draft sound more natural, persuasive, and human-written, (3) reduce generic or AI-sounding phrasing, (4) tighten executive/business writing while preserving the user's facts, scope, and claims, or (5) produce a client-ready proposal in English or Chinese from rough material."
---

# Proposal Humanize

## Overview

Use this skill to transform a draft proposal into a cleaner, more convincing, more human-sounding version while preserving the user's actual commitments and constraints.

Treat the reference proposal as a style source, not as content to copy. Extract its structure, pacing, persuasive moves, and level of specificity, then rewrite the target proposal with original wording.

This skill is not just for light polishing. Use it as a proposal rewriting system: diagnose what is weak, infer the target commercial voice, rebuild sections where needed, and only then run a humanization pass.

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

## Three-Pass Method

Always think in three passes when the user asks for proposal humanization:

1. Diagnostic pass
   - Identify what makes the draft weak: generic claims, vague value, list-heavy structure, repeated buzzwords, stiff cadence, overclaiming, or unclear differentiation.
   - Identify what must not change: pricing logic, scope boundaries, delivery assumptions, regulatory language, or contractual qualifiers.
2. Rewrite pass
   - Rebuild the draft at the paragraph and section level, not just sentence level.
   - Reorder sections when the current structure weakens persuasion or clarity.
   - Strengthen the business narrative: why this matters, why this approach, why this team, why now.
3. Humanization pass
   - Remove formulaic phrasing.
   - Add more natural cadence and selective plainspoken phrasing.
   - Reduce "perfectly polished" symmetry so the result sounds written, not generated.

If the original draft is poor, prioritize reconstruction over surface editing.

## Proposal-Specific Rewriting

A strong proposal usually does more than sound polished. It builds confidence in sequence.

Use these proposal moves where appropriate:

- Frame the client's situation before presenting the solution.
- Translate features into business consequences.
- Explain approach with enough operational detail to sound credible.
- Show restraint. Confidence is stronger than hype.
- Make differentiators feel relevant to the buyer, not self-congratulatory.
- Close with clarity on next steps, partnership logic, or decision readiness.

When a proposal reads like generic service copy, replace broad statements with one of these:

- a sharper problem statement
- a more concrete delivery approach
- clearer ownership or sequencing
- a cleaner statement of business value
- a more grounded closing paragraph

## Reference Extraction

When a reference proposal is provided, extract only the reusable writing pattern:

- Opening strategy: direct, relational, strategic, technical, or consultative
- Structural order: problem, objectives, solution, scope, differentiators, timeline, pricing, close
- Paragraph rhythm: short and punchy, medium and executive, or long and formal
- Evidence style: proof points, process detail, outcomes, or reassurance language
- Sales temperature: restrained, moderate, or assertive
- Level of formality: boardroom, procurement, founder-to-founder, agency, or partnership tone

Then apply that pattern to the user's proposal without mirroring distinctive phrases too closely.

Also extract the reference document's implicit choices:

- how quickly it gets to the point
- whether it sells through outcomes or process confidence
- how much detail it spends on scope versus relationship
- whether it sounds premium, technical, operator-led, or consultative
- how forcefully it asks for action at the end

If the reference is stronger than the target draft, let the target inherit the reference's decision-making pattern, not just its wording style.

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
- Replace ornamental polish with believable specificity.
- Allow slight asymmetry in sentence shape so the draft does not feel machine-balanced.
- Cut "consulting brochure" language when it says less than a simpler sentence would.

Read [rewriting-checklist.md](./references/rewriting-checklist.md) when you need a more detailed pass.

## Anti-Patterns

Watch for these proposal failure modes and correct them decisively:

- opening with generic market language instead of the client's actual need
- paragraphs that say the company is excellent without showing how
- long lists of capabilities with no decision logic
- repeated "tailored / seamless / robust / end-to-end" phrasing
- over-formal language that creates distance instead of trust
- inflated certainty around timelines, impact, or implementation ease
- closing paragraphs that sound like boilerplate vendor copy

If these appear repeatedly, do not lightly edit around them. Rewrite the whole section.

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

For high-value proposal work, prefer full rewritten sections over fragmented sentence tweaks.

## Output Formats

Choose the output shape that best fits the user's material:

- Full rewrite: use when the draft is complete but weak
- Structural rewrite: use when the section order is wrong or the narrative is thin
- Humanize-only pass: use when the content is sound but the language feels synthetic
- Reference-aligned rewrite: use when the user provides a strong sample proposal and wants matching energy and structure

Unless asked otherwise, output only the improved proposal text.

## Working Style

When the user provides both reference and draft:

1. Infer the reference style in a short internal summary.
2. Diagnose the target draft's weaknesses.
3. Rewrite the draft fully, including structural changes if needed.
4. Run one more pass specifically for human cadence and non-generic wording.
5. Return the improved proposal directly unless the user asked for commentary.

When the user provides only a draft:

1. Infer the likely target tone from the draft and request context only if absolutely necessary.
2. Diagnose whether the issue is structure, credibility, cadence, or all three.
3. Rewrite toward a credible business proposal voice.
4. Humanize aggressively enough to remove template-like phrasing, but do not make it casual unless requested.

## Quality Bar

Before finalizing, verify that the rewritten proposal:

- sounds like a competent person making a commercial case
- preserves all material facts from the user's draft
- improves clarity at the section level, not only line by line
- contains fewer generic adjectives and more meaningful claims
- feels more persuasive without sounding louder
- no longer reads like default AI business copy

## Boundaries

- Do not claim the text is "100% human" or promise detector outcomes.
- Do not imitate a named person's proprietary writing too closely.
- Do not preserve weak wording just because it appears in the reference.
- Do not add unsupported numbers, delivery promises, or compliance claims.
