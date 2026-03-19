#!/usr/bin/env python3
import argparse
import csv
import html
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta
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
    "food": [
        "lunch", "dinner", "breakfast", "coffee", "tea", "snack", "grocer", "meal", "restaurant", "milk", "fruit", "food",
        "午饭", "晚饭", "早餐", "早饭", "宵夜", "奶茶", "咖啡", "吃饭", "聚餐", "外卖", "水果", "超市", "买菜", "餐厅", "火锅"
    ],
    "transport": [
        "uber", "lyft", "taxi", "metro", "bus", "train", "gas", "parking", "toll", "transport",
        "打车", "地铁", "公交", "高铁", "火车", "停车", "油费", "过路费", "车费", "滴滴"
    ],
    "shopping": [
        "shopping", "buy", "bought", "clothes", "shirt", "shoes", "household", "amazon",
        "购物", "买了", "衣服", "鞋", "日用品", "淘宝", "京东", "拼多多"
    ],
    "entertainment": [
        "movie", "cinema", "game", "concert", "karaoke", "entertainment",
        "电影", "游戏", "演唱会", "ktv", "娱乐", "桌游"
    ],
    "bills": [
        "bill", "utility", "electric", "water", "internet", "phone", "insurance",
        "电费", "水费", "网费", "话费", "保险", "账单"
    ],
    "housing": [
        "rent", "furniture", "repair", "maintenance", "apartment",
        "房租", "家具", "维修", "住宿", "公寓"
    ],
    "medical": [
        "medicine", "medication", "clinic", "hospital", "doctor", "pharmacy", "drug",
        "药", "买药", "医院", "门诊", "诊所", "挂号", "体检"
    ],
    "education": [
        "tuition", "course", "class", "book", "education", "exam",
        "学费", "课程", "教材", "书", "考试", "报名费"
    ],
    "travel": [
        "flight", "hotel", "trip", "travel", "airbnb", "booking",
        "机票", "酒店", "民宿", "旅行", "旅游"
    ],
    "subscription": [
        "subscription", "monthly", "annual", "netflix", "spotify", "membership",
        "订阅", "会员", "月费", "年费", "自动续费"
    ],
    "gift": [
        "gift", "donation", "hongbao", "red envelope", "present",
        "礼物", "红包", "随礼", "捐款"
    ],
    "digital": [
        "openai", "chatgpt", "claude", "cursor", "github", "domain", "server", "cloud", "vps", "software", "saas",
        "域名", "服务器", "云服务", "软件", "会员服务", "ai"
    ],
    "income": [
        "salary", "refund", "reimbursement", "bonus", "income", "paid back",
        "工资", "退款", "报销", "奖金", "收入", "收款", "到账"
    ],
}


def ensure_ledger(ledger_dir: Path) -> Path:
    ledger_dir.mkdir(parents=True, exist_ok=True)
    csv_path = ledger_dir / "transactions.csv"
    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
    return csv_path


def now_local() -> datetime:
    return datetime.now()


def normalize_date(value: str) -> str:
    return datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d")


def normalize_time(value: str) -> str:
    if not value:
        return ""
    return datetime.strptime(value, "%H:%M").strftime("%H:%M")


def normalize_amount(value: str) -> str:
    return f"{float(value):.2f}"


def parse_relative_date(text: str, base: datetime) -> tuple[str | None, str]:
    date_value = None
    cleaned = text
    if "今天" in cleaned:
        date_value = base
        cleaned = cleaned.replace("今天", " ")
    elif "昨天" in cleaned:
        date_value = base - timedelta(days=1)
        cleaned = cleaned.replace("昨天", " ")
    elif "前天" in cleaned:
        date_value = base - timedelta(days=2)
        cleaned = cleaned.replace("前天", " ")
    elif "明天" in cleaned:
        date_value = base + timedelta(days=1)
        cleaned = cleaned.replace("明天", " ")
    return (date_value.strftime("%Y-%m-%d") if date_value else None, cleaned)


