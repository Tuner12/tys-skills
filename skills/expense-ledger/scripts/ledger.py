#!/usr/bin/env python3
import argparse
import csv
import html
import json
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


COLUMNS = [
    "date",
    "time",
    "description",
    "amount",
    "category",
    "source_text",
    "created_at",
]


CATEGORY_KEYWORDS = {
    "food": ["lunch", "dinner", "breakfast", "coffee", "tea", "snack", "grocer", "meal", "restaurant", "milk", "fruit", "food"],
    "transport": ["uber", "lyft", "taxi", "metro", "bus", "train", "gas", "parking", "toll", "transport"],
    "shopping": ["shopping", "buy", "bought", "clothes", "shirt", "shoes", "household", "amazon"],
    "entertainment": ["movie", "cinema", "game", "concert", "karaoke", "entertainment"],
    "bills": ["bill", "utility", "electric", "water", "internet", "phone", "insurance"],
    "housing": ["rent", "furniture", "repair", "maintenance", "apartment"],
    "medical": ["medicine", "medication", "clinic", "hospital", "doctor", "pharmacy", "drug"],
    "education": ["tuition", "course", "class", "book", "education", "exam"],
    "travel": ["flight", "hotel", "trip", "travel", "airbnb", "booking"],
    "subscription": ["subscription", "monthly", "annual", "netflix", "spotify", "membership"],
    "gift": ["gift", "donation", "hongbao", "red envelope", "present"],
    "digital": ["openai", "chatgpt", "claude", "cursor", "github", "domain", "server", "cloud", "vps", "software", "saas"],
    "income": ["salary", "refund", "reimbursement", "bonus", "income", "paid back"],
}


def ensure_ledger(ledger_dir: Path) -> Path:
    ledger_dir.mkdir(parents=True, exist_ok=True)
    csv_path = ledger_dir / "transactions.csv"
    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
    return csv_path


def parse_entry_text(entry: str) -> dict:
    date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", entry)
    time_match = re.search(r"\b(\d{1,2}:\d{2})\b", entry)
    amount_matches = re.findall(r"(?<!\d)(\d+(?:\.\d{1,2})?)(?!\d)", entry)
    if not date_match or not amount_matches:
        raise ValueError("entry must contain at least a YYYY-MM-DD date and an amount")

    date_value = date_match.group(1)
    time_value = time_match.group(1) if time_match else "00:00"
    amount_value = amount_matches[-1]

    cleaned = entry
    cleaned = cleaned.replace(date_value, "", 1)
    if time_match:
        cleaned = cleaned.replace(time_value, "", 1)
    cleaned = re.sub(rf"{re.escape(amount_value)}(?!.*{re.escape(amount_value)})", "", cleaned, count=1).strip()
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,-")
    if not cleaned:
        cleaned = "unspecified expense"

    return {
        "date": normalize_date(date_value),
        "time": normalize_time(time_value),
        "description": cleaned,
        "amount": normalize_amount(amount_value),
        "source_text": entry,
    }


def normalize_date(value: str) -> str:
    return datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d")


def normalize_time(value: str) -> str:
    return datetime.strptime(value, "%H:%M").strftime("%H:%M")


def normalize_amount(value: str) -> str:
    return f"{float(value):.2f}"


def classify(description: str) -> str:
    text = description.lower()
    scores = defaultdict(int)
    for category, words in CATEGORY_KEYWORDS.items():
        for word in words:
            if word in text:
                scores[category] += 1
    if not scores:
        return "other"
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))[0][0]


def load_rows(csv_path: Path) -> list[dict]:
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_row(csv_path: Path, row: dict) -> None:
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writerow(row)


def detect_duplicate(rows: list[dict], date: str, time: str, amount: str) -> list[dict]:
    return [
        row for row in rows
        if row["date"] == date and row["time"] == time and row["amount"] == amount
    ]


def group_by_date(rows: list[dict]) -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["date"]].append(row)
    return dict(sorted(grouped.items(), reverse=True))


def total_by(rows: list[dict], key: str) -> list[tuple[str, float]]:
    totals = defaultdict(float)
    for row in rows:
        totals[row[key]] += float(row["amount"])
    return sorted(totals.items(), key=lambda item: (-item[1], item[0]))


def total_by_month(rows: list[dict]) -> list[tuple[str, float]]:
    totals = defaultdict(float)
    for row in rows:
        totals[row["date"][:7]] += float(row["amount"])
    return sorted(totals.items())


