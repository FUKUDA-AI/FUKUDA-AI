#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Airレジ Importer v1.0 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト

AirレジのエクスポートCSVを読み込み、共通フォーマット（SalesRecord・35項目）へ正規化して
07_Data/airregi/normalized/ と index.json に保存する。
催事AI・CEO補佐AIの判断材料（催事別/商品別売上・KN-EVT-0001定量検証・Result照合）の入力源。

設計書: 07_Data/airregi/README.md v1.2（CEO回答8点反映済み）
Layer: Connector+Importer（Airレジ）→ Data Layer（07_Data/airregi/）
参照: 07_Data/airregi/raw/（読み取り専用）/ dataset_type_table.json（判別テーブル・読み取り専用）
      07_Data/events/index.json（催事照合・読み取り専用）
更新: 07_Data/airregi/normalized/ と index.json のみ（書込ホワイトリスト・他はPermissionError）

重要ルール（CEO確定 2026-07-07）:
・CSV原本（raw/）は変更・削除しない
・文字コードは自動判別（UTF-8 BOM → Shift_JIS → UTF-8。全失敗は取込まず報告）
・dataset_typeは判別テーブル（外部定義）のみを根拠にヘッダーから判別。
  未知ヘッダーは取込まずCEO確認へ（unknown報告）
・event_name / store_name はraw/サブフォルダ名から。EventRecordと完全一致のみ確定。
  推測できない場合はnull（未確定リストへ）
・売上はAirレジ出力値をそのまま保存（sales_definition="unknown"・税込/割引の推測禁止）
・欠損日を0円補完しない（データのある日だけを事実として保存）
・未マッピング列はraw_fieldsへ保持（重複列名は位置サフィックス _1〜）
・Knowledge直行禁止（Data Layerまで）
・冪等: record_idで重複排除。再実行しても新規0件

使い方:
    python3 airregi_importer.py            # raw/ を取り込み normalized/ + index.json 更新
    python3 airregi_importer.py --check    # 検出・文字コード・type判別・列マッピング確認のみ（書き込みなし）
    python3 airregi_importer.py --base DIR # テスト用: 別ベースディレクトリ（構成は 07_Data/airregi/ と同じ）