def parse_explicit_date(text: str, base: datetime) -> tuple[str | None, str]:
    cleaned = text
    patterns = [
        (r"\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b", True),
        (r"\b(\d{1,2})[-/](\d{1,2})\b", False),
        (r"(\d{1,2})月(\d{1,2})日", False),
    ]
    for pattern, has_year in patterns:
        match = re.search(pattern, cleaned)
        if not match:
            continue
        if has_year:
            year, month, day = map(int, match.groups())
        else:
            month, day = map(int, match.groups())
            year = base.year
        date_value = datetime(year, month, day).strftime("%Y-%m-%d")
        cleaned = cleaned.replace(match.group(0), " ", 1)
        return date_value, cleaned
    return None, cleaned


def parse_time_text(text: str) -> tuple[str, str]:
    cleaned = text
    hhmm = re.search(r"\b(\d{1,2}):(\d{2})\b", cleaned)
    if hhmm:
        hour = int(hhmm.group(1))
        minute = int(hhmm.group(2))
        prefix_match = re.search(r"(凌晨|早上|上午|中午|下午|晚上|傍晚)\s*$", cleaned[:hhmm.start()])
        if prefix_match:
            prefix = prefix_match.group(1)
            if prefix in {"下午", "晚上", "傍晚"} and hour < 12:
                hour += 12
            if prefix == "中午" and hour < 11:
                hour += 12
        time_value = f"{hour:02d}:{minute:02d}"
        cleaned = cleaned.replace(hhmm.group(0), " ", 1)
        return normalize_time(time_value), cleaned

    chinese_time = re.search(r"(凌晨|早上|上午|中午|下午|晚上|傍晚)?\s*(\d{1,2})点(?:(\d{1,2})分?)?", cleaned)
    if chinese_time:
        prefix, hour_text, minute_text = chinese_time.groups()
        hour = int(hour_text)
        minute = int(minute_text or 0)
        if prefix in {"下午", "晚上", "傍晚"} and hour < 12:
            hour += 12
        if prefix == "中午" and hour < 11:
            hour += 12
        time_value = f"{hour:02d}:{minute:02d}"
        cleaned = cleaned.replace(chinese_time.group(0), " ", 1)
        return normalize_time(time_value), cleaned

    cleaned = re.sub(r"(凌晨|早上|上午|中午|下午|晚上|傍晚)", " ", cleaned)
    return "", cleaned


def parse_amount_text(text: str) -> tuple[str, str]:
    cleaned = text
    currency_patterns = [
        r"(?:¥|￥|rmb\s*)?(\d+(?:\.\d{1,2})?)\s*(?:元|块钱|块)",
        r"\$(\d+(?:\.\d{1,2})?)",
    ]
    for pattern in currency_patterns:
        matches = list(re.finditer(pattern, cleaned, flags=re.IGNORECASE))
        if matches:
            match = matches[-1]
            amount_value = normalize_amount(match.group(1))
            cleaned = cleaned[:match.start()] + " " + cleaned[match.end():]
            return amount_value, cleaned

    amount_matches = list(re.finditer(r"(?<!\d)(\d+(?:\.\d{1,2})?)(?!\d)", cleaned))
    if amount_matches:
        match = amount_matches[-1]
        amount_value = normalize_amount(match.group(1))
        cleaned = cleaned[:match.start()] + " " + cleaned[match.end():]
        return amount_value, cleaned
    raise ValueError("entry must contain an amount")


