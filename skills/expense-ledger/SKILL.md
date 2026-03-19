---
name: expense-ledger
description: "Track personal expenses and maintain a structured ledger with automatic categorization, duplicate detection, daily insertion, and dashboard generation. Use when Codex needs to: (1) record a new expense from natural-language text, (2) update an existing expense ledger for a specific day, (3) classify spending into common categories automatically, (4) detect possible duplicate bills when date-time and amount match, or (5) generate readable Markdown and HTML summaries with common bookkeeping charts."
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
3. Let the script auto-classify the expense unless the user explicitly provides a category.
4. If the script reports a duplicate, do not silently write the row. Double check with the user first unless they explicitly want to force the insertion.
5. After each successful write, regenerate the dashboard so the ledger stays current.

## Recommended Ledger Layout

Store the ledger in one folder, for example `~/expense-ledger-data/`, with these files:

- `transactions.csv`
- `dashboard.md`
- `dashboard.html`

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

Regenerate reports:

```bash
python3 scripts/ledger.py report --ledger-dir ~/expense-ledger-data
```

## Duplicate Detection

Treat an entry as a possible duplicate when:

- `date` matches
- `time` matches
- `amount` matches

If this happens, pause and double check with the user. The script will refuse to write unless `--force` is passed.

This rule is intentionally conservative and easy to explain.

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

The script classifies by keywords first. If confidence is weak, it falls back to `other`.

Read [category-rules.md](./references/category-rules.md) when adjusting or extending classification behavior.

## Output Standard

After every successful insertion, keep the ledger updated by regenerating:

- daily grouped entries
- monthly totals
- category totals
- top spending days
- charts in `dashboard.html`

## Working Style

When the user gives a new expense in plain language:

1. Parse the date, time, description, and amount.
2. Infer the category unless the user explicitly states one.
3. Check for duplicates before writing.
4. Insert into `transactions.csv`.
5. Regenerate `dashboard.md` and `dashboard.html`.

When the user asks to review spending:

1. Read the current ledger.
2. Use the generated dashboard first.
3. Summarize the most important trends rather than repeating every row.

## Boundaries

- Do not silently overwrite rows.
- Do not auto-merge possible duplicates without confirmation.
- Do not invent dates, times, or amounts if the input is ambiguous.
- Do not change old categories unless the user asks for reclassification.
