#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Events Importer v1.0 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト

催事実績データ（Excel / CSV）を読み込み、共通フォーマット（EventRecord）へ正規化して
07_Data/events/normalized/ と index.json に保存する。
Morning Brief・催事AI・CEO補佐AIの共通データ基盤（Connector Architecture v1.0準拠）。

Layer: Connector+Importer（催事）→ Data Layer（07_Data/events/）
参照: 07_Data/events/raw/（読み取り専用・変更しない）
更新: 07_Data/events/normalized/ と index.json のみ

重要ルール:
・元データ（raw/）は変更・削除しない（読み取り専用）
・推測禁止: 読めないセル・無い列は null。計算で導ける値（日数=終了日-開始日+1、
  日商=売上÷日数）のみ derived フラグつきで補完する（推測ではなく算術）
・冪等: record_id（ファイル名+催事名+開始日のハッシュ）で重複排除。再実行安全
・既存ファイルを削除しない

使い方:
    python3 events_importer.py            # raw/ を取り込み normalized/ + index.json 更新
    python3 events_importer.py --check    # raw/ の検出と列マッピングの確認のみ（書き込みなし）

rawへの投入方法:
    07_Data/events/raw/ へ .xlsx / .csv を置いて実行するだけ（ファイル名は自由）
"""

import csv
import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime, date
from pathlib import Path

VERSION = "1.0"
STATE = "Experimental"

BASE_DIR = Path(__file__).resolve().parent
EVENTS_DIR = BASE_DIR / "07_Data" / "events"
RAW_DIR = EVENTS_DIR / "raw"
NORM_DIR = EVENTS_DIR / "normalized"
INDEX_PATH = EVENTS_DIR / "index.json"

# ---- 列名マッピング（ゆらぎ吸収。ここに無い列は無視し、metaに記録） ----
COLUMN_ALIASES = {
    "event_name": ["催事名", "イベント名", "催事", "企画名", "タイトル"],
    "brand":      ["ブランド", "brand", "出店ブランド"],
    "venue":      ["会場", "会場名", "場所", "開催場所", "店舗"],
    "start_date": ["開始日", "開始", "初日", "会期開始", "from", "開催日"],
    "end_date":   ["終了日", "最終日", "会期終了", "to"],
    "sales":      ["売上", "売上高", "売上金額", "売上合計", "総売上"],
    "profit":     ["利益", "粗利", "粗利益", "利益額"],
    "daily_sales": ["日商", "日販", "平均日商"],
    "days":       ["日数", "開催日数", "会期日数"],
    "yoy":        ["前年比", "昨対", "昨年比", "前年対比"],
    "notes":      ["メモ", "備考", "コメント", "特記"],
}


def norm_header(h):
    return unicodedata.normalize("NFKC", str(h or "")).strip().lower()


def build_column_map(headers):
    """ヘッダー行 → EventRecordフィールドの対応表。マッピング不能な列は unmapped へ。"""
    cmap, unmapped = {}, []
    for i, h in enumerate(headers):
        nh = norm_header(h)
        if not nh:
            continue
        hit = None
        for field, aliases in COLUMN_ALIASES.items():
            if any(norm_header(a) == nh or norm_header(a) in nh for a in aliases):
                hit = field
                break
        if hit and hit not in cmap.values():
            cmap[i] = hit
        else:
            unmapped.append(str(h))
    return cmap, unmapped


def parse_number(v):
    """数値パース。読めなければNone（推測しない）。"""
    if v is None or (isinstance(v, str) and not v.strip()):
        return None
    if isinstance(v, (int, float)):
        return v
    s = unicodedata.normalize("NFKC", str(v))
    s = re.sub(r"[,¥円\s]", "", s)
    pct = s.endswith("%")
    s = s.rstrip("%")
    try:
        n = float(s)
        return n / 100 if pct else (int(n) if n == int(n) else n)
    except ValueError:
        return None


def parse_date(v):
    """日付パース。読めなければNone。"""
    if v is None:
        return None
    if isinstance(v, (datetime, date)):
        return v.strftime("%Y-%m-%d")
    s = unicodedata.normalize("NFKC", str(v)).strip()
    if not s:
        return None
    s2 = re.sub(r"[年月/.]", "-", s).replace("日", "")
    for fmt in ("%Y-%m-%d", "%y-%m-%d", "%m-%d"):
        try:
            d = datetime.strptime(s2, fmt)
            if fmt == "%m-%d":
                return None  # 年不明の日付は推測しない
            return d.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def read_rows(path: Path):
    """Excel(.xlsx/.xlsm) / CSV から (headers, rows) を返す。読み取り専用。"""
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active  # v1.0は先頭シートのみ（複数シートはv1.1で対応）
        rows = [[c for c in row] for row in ws.iter_rows(values_only=True)]
        wb.close()
    elif path.suffix.lower() == ".csv":
        for enc in ("utf-8-sig", "cp932", "utf-8"):
            try:
                with open(path, encoding=enc, newline="") as f:
                    rows = list(csv.reader(f))
                break
            except UnicodeDecodeError:
                continue
        else:
            return None, None
    else:
        return None, None
    rows = [r for r in rows if any(c not in (None, "") for c in r)]
    if not rows:
        return None, None
    return rows[0], rows[1:]


def to_record(headers, cmap, row, source_file):
    vals = {f: None for f in COLUMN_ALIASES}
    for i, field in cmap.items():
        if i < len(row):
            raw = row[i]
            if field in ("sales", "profit", "daily_sales", "days", "yoy"):
                vals[field] = parse_number(raw)
            elif field in ("start_date", "end_date"):
                vals[field] = parse_date(raw)
            else:
                vals[field] = str(raw).strip() if raw not in (None, "") else None

    if not vals["event_name"] and not vals["venue"]:
        return None  # 催事名も会場も無い行はレコード化しない

    derived = []
    if vals["days"] is None and vals["start_date"] and vals["end_date"]:
        d = (datetime.strptime(vals["end_date"], "%Y-%m-%d")
             - datetime.strptime(vals["start_date"], "%Y-%m-%d")).days + 1
        if d > 0:
            vals["days"] = d
            derived.append("days")
    if vals["daily_sales"] is None and vals["sales"] and vals["days"]:
        vals["daily_sales"] = round(vals["sales"] / vals["days"])
        derived.append("daily_sales")

    rid = "EVT-" + hashlib.md5(
        f"{source_file}|{vals['event_name']}|{vals['venue']}|{vals['start_date']}".encode()
    ).hexdigest()[:10]
    return {
        "record_id": rid,
        "event_name": vals["event_name"], "brand": vals["brand"], "venue": vals["venue"],
        "start_date": vals["start_date"], "end_date": vals["end_date"],
        "sales": vals["sales"], "profit": vals["profit"],
        "daily_sales": vals["daily_sales"], "days": vals["days"], "yoy": vals["yoy"],
        "notes": vals["notes"],
        "source_file": source_file, "derived_fields": derived,
        "imported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "importer_version": f"v{VERSION}", "pii_filtered": True,
    }


def import_events(raw_dir: Path = RAW_DIR, check_only: bool = False):
    raw_dir.mkdir(parents=True, exist_ok=True)
    NORM_DIR.mkdir(parents=True, exist_ok=True)

    existing = {}
    if INDEX_PATH.exists():
        existing = {e["record_id"]: e for e in json.load(open(INDEX_PATH, encoding="utf-8"))["events"]}

    files = sorted([p for p in raw_dir.iterdir()
                    if p.suffix.lower() in (".xlsx", ".xlsm", ".csv") and not p.name.startswith("~")])
    print(f"Events Importer v{VERSION} [{STATE}]")
    print(f"raw/: {len(files)}ファイル検出")

    new, skipped_rows = 0, 0
    for f in files:
        headers, rows = read_rows(f)
        if headers is None:
            print(f"  ⚠ 読めない形式: {f.name}")
            continue
        cmap, unmapped = build_column_map(headers)
        print(f"  {f.name}: {len(rows)}行 / マッピング列{len(cmap)} / 未対応列{len(unmapped)}{'（' + ', '.join(unmapped[:5]) + '）' if unmapped else ''}")
        if check_only:
            continue
        for row in rows:
            rec = to_record(headers, cmap, row, f.name)
            if rec is None:
                skipped_rows += 1
                continue
            if rec["record_id"] in existing:
                continue  # 冪等: 既存は上書きしない
            existing[rec["record_id"]] = rec
            (NORM_DIR / f"{rec['record_id']}.json").write_text(
                json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
            new += 1

    if check_only:
        print("--check: 書き込みなしで終了")
        return

    events = sorted(existing.values(), key=lambda e: e.get("start_date") or "")
    with_sales = [e for e in events if e.get("sales")]
    summary = {
        "total_events": len(events),
        "with_sales": len(with_sales),
        "total_sales": sum(e["sales"] for e in with_sales) if with_sales else None,
        "avg_sales": round(sum(e["sales"] for e in with_sales) / len(with_sales)) if with_sales else None,
        "venues": sorted({e["venue"] for e in events if e.get("venue")}),
        "date_range": [events[0]["start_date"], events[-1]["start_date"]] if events else None,
    }
    index = {
        "meta": {"generator": f"Events Importer v{VERSION} [{STATE}]",
                 "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "note": "催事実績の索引。Morning Brief・催事AI・CEO補佐AIが参照する。生データはraw/（変更禁止）、正規化レコードはnormalized/",
                 "summary": summary},
        "events": events,
    }
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"新規レコード: {new}件 / スキップ行: {skipped_rows} / index合計: {len(events)}件")
    if summary["avg_sales"]:
        print(f"サマリー: 売上あり{summary['with_sales']}件・平均売上 {summary['avg_sales']:,}円")


if __name__ == "__main__":
    import_events(check_only="--check" in sys.argv)