def render_markdown(ledger_dir: Path, rows: list[dict]) -> None:
    total = sum(float(row["amount"]) for row in rows)
    by_category = total_by(rows, "category")
    by_month = total_by_month(rows)
    top_days = sorted(
        ((day, sum(float(item["amount"]) for item in items)) for day, items in group_by_date(rows).items()),
        key=lambda item: (-item[1], item[0]),
    )[:10]

    lines = [
        "# Expense Dashboard",
        "",
        f"- Total records: {len(rows)}",
        f"- Total spend: {total:.2f}",
        "",
        "## Category Summary",
        "",
        "| Category | Amount |",
        "| --- | ---: |",
    ]
    for category, amount in by_category:
        lines.append(f"| {category} | {amount:.2f} |")

    lines += [
        "",
        "## Monthly Summary",
        "",
        "| Month | Amount |",
        "| --- | ---: |",
    ]
    for month, amount in by_month:
        lines.append(f"| {month} | {amount:.2f} |")

    lines += [
        "",
        "## Top Spending Days",
        "",
        "| Date | Amount |",
        "| --- | ---: |",
    ]
    for day, amount in top_days:
        lines.append(f"| {day} | {amount:.2f} |")

    lines += ["", "## Entries By Day", ""]
    for day, items in group_by_date(rows).items():
        lines.append(f"### {day}")
        lines.append("")
        lines.append("| Time | Description | Category | Amount |")
        lines.append("| --- | --- | --- | ---: |")
        for item in sorted(items, key=lambda row: row["time"]):
            lines.append(
                f"| {item['time']} | {item['description']} | {item['category']} | {float(item['amount']):.2f} |"
            )
        lines.append("")

    (ledger_dir / "dashboard.md").write_text("\n".join(lines), encoding="utf-8")


