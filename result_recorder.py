#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Result Recorder v1.1 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト（Result Layer v1.1・Architecture v1.4）

Decision Logに記録された判断から「結果待ち」を抽出し、**2層**のResult Draftを 07_Data/results/ に生成する。
Result Layer v1.1（09_Learning/RESULT_LAYER_V11.md・CEO承認 2026-07-18）の実装。

2層構造（v1.1の核心）:
    Decision（CEO確定判断）
      → Action Result（ARES）  「判断したことを実行できたか」 status: 成功/失敗/延期/保留（実行直後に判定）
      → Business Result（BRES）「その判断は経営として成功だったか」 status: 成功/失敗/継続観察（review_after_days経過後）
      → learning_ready=true の Business Result のみ Insight→…→Knowledge（Action Resultは実行率/運営/SOP改善用）

フロー:
    decision_log.json（読み取りのみ・書き換えない）
      → 結果待ちDecision抽出（trackable=実行済みの実行系）
      → Action Result Draft（実行の事実）+ Business Result Draft（経営結果・expected vs actual）
      → 07_Data/results/result_draft_log.json + index.json（action_due / business_due 分離）
      → Morning Brief「⏰ 結果確認待ち」（ceo_assistant経由・Action/Businessをタグ表示）
      → CEO判定 → CEO確認後に result_log.json へ確定（別操作）

重要ルール（不変）:
・AI/機械はResultを推測しない（outcome/数値/status はCEO記入 or 実績データのみ・判定はCEOのみ）
・Action Result / Business Result どちらもCEOのみが確定する
・Evidence必須（無ければ learning_ready=false のまま学習に使われない）
・書き込み先は 07_Data/results/ のみ・冪等（decision指紋×layerで重複生成しない）
・**既存v1.0 Draft（RES-xxxx・layerなし）は削除・書き換えしない**。layer読み替え（readmap）で解釈する（正本は既存レコード・確定はCEO）

使い方:
    python3 result_recorder.py            # 抽出 + 2層Draft生成 + index更新
    python3 result_recorder.py --check    # 抽出結果の確認のみ（書き込みなし）
"""

import hashlib
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

VERSION = "1.1"
STATE = "Experimental"

BASE_DIR = Path(__file__).resolve().parent
DECISION_LOG = BASE_DIR / "01_Knowledge" / "08_Decision_Log" / "decision_log.json"  # 読み取りのみ
RESULTS_DIR = BASE_DIR / "07_Data" / "results"                                       # 書き込みはここのみ
DRAFT_PATH = RESULTS_DIR / "result_draft_log.json"
LOG_PATH = RESULTS_DIR / "result_log.json"        # 確定Result（CEO確認後の別操作でのみ追記）
INDEX_PATH = RESULTS_DIR / "index.json"

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
    raw = f"{entry.get('判断内容','')}|{entry.get('日時','')}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def load_decisions():
    data = json.load(open(DECISION_LOG, encoding="utf-8"))
    return data.get("decisions", [])


def is_trackable(entry: dict) -> bool:
    result = str(entry.get("結果", ""))
    if not any(result.startswith(x) for x in EXECUTED_RESULTS):
        return False
    text = str(entry.get("判断内容", "")) + result
    if NON_TRACKABLE_RE.search(text):
        return False
    return True


def check_due_date(entry: dict):
    """Business確認予定日 = 判断日 + review_after_days。未設定なら None（実行済み=確認可）。"""
    rad = entry.get("review_after_days")
    date_s = str(entry.get("日時", ""))[:10]
    if rad is None or not date_s:
        return None
    try:
        return (date.fromisoformat(date_s) + timedelta(days=int(rad))).isoformat()
    except ValueError:
        return None


def _decision_ref(entry):
    return {"判断内容": entry.get("判断内容"), "日時": entry.get("日時"),
            "関連カテゴリ": entry.get("関連カテゴリ"), "結果": entry.get("結果")}


def build_action_draft(entry, fp, seq):
    """Action Result（実行の成否）。実行直後に判定可（review_after_daysを待たない）。status 4分類。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "action_result_id": f"ARES-{seq:04d}",
        "layer": "action",
        "decision_fingerprint": fp,
        "decision_ref": _decision_ref(entry),
        "action_date": str(entry.get("日時", ""))[:10] or None,
        "action_source": "decision_log.json（結果欄の実行記録）",
        "actor": "CEO",
        "what": entry.get("判断内容"),
        "status": "（CEO判定待ち: 成功 / 失敗 / 延期 / 保留）",  # 4分類・CEOのみ確定
        "check_due_date": None,  # 実行済み=すぐ確認可
        "decision_type_main": entry.get("decision_type_main"),
        "decision_importance": entry.get("decision_importance"),
        "evidence": {"type": "実行の事実", "source": "decision_log.json", "fingerprint": fp,
                     "result_evidence": None,
                     "note": "FOS完了記録 or CEO記入+日付 が入るまで確定不可"},
        "record_status": "draft",
        "created_at": now, "recorder_version": f"v{VERSION}",
    }


