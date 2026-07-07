#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Insight Generator v1.0 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト

Decision Log（CEO確定判断）から Insight Draft を自動生成する。
Learning Cycle v2.0（09_Learning/LEARNING_CYCLE_V2.md §2）の第一コンポーネント。

学習フロー上の位置: Decision Log → 【Insight Draft（本機能）】 → Pattern → Knowledge → CEO Review

重要ルール:
・入力は「CEO確定判断」のみ（会話からの機械抽出分・Draft状態の判断からは学ばない）
・判断理由が未記入（理由未記入/理由の記録なし/内容と同文）のDecisionからは生成しない（推測禁止）
・却下・保留の理由を最優先の学習素材として扱う（何をしないか=判断基準の輪郭）
・Evidence必須: 全InsightにDecision ID・日時・出典を封入。無ければ生成しない
・冪等: 処理済みDecisionの指紋をメタに記録し、再実行しても重複生成しない
・書き込み先は 09_Learning/insights/ のみ（decision_log本体には一切書かない）
・AIは昇格しない: 全Insightは status: draft / needs_ceo_review: true

使い方:
    python3 insight_generator.py            # 生成 + insight_draft_log.json 更新
    python3 insight_generator.py --check    # 対象Decisionの検出のみ（書き込みなし）
"""

import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# 意味的類似の判定に既存ロジックを再利用（重複判定§7の第2層）
from pattern_analyzer import normalize, ngrams, cosine, build_idf

VERSION = "1.0"
STATE = "Experimental"

BASE_DIR = Path(__file__).resolve().parent
DECISION_PATH = BASE_DIR / "01_Knowledge" / "08_Decision_Log" / "decision_log.json"
EVOLVING_PATH = BASE_DIR / "00_MASTER" / "EVOLVING_PRINCIPLES.md"
OUT_DIR = BASE_DIR / "09_Learning" / "insights"
OUT_PATH = OUT_DIR / "insight_draft_log.json"

NO_REASON = ("理由未記入", "理由の記録なし", "（CEO記入待ち）", "")
SIMILARITY_SKIP = 0.80  # 既存Insight/EPとの類似がこれ以上なら新規生成せずEvidence強化


def is_confirmed(d):
    """CEO確定判断のみ対象（Morning Brief経由・CEO確定記録のみ）。"""
    src = str(d.get("source", ""))
    result = str(d.get("結果", ""))
    return ("Morning Brief" in src or "CEO確定" in src
            or "CEO承認済み" in result)


def has_reason(d):
    r = str(d.get("判断理由", "")).strip()
    return r not in NO_REASON and r != str(d.get("判断内容", "")).strip()


def classify(d):
    """結果から学びのタイプを判定（承認基準 / 却下基準 / 保留・不足情報）。"""
    result = str(d.get("結果", ""))
    if re.search(r"却下|Reject", result, re.I):
        return "却下基準"
    if re.search(r"保留|Hold", result, re.I):
        return "保留・不足情報"
    return "承認基準"


def decision_fingerprint(d):
    return hashlib.md5(
        f"{d.get('日時','')}|{d.get('判断内容','')[:80]}".encode()).hexdigest()[:12]


def load_ep_titles():
    """既存EPタイトル（類似チェック用・EPの言い換えを新Insightにしない）。"""
    if not EVOLVING_PATH.exists():
        return []
    text = EVOLVING_PATH.read_text(encoding="utf-8")
    return [f"{m[0]}: {m[1].strip()}" for m in re.findall(r"^### (EP-\d+): (.+)$", text, re.M)]


def build_insight(d, fp):
    itype = classify(d)
    reason = str(d["判断理由"]).strip()
    content = str(d["判断内容"]).strip()
    # 推測禁止: 内容は判断内容+理由の構造化のみ（言い換え・要約による情報の追加をしない）
    if itype == "却下基準":
        text = f"やらないと判断したこと:「{content[:100]}」。理由: {reason}"
    elif itype == "保留・不足情報":
        text = f"保留した判断:「{content[:100]}」。保留理由・条件: {reason}"
    else:
        text = f"承認した判断:「{content[:100]}」。判断基準: {reason}"
    return {
        "insight_id": None,  # 採番は保存時
        "type": itype,
        "内容": text,
        "判断理由_原文": reason,
        "source_decisions": [fp],
        "evidence": {
            "decision_dates": [d.get("日時")],
            "source": d.get("source", d.get("Conversation ID", "")),
            "関連カテゴリ": d.get("関連カテゴリ"),
            "根拠EP_KN": d.get("根拠", []),
        },
        "status": "draft",
        "needs_ceo_review": True,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "generator_version": f"v{VERSION}",
    }


def main():
    check_only = "--check" in sys.argv
    decisions = json.load(open(DECISION_PATH, encoding="utf-8"))["decisions"]

    if OUT_PATH.exists():
        out = json.load(open(OUT_PATH, encoding="utf-8"))
    else:
        out = {"meta": {"generator": f"Insight Generator v{VERSION} [{STATE}]",
                        "note": "Decision Log（CEO確定判断）由来のInsight Draft。全件draft・CEOレビュー前にKnowledge/Principlesへ反映しない。",
                        "processed_fingerprints": []},
               "insights": []}
    processed = set(out["meta"].get("processed_fingerprints", []))

    # 対象抽出
    candidates, skipped = [], {"未確定": 0, "理由なし": 0, "処理済み": 0}
    for d in decisions:
        fp = decision_fingerprint(d)
        if fp in processed:
            skipped["処理済み"] += 1
            continue
        if not is_confirmed(d):
            skipped["未確定"] += 1
            continue
        if not has_reason(d):
            skipped["理由なし"] += 1
            processed.add(fp)  # 理由なしは今後も対象外（理由が追記されたら指紋が変わる設計ではないため注記）
            continue
        candidates.append((d, fp))

    print(f"Insight Generator v{VERSION} [{STATE}]")
    print(f"Decision Log: {len(decisions)}件 → 対象{len(candidates)}件 / "
          f"スキップ（未確定{skipped['未確定']}・理由なし{skipped['理由なし']}・処理済み{skipped['処理済み']}）")

    if check_only:
        for d, _ in candidates:
            print(f"  ・[{classify(d)}] {d['判断内容'][:60]}")
        print("--check: 書き込みなしで終了")
        return

    # 重複判定: 既存Insight+EPタイトルとの意味類似
    existing_texts = [i["内容"] for i in out["insights"]] + load_ep_titles()
    new_items = []
    for d, fp in candidates:
        ins = build_insight(d, fp)
        vecs = [ngrams(normalize(t)) for t in existing_texts + [ins["内容"]]]
        idf = build_idf(vecs)
        dup = None
        for j, t in enumerate(existing_texts):
            if cosine(vecs[j], vecs[-1], idf) >= SIMILARITY_SKIP:
                dup = j
                break
        if dup is not None and dup < len(out["insights"]):
            # 既存Insightの強化（新規作成しない）
            out["insights"][dup]["source_decisions"].append(fp)
            out["insights"][dup]["evidence"]["decision_dates"].append(d.get("日時"))
            print(f"  ↻ 既存強化: {out['insights'][dup]['insight_id']} ← {d['判断内容'][:40]}")
        else:
            new_items.append(ins)
            existing_texts.append(ins["内容"])
        processed.add(fp)

    for ins in new_items:
        ins["insight_id"] = f"INS2-{len(out['insights'])+1:03d}"
        out["insights"].append(ins)

    out["meta"]["processed_fingerprints"] = sorted(processed)
    out["meta"]["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out["meta"]["total_insights"] = len(out["insights"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    from collections import Counter
    print(f"新規Insight Draft: {len(new_items)}件 / 累計: {len(out['insights'])}件")
    for k, v in Counter(i["type"] for i in out["insights"]).most_common():
        print(f"  {k}: {v}件")
    for i in out["insights"]:
        print(f"  {i['insight_id']} [{i['type']}] {i['内容'][:70]}")


if __name__ == "__main__":
    main()
