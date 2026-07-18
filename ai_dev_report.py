#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Dev Report Generator v1.0 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト

「AI開発レポート」— FUKUDA AI自身の開発案件（Learning Cycle / Dashboard / Result Layer /
Importer / レビュー待ち / 保留）を、Morning Briefから**完全分離**して表示する別画面。

背景（CEO指示 2026-07-11）:
    Morning BriefはCEOが会社を経営するためのレポートであり、
    FUKUDA AIを開発するためのレポートではない。
    Briefの判断候補の正本はFOS（実業データ）のみ。
    AI開発タスクは本レポートに表示する。

入力（すべて読み取り専用）:
    10_AI_Memory/PENDING.md / NEXT.md / CURRENT_STATE.md（Current Sprint/Mode）
    09_Learning/insights・patterns の各draft log / 01_Knowledge/knowledge_index.json

出力: 06_Reports/ai_dev_report/YYYY-MM-DD.md（追記型・上書き禁止・書込先はここのみ）

使い方:
    python3 ai_dev_report.py            # レポート生成
    python3 ai_dev_report.py --check    # 読込確認のみ（書き込みなし）
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

VERSION = "1.0"
STATE = "Experimental"

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "06_Reports" / "ai_dev_report"   # 書き込みはここのみ
MEMORY_DIR = BASE_DIR / "10_AI_Memory"


def safe_write(path: Path, text: str):
    path = path.resolve()
    if not str(path).startswith(str(OUT_DIR.resolve())):
        raise PermissionError(f"書き込み禁止: {path} は 06_Reports/ai_dev_report/ の外")
    if path.exists():
        raise PermissionError(f"上書き禁止: {path}（追記型命名を使う）")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def jload(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def read_pending():
    """PENDING.mdの未完了項目（旧Brief候補ロジックをこちらへ移設）。"""
    p = MEMORY_DIR / "PENDING.md"
    if not p.exists():
        return []
    items = []
    for line in p.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"\| (\S+) \| (.+?) \| (.+?) \| (.+?) \|$", line.strip())
        if not m:
            continue
        no, item, place, prio = (x.strip() for x in m.groups())
        if no in ("#",) or "---" in no:
            continue
        if "~~" in item or "✅" in item or prio == "完了":
            continue
        items.append({"no": no, "item": re.sub(r"\*\*", "", item), "place": place, "priority": prio})
    return items


def read_current(name, max_lines):
    p = MEMORY_DIR / f"{name}.md"
    if not p.exists():
        return []
    return [l.strip() for l in p.read_text(encoding="utf-8").split("\n")
            if l.strip().startswith("- ") or l.strip().startswith("| Current")][:max_lines]


def next_path(today):
    p = OUT_DIR / f"{today}.md"
    n = 1
    while p.exists():
        n += 1
        p = OUT_DIR / f"{today}_{n}.md"
    return p


def main():
    check_only = "--check" in sys.argv
    today = datetime.now().strftime("%Y-%m-%d")
    pending = read_pending()
    nexts = read_current("NEXT", 8)
    ins = jload(BASE_DIR / "09_Learning" / "insights" / "insight_draft_log.json") or {"insights": []}
    pat = jload(BASE_DIR / "09_Learning" / "patterns" / "pattern_draft_log.json") or {"patterns": []}
    ki = jload(BASE_DIR / "01_Knowledge" / "knowledge_index.json") or {"knowledge": []}
    in_review = sum(1 for k in ki["knowledge"] if k.get("status") in ("draft", "in_review"))

    print(f"AI Dev Report v{VERSION} [{STATE}]（Morning Briefから分離・書込先=06_Reports/ai_dev_report/のみ）")
    print(f"PENDING未完了: {len(pending)}件 / Insight draft: {len(ins['insights'])} / "
          f"Pattern draft: {len(pat['patterns'])} / Knowledge in_review: {in_review}")
    if check_only:
        print("--check: 書き込みなしで終了")
        return

    L = [f"# AI開発レポート — {today}",
         "",
         f"発行: AI Dev Report v{VERSION} [{STATE}]（{datetime.now().strftime('%H:%M')}）",
         "**FUKUDA AI開発の案件のみ**を扱う（Morning Briefには載せない。経営判断はFOS→Briefへ）。",
         "",
         "---", "",
         "## 🔧 レビュー待ち・保留（PENDING）", ""]
    if pending:
        for it in pending:
            L.append(f"- #{it['no']}【{it['priority']}】{it['item'][:100]}（{it['place']}）")
    else:
        L.append("- なし")
    L += ["", "## ⏭ 次Sprint候補（NEXT.md）", ""]
    L += (nexts or ["- なし"])
    L += ["", "## 🧠 Learning Cycle開発状況", "",
          f"- Insight Draft: {len(ins['insights'])}件 / Pattern Draft: {len(pat['patterns'])}件 / "
          f"Knowledge in_review: {in_review}件",
          "",
          "---",
          "*本レポートの案件はCEOの指示があるまで実行されません（AI_CHARTER準拠）。*"]
    path = next_path(today)
    safe_write(path, "\n".join(L))
    print(f"発行: {path}")


if __name__ == "__main__":
    main()