def build_business_draft(entry, fp, seq):
    """Business Result（経営の成否）。review_after_days経過後に判定。status 3分類。学習対象はこちらのみ。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    imp = entry.get("decision_importance")
    return {
        "business_result_id": f"BRES-{seq:04d}",
        "layer": "business",
        "decision_fingerprint": fp,
        "action_result_ref": f"ARES-{seq:04d}",
        "decision_ref": _decision_ref(entry),
        "result_date": None,
        "status": "（CEO判定待ち: 成功 / 失敗 / 継続観察）",  # 3分類・CEOのみ確定
        # expected（引き継ぎ）vs actual（CEO記入）。数値・定性・要因はCEO/実績データのみ（AIは推測しない）
        "expected_result": entry.get("expected_result"),
        "actual_result": None,
        "想定との差異": None,
        "数値結果": None, "定性評価": None, "成功要因": None, "失敗要因": None,
        "decision_type_main": entry.get("decision_type_main"),
        "decision_type_sub": entry.get("decision_type_sub"),
        "decision_importance": imp,
        "review_after_days": entry.get("review_after_days"),
        "review_after_days_proposal": IMPORTANCE_DEFAULT_REVIEW.get(imp),  # 提案のみ・確定はCEO
        "check_due_date": check_due_date(entry),  # null=実行済みのため確認可
        "evidence": {"type": "実績データ/CEO記入", "result_evidence": None,
                     "note": "実績データID(EventRecord/SalesRecord等) or CEO記入+日付 が入るまで learning_ready不可"},
        "learning_ready": False,  # status確定(成功/失敗)+Evidence完備 で機械がtrue化（Insight Generator v1.1が読む唯一の層）
        "record_status": "draft",
        "created_at": now, "recorder_version": f"v{VERSION}",
    }


def _due_item(d, layer):
    return {"result_id": d.get("action_result_id") or d.get("business_result_id"),
            "layer": layer,
            "判断": d["decision_ref"]["判断内容"],
            "判断日": (d["decision_ref"].get("日時") or "")[:10],
            "確認予定日": d.get("check_due_date") or "未設定（実行済み=確認可）",
            "expected_result": d.get("expected_result"),
            "decision_type_main": d.get("decision_type_main"),
            "decision_importance": d.get("decision_importance")}


def main():
    check_only = "--check" in sys.argv
    decisions = load_decisions()
    trackable = [(fingerprint(e), e) for e in decisions if is_trackable(e)]

    if DRAFT_PATH.exists():
        draft_data = json.load(open(DRAFT_PATH, encoding="utf-8"))
    else:
        draft_data = {"meta": {"note": "Result Draft置き場（v1.1・2層）。判定はCEOのみ。CEO確認後に result_log.json へ確定",
                               "generator": f"Result Recorder v{VERSION} [{STATE}]"}, "drafts": []}
    draft_data.setdefault("drafts", [])

    # 既存の識別: legacy=v1.0(layerなし) / 2層=(fp,layer)
    legacy_fps = {d.get("decision_fingerprint") for d in draft_data["drafts"] if not d.get("layer")}
    existing_keys = {(d.get("decision_fingerprint"), d.get("layer"))
                     for d in draft_data["drafts"] if d.get("layer")}
    drafted_fps = {d.get("decision_fingerprint") for d in draft_data["drafts"]}

    new_drafts, seq = [], len(drafted_fps)
    for fp, e in trackable:
        if fp in legacy_fps:            # v1.0で生成済み → readmapで解釈（再生成しない・削除しない）
            continue
        if (fp, "action") in existing_keys and (fp, "business") in existing_keys:
            continue
        seq += 1
        if (fp, "action") not in existing_keys:
            new_drafts.append(build_action_draft(e, fp, seq))
        if (fp, "business") not in existing_keys:
            new_drafts.append(build_business_draft(e, fp, seq))

    print(f"Result Recorder v{VERSION} [{STATE}]（2層・Decision Log読み取りのみ・書込先=07_Data/results/）")
    print(f"Decision Log: {len(decisions)}件 → 結果待ち（trackable）: {len(trackable)}件")
    print(f"既存Draft: {len(draft_data['drafts'])}件（うちlegacy v1.0 {len(legacy_fps)}判断）/ 新規Draft: {len(new_drafts)}件（ARES+BRES・冪等）")
    for d in new_drafts:
        rid = d.get("action_result_id") or d.get("business_result_id")
        print(f"  + [{d['layer']}] {rid} {str(d['decision_ref']['判断内容'])[:36]}")

    if check_only:
        print("--check: 書き込みなしで終了")
        return

    draft_data["drafts"].extend(new_drafts)
    draft_data["meta"]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draft_data["meta"]["total_drafts"] = len(draft_data["drafts"])
    draft_data["meta"]["schema"] = "v1.1（layer: action|business。legacy=layerなし=v1.0）"
    safe_write(DRAFT_PATH, json.dumps(draft_data, ensure_ascii=False, indent=2))

    if not LOG_PATH.exists():
        safe_write(LOG_PATH, json.dumps(
            {"meta": {"note": "確定Result（CEO判定済みのみ）。DraftからのCEO確認後の確定操作でのみ追記。AIは判定しない"},
             "results": []}, ensure_ascii=False, indent=2))

    today = date.today().isoformat()
    drafts = draft_data["drafts"]
    pend_action = [d for d in drafts if d.get("layer") == "action" and d["record_status"] in ("draft", "watching")]
    pend_business = [d for d in drafts if d.get("layer") == "business" and d["record_status"] in ("draft", "watching")]
    action_due = [_due_item(d, "action") for d in pend_action
                  if d.get("check_due_date") is None or d["check_due_date"] <= today]
    business_due = [_due_item(d, "business") for d in pend_business
                    if d.get("check_due_date") is None or d["check_due_date"] <= today]

    # v1.0レガシーの読み替え（§9・正本は既存レコード・outcome確定はCEO）
    legacy_readmap = [
        {"legacy_id": d.get("result_id"), "判断": d["decision_ref"]["判断内容"],
         "interpret": {"action_result": "成功（実行済み）", "business_result": "継続観察（経営結果は要確認）"},
         "note": "v1.0記録のlayer読み替え（確定はCEO・既存レコードは不変）"}
        for d in drafts if not d.get("layer")
    ]

    confirmed = len(json.load(open(LOG_PATH, encoding="utf-8"))["results"])
    index = {
        "meta": {"generator": f"Result Recorder v{VERSION} [{STATE}]",
                 "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "note": "Brief『結果確認待ち』の参照元（v1.1・Action/Business分離）。判定はCEOのみ"},
        "summary": {"drafts_total": len(drafts),
                    "action_pending": len(pend_action), "business_pending": len(pend_business),
                    "action_due_now": len(action_due), "business_due_now": len(business_due),
                    "legacy_v10": len(legacy_readmap),
                    "confirmed_results": confirmed},
        "action_due": action_due,
        "business_due": business_due,
        "check_due": action_due + business_due,   # ceo_assistant後方互換（layerタグ付き）
        "legacy_readmap": legacy_readmap,
    }
    safe_write(INDEX_PATH, json.dumps(index, ensure_ascii=False, indent=2))
    print(f"保存: {DRAFT_PATH.name}（累計{len(drafts)}件）/ {INDEX_PATH.name}"
          f"（Action確認{len(action_due)} / Business確認{len(business_due)} / legacy {len(legacy_readmap)}）")
    print("→ Brief「⏰ 結果確認待ち」にAction/Businessを分けて掲載 → CEOが判定 → 確定はCEO確認後")


if __name__ == "__main__":
    main()
