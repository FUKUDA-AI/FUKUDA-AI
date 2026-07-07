#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Result Recorder v1.0 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト（Sprint 15）

Decision Logに記録された判断から「結果待ち」を抽出し、
Action Record + Result Draft を 07_Data/results/ に生成する。
Result Layer（09_Learning/RESULT_LAYER_DESIGN.md・CEO承認済み設計）の初実装。

フロー:
    decision_log.json（読み取りのみ・書き換えない）
      → 【Result Recorder（本機能）】 結果待ちDecision抽出
      → Action Record（誰が・いつ・何をしたか＝事実のみ）
      → Result Draft（status=CEO判定待ち。AIは成功/失敗を書かない）
      → 07_Data/results/result_draft_log.json + index.json
      → Morning Brief「⏰ 結果確認待ち」（ceo_assistant経由）
      → CEO判定（成功/失敗/継続観察）→ CEO確認後に result_log.json へ確定（別操作）

重要ルール（CEO指示・Sprint 15）:
・AIはResultを推測しない（outcome/数値/status はCEO記入 or 実績データのみ）
・成功/失敗/継続観察の判定はCEOのみ
・Evidence必須（無ければ learning_ready=false のまま学習に使われない）
・書き込み先は 07_Data/results/ のみ（Decision Log本体は書き換えない）
・Result Draft → CEO確認後に確定（result_log.jsonへはCEO確認後の別操作でのみ移す）
・expected_result / review_after_days / decision_importance / decision_type を引き継ぐ
・既存ファイル削除禁止・冪等（decision指紋で重複生成しない）

結果待ちDecisionの抽出条件（v1.0・透明化のため明記）:
・結果が「完了（実施済み）」「実行済み」= 実行された判断（trackable）
・ただし開発・記録系（Git/コミット/レビュー/文書/リリース/昇格 等）は対象外
・「保留（Hold）」「確定（承認のみ）」は実行前のため対象外（実行後に対象化）
・review_after_days があるものは 判断日+日数 を確認予定日に。無ければ「実行済み=確認可」

使い方:
    python3 result_recorder.py            # 抽出 + Draft生成 + index更新
    python3 result_recorder.py --check    # 抽出結果の確認のみ（書き込みなし）
