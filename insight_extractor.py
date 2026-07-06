#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Insight Extractor v2.0 — NOMADO株式会社 FUKUDA AI プロジェクト

展開済みChatGPTエクスポートから「経営上の気付き・仮説・学び」を抽出し、
正式保存先 01_Knowledge/08_Decision_Log/insight_log.json に保存する。

v2.0 (2026-07-06): 出力先を正式保存先へ変更（decision_extractor.pyのLOG_DIRに追随。
CEO決定・フォルダ構成変更のためメジャー更新）。抽出ロジックはv1.0から無変更。

抽出タイプ:
  気付き / 仮説 / 学び / 改善案 / 成功要因 / 失敗要因 /
  ブランドへの考え / 職人との考え / お客様理解

・Decisionより緩い条件で抽出(確定表現でなくてもよい)
・Conversation全文は保存しない(Insight文のみ)
・decision_log.json とは別ファイルで管理
・何度でも再実行可能(マージ / --rebuild で再構築)

使い方:
    python3 insight_extractor.py            # 既存ログとマージ
    python3 insight_extractor.py --rebuild  # ゼロから再構築
"""

import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from chatgpt_importer import extract_messages, format_ts
from decision_extractor import (
    BRAND_KEYWORDS, detect_brand, split_sentences, iter_conversations,
    load_index_meta, LOG_DIR,
)

BASE_DIR = Path(__file__).resolve().parent
LOG_PATH = LOG_DIR / "insight_log.json"

MAX_LEN = 250
MAX_PER_CONV = 10  # 1会話あたりの上限(ノイズ防止)

# ---------------------------------------------------------------
# Insightタイプ定義(上から優先判定)
# 主題ベース(職人・顧客・ブランド)を先に、表現ベースを後に
# ---------------------------------------------------------------
INSIGHT_TYPES = [
    ("職人との考え", re.compile(
        r"(職人|工房|作り手|縫製さん|革屋|工場さん)")),
    ("お客様理解", re.compile(
        r"(お客様は|お客様が|お客さんは|お客さんが|顧客は|顧客が|"
        r"お客様の声|レビューで|購入される方|買われる方|リピーター|"
        r"ファンの方|来店される)")),
    ("ブランドへの考え", re.compile(
        r"(ブランドとして|ブランドの方向|ブランド価値|らしさ|世界観|"
        r"ブランドを育て|ブランドの軸|コンセプトは)")),
    ("成功要因", re.compile(
        r"(うまくいった|好評だった|好評でした|完売した|完売しました|"
        r"売れた理由|好調だった|好調でした|成功した|効果があった|"
        r"反応が良かった|よく売れた)")),
    ("失敗要因", re.compile(
        r"(失敗した|失敗でした|売れなかった|うまくいかなかった|"
        r"反省|課題が残った|不調だった|効果がなかった|反応が悪かった|"
        r"想定より売れ)")),
    ("学び", re.compile(
        r"(学んだ|学びました|勉強になった|教訓|痛感した|痛感しました|"
        r"身にしみ|思い知)")),
    ("改善案", re.compile(
        r"(改善したい|改善すべき|改善した方|した方が良い|したほうが良い|"
        r"すべきだと|する必要がある|見直したい|見直すべき|"
        r"次回は|今後は.{0,30}(したい|する|していく))")),
    ("気付き", re.compile(
        r"(気づいた|気付いた|気づきました|気付きました|わかった|"
        r"分かった|判明した|発見した|実感した|実感して|感じている|"
        r"感じました|と感じた)")),
    ("仮説", re.compile(
        r"(のではないか|ではないかと|かもしれない|かもしれません|"
        r"と仮説|と予想|と見ている|気がする|気がします|と思っている|"
        r"と考えている|と読んで)")),
]

# 疑問・依頼・AI出力の混入を除外
EXCLUDE = re.compile(
    r"(ですか|ますか|でしょうか|\?|？|どうすれば|べきか|"
    r"教えて|作って|作成して|してください|お願いします|お願いいたします|"
    r"コマンドを実行|モーダル|チェックボックス|\.zip|```|</|<p|http)"
)


def classify_insight(sentence: str) -> str | None:
    for itype, pattern in INSIGHT_TYPES:
        if pattern.search(sentence):
            return itype
    return None


def extract_insights(conv: dict, meta: dict) -> list[dict]:
    if meta.get("category") in ("家族", "雑談"):
        return []

    messages = extract_messages(conv)
    insights = []
    seen = set()

    for role, text in messages:
        if role != "user":  # 本人の発言のみ(AIの一般論は除外)
            continue
        for sentence in split_sentences(text):
            if len(sentence) < 15 or len(sentence) > 500:
                continue
            if EXCLUDE.search(sentence):
                continue
            # 英文主体の文(混入したシステムプロンプト等)を除外
            ascii_ratio = sum(c.isascii() for c in sentence) / len(sentence)
            if ascii_ratio > 0.5:
                continue
            itype = classify_insight(sentence)
            if itype is None:
                continue
            key = sentence[:60]
            if key in seen:
                continue
            seen.add(key)

            insights.append({
                "タイプ": itype,
                "内容": sentence[:MAX_LEN],
                "関連ブランド": detect_brand(
                    sentence + " " + meta.get("title", "")),
                "関連カテゴリ": meta.get("category", "その他"),
                "重要度": meta.get("importance", "低"),
                "日時": meta.get("created_at", ""),
                "Conversation ID": meta.get("id", ""),
            })
            if len(insights) >= MAX_PER_CONV:
                return insights
    return insights


def merge_insights(existing: list[dict], new: list[dict]) -> list[dict]:
    def key(d):
        # 会話をまたぐ同一文(使い回しメール文面等)も1件に集約
        return re.sub(r"\s+", "", d["内容"])[:60]
    by_key = {key(d): d for d in existing}
    for d in new:
        by_key[key(d)] = d
    merged = list(by_key.values())
    merged.sort(key=lambda d: d.get("日時", ""), reverse=True)
    return merged


def main():
    print("Insight Extractor v2.0 開始")
    meta_by_id = load_index_meta()

    new_insights = []
    conv_count = 0
    for conv in iter_conversations():
        conv_count += 1
        cid = conv.get("conversation_id") or conv.get("id") or ""
        meta = meta_by_id.get(cid, {"id": cid})
        if not meta.get("created_at"):
            meta["created_at"] = format_ts(conv.get("create_time"))
        if not meta.get("title"):
            meta["title"] = conv.get("title") or ""
        new_insights.extend(extract_insights(conv, meta))

    print(f"走査したConversation数: {conv_count}")

    existing = []
    if "--rebuild" in sys.argv:
        print("再構築モード: 既存ログを無視して新規作成します")
    elif LOG_PATH.exists():
        try:
            existing = json.loads(
                LOG_PATH.read_text(encoding="utf-8")).get("insights", [])
        except json.JSONDecodeError:
            print("[警告] 既存Insight Logが破損しているため新規作成します")

    merged = merge_insights(existing, new_insights)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps({
        "meta": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_insights": len(merged),
            "note": "Insight LogのみでKnowledge未反映",
        },
        "insights": merged,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"保存: {LOG_PATH.relative_to(BASE_DIR)}")

    # ---- 統計表示 ----
    print("\n" + "=" * 50)
    print("Insight Log 統計")
    print("=" * 50)
    print(f"Insight総数: {len(merged)}")

    print("\n【タイプ別件数】")
    for t, n in Counter(d["タイプ"] for d in merged).most_common():
        print(f"  {t}: {n}件")

    print("\n【カテゴリ別件数】")
    for c, n in Counter(d["関連カテゴリ"] for d in merged).most_common():
        print(f"  {c}: {n}件")

    print("\n【ブランド別件数】")
    for b, n in Counter(d["関連ブランド"] for d in merged).most_common():
        print(f"  {b}: {n}件")


if __name__ == "__main__":
    main()