"""

import csv
import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

VERSION = "1.0"
STATE = "Experimental"

BASE_DIR = Path(__file__).resolve().parent
AIRREGI_DIR = BASE_DIR / "07_Data" / "airregi"
EVENTS_INDEX = BASE_DIR / "07_Data" / "events" / "index.json"

RECORD_FIELDS = [
    "record_id", "source", "channel", "event_name", "store_name", "terminal_id",
    "business_date", "period_start", "period_end", "dataset_type",
    "product_name", "product_code", "product_id", "category", "tax_type",
    "qty", "return_qty", "gross_sales", "discount", "net_sales", "gross_profit",
    "payment_method", "cash_sales", "non_cash_sales", "receipt_count", "customer_count",
    "event_ref", "sales_definition", "raw_fields", "source_subfolder",
    "notes", "source_file", "imported_at", "importer_version", "pii_filtered",
]
NUM_FIELDS = {"qty", "return_qty", "gross_sales", "discount", "net_sales", "gross_profit",
              "cash_sales", "non_cash_sales", "receipt_count", "customer_count"}


def norm(s):
    return unicodedata.normalize("NFKC", str(s or "")).strip()


def norm_venue(s):
    """会場名正規化: 空白/全半角ゆらぎ+接尾辞（店/会場）のみ吸収。意味的推測はしない。"""
    t = norm(s).replace(" ", "").replace("　", "")
    return re.sub(r"(店|会場)$", "", t)


def parse_number(v):
    """数値パース。読めなければNone（推測しない）。"""
    s = norm(v)
    if not s:
        return None
    s = re.sub(r"[,¥円\s]", "", s)
    try:
        n = float(s)
        return int(n) if n == int(n) else n
    except ValueError:
        return None


def parse_ymd(v):
    """YYYYMMDD → YYYY-MM-DD。読めなければNone。"""
    s = norm(v)
    if re.fullmatch(r"\d{8}", s):
        try:
            return datetime.strptime(s, "%Y%m%d").strftime("%Y-%m-%d")
        except ValueError:
            return None
    return None


def read_csv_auto(path: Path):
    """文字コード自動判別で読む（UTF-8 BOM → Shift_JIS → UTF-8）。失敗は (None, None)。"""
    for enc, label in (("utf-8-sig", "UTF-8(BOM)"), ("cp932", "Shift_JIS"), ("utf-8", "UTF-8")):
        try:
            with open(path, encoding=enc, newline="") as f:
                rows = list(csv.reader(f))
            rows = [r for r in rows if any(norm(c) for c in r)]
            if not rows:
                return None, label
            return rows, label
        except (UnicodeDecodeError, UnicodeError):
            continue
    return None, None


def detect_type(headers, table):
    """判別テーブルのみを根拠にdataset_typeを判別。一致なし=None（unknown）。"""
    hset = {norm(h) for h in headers}
    for tname, tdef in table["types"].items():
        sig = tdef["signature"]
        if norm(headers[0]) == norm(sig["first_header"]) and \
           all(norm(c) in hset for c in sig["contains"]):
            return tname
    return None


def filename_period(name):
    m = re.search(r"_(\d{8})-(\d{8})", name)
    if m:
        return parse_ymd(m.group(1)), parse_ymd(m.group(2))
    return None, None


def dedup_headers(headers):
    """重複ヘッダーへ位置サフィックス付与（例: 構成比%_1〜_4）。raw_fieldsキー用。"""
    seen, out = {}, []
    dup = {h for h in map(norm, headers) if [norm(x) for x in headers].count(h) > 1}
    for h in headers:
        nh = norm(h)
        if nh in dup:
            seen[nh] = seen.get(nh, 0) + 1
            out.append(f"{nh}_{seen[nh]}")
        else:
            out.append(nh)
    return out


def load_events():
    """催事照合用（読み取り専用）。無ければ空。"""
    if EVENTS_INDEX.exists():
        try:
            return json.load(open(EVENTS_INDEX, encoding="utf-8")).get("events", [])
        except (json.JSONDecodeError, OSError):
            return []
    return []


def match_event(label, d_from, d_to, events):
    """サブフォルダ名称部分×EventRecordの照合。完全一致のみ確定（推測しない）。
    戻り: (event_ref, event_name, candidates[])"""
    cands = []
    for e in events:
        s, t = e.get("start_date"), e.get("end_date") or e.get("start_date")
        overlap = bool(d_from and s and not (d_to and s and d_to < s) and not (t and d_from > t)) if d_from else False
        name_hit = label and (norm_venue(label) in (norm_venue(e.get("event_name")), norm_venue(e.get("venue"))))
        if name_hit and (overlap or not d_from):
            return e["record_id"], e.get("event_name"), []
        if overlap:
            cands.append({"event_ref": e["record_id"], "event_name": e.get("event_name"), "venue": e.get("venue")})
    return None, None, cands


class Guard:
    """書込ホワイトリスト: normalized/ と index.json のみ。他はPermissionError。"""
    def __init__(self, norm_dir: Path, index_path: Path):
        self.norm_dir, self.index_path = norm_dir.resolve(), index_path.resolve()

    def write(self, path: Path, text: str):
        p = path.resolve()
        if not (p == self.index_path or self.norm_dir in p.parents):
            raise PermissionError(f"書込禁止領域: {p}（許可: normalized/ と index.json のみ）")
        p.write_text(text, encoding="utf-8")


def to_records(rows, enc, tdef, dataset_type, table, fpath, subfolder, events, report):
    headers, data = rows[0], rows[1:]
    keys = dedup_headers(headers)
    cmap = {}   # 列index → SalesRecordフィールド（確定マッピング・完全一致のみ）
    used = set()
    for i, h in enumerate(headers):
        f = tdef["column_map"].get(norm(h))
        if f and f not in used:
            cmap[i] = f
            used.add(f)

    label = re.sub(r"^\d{4}-\d{2}[_-]", "", subfolder) if subfolder else None
    p_start, p_end = filename_period(fpath.name) if tdef["date_source"] == "filename_period" else (None, None)

    recs = []
    for row in data:
        vals = {f: None for f in RECORD_FIELDS}
        raw_fields = {}
        for i, cell in enumerate(row):
            if i >= len(headers):
                break
            f = cmap.get(i)
            if f is None:
                if norm(cell):
                    raw_fields[keys[i]] = norm(cell)
            elif f == "business_date":
                vals[f] = parse_ymd(cell)
            elif f in NUM_FIELDS:
                vals[f] = parse_number(cell)
            else:
                vals[f] = norm(cell) or None

        d_from = vals["business_date"] or p_start
        d_to = vals["business_date"] or p_end
        ev_ref, ev_name, cands = match_event(label, d_from, d_to, events)
        if cands:
            report["match_candidates"].append(
                {"source_file": fpath.name, "subfolder": subfolder, "date": d_from, "candidates": cands})

        vals.update({
            "source": "airregi",
            "channel": table["defaults"]["channel"],
            "event_name": ev_name,                     # 完全一致のみ。不明はnull
            "store_name": None,                        # CSV/サブフォルダから確定できるまでnull
            "period_start": p_start, "period_end": p_end,
            "dataset_type": dataset_type,
            "event_ref": ev_ref,
            "sales_definition": table["defaults"]["sales_definition"],
            "raw_fields": raw_fields,
            "source_subfolder": subfolder,
            "source_file": fpath.name,
            "imported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "importer_version": f"v{VERSION}",
            "pii_filtered": True,
        })
        key = "|".join(str(vals[k]) for k in
                       ("source_file", "source_subfolder", "dataset_type", "business_date",
                        "period_start", "period_end", "product_name", "product_id", "terminal_id"))
        vals["record_id"] = "SLS-" + hashlib.md5(key.encode()).hexdigest()[:10]
        recs.append({k: vals[k] for k in RECORD_FIELDS})
    return recs


def import_airregi(base_dir: Path = AIRREGI_DIR, check_only: bool = False):
    raw_dir, norm_dir, index_path = base_dir / "raw", base_dir / "normalized", base_dir / "index.json"
    table_path = base_dir / "dataset_type_table.json"
    if not table_path.exists():
        print(f"✗ 判別テーブルなし: {table_path}（登録はCEO確認後のみ）")
        return 1
    table = json.load(open(table_path, encoding="utf-8"))
    events = load_events()

    files = sorted(p for p in raw_dir.rglob("*.csv") if not p.name.startswith("~")) if raw_dir.exists() else []
    print(f"Airレジ Importer v{VERSION} [{STATE}]")
    print(f"raw/: {len(files)}ファイル検出 / 判別テーブル: {len(table['types'])}type / 催事index: {len(events)}件")

    existing = {}
    if index_path.exists():
        existing = {r["record_id"]: r for r in json.load(open(index_path, encoding="utf-8"))["records"]}

    report = {"files": [], "unknown_type_files": [], "unresolved_event_store": [], "match_candidates": []}
    new_records, new_count = dict(existing), 0

    for f in files:
        rel = f.relative_to(raw_dir)
        subfolder = rel.parts[0] if len(rel.parts) > 1 else None
        rows, enc = read_csv_auto(f)
        if rows is None:
            print(f"  ✗ 文字コード判別不能/空: {rel} → 取込まずCEO確認へ")
            report["unknown_type_files"].append({"file": str(rel), "reason": "文字コード判別不能または空"})
            continue
        dtype = detect_type(rows[0], table)
        if dtype is None:
            print(f"  ⚠ 未知type: {rel}（{enc}・先頭列「{norm(rows[0][0])}」）→ 取込まずCEO確認へ")
            report["unknown_type_files"].append(
                {"file": str(rel), "reason": "判別テーブルに一致なし", "headers": [norm(h) for h in rows[0]]})
            continue
        tdef = table["types"][dtype]
        mapped = sum(1 for h in rows[0] if norm(h) in tdef["column_map"])
        print(f"  {rel}: {enc} / type={dtype} / {len(rows)-1}行 / マッピング{mapped}列 / raw_fields{len(rows[0])-mapped}列")
        if subfolder is None or not any(e for e in events):
            pass  # 未確定判定はレコード生成後にまとめて行う
        if check_only:
            report["files"].append({"file": str(rel), "encoding": enc, "dataset_type": dtype, "rows": len(rows) - 1})
            continue

        recs = to_records(rows, enc, tdef, dtype, table, f, subfolder, events, report)
        added = 0
        for r in recs:
            if r["record_id"] in new_records:
                continue  # 冪等: 既存は上書きしない
            new_records[r["record_id"]] = r
            added += 1
        if any(r["event_name"] is None for r in recs):
            report["unresolved_event_store"].append(
                {"file": str(rel), "subfolder": subfolder or "（直置き）",
                 "note": "event_name/store_name未確定（null）。サブフォルダ方式で確定後に更新可"})
        new_count += added
        report["files"].append({"file": str(rel), "encoding": enc, "dataset_type": dtype,
                                "rows": len(rows) - 1, "new_records": added})

    if check_only:
        print("--check: 書き込みなしで終了")
        return 0

    guard = Guard(norm_dir, index_path)
    norm_dir.mkdir(parents=True, exist_ok=True)
    for rid, r in new_records.items():
        if rid not in existing:
            guard.write(norm_dir / f"{rid}.json", json.dumps(r, ensure_ascii=False, indent=2))

    records = sorted(new_records.values(),
                     key=lambda r: (r.get("business_date") or r.get("period_start") or "", r["record_id"]))
    daily = [r for r in records if r["dataset_type"] == "daily_sales"]
    product = [r for r in records if r["dataset_type"] == "product_sales"]
    d_sales = [r["gross_sales"] for r in daily if r["gross_sales"] is not None]
    top = sorted((r for r in product if r["gross_sales"] is not None),
                 key=lambda r: -r["gross_sales"])[:10]
    summary = {
        "total_records": len(records),
        "by_dataset_type": {t: sum(1 for r in records if r["dataset_type"] == t)
                            for t in sorted({r["dataset_type"] for r in records})},
        "by_channel": {c: sum(1 for r in records if r["channel"] == c)
                       for c in sorted({r["channel"] for r in records})},
        "daily_sales": {
            "days_with_data": len(daily),
            "total_gross_sales": sum(d_sales) if d_sales else None,
            "avg_gross_sales": round(sum(d_sales) / len(d_sales)) if d_sales else None,
            "date_range": [daily[0]["business_date"], daily[-1]["business_date"]] if daily else None,
            "note": "データのある日のみの集計（欠損日は0円補完しない・CEO回答#7）",
        },
        "product_top10": [{"product_name": r["product_name"], "gross_sales": r["gross_sales"],
                           "qty": r["qty"]} for r in top],
        "unresolved_event_store": report["unresolved_event_store"],
        "match_candidates": report["match_candidates"],
        "unknown_type_files": report["unknown_type_files"],
    }
    index = {
        "meta": {
            "generator": f"Airレジ Importer v{VERSION} [{STATE}]",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": "Airレジ売上の索引。催事AI・CEO補佐AIが参照。生データはraw/（変更禁止）・正規化はnormalized/。"
                    "sales_definition=unknown（税込/割引の解釈はAirレジ仕様確認後）。Knowledge直行禁止（Data Layerまで）",
            "summary": summary,
            "files": report["files"],
        },
        "records": records,
    }
    guard.write(index_path, json.dumps(index, ensure_ascii=False, indent=2))
    print(f"新規レコード: {new_count}件 / index合計: {len(records)}件"
          f"（daily_sales {len(daily)} / product_sales {len(product)}）")
    print(f"未確定event/store: {len(report['unresolved_event_store'])}ファイル / "
          f"照合候補: {len(report['match_candidates'])}件 / 未知type: {len(report['unknown_type_files'])}件")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    base = AIRREGI_DIR
    if "--base" in args:
        base = Path(args[args.index("--base") + 1]).resolve()
    sys.exit(import_airregi(base_dir=base, check_only="--check" in args))
