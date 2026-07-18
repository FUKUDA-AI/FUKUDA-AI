#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Calendar Export v1.0 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト

催事スケジュール（07_Data/event_schedule/index.json・DS-EVT-0002）から
**Apple カレンダー取込用の .ics ファイル**を生成する（CEO指示 2026-07-11・Brief 7/11判断2）。

ルール:
・対象は**出店決定のみ**（プランA/Bは出力しない）
・生成イベント: 【催事】会期（終日・複数日）/【搬入】/【搬出】（終日）
・読み取り専用（index.jsonを読むだけ）。書き込み先は 06_Reports/calendar/ のみ
・日付つきファイル名で追記型（上書きしない）
・シートは日々更新されるため、更新後に再生成して再取込する
  （重複を避けるため、Apple カレンター側に専用カレンダー「NOMADO催事」を作って取込み、
    更新時はそのカレンダーを削除→新しい.icsを再取込する運用を推奨）

使い方:
    python3 event_calendar_export.py    # .ics生成（事前にevent_schedule_importer.py実行）
"""

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

VERSION = "1.0"
BASE_DIR = Path(__file__).resolve().parent
INDEX = BASE_DIR / "07_Data" / "event_schedule" / "index.json"
OUT_DIR = BASE_DIR / "06_Reports" / "calendar"


def esc(s):
    """ICSテキストエスケープ。"""
    return str(s).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def dt(d):  # '2026-09-16' → '20260916'
    return d.replace("-", "")


def vevent(uid, start, end_exclusive, summary, description=""):
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}@fukuda-ai.nomado",
        f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
        f"DTSTART;VALUE=DATE:{dt(start)}",
        f"DTEND;VALUE=DATE:{dt(end_exclusive)}",
        f"SUMMARY:{esc(summary)}",
    ]
    if description:
        lines.append(f"DESCRIPTION:{esc(description)}")
    lines.append("END:VEVENT")
    return lines


def plus1(d):
    return (date.fromisoformat(d) + timedelta(days=1)).isoformat()


def main():
    if not INDEX.exists():
        print("催事スケジュール未取込。先に python3 event_schedule_importer.py を実行してください")
        sys.exit(1)
    idx = json.load(open(INDEX, encoding="utf-8"))
    confirmed = [r for r in idx.get("records", []) if r.get("confirmed")]

    L = ["BEGIN:VCALENDAR", "VERSION:2.0",
         "PRODID:-//NOMADO FUKUDA AI//Event Calendar Export v" + VERSION + "//JA",
         "CALSCALE:GREGORIAN", "X-WR-CALNAME:NOMADO催事スケジュール",
         "X-WR-TIMEZONE:Asia/Tokyo"]
    n = 0
    for r in confirmed:
        name, rid = r["name"], r["record_id"]
        desc_parts = [f"販売会社: {r.get('vendor') or '-'}",
                      f"日商予算: {r.get('daily_budget_man') or '-'}万円 / 期間予算: {r.get('period_budget_man') or '-'}万円"]
        if r.get("notes"):
            desc_parts.append(f"備考: {r['notes']}")
        desc = "\n".join(desc_parts) + "\n出典: 18期催事管理シート（出店決定）"
        if r.get("start") and r.get("end"):
            L += vevent(f"{rid}-kaiki", r["start"], plus1(r["end"]),
                        f"【催事】{name}（{r.get('days') or '?'}日間）", desc); n += 1
        if r.get("setup_date"):
            L += vevent(f"{rid}-setup", r["setup_date"], plus1(r["setup_date"]),
                        f"【搬入】{name}", f"搬入日\n{desc}"); n += 1
        if r.get("teardown_date"):
            L += vevent(f"{rid}-teardown", r["teardown_date"], plus1(r["teardown_date"]),
                        f"【搬出】{name}", f"搬出日\n{desc}"); n += 1
    L.append("END:VCALENDAR")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    out = OUT_DIR / f"NOMADO催事スケジュール_{today}.ics"
    k = 1
    while out.exists():
        k += 1
        out = OUT_DIR / f"NOMADO催事スケジュール_{today}_{k}.ics"
    out.write_text("\r\n".join(L) + "\r\n", encoding="utf-8")
    print(f"生成: {out.name} — 出店決定{len(confirmed)}催事 → カレンダーイベント{n}件（会期/搬入/搬出）")
    print("取込方法: ファイルをダブルクリック → Apple カレンダーで追加先に「NOMADO催事」（新規作成推奨）を選択")


if __name__ == "__main__":
    main()
