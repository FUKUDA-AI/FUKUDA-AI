#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGPT Importer — NOMADO株式会社 FUKUDA AI プロジェクト

09_ChatGPT_Archive に置かれた ChatGPT エクスポートZIPを検出・展開し、
各Conversationを分類して「Conversation Index」を
07_Data/chatgpt_index.json に保存する。

・何度でも再実行可能(既存Indexとマージ、同一IDは更新日時が新しい方を採用)
・Knowledgeへの書き込みは行わない(Index作成のみ)

使い方:
    python3 chatgpt_importer.py
"""

import json
import re
import sys
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------
# パス設定(スクリプト位置 = プロジェクトルート基準)
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
ARCHIVE_DIR = BASE_DIR / "01_Knowledge" / "09_ChatGPT_Archive"
EXTRACT_DIR = ARCHIVE_DIR / "_extracted"
DATA_DIR = BASE_DIR / "07_Data"
INDEX_PATH = DATA_DIR / "chatgpt_index.json"

# ---------------------------------------------------------------
# カテゴリ定義(上から優先。専門カテゴリを先に判定)
# ---------------------------------------------------------------
CATEGORY_KEYWORDS = [
    ("so u",        ["so u", "sou ", "ソウ", "レザー", "革", "財布", "バッグ",
                     "名刺入れ", "キーケース", "コードバン", "ヌメ革", "栃木レザー"]),
    ("SUNNY NOMADO", ["sunny nomado", "サニーノマド", "サニー", "帆布", "キャンバス",
                      "トート", "サコッシュ"]),
    ("催事",         ["催事", "ポップアップ", "pop-up", "popup", "百貨店", "出店",
                     "催場", "物産展", "阪急", "伊勢丹", "高島屋", "大丸", "松坂屋",
                     "三越", "そごう", "東急", "小田急", "京王", "近鉄", "岩田屋"]),
    ("在庫・発注",   ["在庫", "発注", "仕入", "入荷", "納期", "納品", "欠品",
                     "リードタイム", "ロット", "工場", "生産", "検品", "sku"]),
    ("資金繰り",     ["資金繰り", "キャッシュフロー", "資金", "運転資金", "支払",
                     "入金", "手形", "売掛", "買掛"]),
    ("銀行",         ["銀行", "融資", "借入", "返済", "信用金庫", "信金", "公庫",
                     "日本政策金融公庫", "保証協会", "利率", "金利"]),
    ("広告",         ["広告", "meta広告", "リスティング", "cpa", "cpc", "roas",
                     "インスタ広告", "facebook広告", "google広告", "運用型"]),
    ("SEO",          ["seo", "検索順位", "キーワード選定", "被リンク", "コンテンツマーケ",
                     "検索流入", "メタディスクリプション"]),
    ("EC",           ["shopify", "ec", "ネットショップ", "オンラインストア", "楽天",
                     "amazon", "カート", "コンバージョン", "cvr", "ランディングページ",
                     "lp", "通販", "越境"]),
    ("SNS",          ["インスタ", "instagram", "sns", "tiktok", "リール", "フォロワー",
                     "投稿", "ハッシュタグ", "x(twitter)", "twitter", "youtube",
                     "エンゲージメント"]),
    ("商品企画",     ["商品企画", "新商品", "新作", "企画", "サンプル", "試作",
                     "デザイン案", "商品開発", "ラインナップ", "価格設定", "プライシング"]),
    ("営業",         ["営業", "商談", "卸", "取引先", "バイヤー", "展示会", "見積",
                     "提案書", "アポ", "顧客リスト", "法人"]),
    ("デザイン",     ["デザイン", "ロゴ", "パッケージ", "タグ", "リーフレット",
                     "チラシ", "dm", "illustrator", "photoshop", "フォント", "配色"]),
    ("写真",         ["写真", "撮影", "カメラ", "ライティング", "物撮り", "レタッチ",
                     "lightroom", "画像編集", "モデル撮影"]),
    ("ブランド",     ["ブランド", "ブランディング", "世界観", "コンセプト", "ストーリー",
                     "ミッション", "ビジョン", "バリュー", "らしさ", "ブランド価値"]),
    ("経営",         ["経営", "売上", "利益", "粗利", "戦略", "事業計画", "決算",
                     "損益", "pl", "bs", "kpi", "組織", "採用", "人事", "税理士",
                     "会社", "法人化", "節税", "経費"]),
    ("AI",           ["ai", "chatgpt", "claude", "gpt", "プロンプト", "自動化",
                     "エージェント", "llm", "機械学習", "notebooklm", "gemini"]),
    ("家族",         ["家族", "妻", "子供", "息子", "娘", "実家", "両親", "父", "母",
                     "育児", "学校", "保育園"]),
    ("雑談",         ["雑談", "おすすめ", "旅行", "ランチ", "映画", "健康", "筋トレ",
                     "ダイエット", "レシピ", "趣味"]),
]

CATEGORIES = [c for c, _ in CATEGORY_KEYWORDS] + ["その他"]

# 重要度判定用: 経営インパクトの大きい語
HIGH_IMPORTANCE_WORDS = [
    "売上", "利益", "粗利", "資金繰り", "融資", "借入", "戦略", "事業計画",
    "催事", "百貨店", "発注", "在庫", "価格", "ブランド価値", "決算", "契約",
]


# ---------------------------------------------------------------
# ZIP検出・展開
# ---------------------------------------------------------------
def find_zips() -> list[Path]:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(ARCHIVE_DIR.glob("*.zip"))


def extract_zip(zip_path: Path) -> Path:
    """ZIPを _extracted/<zip名>/ に展開(既展開ならスキップ)"""
    dest = EXTRACT_DIR / zip_path.stem
    if dest.exists() and any(dest.iterdir()):
        print(f"  展開済みのためスキップ: {zip_path.name}")
        return dest
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)
    print(f"  展開完了: {zip_path.name} → {dest.relative_to(BASE_DIR)}")
    return dest


# ---------------------------------------------------------------
# conversation JSON の読み込み
# ---------------------------------------------------------------
def load_conversations(extracted_dir: Path) -> list[dict]:
    """
    ChatGPTエクスポートの両形式に対応:
      A) conversations.json(全会話が1つの配列)
      B) conversation-*.json(1会話1ファイル)
    """
    conversations = []

    # 形式B: conversation-*.json
    for f in sorted(extracted_dir.rglob("conversation*.json")):
        if f.name == "conversations.json":
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, list):
                conversations.extend(data)
            else:
                conversations.append(data)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"  [警告] 読み込み失敗: {f.name} ({e})")

    # 形式A: conversations.json
    for f in sorted(extracted_dir.rglob("conversations.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, list):
                conversations.extend(data)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"  [警告] 読み込み失敗: {f.name} ({e})")

    return conversations


# ---------------------------------------------------------------
# 会話からテキスト抽出
# ---------------------------------------------------------------
def extract_messages(conv: dict) -> list[tuple[str, str]]:
    """mapping構造から (role, text) を時系列で取り出す"""
    messages = []
    mapping = conv.get("mapping") or {}
    nodes = []
    for node in mapping.values():
        msg = node.get("message")
        if not msg:
            continue
        content = msg.get("content") or {}
        parts = content.get("parts") or []
        text = " ".join(str(p) for p in parts
                        if isinstance(p, str) and p.strip())
        if not text.strip():
            continue
        role = (msg.get("author") or {}).get("role", "")
        if role in ("user", "assistant"):
            nodes.append((msg.get("create_time") or 0, role, text.strip()))
    nodes.sort(key=lambda x: x[0])
    messages = [(role, text) for _, role, text in nodes]
    return messages


# ---------------------------------------------------------------
# 分類・重要度・概要
# ---------------------------------------------------------------
def classify(title: str, messages: list[tuple[str, str]]) -> str:
    # タイトルは重み3、ユーザー発言は重み2、AI発言は重み1
    scores: Counter = Counter()
    corpus = [(title.lower(), 3)]
    corpus += [(t.lower(), 2 if r == "user" else 1)
               for r, t in messages[:30]]  # 冒頭30メッセージで判定

    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            for text, weight in corpus:
                scores[category] += text.count(kw.lower()) * weight

    if not scores or scores.most_common(1)[0][1] == 0:
        return "その他"
    return scores.most_common(1)[0][0]


def judge_importance(title: str, messages: list[tuple[str, str]],
                     category: str) -> str:
    """高 / 中 / 低"""
    full_text = (title + " " + " ".join(t for _, t in messages)).lower()
    hits = sum(full_text.count(w.lower()) for w in HIGH_IMPORTANCE_WORDS)
    n = len(messages)

    if category in ("雑談", "その他") and hits < 3:
        return "低"
    if hits >= 5 or (n >= 20 and hits >= 2):
        return "高"
    if hits >= 1 or n >= 10:
        return "中"
    return "低"


def make_summary(title: str, messages: list[tuple[str, str]],
                 max_len: int = 120) -> str:
    """最初の実質的なユーザー発言から概要を作る"""
    for role, text in messages:
        if role != "user":
            continue
        clean = re.sub(r"\s+", " ", text).strip()
        if len(clean) < 5:  # 「はい」等はスキップ
            continue
        return clean[:max_len] + ("…" if len(clean) > max_len else "")
    return title  # ユーザー発言が無ければタイトルで代用


def format_ts(ts) -> str:
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M")
    except (ValueError, OSError, OverflowError):
        return ""


# ---------------------------------------------------------------
# Index構築
# ---------------------------------------------------------------
def build_entry(conv: dict, source_zip: str) -> dict | None:
    conv_id = conv.get("conversation_id") or conv.get("id") or ""
    title = (conv.get("title") or "(無題)").strip()
    messages = extract_messages(conv)
    if not conv_id and not messages:
        return None

    category = classify(title, messages)
    return {
        "id": conv_id or f"untitled-{hash(title) & 0xffffffff:x}",
        "title": title,
        "created_at": format_ts(conv.get("create_time")),
        "updated_at": format_ts(conv.get("update_time")),
        "category": category,
        "importance": judge_importance(title, messages, category),
        "summary": make_summary(title, messages),
        "message_count": len(messages),
        "source_zip": source_zip,
    }


def load_existing_index() -> dict:
    if INDEX_PATH.exists():
        try:
            return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("[警告] 既存Indexが破損しているため新規作成します")
    return {"meta": {}, "conversations": []}


def merge_entries(existing: list[dict], new: list[dict]) -> list[dict]:
    """IDでマージ。updated_atが新しい方を採用"""
    by_id = {e["id"]: e for e in existing}
    for entry in new:
        old = by_id.get(entry["id"])
        if old is None or entry["updated_at"] >= old.get("updated_at", ""):
            by_id[entry["id"]] = entry
    merged = list(by_id.values())
    merged.sort(key=lambda e: e.get("created_at", ""), reverse=True)
    return merged


# ---------------------------------------------------------------
# 統計表示
# ---------------------------------------------------------------
def print_stats(entries: list[dict], new_count: int):
    print("\n" + "=" * 50)
    print("Conversation Index 統計")
    print("=" * 50)
    print(f"今回取り込んだConversation数: {new_count}")
    print(f"Index内の総Conversation数:   {len(entries)}")

    print("\n【カテゴリ別件数】")
    cat_counts = Counter(e["category"] for e in entries)
    for cat in CATEGORIES:
        if cat_counts.get(cat):
            print(f"  {cat}: {cat_counts[cat]}件")

    print("\n【年代別件数】")
    year_counts = Counter(
        (e.get("created_at") or "不明")[:4] for e in entries)
    for year in sorted(year_counts):
        print(f"  {year if year != '不明' else '不明'}: {year_counts[year]}件")

    print("\n【重要度別件数】")
    imp_counts = Counter(e["importance"] for e in entries)
    for imp in ("高", "中", "低"):
        if imp_counts.get(imp):
            print(f"  {imp}: {imp_counts[imp]}件")


# ---------------------------------------------------------------
# メイン
# ---------------------------------------------------------------
def main():
    print("ChatGPT Importer 開始")
    print(f"アーカイブフォルダ: {ARCHIVE_DIR.relative_to(BASE_DIR)}")

    zips = find_zips()
    if not zips:
        print("\nZIPファイルが見つかりません。")
        print(f"ChatGPTエクスポートZIPを {ARCHIVE_DIR} に置いて再実行してください。")
        sys.exit(0)

    print(f"検出したZIP: {len(zips)}件")

    new_entries = []
    for zip_path in zips:
        print(f"\n処理中: {zip_path.name}")
        extracted = extract_zip(zip_path)
        convs = load_conversations(extracted)
        print(f"  Conversation数: {len(convs)}")
        for conv in convs:
            entry = build_entry(conv, zip_path.name)
            if entry:
                new_entries.append(entry)

    index = load_existing_index()
    merged = merge_entries(index.get("conversations", []), new_entries)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "meta": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_zips": sorted({e["source_zip"] for e in merged}),
            "total_conversations": len(merged),
            "note": "Conversation IndexのみでKnowledge未反映",
        },
        "conversations": merged,
    }
    INDEX_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"\nIndex保存: {INDEX_PATH.relative_to(BASE_DIR)}")

    print_stats(merged, len(new_entries))


if __name__ == "__main__":
    main()
