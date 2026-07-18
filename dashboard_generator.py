#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Generator v1.1 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト（Sprint 15.2 → Airレジ接続）

CEO Dashboard v1.0設計（03_Agents/CEO_DASHBOARD.md・CEO承認 2026-07-07）に基づき、
接続済みデータ**だけ**を使って毎朝1枚のCEO Dashboardを生成する。

セクション: ①Company Health ②Today's Dashboard ③Morning Brief（統合）
           ④Result Review ⑤Dataset Status ⑥AI Learning Status

入力（すべて読み取り専用）:
    07_Data/fos/index.json                       FOS TaskRecord
    07_Data/airregi/index.json                   Airレジ SalesRecord（v1.1追加・DS-POS-0001 active）
    07_Data/results/index.json                   Result Recorder（結果確認待ち）
    07_Data/datasets/dataset_registry.json       Dataset Registry
    01_Knowledge/08_Decision_Log/decision_log.json
    09_Learning/insights/insight_draft_log.json / patterns/pattern_draft_log.json
    01_Knowledge/knowledge_index.json
    06_Reports/morning_brief/（当日の最新Brief。無ければ「未発行」表示）

重要ルール（CEO指示・Sprint 15.2）:
・未接続データは推測しない（「未接続」と表示）
・Dashboardは読み取り専用の表示物（本ツールはDashboard以外に何も書かない）
・DashboardからKnowledgeを作らない（Learning Cycleへの書込なし）
・Company Healthは未接続項目を除外して按分表示
・Morning Briefは既存出力を統合（生成はしない。⏰結果確認待ちセクションはResult Reviewへ集約し重複排除）
・書き込み先は 06_Reports/dashboard/ のみ（コードで強制）
・追記型（YYYY-MM-DD.md → _2.md…）・上書き禁止・既存ファイル削除禁止

使い方:
    python3 dashboard_generator.py            # Dashboard生成
    python3 dashboard_generator.py --check    # 読込と算定の確認のみ（書き込みなし）
