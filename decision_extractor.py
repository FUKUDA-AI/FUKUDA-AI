#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decision Extractor v2.0 — NOMADO株式会社 FUKUDA AI プロジェクト

展開済みChatGPTエクスポート(01_Knowledge/09_ChatGPT_Archive/_extracted/)から
「経営判断」だけを抽出し、Decision Logを正式保存先 01_Knowledge/08_Decision_Log/ に保存する。

v2.0 (2026-07-06): 出力先をルート08_Decision_Log/から正式保存先
01_Knowledge/08_Decision_Log/へ変更（CEO決定・フォルダ構成変更のためメジャー更新）。
抽出ロジックはv1.0から無変更。

・Conversation全文は保存しない(判断・理由・結果のみ)
・1Conversationに複数Decisionがあればすべて抽出
・何度でも再実行可能(同一判断はマージ)
・Knowledgeへの転記は行わない

使い方:
    python3 decision_extractor.py            # 既存ログとマージ
    python3 decision_extractor.py --rebuild  # ゼロから再構築
"""

import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from chatgpt_importer import extract_messages, format_ts

BASE_DIR = Path(__file__).resolve().parent
EXTRACT_DIR = BASE_DIR / "01_Knowledge" / "09_ChatGPT_Archive" / "_extracted"
INDEX_PATH = BASE_DIR / "07_Data" / "chatgpt_index.json"
LOG_DIR = BASE_DIR / "01_Knowledge" / "08_Decision_Log"  # v2.0: 正式保存先へ変更
LOG_PATH = LOG_DIR / "decision_log.json"

# ---------------------------------------------------------------
# 判断検出パターン(ユーザー発言の「決めた・実行した」表現のみ)
# ---------------------------------------------------------------
DECISION_PATTERNS = re.compile(
    r"(ことにした|ことにしました|ことに決めた|と決めた|決めました|"
    r"決定しました|決定した|を決定|採用しました|採用した|採用することに|"
    r"やめることに|やめました|中止しました|中止した|中止することに|"
    r"導入しました|導入した|導入することに|変更しました|変更した|変更することに|"
    r"切り替えました|切り替えた|切り替えることに|撤退します|撤退した|撤退することに|"
    r"で行くことに|でいくことに|で進めます|で進めることに|"
    r"契約しました|契約することに|"
    r"値上げしました|値上げすることに|値下げしました|値下げすることに|"
    r"出店します|出店することに|出店を決め)"
)

# 判断でない文を除外(疑問・仮定・相談・作業依頼)
EXCLUDE_PATTERNS = re.compile(
    r"(どうすれば|べきか|しようか|でしょうか|ますか|ですか|\?|？|"
    r"としたら|とした場合|するとしたら|迷って|"
    r"ものの|作って|作成して|教えて|してください|お願いします|"
    r"したい|たい場合|た場合|た方が|たほうが|切り替わ|"
    r"コマンドを実行|モーダル|チェックボックス|\.zip|```)"
)

REASON_MARKERS = re.compile(r"(ため|ので|から|理由は|背景|狙い)")
RESULT_MARKERS = re.compile(
    r"(結果|完売|売れた|売れなかった|好調|不調|増えた|減った|"
    r"うまくいった|うまくいかなかった|failed|成功した|失敗した|"
    r"できました|できた|達成)"
)

BRAND_KEYWORDS = {
    "so u": ["so u", "sou ", "ソウ", "レザー", "革", "財布", "コードバン",
             "ヌメ革", "栃木レザー", "名刺入れ", "キーケース"],
    "SUNNY NOMADO": ["sunny nomado", "サニーノマド", "サニー", "帆布",
                     "キャンバス", "トート", "サコッシュ"],
}

MAX_LEN = 200  # 保存する文の最大長


# ---------------------------------------------------------------
# ヘルパー
# ---------------------------------------------------------------
def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text)
    return [s.strip() for s in re.split(r"[。\n！!]", text) if s.strip()]


def detect_brand(text: str) -> str:
    t = text.lower()
    hits = [b for b, kws in BRAND_KEYWORDS.items()
            if any(k.lower() in t for k in kws)]
    if len(hits) == 2:
        return "両ブランド"
    if hits:
        return hits[0]
    return "全社"


def find_reason(sentences: list[str], idx: int) -> str:
    """判断文の前後1文と判断文自体から理由を探す"""
    for i in (idx, idx - 1, idx + 1):
        if 0 <= i < len(sentences) and REASON_MARKERS.search(sentences[i]):
            return sentences[i][:MAX_LEN]
    return "理由の記録なし"


def find_result(messages: list, msg_idx: int) -> str:
    """判断より後のユーザー発言から結果らしい文を探す"""
    for role, text in messages[msg_idx + 1:]:
        if role != "user":
            continue
        for s in split_sentences(text):
            if RESULT_MARKERS.search(s) and not EXCLUDE_PATTERNS.search(s):
                return s[:MAX_LEN]
    return "結果未記録"


# ---------------------------------------------------------------
# 抽出本体
# ---------------------------------------------------------------
def extract_decisions(conv: dict, meta: dict) -> list[dict]:
    messages = extract_messages(conv)
    decisions = []
    seen = set()

    # 経営判断のみ対象(私的な会話は除外)
    if meta.get("category") in ("家族", "雑談"):
        return []

    for msg_idx, (role, text) in enumerate(messages):
        if role != "user":  # 判断は本人(ユーザー)の発言のみ
            continue
        sentences = split_sentences(text)
        for s_idx, sentence in enumerate(sentences):
            if len(sentence) < 8 or len(sentence) > 500:
                continue
            if not DECISION_PATTERNS.search(sentence):
                continue
            if EXCLUDE_PATTERNS.search(sentence):
                continue
            key = sentence[:60]
            if key in seen:
                continue
            seen.add(key)

            context = text  # ブランド判定はメッセージ全体で
            decisions.append({
                "判断内容": sentence[:MAX_LEN],
                "判断理由": find_reason(sentences, s_idx),
                "結果": find_result(messages, msg_idx),
                "関連ブランド": detect_brand(context + " " + meta.get("title", "")),
                "関連カテゴリ": meta.get("category", "その他"),
                "重要度": meta.get("importance", "低"),
                "日時": meta.get("created_at", ""),
                "Conversation ID": meta.get("id", ""),
            })
    return decisions


def load_index_meta() -> dict:
    """Conversation ID → index情報(カテゴリ・重要度・日時)"""
    if not INDEX_PATH.exists():
        print("[エラー] 07_Data/chatgpt_index.json がありません。"
              "先に chatgpt_importer.py を実行してください。")
        raise SystemExit(1)
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return {e["id"]: e for e in index.get("conversations", [])}


def iter_conversations():
    """展開済みフォルダから全conversationを読み込む"""
    if not EXTRACT_DIR.exists():
        print("[エラー] 展開済みデータがありません。"
              "先に chatgpt_importer.py を実行してください。")
        raise SystemExit(1)
    for f in sorted(EXTRACT_DIR.rglob("conversation*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"  [警告] 読み込み失敗: {f.name} ({e})")
            continue
        if isinstance(data, list):
            yield from data
        else:
            yield data


# ---------------------------------------------------------------
# マージ・保存・統計
# ---------------------------------------------------------------
def merge_decisions(existing: list[dict], new: list[dict]) -> list[dict]:
    def key(d):
        return (d["Conversation ID"], d["判断内容"])
    by_key = {key(d): d for d in existing}
    for d in new:
        by_key[key(d)] = d
    merged = list(by_key.values())
    merged.sort(key=lambda d: d.get("日時", ""), reverse=True)
    return merged


def main():
    print("Decision Extractor 開始")
    meta_by_id = load_index_meta()

    new_decisions = []
    conv_count = 0
    for conv in iter_conversations():
        conv_count += 1
        cid = conv.get("conversation_id") or conv.get("id") or ""
        meta = meta_by_id.get(cid, {"id": cid})
        if not meta.get("created_at"):
            meta["created_at"] = format_ts(conv.get("create_time"))
        if not meta.get("title"):
            meta["title"] = conv.get("title") or ""
        new_decisions.extend(extract_decisions(conv, meta))

    print(f"走査したConversation数: {conv_count}")

    existing = []
    if "--rebuild" in sys.argv:
        print("再構築モード: 既存ログを無視して新規作成します")
    elif LOG_PATH.exists():
        try:
            existing = json.loads(
                LOG_PATH.read_text(encoding="utf-8")).get("decisions", [])
        except json.JSONDecodeError:
            print("[警告] 既存Decision Logが破損しているため新規作成します")

    merged = merge_decisions(existing, new_decisions)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps({
        "meta": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_decisions": len(merged),
            "note": "Decision LogのみでKnowledge未反映",
        },
        "decisions": merged,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"保存: {LOG_PATH.relative_to(BASE_DIR)}")

    # ---- 統計表示 ----
    print("\n" + "=" * 50)
    print("Decision Log 統計")
    print("=" * 50)
    print(f"Decision総数: {len(merged)}")

    print("\n【カテゴリ別件数】")
    for cat, n in Counter(d["関連カテゴリ"] for d in merged).most_common():
        print(f"  {cat}: {n}件")

    print("\n【ブランド別件数】")
    for brand, n in Counter(d["関連ブランド"] for d in merged).most_common():
        print(f"  {brand}: {n}件")


if __name__ == "__main__":
    main()
