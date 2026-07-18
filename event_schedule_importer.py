#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Schedule Importer v1.0 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト

催事スケジュール（Google Sheets「18期 催事管理」・DS-EVT-0002）を読み取り専用で取り込み、
EventPlanRecordへ正規化して 07_Data/event_schedule/ に保存する。
**日々更新されるため毎朝実行する**（毎朝の型: fos_importer → event_schedule_importer → ceo_assistant → dashboard_generator）。

フロー: Google Sheets（公開CSV・認証不要）→ 本Importer → EventPlanRecord → Brief「Event Status」/ Dashboard「Today's/Upcoming Events」

重要ルール（CEO指示 2026-07-11）:
・**Brief/Dashboardのスケジュールに入れるのは「出店決定」のみ**（プランA/Bはデータとして保持・表示は営業状況欄のみ）
・読み取り専用（シートへの書き込み・変更はしない）
・Knowledge直行禁止（Data Layer経由。Planning中はLearning対象外）
・書き込み先は 07_Data/event_schedule/ のみ
・冪等（内容ハッシュが同じならスナップショット再保存しない）
・オフライン時は最新スナップショットへフォールバック（推測しない・取得日時を明示）

使い方:
    python3 event_schedule_importer.py            # 取込 + index.json更新
    python3 event_schedule_importer.py --check    # 読込と件数確認のみ（書き込みなし）
"""

import csv
import hashlib
import io
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

VERSION = "1.0"
STATE = "Experimental"

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "07_Data" / "event_schedule"     # 書き込みはここのみ
SNAP_DIR = OUT_DIR / "snapshots"
INDEX_PATH = OUT_DIR / "index.json"

SHEET_ID = "16kd-pP5vDQAgstrpyMZEFVqzW9446OhsiPJYBmdRm7k"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

CONFIRMED = "出店決定"  # Brief/Dashboard表示対象のステータス


def safe_write(path: Path, text: str):
    path = path.resolve()
    if not str(path).startswith(str(OUT_DIR.resolve())):
        raise PermissionError(f"書き込み禁止: {path} は 07_Data/event_schedule/ の外")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fetch_csv():
    """公開CSVを取得（読み取りのみ）。失敗時は最新スナップショットへフォールバック。"""
    try:
        with urllib.request.urlopen(CSV_URL, timeout=30) as r:
            raw = r.read().decode("utf-8")
        return raw, "online", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        snaps = sorted(SNAP_DIR.glob("*.csv")) if SNAP_DIR.exists() else []
        if not snaps:
            raise RuntimeError(f"シート取得失敗・スナップショットもなし: {e}")
        latest = snaps[-1]
        return latest.read_text(encoding="utf-8"), f"offline_fallback({latest.name})", latest.name[:10]


def iso(d: str):
    """'2026/9/16' → '2026-09-16'。空・不正はNone（推測しない）。"""
    d = (d or "").strip()
    if not d:
        return None
    try:
        return datetime.strptime(d, "%Y/%m/%d").strftime("%Y-%m-%d")
    except ValueError:
        return None


def build_records(raw_csv: str):
    rows = list(csv.reader(io.StringIO(raw_csv)))
    records = []
    for row in rows[1:]:  # 先頭行=ヘッダー（説明文含む）
        if len(row) < 12:
            continue
        no, status, name = row[0].strip(), row[1].strip(), row[2].strip()
        if not name or "合計" in name:
            continue
        records.append({
            "record_id": f"EVS-{no or 'x'}-{hashlib.md5(name.encode()).hexdigest()[:6]}",
            "no": no or None,
            "status": status or None,             # 出店決定 / プランA / プランB / null
            "confirmed": status == CONFIRMED,      # Brief/Dashboard表示対象
            "name": name,                          # 催事名
            "vendor": row[3].strip() or None,      # 販売会社
            "start": iso(row[4]), "end": iso(row[5]),
            "days": row[6].strip() or None,
            "setup_date": iso(row[7]),             # 搬入日
            "teardown_date": iso(row[8]),          # 搬出日
            "daily_budget_man": row[9].strip() or None,    # 売上日商予算(万円)
            "period_budget_man": row[10].strip() or None,  # 売上期間予算(万円)
            "month": row[11].strip() or None,
            "notes": (row[12].strip() or None) if len(row) > 12 else None,
        })
    return records


def main():
    check_only = "--check" in sys.argv
    raw, mode, fetched_at = fetch_csv()
    content_hash = hashlib.md5(raw.encode()).hexdigest()[:12]
    records = build_records(raw)
    confirmed = [r for r in records if r["confirmed"]]
    plans = [r for r in records if not r["confirmed"]]

    print(f"Event Schedule Importer v{VERSION} [{STATE}]（Sheets読み取り専用・{mode}）")
    print(f"催事: {len(records)}件 = 出店決定 {len(confirmed)}件（Brief/Dashboard表示対象）+ プランA/B等 {len(plans)}件（表示対象外）")
    for r in confirmed[:5]:
        print(f"  ■ {r['name']} {r['start']}〜{r['end']}（搬入{r['setup_date']}・日商予算{r['daily_budget_man']}万）")

    if check_only:
        print("--check: 書き込みなしで終了")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    if mode == "online":
        snap = SNAP_DIR / f"{today}_{content_hash}.csv"
        if not snap.exists():
            safe_write(snap, raw)
            print(f"スナップショット保存: {snap.name}")
        else:
            print("スナップショット: 同一内容のためスキップ（冪等）")

    index = {
        "meta": {"generator": f"Event Schedule Importer v{VERSION} [{STATE}]",
                 "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "source": f"Google Sheets（18期催事管理・{SHEET_ID[:8]}…・読み取り専用）",
                 "fetch_mode": mode, "fetched_at": fetched_at,
                 "content_hash": content_hash,
                 "note": "Brief/Dashboard表示は confirmed=true（出店決定）のみ。Planning Layer=Learning対象外。Knowledge直行禁止",
                 "total": len(records)},
        "summary": {"confirmed": len(confirmed), "plan_a": sum(1 for r in plans if r["status"] == "プランA"),
                    "plan_b": sum(1 for r in plans if r["status"] == "プランB")},
        "records": records,
    }
    safe_write(INDEX_PATH, json.dumps(index, ensure_ascii=False, indent=2))
    print(f"index.json更新: {len(records)}件 → Brief/Dashboard参照可能（表示は出店決定のみ）")


if __name__ == "__main__":
    main()