def cleanup_description(text: str) -> str:
    cleaned = text
    cleaned = re.sub(r"(花了|花费|花|用了|买了|买|消费了|消费|支出|付了|付款|记账|记一下|记一笔|帮我记|收入|报销到账|报销|退款到账|退款)", " ", cleaned)
    cleaned = re.sub(r"(凌晨|早上|上午|中午|下午|晚上|傍晚)", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,.-，。")
    return cleaned or "unspecified expense"


def parse_entry_text(entry: str) -> dict:
    base = now_local()
    cleaned = entry.strip()

    date_value, cleaned = parse_relative_date(cleaned, base)
    if not date_value:
        explicit_date, cleaned = parse_explicit_date(cleaned, base)
        date_value = explicit_date
    if not date_value:
        iso_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", entry)
        if iso_match:
            date_value = normalize_date(iso_match.group(1))
            cleaned = cleaned.replace(iso_match.group(1), " ", 1)
    if not date_value:
        date_value = base.strftime("%Y-%m-%d")

    time_value, cleaned = parse_time_text(cleaned)
    amount_value, cleaned = parse_amount_text(cleaned)
    description = cleanup_description(cleaned)

    return {
        "date": normalize_date(date_value),
        "time": normalize_time(time_value),
        "description": description,
        "amount": amount_value,
        "source_text": entry,
    }


def classify(description: str) -> str:
    text = description.lower()
    scores = defaultdict(int)
    for category, words in CATEGORY_KEYWORDS.items():
        for word in words:
            if word.lower() in text:
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
    return [row for row in rows if row["date"] == date and row["amount"] == amount]


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
            lines.append(f"| {item['time'] or '-'} | {item['description']} | {item['category']} | {float(item['amount']):.2f} |")
        lines.append("")

    (ledger_dir / "dashboard.md").write_text("\n".join(lines), encoding="utf-8")


def html_shell(title: str, intro: str, sections: str, script: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
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
    .wrap {{ max-width: 1120px; margin: 0 auto; padding: 32px 20px 64px; }}
    .hero, .card {{ background: var(--card); border: 1px solid var(--line); border-radius: 24px; box-shadow: 0 12px 30px rgba(31,41,55,0.05); }}
    .hero {{ padding: 28px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; margin-top: 20px; }}
    .card {{ padding: 20px; }}
    h1, h2, h3 {{ margin: 0 0 12px; }}
    p, li {{ color: var(--muted); }}
    .bar-row {{ display: grid; grid-template-columns: 120px 1fr 72px; gap: 10px; align-items: center; margin: 10px 0; }}
    .bar {{ height: 12px; border-radius: 999px; background: #ece4d8; overflow: hidden; }}
    .fill {{ height: 100%; border-radius: 999px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ text-align: left; padding: 10px 8px; border-bottom: 1px solid var(--line); }}
    .pie-wrap {{ display: flex; justify-content: center; align-items: center; min-height: 280px; }}
    @media (max-width: 640px) {{
      .bar-row {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>{html.escape(title)}</h1>
      <p>{html.escape(intro)}</p>
    </section>
    {sections}
  </div>
  {script}
</body>
</html>"""


def render_dashboard_html(ledger_dir: Path, rows: list[dict]) -> None:
    by_category = total_by(rows, "category")
    by_month = total_by_month(rows)
    grouped = group_by_date(rows)
    category_json = json.dumps(by_category)
    month_json = json.dumps(by_month)

    day_cards = []
    for day, items in grouped.items():
        rows_html = "".join(
            f"<tr><td>{html.escape(item['time'] or '-')}</td><td>{html.escape(item['description'])}</td><td>{html.escape(item['category'])}</td><td>{float(item['amount']):.2f}</td></tr>"
            for item in sorted(items, key=lambda row: row["time"])
        )
        day_cards.append(
            f"<section class='card'><h3>{html.escape(day)}</h3><table><thead><tr><th>Time</th><th>Description</th><th>Category</th><th>Amount</th></tr></thead><tbody>{rows_html}</tbody></table></section>"
        )

    sections = f"""
    <div class="grid">
      <section class="card"><h2>Category Spend</h2><div id="category-bars"></div></section>
      <section class="card"><h2>Monthly Spend</h2><div id="month-bars"></div></section>
      <section class="card"><h2>Category Share</h2><div class="pie-wrap"><svg id="pie" width="260" height="260" viewBox="0 0 260 260"></svg></div></section>
    </div>
    <h2 style="margin-top:28px;">Daily Entries</h2>
    {' '.join(day_cards)}
    """
    script = f"""
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
    """
    (ledger_dir / "dashboard.html").write_text(html_shell("Expense Dashboard", "Auto-generated from transactions.csv. The ledger stays structured in CSV and readable in this dashboard.", sections, script), encoding="utf-8")


def render_reports(ledger_dir: Path, rows: list[dict]) -> None:
    render_markdown(ledger_dir, rows)
    render_dashboard_html(ledger_dir, rows)


def build_row(args: argparse.Namespace) -> dict:
    if args.entry:
        row = parse_entry_text(args.entry)
    else:
        if not (args.date and args.description and args.amount is not None):
            raise ValueError("structured input requires --date, --description, and --amount")
        row = {
            "date": normalize_date(args.date),
            "time": normalize_time(args.time or ""),
            "description": args.description.strip(),
            "amount": normalize_amount(str(args.amount)),
            "source_text": args.entry or "",
        }
    row["category"] = args.category or classify(row["description"])
    row["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return row


def add_row_to_ledger(ledger_dir: Path, row: dict, force: bool = False, interactive: bool = False) -> int:
    csv_path = ensure_ledger(ledger_dir)
    rows = load_rows(csv_path)
    duplicates = detect_duplicate(rows, row["date"], row["time"], row["amount"])
    if duplicates and not force:
        print("DUPLICATE_DETECTED")
        print(json.dumps(duplicates, ensure_ascii=False, indent=2))
        if interactive:
            answer = input("发现同一天金额相同的疑似重复账单，仍然写入吗？输入 yes 确认: ").strip().lower()
            if answer not in {"y", "yes"}:
                print("Skipped.")
                return 2
        else:
            return 2
    save_row(csv_path, row)
    rows = load_rows(csv_path)
    render_reports(ledger_dir, rows)
    print(json.dumps({"status": "added", "row": row}, ensure_ascii=False))
    return 0


def period_bounds(period: str, base: datetime) -> tuple[str, datetime, datetime]:
    if period in {"本周", "week", "this-week"}:
        start = base - timedelta(days=base.weekday())
        end = start + timedelta(days=6)
        return "week", start.replace(hour=0, minute=0, second=0, microsecond=0), end.replace(hour=23, minute=59, second=59, microsecond=0)
    if period in {"本月", "month", "this-month"}:
        start = base.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start.month == 12:
            next_month = start.replace(year=start.year + 1, month=1)
        else:
            next_month = start.replace(month=start.month + 1)
        end = next_month - timedelta(seconds=1)
        return "month", start, end
    raise ValueError("period must be 本周 or 本月")


def filter_rows_by_period(rows: list[dict], start: datetime, end: datetime) -> list[dict]:
    result = []
    for row in rows:
        day = datetime.strptime(row["date"], "%Y-%m-%d")
        if start.date() <= day.date() <= end.date():
            result.append(row)
    return result


def summarize_rows(rows: list[dict], period_label: str) -> str:
    total = sum(float(row["amount"]) for row in rows)
    count = len(rows)
    by_category = total_by(rows, "category")
    top_category = by_category[0] if by_category else ("none", 0.0)
    by_day = sorted(
        ((day, sum(float(item["amount"]) for item in items)) for day, items in group_by_date(rows).items()),
        key=lambda item: (-item[1], item[0]),
    )
    top_day = by_day[0] if by_day else ("none", 0.0)
    largest = sorted(rows, key=lambda row: (-float(row["amount"]), row["date"]))[:3]
    lines = [
        f"{period_label}消费总结",
        f"- 总支出: {total:.2f}",
        f"- 记录笔数: {count}",
        f"- 最大分类: {top_category[0]} ({top_category[1]:.2f})",
        f"- 花费最高的一天: {top_day[0]} ({top_day[1]:.2f})",
        "- 最大额支出:",
    ]
    for row in largest:
        lines.append(f"  - {row['date']} {row['description']} {float(row['amount']):.2f} [{row['category']}]")
    return "\n".join(lines)


def render_period_summary(ledger_dir: Path, rows: list[dict], period_key: str, start: datetime, end: datetime) -> tuple[Path, Path]:
    period_rows = filter_rows_by_period(rows, start, end)
    label = "本周" if period_key == "week" else "本月"
    category_data = total_by(period_rows, "category")
    day_data = sorted(
        ((day, sum(float(item["amount"]) for item in items)) for day, items in group_by_date(period_rows).items()),
        key=lambda item: item[0],
    )
    top_rows = sorted(period_rows, key=lambda row: (-float(row["amount"]), row["date"]))[:10]
    intro = f"{label}范围: {start.strftime('%Y-%m-%d')} 到 {end.strftime('%Y-%m-%d')}。共 {len(period_rows)} 笔记录。"

    category_json = json.dumps(category_data)
    day_json = json.dumps(day_data)

    top_table = "".join(
        f"<tr><td>{html.escape(row['date'])}</td><td>{html.escape(row['description'])}</td><td>{html.escape(row['category'])}</td><td>{float(row['amount']):.2f}</td></tr>"
        for row in top_rows
    )

    sections = f"""
    <div class="grid">
      <section class="card"><h2>分类占比</h2><div class="pie-wrap"><svg id="pie" width="260" height="260" viewBox="0 0 260 260"></svg></div></section>
      <section class="card"><h2>分类排行</h2><div id="category-bars"></div></section>
      <section class="card"><h2>每日支出</h2><div id="day-bars"></div></section>
    </div>
    <section class="card" style="margin-top:20px;">
      <h2>分析摘要</h2>
      <pre style="white-space:pre-wrap;font-family:Georgia,'Times New Roman',serif;color:#6b7280;">{html.escape(summarize_rows(period_rows, label))}</pre>
    </section>
    <section class="card" style="margin-top:20px;">
      <h2>大额支出</h2>
      <table><thead><tr><th>Date</th><th>Description</th><th>Category</th><th>Amount</th></tr></thead><tbody>{top_table}</tbody></table>
    </section>
    """
    script = f"""
    <script>
      const categoryData = {category_json};
      const dayData = {day_json};
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
      renderBars('day-bars', dayData);
      renderPie('pie', categoryData);
    </script>
    """

    suffix = start.strftime("%Y-%m-%d") if period_key == "week" else start.strftime("%Y-%m")
    html_path = ledger_dir / f"{period_key}-summary-{suffix}.html"
    md_path = ledger_dir / f"{period_key}-summary-{suffix}.md"
    html_path.write_text(html_shell(f"{label}消费总结", intro, sections, script), encoding="utf-8")
    md_path.write_text(summarize_rows(period_rows, label), encoding="utf-8")
    return md_path, html_path


def do_init(args: argparse.Namespace) -> int:
    ledger_dir = Path(os.path.expanduser(args.ledger_dir))
    ensure_ledger(ledger_dir)
    render_reports(ledger_dir, [])
    print(f"Initialized ledger at {ledger_dir}")
    return 0


def do_add(args: argparse.Namespace) -> int:
    ledger_dir = Path(os.path.expanduser(args.ledger_dir))
    row = build_row(args)
    return add_row_to_ledger(ledger_dir, row, force=args.force)


def do_chat(args: argparse.Namespace) -> int:
    ledger_dir = Path(os.path.expanduser(args.ledger_dir))
    ensure_ledger(ledger_dir)
    print("记账模式已启动。直接输入账单，例如：今天午饭 25元 / 昨天打车 18.5 / 3月18日咖啡 4.5")
    print("输入 empty 或 quit 退出。")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line or line.lower() in {"quit", "exit", "q"}:
            break
        try:
            parsed = parse_entry_text(line)
            row = {**parsed, "category": classify(parsed["description"]), "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            add_row_to_ledger(ledger_dir, row, interactive=True)
        except Exception as exc:
            print(f"无法识别这条账单: {exc}")
    print(f"Ledger updated in {ledger_dir}")
    return 0


def do_report(args: argparse.Namespace) -> int:
    ledger_dir = Path(os.path.expanduser(args.ledger_dir))
    csv_path = ensure_ledger(ledger_dir)
    rows = load_rows(csv_path)
    render_reports(ledger_dir, rows)
    print(f"Generated reports in {ledger_dir}")
    return 0


def do_summary(args: argparse.Namespace) -> int:
    ledger_dir = Path(os.path.expanduser(args.ledger_dir))
    csv_path = ensure_ledger(ledger_dir)
    rows = load_rows(csv_path)
    period_key, start, end = period_bounds(args.period, now_local())
    md_path, html_path = render_period_summary(ledger_dir, rows, period_key, start, end)
    print(summarize_rows(filter_rows_by_period(rows, start, end), "本周" if period_key == "week" else "本月"))
    print(f"\nMarkdown: {md_path}")
    print(f"HTML: {html_path}")
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

    chat_parser = subparsers.add_parser("chat")
    chat_parser.add_argument("--ledger-dir", required=True)
    chat_parser.set_defaults(func=do_chat)

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--ledger-dir", required=True)
    report_parser.set_defaults(func=do_report)

    summary_parser = subparsers.add_parser("summary")
    summary_parser.add_argument("--ledger-dir", required=True)
    summary_parser.add_argument("--period", required=True)
    summary_parser.set_defaults(func=do_summary)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