"""

import hashlib
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

VERSION = "1.0"
STATE = "Experimental"

BASE_DIR = Path(__file__).resolve().parent
DECISION_LOG = BASE_DIR / "01_Knowledge" / "08_Decision_Log" / "decision_log.json"  # 読み取りのみ
RESULTS_DIR = BASE_DIR / "07_Data" / "results"                                       # 書き込みはここのみ
DRAFT_PATH = RESULTS_DIR / "result_draft_log.json"
LOG_PATH = RESULTS_DIR / "result_log.json"        # 確定Result（CEO確認後の別操作でのみ追記）
INDEX_PATH = RESULTS_DIR / "index.json"

# 実行済みとみなす結果表現 / 対象外キーワード（開発・記録系）
EXECUTED_RESULTS = ("完了（実施済み）", "実行済み")
NON_TRACKABLE_RE = re.compile(r"Git|git|コミット|レビュー|文書|リリース|昇格|released|EVOLVING|v\d+\.\d+")

IMPORTANCE_DEFAULT_REVIEW = {"S": 30, "A": 14, "B": 7}  # FOS Operating Rule v1.2 §4-5


def safe_write(path: Path, text: str):
    """07_Data/results/ 以外への書き込みをコードで拒否する。"""
    path = path.resolve()
    if not str(path).startswith(str(RESULTS_DIR.resolve())):
        raise PermissionError(f"書き込み禁止: {path} は 07_Data/results/ の外")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fingerprint(entry: dict) -> str:
    """Decisionの指紋（冪等キー）。判断内容+日時で一意化。"""
    raw = f"{entry.get('判断内容','')}|{entry.get('日時','')}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def load_decisions():
    data = json.load(open(DECISION_LOG, encoding="utf-8"))
    return data.get("decisions", [])


def is_trackable(entry: dict) -> bool:
    """実行済みの実行系判断のみ対象（推測せず、条件はdocstringに明記した機械的判定のみ）。"""
    result = str(entry.get("結果", ""))
    if not any(result.startswith(x) for x in EXECUTED_RESULTS):
        return False
    text = str(entry.get("判断内容", "")) + result
    if NON_TRACKABLE_RE.search(text):
        return False
    return True


def check_due_date(entry: dict):
    """確認予定日 = 判断日 + review_after_days。review未設定なら None（実行済み=確認可）。"""
    rad = entry.get("review_after_days")
    date_s = str(entry.get("日時", ""))[:10]
    if rad is None or not date_s:
        return None
    try:
        return (date.fromisoformat(date_s) + timedelta(days=int(rad))).isoformat()
    except ValueError:
        return None


def build_draft(entry: dict, fp: str, seq: int) -> dict:
    """Action Record + Result Draft（AIが書けるのは事実と引き継ぎのみ）。"""
    decision_date = str(entry.get("日時", ""))[:10] or None
    imp = entry.get("decision_importance")
    return {
        "result_id": f"RES-{seq:04d}",
        "decision_fingerprint": fp,
        "decision_ref": {"判断内容": entry.get("判断内容"), "日時": entry.get("日時"),
                         "関連カテゴリ": entry.get("関連カテゴリ"), "結果": entry.get("結果")},
        # ---- Action Record（事実のみ）----
        "action": {
            "action_date": decision_date,  # 出典: decision_logの「結果=実行済み」記載（推測ではなく記録の転記）
            "action_source": "decision_log.json（結果欄の実行記録）",
            "actor": "CEO",
            "what": entry.get("判断内容"),
        },
        # ---- 引き継ぎ（FOS Metadata v1.2。無い項目はnull=未設定・AIは埋めない）----
        "decision_type_main": entry.get("decision_type_main"),
        "decision_type_sub": entry.get("decision_type_sub"),
        "decision_importance": imp,
        "expected_result": entry.get("expected_result"),
        "review_after_days": entry.get("review_after_days"),
        "review_after_days_proposal": IMPORTANCE_DEFAULT_REVIEW.get(imp),  # 提案のみ・確定はCEO
        "check_due_date": check_due_date(entry),  # null=実行済みのため確認可
        # ---- Result（CEO記入欄。AIは推測しない）----
        "result_date": None,
        "status": "（CEO判定待ち: 成功 / 失敗 / 継続観察）",
        "outcome": None,
        "数値結果": None,
        "成功要因": None,
        "失敗要因": None,
        "想定との差異": None,  # expected_result vs actual の比較（CEO記入時に機械が期待値を並記）
        # ---- Evidence（必須。無ければ学習に使われない）----
        "evidence": {"decision_source": "decision_log.json", "decision_fingerprint": fp,
                     "result_evidence": None,
                     "note": "result_evidence（実績データID/CEO記入+日付）が入るまで learning_ready 不可"},
        "reviewer": None,
        "learning_ready": False,  # status確定 + evidence完備 で機械がtrue化（判定自体はCEO）
        "record_status": "draft",  # draft → CEO確認後に result_log.json へ確定（別操作）
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "recorder_version": f"v{VERSION}",
    }


def main():
    check_only = "--check" in sys.argv
    decisions = load_decisions()
    trackable = [(fingerprint(e), e) for e in decisions if is_trackable(e)]

    # 既存Draft読込（冪等: 指紋一致は再生成しない）
    if DRAFT_PATH.exists():
        draft_data = json.load(open(DRAFT_PATH, encoding="utf-8"))
    else:
        draft_data = {"meta": {"note": "Result Draft置き場。判定（成功/失敗/継続観察）はCEOのみ。"
                                        "CEO確認後に result_log.json へ確定する（AIは本体へ勝手に書かない）",
                               "generator": f"Result Recorder v{VERSION} [{STATE}]"},
                      "drafts": []}
    existing = {d["decision_fingerprint"] for d in draft_data["drafts"]}

    new_drafts = []
    seq = len(draft_data["drafts"])
    for fp, e in trackable:
        if fp in existing:
            continue
        seq += 1
        new_drafts.append(build_draft(e, fp, seq))

    print(f"Result Recorder v{VERSION} [{STATE}]（Decision Log読み取りのみ・書込先=07_Data/results/）")
    print(f"Decision Log: {len(decisions)}件 → 結果待ち（trackable・実行済み）: {len(trackable)}件")
    print(f"既存Draft: {len(draft_data['drafts'])}件 / 新規Draft: {len(new_drafts)}件（冪等: 指紋重複はスキップ）")
    for d in new_drafts:
        due = d["check_due_date"] or "未設定（実行済み=確認可）"
        print(f"  + {d['result_id']} {str(d['decision_ref']['判断内容'])[:40]} / 確認予定: {due}")

    if check_only:
        print("--check: 書き込みなしで終了")
        return

    draft_data["drafts"].extend(new_drafts)
    draft_data["meta"]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draft_data["meta"]["total_drafts"] = len(draft_data["drafts"])
    safe_write(DRAFT_PATH, json.dumps(draft_data, ensure_ascii=False, indent=2))

    # 確定ログの器（空で作成・既存があれば触らない=削除禁止）
    if not LOG_PATH.exists():
        safe_write(LOG_PATH, json.dumps(
            {"meta": {"note": "確定Result（CEO判定済みのみ）。DraftからのCEO確認後の確定操作でのみ追記。AIは判定しない"},
             "results": []}, ensure_ascii=False, indent=2))

    # index: Brief「結果確認待ち」の参照元
    today = date.today().isoformat()
    pending = [d for d in draft_data["drafts"] if d["record_status"] == "draft"]
    check_due = [
        {"result_id": d["result_id"], "判断": d["decision_ref"]["判断内容"],
         "判断日": (d["decision_ref"].get("日時") or "")[:10],
         "確認予定日": d["check_due_date"] or "未設定（実行済み=確認可）",
         "expected_result": d["expected_result"],
         "decision_type_main": d["decision_type_main"],
         "decision_importance": d["decision_importance"]}
        for d in pending if d["check_due_date"] is None or d["check_due_date"] <= today
    ]
    index = {"meta": {"generator": f"Result Recorder v{VERSION} [{STATE}]",
                      "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                      "note": "Brief『結果確認待ち』の参照元。判定はCEOのみ"},
             "summary": {"drafts_total": len(draft_data["drafts"]),
                         "pending_ceo_review": len(pending),
                         "check_due_now": len(check_due),
                         "confirmed_results": len(json.load(open(LOG_PATH, encoding="utf-8"))["results"])},
             "check_due": check_due}
    safe_write(INDEX_PATH, json.dumps(index, ensure_ascii=False, indent=2))
    print(f"保存: {DRAFT_PATH.name}（累計{len(draft_data['drafts'])}件）/ {INDEX_PATH.name}（確認待ち{len(check_due)}件）")
    print("→ 次工程: Morning Brief「⏰ 結果確認待ち」に掲載 → CEOが成功/失敗/継続観察を判定 → 確定反映はCEO確認後")


if __name__ == "__main__":
    main()