"""

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

VERSION = "1.1"
STATE = "Experimental"

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "06_Reports" / "dashboard"       # 書き込みはここのみ
STATE_PATH = OUT_DIR / "_state.json"                   # 前回件数（今日増えた件数の算出用）

FOS_INDEX = BASE_DIR / "07_Data" / "fos" / "index.json"
AIRREGI_INDEX = BASE_DIR / "07_Data" / "airregi" / "index.json"
RESULT_INDEX = BASE_DIR / "07_Data" / "results" / "index.json"
REGISTRY = BASE_DIR / "07_Data" / "datasets" / "dataset_registry.json"
DECISION_LOG = BASE_DIR / "01_Knowledge" / "08_Decision_Log" / "decision_log.json"
INSIGHT_LOG = BASE_DIR / "09_Learning" / "insights" / "insight_draft_log.json"
PATTERN_LOG = BASE_DIR / "09_Learning" / "patterns" / "pattern_draft_log.json"
KNOWLEDGE_INDEX = BASE_DIR / "01_Knowledge" / "knowledge_index.json"
BRIEF_DIR = BASE_DIR / "06_Reports" / "morning_brief"

# Dataset → Importer index の対応（最終同期の確認先。機械的判定のみ）
DATASET_INDEX_MAP = {
    "DS-AI-0001": "07_Data/fos/index.json",
    "DS-AI-0002": "07_Data/chatgpt_index.json",
    "DS-EVT-0001": "07_Data/events/index.json",
    "DS-POS-0001": "07_Data/airregi/index.json",  # v1.1追加（Airレジ・active 2026-07-07）
    "DS-EVT-0002": "07_Data/event_schedule/index.json",  # 催事スケジュールSheets（2026-07-11・毎朝取込）
}
EVENT_SCHEDULE_INDEX = BASE_DIR / "07_Data" / "event_schedule" / "index.json"


def safe_write(path: Path, text: str):
    """06_Reports/dashboard/ 以外への書き込みを拒否。Dashboard本体は上書きも禁止。"""
    path = path.resolve()
    if not str(path).startswith(str(OUT_DIR.resolve())):
        raise PermissionError(f"書き込み禁止: {path} は 06_Reports/dashboard/ の外")
    if path.suffix == ".md" and path.exists():
        raise PermissionError(f"上書き禁止: {path} は既に存在（追記型命名を使う）")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def jload(path: Path):
    """読み取り専用ロード。無ければNone（推測しない=未接続扱い）。"""
    try:
        return json.load(open(path, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


# ================================================================
# ① Company Health（接続済み項目のみ按分。機械的算定式を明記）
# ================================================================

def company_health(fos_idx, learning):
    """v1.0算定対象=接続済み3項目（未対応10・期限10・Learning10）=30点分。
    未接続（売上/利益/現金/在庫/出荷=70点分）は対象外と明示し、推測しない。"""
    items, score = [], 0
    if fos_idx:
        recs = fos_idx.get("records", [])
        waiting = sum(1 for r in recs if r.get("source_type") == "staff_request" or r.get("consultation"))
        overdue = fos_idx.get("summary", {}).get("overdue", 0)
        s_wait = max(0, 10 - 5 * waiting)   # 待たせている相談1件ごとに-5
        s_due = max(0, 10 - 5 * overdue)    # 期限超過1件ごとに-5
        items.append(("未対応（人を待たせない）", s_wait, 10, f"スタッフ待ち{waiting}件"))
        items.append(("期限", s_due, 10, f"期限超過{overdue}件"))
        score += s_wait + s_due
    # Learning: released Knowledgeがある(+5) / 直近7日にDecision追加あり(+5)
    s_learn = (5 if learning["released"] > 0 else 0) + (5 if learning["decisions_7d"] > 0 else 0)
    items.append(("Learning", s_learn, 10,
                  f"released {learning['released']}件・直近7日Decision {learning['decisions_7d']}件"))
    score += s_learn
    max_score = sum(m for _, _, m, _ in items)
    return {"score": score, "max": max_score, "items": items,
            "excluded": "売上20・利益15・現金15・在庫10・出荷10（計70点分）= 算定対象外"
                        "（Airレジは接続済みだが売上の点数化基準が未定義のため推測しない。基準はCEOと定義後にv2.0で算定）"}


# ================================================================
# ② Today's Dashboard（接続済み=FOSのみ。他は未接続表示）
# ================================================================

def todays_dashboard(fos_idx, airregi_idx, today):
    rows = []
    if fos_idx:
        recs = fos_idx.get("records", [])
        waiting = [r for r in recs if r.get("source_type") == "staff_request" or r.get("consultation")]
        overdue = [r for r in recs if r.get("overdue")]
        today_ev = [r for r in recs if r.get("source_type") == "event"
                    and str(r.get("due_date") or "").startswith(today)]
        rows.append(("スタッフ待ち", f"{len(waiting)}件" +
                     ("（" + " / ".join(str(r['title'])[:30] for r in waiting[:2]) + "）" if waiting else "")))
        rows.append(("期限超過", f"{len(overdue)}件" +
                     ("（" + " / ".join(str(r['title'])[:20] for r in overdue[:3]) + "）" if overdue else "")))
        rows.append(("本日予定", f"{len(today_ev)}件" +
                     ("（" + " / ".join(str(r['title'])[:20] for r in today_ev[:3]) + "）" if today_ev else "")))
    else:
        rows.append(("FOS", "未接続（fos_importer.py未実行）"))

    # --- 売上欄（v1.1: Airレジ=DS-POS-0001接続。表示は機械的集計のみ・推測しない） ---
    if airregi_idx:
        sm = airregi_idx.get("meta", {}).get("summary", {})
        dsum = sm.get("daily_sales", {})
        srecs = airregi_idx.get("records", [])
        today_sales = [r for r in srecs if r.get("dataset_type") == "daily_sales"
                       and r.get("business_date") == today]
        if today_sales:
            total = sum(r["gross_sales"] for r in today_sales if r.get("gross_sales") is not None)
            rows.append(("本日の売上（Airレジ）", f"{total:,}円（{len(today_sales)}レコード・sales_definition=unknown）"))
        else:
            last = (dsum.get("date_range") or [None, None])[1]
            rows.append(("本日の売上（Airレジ）",
                         f"本日分データなし（取込は催事終了時運用・最終データ日 {last or '—'}）"))
        rng = dsum.get("date_range")
        if dsum.get("total_gross_sales") is not None and rng:
            rows.append(("催事売上（Airレジ・取込済み期間）",
                         f"{dsum['total_gross_sales']:,}円（{rng[0]}〜{rng[1]}・データのある{dsum.get('days_with_data')}日分・欠損日0円補完なし）"))
        else:
            rows.append(("催事売上（Airレジ・取込済み期間）", "データなし"))
        top3 = sm.get("product_top10", [])[:3]
        if top3:
            rows.append(("商品別売上TOP3（Airレジ）",
                         " / ".join(f"{str(t['product_name'])[:20]} {t['gross_sales']:,}円" for t in top3)))
        unresolved = len(sm.get("unresolved_event_store", []))
        if unresolved:
            rows.append(("Airレジ 店舗/催事 未確定", f"{unresolved}ファイル（raw/サブフォルダ整理でCEO確定待ち）"))
        rows.append(("EC売上", "未接続（Shopify接続後に表示）"))
    else:
        rows.append(("本日の売上 / 催事売上 / EC売上", "未接続（airregi_importer.py未実行 / Shopify未接続）"))
    for name in ("受注件数 / 出荷件数 / 未出荷", "入金予定"):
        rows.append((name, "未接続（Shopify/FLAM/はぴロジ/Airペイ接続後に表示）"))

    # --- Today's Events / Upcoming Events（催事スケジュールSheets・出店決定のみ・DS-EVT-0002） ---
    es = jload(EVENT_SCHEDULE_INDEX)
    if es:
        from datetime import timedelta
        ev = [r for r in es.get("records", []) if r.get("confirmed")]  # 出店決定のみ
        try:
            week_end = (date.fromisoformat(today) + timedelta(days=7)).isoformat()
        except ValueError:
            week_end = today
        t = [r for r in ev if (r.get("start") and r.get("end") and r["start"] <= today <= r["end"])
             or r.get("setup_date") == today or r.get("teardown_date") == today]
        up = [r for r in ev if r.get("start") and today < r["start"] <= week_end]
        _f = lambda r: f"{r['name']}（{r.get('start')}〜{r.get('end')}）"
        rows.append(("Today's Events（出店決定）", f"{len(t)}件" + ("（" + " / ".join(_f(r) for r in t[:3]) + "）" if t else "")))
        rows.append(("Upcoming Events（7日以内開始・出店決定）", f"{len(up)}件" + ("（" + " / ".join(_f(r) for r in up[:3]) + "）" if up else "")))
    else:
        rows.append(("Today's Events / Upcoming Events", "未取込（event_schedule_importer.py実行で接続）"))
    return rows


# ================================================================
# ③ Morning Brief統合（既存出力の転記のみ・生成しない）
# ================================================================

def load_brief(today):
    """当日の最新Brief本文を返す（⏰結果確認待ちセクションは除外=Result Reviewへ集約）。"""
    if not BRIEF_DIR.exists():
        return None, None
    cands = sorted(BRIEF_DIR.glob(f"{today}*.md"))
    if not cands:
        return None, None
    latest = cands[-1]
    text = latest.read_text(encoding="utf-8")
    # ⏰セクションを除去（次の"## "まで）。他は原文のまま転記
    text = re.sub(r"\n## ⏰ 結果確認待ち.*?(?=\n## )", "", text, flags=re.S)
    # 見出しレベルを1段下げてDashboardに収める（# → ###）
    text = re.sub(r"^(#{1,2}) ", lambda m: "#" * (len(m.group(1)) + 2) + " ", text, flags=re.M)
    return latest.name, text.strip()


# ================================================================
# ④ Result Review（07_Data/results/index.json参照）
# ================================================================

def result_review(res_idx):
    if not res_idx:
        return None
    return {"due": res_idx.get("check_due", []),
            "summary": res_idx.get("summary", {})}


# ================================================================
# ⑤ Dataset Status（Registry+index生成時刻。機械的判定のみ）
# ================================================================

def dataset_status(registry, today):
    rows = []
    for ds in (registry or {}).get("datasets", []):
        sync = "—"
        state = None
        idx_rel = DATASET_INDEX_MAP.get(ds["dataset_id"])
        if ds["status"] == "active" and idx_rel:
            idx = jload(BASE_DIR / idx_rel)
            if idx is None:
                state = "ERROR（index読込不可）"
            else:
                sync = (idx.get("meta", {}).get("generated_at")
                        or idx.get("generated_at") or "記録なし")
                if "日次" in str(ds.get("update_frequency", "")) and str(sync)[:10] < today:
                    state = f"WARNING（最終同期 {str(sync)[:10]} < 今日・日次更新のはず）"
                else:
                    state = "ACTIVE"
        elif ds["status"] == "active":
            state = "ACTIVE（index対応未定義）"
        else:
            state = f"{ds['status'].upper()}（実接続確認待ち・読まない）"
        rows.append((ds["name"], ds["source_type"], state, str(sync)[:19]))
    return rows


# ================================================================
# ⑥ AI Learning Status（各ログの件数。今日の増分=_state.json比較）
# ================================================================

def learning_status(today):
    dec = jload(DECISION_LOG) or {"decisions": []}
    ins = jload(INSIGHT_LOG) or {"insights": []}
    pat = jload(PATTERN_LOG) or {"patterns": []}
    ki = jload(KNOWLEDGE_INDEX) or {"knowledge": []}
    decisions = dec.get("decisions", [])
    counts = {
        "Decision": len(decisions),
        "Insight": len(ins.get("insights", [])),
        "Pattern": len(pat.get("patterns", [])),
        "Knowledge": len(ki.get("knowledge", [])),
        "Released": sum(1 for k in ki.get("knowledge", []) if k.get("status") == "released"),
        "Verified": sum(1 for k in ki.get("knowledge", []) if k.get("status") == "verified"),
    }
    # 直近7日のDecision（Health用）
    decisions_7d = 0
    for d in decisions:
        ds = str(d.get("日時", ""))[:10]
        try:
            if (date.fromisoformat(today) - date.fromisoformat(ds)).days <= 7:
                decisions_7d += 1
        except ValueError:
            continue
    # Evidence付与率（Score平均はEvidence Scorer実装後。推測値は出さない）
    with_ev = sum(1 for i in ins.get("insights", []) if i.get("evidence"))
    ev_rate = f"{with_ev}/{counts['Insight']}" if counts["Insight"] else "対象なし"
    # 今日増えた件数 = 前回スナップショットとの差分
    prev = jload(STATE_PATH) or {}
    prev_counts = prev.get("counts", {})
    delta = {k: counts[k] - prev_counts.get(k, counts[k]) for k in counts}
    return {"counts": counts, "delta": delta, "evidence_rate": ev_rate,
            "decisions_7d": decisions_7d, "released": counts["Released"],
            "prev_date": prev.get("date")}


# ================================================================
# 生成
# ================================================================

def next_path(today):
    p = OUT_DIR / f"{today}.md"
    n = 1
    while p.exists():
        n += 1
        p = OUT_DIR / f"{today}_{n}.md"
    return p


def build(today, now, health, todays, brief_name, brief_text, res, ds_rows, learn):
    L = [f"# CEO Dashboard — {today}",
         "",
         f"発行: Dashboard Generator v{VERSION} [{STATE}]（{now}・読み取り専用・接続済みデータのみ表示）",
         "",
         "---", "",
         "## 1. 🩺 Company Health",
         "",
         f"### **{health['score']} / {health['max']}**（算定対象{health['max']}点分のみ・100点満点中70点分は未接続のため対象外）",
         ""]
    for name, s, m, note in health["items"]:
        L.append(f"- {name}: **{s}/{m}**（{note}）")
    L += [f"- 対象外: {health['excluded']}", "",
          "## 2. 📊 Today's Dashboard", ""]
    for name, val in todays:
        L.append(f"- {name}: {val}")
    L += ["", "## 3. 🔴 Morning Brief", ""]
    if brief_text:
        L += [f"（本日のBrief `{brief_name}` を統合表示。⏰結果確認待ちは§4へ集約）", "", brief_text]
    else:
        L.append("本日のMorning Briefは未発行（`python3 fos_importer.py && python3 ceo_assistant.py` で発行）")
    L += ["", "## 4. 🔁 Result Review（判定はCEOのみ）", ""]
    if res and res["due"]:
        for d in res["due"]:
            L += [f"- **{d.get('判断')}**（{d.get('result_id')} / 判断日 {d.get('判断日')} / 確認予定 {d.get('確認予定日')}）",
                  f"  - 期待結果: {d.get('expected_result') or '未入力'} / 実績（CEO記入）: ______ / 差分: ______",
                  "  - 判定: [ 成功 / 失敗 / 継続観察 ] ______"]
        s = res["summary"]
        L.append(f"- 集計: Draft {s.get('drafts_total', 0)}件 / CEO判定待ち {s.get('pending_ceo_review', 0)}件 / 確定 {s.get('confirmed_results', 0)}件")
    elif res:
        L.append("- 結果確認待ちはありません")
    else:
        L.append("- 未接続（result_recorder.py未実行）")
    L += ["", "## 5. 🔌 Dataset Status", "",
          "| Dataset | source_type | 状態 | 最終同期 |", "|---|---|---|---|"]
    for name, st, state, sync in ds_rows:
        L.append(f"| {name} | {st} | {state} | {sync} |")
    L += ["", "## 6. 🧠 AI Learning Status", "",
          "| 段階 | 件数 | 今日の増分 |", "|---|---|---|"]
    for k, v in learn["counts"].items():
        d = learn["delta"][k]
        L.append(f"| {k} | {v} | {'+' + str(d) if d > 0 else (str(d) if d < 0 else '±0')} |")
    L += [f"", f"- Evidence付与率（Insight）: {learn['evidence_rate']}（Evidence Score平均はScorer実装後）",
          f"- 増分の比較基準: {learn['prev_date'] or '初回（比較基準なし・±0表示）'}",
          "", "---",
          f"*生成元: Dataset → Morning Brief → Decision Log → Learning（読み取りのみ）。"
          f"本DashboardからKnowledgeは作られません。実行系の提案はありません。*"]
    return "\n".join(L)


def main():
    check_only = "--check" in sys.argv
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M")

    fos_idx = jload(FOS_INDEX)
    airregi_idx = jload(AIRREGI_INDEX)
    res = result_review(jload(RESULT_INDEX))
    registry = jload(REGISTRY)
    learn = learning_status(today)
    health = company_health(fos_idx, learn)
    todays = todays_dashboard(fos_idx, airregi_idx, today)
    brief_name, brief_text = load_brief(today)
    ds_rows = dataset_status(registry, today)

    print(f"Dashboard Generator v{VERSION} [{STATE}]（読み取り専用・書込先=06_Reports/dashboard/のみ）")
    print(f"Health: {health['score']}/{health['max']}（未接続70点分は対象外）")
    print(f"Result Review: 確認待ち{len(res['due']) if res else 0}件 / Dataset: {len(ds_rows)}件 / "
          f"Learning: {learn['counts']}")
    print(f"Brief統合: {brief_name or '本日未発行'}")

    if check_only:
        print("--check: 書き込みなしで終了")
        return

    path = next_path(today)
    safe_write(path, build(today, now, health, todays, brief_name, brief_text, res, ds_rows, learn))
    # スナップショット更新（増分算出用。dashboard/内のみ・mdではないので更新可）
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps({"date": today, "counts": learn["counts"]},
                                     ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Dashboard発行: {path}")


if __name__ == "__main__":
    main()
