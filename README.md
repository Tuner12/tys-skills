<div align="center">

# tys's skills

### A growing home for reusable Codex skills

[![GitHub Stars](https://img.shields.io/github/stars/Tuner12/tys-skills?labelColor=2f353d&color=4c566a)](https://github.com/Tuner12/tys-skills/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Tuner12/tys-skills?labelColor=2f353d&color=4c566a)](https://github.com/Tuner12/tys-skills/network/members)
[![last commit](https://img.shields.io/github/last-commit/Tuner12/tys-skills?logo=git&label=last%20commit)](https://github.com/Tuner12/tys-skills/commits/main)
[![repo size](https://img.shields.io/github/repo-size/Tuner12/tys-skills?label=repo%20size)](https://github.com/Tuner12/tys-skills)
[![top language](https://img.shields.io/github/languages/top/Tuner12/tys-skills?label=top%20language)](https://github.com/Tuner12/tys-skills)

![codex skills collection](https://img.shields.io/badge/codex%20skills-collection-6d28d9)
![status](https://img.shields.io/badge/status-active%20%26%20growing-0f766e)

</div>

> [!NOTE]
> This repository is designed as a long-term skill library, not a single-skill dump. New Codex skills can be added over time under a consistent structure.

> [!TIP]
> If a skill is useful enough to reuse twice, it belongs here.

## Overview

`tys's skills` collects self-contained Codex skills in one place so they can be versioned, improved, and extended over time. Each skill is packaged in its own directory and can include its own `SKILL.md`, references, scripts, assets, and agent metadata.

The current focus is practical, reusable workflow skills rather than one-off prompts.

## Highlights

- Reusable multi-skill repository structure
- Self-contained skill folders for cleaner maintenance
- Ready to grow into a broader personal skill library
- Includes a proposal rewriting and humanization skill built for real client-facing work

## Repository Layout

```text
tys-skills/
├── README.md
└── skills/
    ├── proposal-humanize/
        ├── SKILL.md
        ├── agents/
        └── references/
    └── readme-styler/
        ├── SKILL.md
        ├── agents/
        └── references/
```

## Current Skills

| Skill | Purpose | Status |
| --- | --- | --- |
| `proposal-humanize` | Rewrites business proposals using a reference proposal's structure, tone, and persuasive flow while removing generic AI-style phrasing | Active |
| `readme-styler` | Designs polished GitHub README files with stronger hierarchy, visuals, badges, and repository storytelling | Active |

## Featured Skill

### `proposal-humanize`

This skill is built for proposal work that needs more than cosmetic editing. It helps:

- infer style from a reference proposal
- restructure weak draft sections
- tighten business logic and persuasive flow
- remove generic, templated, or AI-sounding prose
- preserve actual scope, commitments, and commercial boundaries

Path: `skills/proposal-humanize/`

### `readme-styler`

This skill is built for repositories that need a stronger first impression on GitHub. It helps:

- redesign flat README files into clearer landing pages
- choose better section order and visual hierarchy
- add badges, callouts, tables, and repo maps without clutter
- match README tone to the repository type
- make a project look maintained, intentional, and easier to understand

Path: `skills/readme-styler/`

## Design Principles

- One folder per skill
- Keep each skill self-contained
- Prefer reusable workflow logic over ad hoc prompt fragments
- Preserve room for references, scripts, and assets as the library grows

## Adding More Skills

Add new skills under `skills/<skill-name>/` and keep each one independently usable. A typical skill can include:

- `SKILL.md`
- `agents/openai.yaml`
- `references/`
- `scripts/`
- `assets/`

## Roadmap

- Add more writing and document-oriented skills
- Expand the repository into a broader personal Codex toolkit
- Keep improving skill quality based on real usage

---

<div align="center">
Built as a living Codex skill library for repeatable workflows.
</div>