def render_html(ledger_dir: Path, rows: list[dict]) -> None:
    by_category = total_by(rows, "category")
    by_month = total_by_month(rows)
    grouped = group_by_date(rows)

    category_json = json.dumps(by_category)
    month_json = json.dumps(by_month)

    day_cards = []
    for day, items in grouped.items():
        rows_html = "".join(
            f"<tr><td>{html.escape(item['time'])}</td><td>{html.escape(item['description'])}</td><td>{html.escape(item['category'])}</td><td>{float(item['amount']):.2f}</td></tr>"
            for item in sorted(items, key=lambda row: row["time"])
        )
        day_cards.append(
            f"<section class='day-card'><h3>{html.escape(day)}</h3><table><thead><tr><th>Time</th><th>Description</th><th>Category</th><th>Amount</th></tr></thead><tbody>{rows_html}</tbody></table></section>"
        )

    html_text = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Expense Dashboard</title>
  <style>
    :root {{
      --bg: #f6f3ee;
      --card: #fffaf3;
      --ink: #1f2937;
      --muted: #6b7280;
      --accent: #0f766e;
      --accent-2: #d97706;
      --line: #e5dccf;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Georgia, 'Times New Roman', serif; color: var(--ink); background: linear-gradient(180deg, #f4efe8 0%, #f8f6f1 100%); }}
    .wrap {{ max-width: 1080px; margin: 0 auto; padding: 32px 20px 64px; }}
    .hero {{ background: var(--card); border: 1px solid var(--line); border-radius: 24px; padding: 28px; box-shadow: 0 12px 30px rgba(31,41,55,0.05); }}
    h1, h2, h3 {{ margin: 0 0 12px; }}
    p {{ color: var(--muted); }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 18px; margin-top: 20px; }}
    .card {{ background: var(--card); border: 1px solid var(--line); border-radius: 20px; padding: 20px; }}
    .bar-row {{ display: grid; grid-template-columns: 120px 1fr 72px; gap: 10px; align-items: center; margin: 10px 0; }}
    .bar {{ height: 12px; border-radius: 999px; background: #ece4d8; overflow: hidden; }}
    .fill {{ height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--accent), var(--accent-2)); }}
    .pie-wrap {{ display: flex; justify-content: center; align-items: center; min-height: 300px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ text-align: left; padding: 10px 8px; border-bottom: 1px solid var(--line); }}
    .day-card {{ background: rgba(255,250,243,0.9); border: 1px solid var(--line); border-radius: 20px; padding: 18px; margin-top: 18px; }}
    .section-title {{ margin-top: 28px; }}
    @media (max-width: 640px) {{
      .bar-row {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>Expense Dashboard</h1>
      <p>Auto-generated from transactions.csv. The ledger stays structured in CSV and readable in this dashboard.</p>
    </section>
    <div class="grid">
      <section class="card">
        <h2>Category Spend</h2>
        <div id="category-bars"></div>
      </section>
      <section class="card">
        <h2>Monthly Spend</h2>
        <div id="month-bars"></div>
      </section>
      <section class="card">
        <h2>Category Share</h2>
        <div class="pie-wrap"><svg id="pie" width="260" height="260" viewBox="0 0 260 260"></svg></div>
      </section>
    </div>
    <h2 class="section-title">Daily Entries</h2>
    {''.join(day_cards)}
  </div>
  <script>
    const categoryData = {category_json};
    const monthData = {month_json};
    const palette = ['#0f766e', '#d97706', '#7c3aed', '#2563eb', '#be123c', '#0891b2', '#65a30d', '#9333ea'];

    function renderBars(targetId, data) {{
      const max = Math.max(...data.map(item => item[1]), 1);
      const root = document.getElementById(targetId);
      root.innerHTML = data.map(([label, value], idx) => `
        <div class="bar-row">
          <div>${{label}}</div>
          <div class="bar"><div class="fill" style="width:${{(value / max) * 100}}%; background:${{palette[idx % palette.length]}};"></div></div>
          <div>${{value.toFixed(2)}}</div>
        </div>
      `).join('');
    }}

    function renderPie(targetId, data) {{
      const total = data.reduce((sum, item) => sum + item[1], 0) || 1;
      const svg = document.getElementById(targetId);
      const cx = 130, cy = 130, r = 90;
      let start = 0;
      let slices = '';
      data.forEach(([label, value], idx) => {{
        const angle = (value / total) * Math.PI * 2;
        const end = start + angle;
        const x1 = cx + r * Math.cos(start - Math.PI / 2);
        const y1 = cy + r * Math.sin(start - Math.PI / 2);
        const x2 = cx + r * Math.cos(end - Math.PI / 2);
        const y2 = cy + r * Math.sin(end - Math.PI / 2);
        const large = angle > Math.PI ? 1 : 0;
        slices += `<path d="M ${{cx}} ${{cy}} L ${{x1}} ${{y1}} A ${{r}} ${{r}} 0 ${{large}} 1 ${{x2}} ${{y2}} Z" fill="${{palette[idx % palette.length]}}"></path>`;
        start = end;
      }});
      svg.innerHTML = slices + '<circle cx="130" cy="130" r="46" fill="#fffaf3"></circle>';
    }}

    renderBars('category-bars', categoryData);
    renderBars('month-bars', monthData);
    renderPie('pie', categoryData);
  </script>
</body>
</html>"""
    (ledger_dir / "dashboard.html").write_text(html_text, encoding="utf-8")


def build_row(args: argparse.Namespace) -> dict:
    if args.entry:
        row = parse_entry_text(args.entry)
    else:
        if not (args.date and args.description and args.amount is not None):
            raise ValueError("structured input requires --date, --description, and --amount")
        row = {
            "date": normalize_date(args.date),
            "time": normalize_time(args.time or "00:00"),
            "description": args.description.strip(),
            "amount": normalize_amount(str(args.amount)),
            "source_text": args.entry or "",
        }
    row["category"] = args.category or classify(row["description"])
    row["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return row


def do_init(args: argparse.Namespace) -> int:
    ledger_dir = Path(os.path.expanduser(args.ledger_dir))
    ensure_ledger(ledger_dir)
    render_markdown(ledger_dir, [])
    render_html(ledger_dir, [])
    print(f"Initialized ledger at {ledger_dir}")
    return 0


def do_add(args: argparse.Namespace) -> int:
    ledger_dir = Path(os.path.expanduser(args.ledger_dir))
    csv_path = ensure_ledger(ledger_dir)
    rows = load_rows(csv_path)
    row = build_row(args)
    duplicates = detect_duplicate(rows, row["date"], row["time"], row["amount"])
    if duplicates and not args.force:
        print("DUPLICATE_DETECTED")
        print(json.dumps(duplicates, ensure_ascii=False, indent=2))
        return 2
    save_row(csv_path, row)
    rows = load_rows(csv_path)
    render_markdown(ledger_dir, rows)
    render_html(ledger_dir, rows)
    print(json.dumps({"status": "added", "row": row}, ensure_ascii=False))
    return 0


def do_report(args: argparse.Namespace) -> int:
    ledger_dir = Path(os.path.expanduser(args.ledger_dir))
    csv_path = ensure_ledger(ledger_dir)
    rows = load_rows(csv_path)
    render_markdown(ledger_dir, rows)
    render_html(ledger_dir, rows)
    print(f"Generated reports in {ledger_dir}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Maintain an expense ledger with reports.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--ledger-dir", required=True)
    init_parser.set_defaults(func=do_init)

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--ledger-dir", required=True)
    add_parser.add_argument("--entry")
    add_parser.add_argument("--date")
    add_parser.add_argument("--time")
    add_parser.add_argument("--description")
    add_parser.add_argument("--amount")
    add_parser.add_argument("--category")
    add_parser.add_argument("--force", action="store_true")
    add_parser.set_defaults(func=do_add)

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--ledger-dir", required=True)
    report_parser.set_defaults(func=do_report)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
