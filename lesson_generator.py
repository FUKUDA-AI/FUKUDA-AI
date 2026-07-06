#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lesson Generator v1.0 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト

Pattern / Insight / Decision から「今後の経営判断に再利用できる学び（Lesson）」を
抽象化して生成し、lesson_log.json に保存する。

Architecture v1.2 上の位置づけ:
    Pattern → 【Lesson（本機能）】 → Evolving Principles → CEO Review → Core Principles

Layer: ③Knowledge Layerへの供給ライン（Lesson層）
参照: 01_Knowledge/08_Decision_Log/ の pattern_log.json / insight_log.json / decision_log.json（読み取りのみ）
更新: 01_Knowledge/08_Decision_Log/lesson_log.json（新規出力のみ）

重要ルール（KNOWLEDGE_PROMOTION_RULES.md準拠）:
・全Lessonは status: draft / needs_ceo_review: true
・正式Knowledge / EVOLVING_PRINCIPLES / CORE_PRINCIPLES へは反映しない（CEO Review後のみ）

生成ロジック:
1) Pattern由来: 全Pattern（3会話以上の反復）→ 行動指針として抽象化
2) Insight由来: 成功要因 / 失敗要因 / 学び / 改善案（重要度 中・高）
   → ノイズ除去 → 意味的に近いものを統合 → タイプ別テンプレートで行動指針化
3) Decision由来: 判断理由が実記録された経営判断 → 判断基準として再利用可能な形に

使い方:
    python3 lesson_generator.py
