---
name: expense-ledger
description: "Track personal expenses and maintain a structured ledger with automatic categorization, duplicate detection, daily insertion, and dashboard generation. Use when Codex needs to: (1) record a new expense from natural-language text in English or Chinese, (2) handle Chinese bookkeeping requests such as '记账', '记一笔', '今天花了', '帮我记一下', '昨天买了', or '我花了多少钱', (3) update an existing expense ledger for a specific day, (4) classify spending into common categories automatically, (5) detect possible duplicate bills when the same day and amount both match, (6) run an interactive Chinese bookkeeping session where the user keeps entering bills one by one, (7) generate readable Markdown and HTML summaries with common bookkeeping charts, or (8) generate Chinese week/month spending summaries such as '本周' and '本月' with charts and short analysis."
---

# Expense Ledger

## Overview

Use this skill to maintain a personal expense ledger that stays easy to read and easy to grow.

The recommended presentation format is:

- `transactions.csv` as the single source of truth
- `dashboard.md` for quick reading in text or GitHub-style viewers
- `dashboard.html` for cleaner visual charts

This split is the most practical tradeoff. CSV makes updates and deduplication reliable, while Markdown and HTML make review much easier than raw rows.

## Workflow

1. Use `scripts/ledger.py init` to create a new ledger folder if it does not exist.
2. Use `scripts/ledger.py add` to record each new expense.
3. Use `scripts/ledger.py chat` when the user wants to start bookkeeping mode first and then type expenses one by one.
4. Let the script auto-classify the expense unless the user explicitly provides a category.
5. If the script reports a duplicate, do not silently write the row. Treat same-day and same-amount entries as suspicious and double check first unless the user explicitly wants to force the insertion.
6. After each successful write, regenerate the dashboard so the ledger stays current.

## Recommended Ledger Layout

Store the ledger in one folder, for example `~/expense-ledger-data/`, with these files:

- `transactions.csv`
- `dashboard.md`
- `dashboard.html`
- `week-summary-*.md`
- `week-summary-*.html`
- `month-summary-*.md`
- `month-summary-*.html`

This is easier to maintain than one file per day and still supports daily browsing because the dashboard groups entries by day.

## Commands

Initialize a ledger:

```bash
python3 scripts/ledger.py init --ledger-dir ~/expense-ledger-data
```

Add an expense from structured fields:

```bash
python3 scripts/ledger.py add \
  --ledger-dir ~/expense-ledger-data \
  --date 2026-03-18 \
  --time 12:30 \
  --description "lunch with lab group" \
  --amount 18.50
```

Add an expense from a natural-language sentence:

```bash
python3 scripts/ledger.py add \
  --ledger-dir ~/expense-ledger-data \
  --entry "2026-03-18 12:30 lunch with lab group 18.50"
```

Add an expense from a more natural Chinese sentence:

```bash
python3 scripts/ledger.py add \
  --ledger-dir ~/expense-ledger-data \
  --entry "今天中午午饭 25元"
```

Start interactive bookkeeping mode:

```bash
python3 scripts/ledger.py chat --ledger-dir ~/expense-ledger-data
```

Regenerate reports:

```bash
python3 scripts/ledger.py report --ledger-dir ~/expense-ledger-data
```

Generate a weekly or monthly summary:

```bash
python3 scripts/ledger.py summary --ledger-dir ~/expense-ledger-data --period 本周
python3 scripts/ledger.py summary --ledger-dir ~/expense-ledger-data --period 本月
```

## Duplicate Detection

Treat an entry as a possible duplicate when:

- `date` matches
- `amount` matches

If this happens, pause and double check with the user. The script will refuse to write unless `--force` is passed.

This rule is intentionally conservative and easy to explain. The ledger is day-based by default, so precise time is optional rather than required.

## Categorization

Default categories include:

- food
- transport
- shopping
- entertainment
- bills
- housing
- medical
- education
- travel
- subscription
- gift
- digital
- income
- other

The script classifies by keywords first in both English and Chinese. If confidence is weak, it falls back to `other`.

Read [category-rules.md](./references/category-rules.md) when adjusting or extending classification behavior.

## Output Standard

After every successful insertion, keep the ledger updated by regenerating:

- daily grouped entries
- monthly totals
- category totals
- top spending days
- charts in `dashboard.html`

When the user asks for weekly or monthly review, also generate:

- a short terminal summary
- a Markdown summary file
- an HTML summary file with period charts

## Working Style

When the user gives a new expense in plain language:

1. Parse the date, description, and amount.
2. Infer the category unless the user explicitly states one.
3. Check for duplicates before writing.
4. Insert into `transactions.csv`.
5. Regenerate `dashboard.md` and `dashboard.html`.

When the user wants a conversational Chinese workflow:

1. Start `scripts/ledger.py chat`.
2. Let the user keep entering lines such as `今天咖啡 18`, `昨天地铁 4`, or `3月18日晚上聚餐 86元`.
3. Confirm duplicates before inserting when same-day and same-amount entries match.
4. Stop when the user enters `quit`, `exit`, `q`, or an empty line.

When the user asks to review spending:

1. Read the current ledger.
2. Use the generated dashboard first.
3. Summarize the most important trends rather than repeating every row.

When the user asks for `本周` or `本月` summary:

1. Run `scripts/ledger.py summary`.
2. Print a short summary directly in the terminal.
3. Generate the corresponding Markdown and HTML files.
4. Highlight total spend, largest category, top spending day, and a few large expenses.

## Boundaries

- Do not silently overwrite rows.
- Do not auto-merge possible duplicates without confirmation.
- Do not invent dates, times, or amounts if the input is ambiguous.
- Do not change old categories unless the user asks for reclassification.