"""

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# Pattern Analyzerの正規化・類似度ロジックを再利用
from pattern_analyzer import normalize, ngrams, cosine, build_idf, keywords

VERSION = "1.0"
STATE = "Experimental"

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "01_Knowledge" / "08_Decision_Log"
PATTERN_PATH = LOG_DIR / "pattern_log.json"
INSIGHT_PATH = LOG_DIR / "insight_log.json"
DECISION_PATH = LOG_DIR / "decision_log.json"
OUTPUT_PATH = LOG_DIR / "lesson_log.json"

# 対象とするInsightタイプと重要度
LEARNING_TYPES = ("成功要因", "失敗要因", "学び", "改善案")
MIN_IMPORTANCE = ("高", "中")
MERGE_THRESHOLD = 0.45  # 近接Insightの統合しきい値

# ノイズ除去: 経営の学びと無関係な文（ニュース断片・私物売買等）
NOISE_RE = re.compile(
    r"報道官|外務省|日銀|原油価格|軍民|防衛研究所|オールドレンズ|くもりなし|出品します"
)
NOISE_CATEGORIES = {"写真"}

TODAY = datetime.now().strftime("%Y-%m-%d")


def polish(text: str, limit: int = 160) -> str:
    """メール文体の枕・結びを軽く落とし、学び本文を取り出す。"""
    t = re.sub(r"<[^>]+>", " ", str(text))
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"^(もしすでにご存知でしたら恐縮ですが、|お世話になっております。?)", "", t)
    t = re.sub(r"(何卒|今後とも).{0,20}(お願い致します|お願いいたします)。?$", "", t)
    return t[:limit].strip()


# タイプ別テンプレート: (lesson type, 指針化, expected_effect, risk)
TEMPLATES = {
    "成功要因": (
        "成功要因",
        "この成功要因を他の販路・商品・催事でも意図的に再現する",
        "実績のある打ち手の横展開により、成功確率の高い判断ができる",
        "当時の条件（場所・季節・商材）に依存する可能性。再現時は条件の一致を確認する",
    ),
    "失敗要因": (
        "失敗要因",
        "同種の失敗を繰り返さないよう、事前チェック項目に組み込む",
        "同じ失敗の再発防止。事故・信用毀損コストの回避",
        "個別事情の一般化しすぎ。原因の特定が浅い場合は対策が形骸化する",
    ),
    "学び": (
        "会社の学び",
        "この学びを標準プロセスへ反映する",
        "業務品質の底上げと属人化の防止",
        "一度の経験からの一般化。適用範囲の見極めが必要",
    ),
    "改善案": (
        "今後の行動指針",
        "実施可否を判断し、実行する場合は担当・期限を決める",
        "業務・商品・サービスの具体的改善",
        "未実行のアイデア段階。効果は未検証",
    ),
}


def load_json(path, key):
    return json.load(open(path, encoding="utf-8"))[key]


def is_noise(item):
    if NOISE_RE.search(item.get("内容", "")):
        return True
    if item.get("関連カテゴリ") in NOISE_CATEGORIES:
        return True
    return False


def merge_similar(items):
    """意味的に近いInsightを1つの学びに統合する。"""
    if not items:
        return []
    vecs = [ngrams(normalize(i["内容"])) for i in items]
    idf = build_idf(vecs)
    groups = []
    for idx, it in enumerate(items):
        placed = False
        for g in groups:
            if cosine(vecs[idx], vecs[g[0]], idf) >= MERGE_THRESHOLD:
                g.append(idx)
                placed = True
                break
        if not placed:
            groups.append([idx])
    return [[items[i] for i in g] for g in groups]


def confidence_for(evidence_convs, base="low"):
    n = len(set(evidence_convs))
    if n >= 4:
        return "high"
    if n >= 2:
        return "medium"
    return base


def main():
    patterns = load_json(PATTERN_PATH, "patterns")
    insights = load_json(INSIGHT_PATH, "insights")
    decisions = load_json(DECISION_PATH, "decisions")
    lessons = []

    # ---- 1) Pattern由来 ----
    for p in patterns:
        core = polish(p["summary"], 120)
        verbatim = p.get("verbatim_suspected", False)
        lessons.append({
            "title": f"反復パターン: {p['pattern_name'].split(': ', 1)[-1]}",
            "summary": f"「{core}」— 異なる会話で{p['conversation_count']}回反復された考え方。今後の発信・判断でも一貫して適用する",
            "type": "今後の行動指針" if p["type"] != "経営判断" else "判断理由",
            "category": p["category"],
            "brand": p["brand"],
            "reason": f"{p['first_seen'][:10]}〜{p['last_seen'][:10]}に{p['conversation_count']}会話で反復。単発の思いつきではなく検証された考え方（{p['pattern_id']}）",
            "expected_effect": "ブランドの語り口・判断の一貫性が保たれ、憲法（歩みゆたかに）との整合を維持できる",
            "risk": "定型文由来の可能性があり、実際の判断で使われた思想か要確認" if verbatim else "文脈が変わった場合の適用可否はCEO判断が必要",
            "related_patterns": [p["pattern_id"]],
            "related_insights": [],
            "related_decisions": [],
            "source_ids": p["source_ids"],
            "confidence": p["confidence"],
        })

    # ---- 2) Insight由来（学び系タイプ・ノイズ除去・近接統合） ----
    cands = [i for i in insights
             if i["タイプ"] in LEARNING_TYPES and i["重要度"] in MIN_IMPORTANCE
             and not is_noise(i)]
    by_type = defaultdict(list)
    for i in cands:
        by_type[i["タイプ"]].append(i)

    for typ, items in by_type.items():
        ltype, directive, effect, risk = TEMPLATES[typ]
        for group in merge_similar(items):
            rep = max(group, key=lambda x: (x["重要度"] == "高", len(x["内容"])))
            convs = [g["Conversation ID"] for g in group]
            core = polish(rep["内容"])
            kw = keywords([g["内容"] for g in group], 2)
            lessons.append({
                "title": f"{typ}: {'・'.join(kw) if kw else core[:20]}",
                "summary": f"「{core}」— {directive}",
                "type": ltype,
                "category": Counter(g["関連カテゴリ"] for g in group).most_common(1)[0][0],
                "brand": Counter(g["関連ブランド"] for g in group).most_common(1)[0][0],
                "reason": f"Insight Logの{typ}（重要度{rep['重要度']}・{len(group)}件）より抽出",
                "expected_effect": effect,
                "risk": risk,
                "related_patterns": [],
                "related_insights": [f"{g['タイプ']}@{g['Conversation ID']}" for g in group],
                "related_decisions": [],
                "source_ids": sorted(set(convs)),
                "confidence": confidence_for(convs),
            })

    # ---- 3) Decision由来（判断理由が実記録されたもの） ----
    for d in decisions:
        reason = d.get("判断理由", "")
        if not reason or reason == "理由の記録なし" or reason == d.get("判断内容"):
            continue
        if NOISE_RE.search(d.get("判断内容", "")):
            continue
        content = polish(d["判断内容"], 100)
        lessons.append({
            "title": f"判断事例: {keywords([d['判断内容']], 2) and '・'.join(keywords([d['判断内容']], 2)) or content[:20]}",
            "summary": f"「{content}」判断理由:「{polish(reason, 100)}」— 類似の判断（{d['関連カテゴリ']}）の際の基準として再利用する",
            "type": "判断理由",
            "category": d["関連カテゴリ"],
            "brand": d["関連ブランド"],
            "reason": f"Decision Logで判断と理由がセットで記録された事例（重要度{d['重要度']}）",
            "expected_effect": "過去の判断根拠（実績数値を含む）を次回の類似判断で参照できる",
            "risk": "単一事例。市況・時期が変われば前提が崩れる可能性",
            "related_patterns": [],
            "related_insights": [],
            "related_decisions": [f"decision@{d['Conversation ID']}"],
            "source_ids": [d["Conversation ID"]],
            "confidence": "medium" if d["重要度"] == "高" else "low",
        })

    # ---- 採番・共通フィールド・保存 ----
    order = {"high": 0, "medium": 1, "low": 2}
    lessons.sort(key=lambda l: (order[l["confidence"]], -len(l["source_ids"])))
    for i, l in enumerate(lessons, 1):
        l_final = {
            "lesson_id": f"LSN-{i:03d}",
            **l,
            "status": "draft",
            "needs_ceo_review": True,
            "created_at": TODAY,
            "updated_at": TODAY,
        }
        lessons[i - 1] = l_final

    out = {
        "meta": {
            "generator": f"Lesson Generator v{VERSION} [{STATE}]",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "inputs": {"patterns": len(patterns), "insights_candidates": len(cands),
                       "decisions_with_reason": sum(1 for l in lessons if l["type"] == "判断理由" and l["related_decisions"])},
            "note": "全Lessonはdraft。CEO Review前にKnowledge / EVOLVING_PRINCIPLES / CORE_PRINCIPLESへ反映しないこと（KNOWLEDGE_PROMOTION_RULES.md準拠）。",
            "total_lessons": len(lessons),
        },
        "lessons": lessons,
    }
    OUTPUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- 統計 ----
    print(f"Lesson Generator v{VERSION} [{STATE}]")
    print(f"Lesson総数: {len(lessons)}")
    for label in ("type", "category", "brand", "confidence"):
        print(f"\n[{label}別]")
        for k, v in Counter(l[label] for l in lessons).most_common():
            print(f"  {k}: {v}")
    print("\n[全Lesson一覧]")
    for l in lessons:
        print(f"  {l['lesson_id']} [{l['confidence']}] ({l['type']}/{l['category']}) {l['title']}")
        print(f"      {l['summary'][:90]}")


if __name__ == "__main__":
    main()
