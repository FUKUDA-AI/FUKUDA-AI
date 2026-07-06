#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pattern Analyzer v1.0 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト

Insight Log / Decision Log から「意味的に近い内容」をグルーピングし、
異なる会話で3回以上出現した思想・判断・学びを Pattern として抽出する。

Architecture上の位置づけ（学習サイクル・2026-07-06 CEO承認）:
    Conversation → Insight / Decision → Pattern → Lesson
    → EVOLVING_PRINCIPLES → CEO Review → CORE_PRINCIPLES

Layer: ③Knowledge Layerへの供給ライン（Pattern層）
参照: 01_Knowledge/08_Decision_Log/insight_log.json, decision_log.json（読み取りのみ）
更新: 01_Knowledge/08_Decision_Log/pattern_log.json（新規出力のみ）

重要ルール:
・全Patternは status: draft / needs_ceo_review: true
・CEOレビュー前に CORE/EVOLVING/Knowledge Released へ反映しない
・単なる件数集計ではなく、文字n-gram TF-IDF + コサイン類似度による意味的グルーピング
・定型文（ほぼ同一文面の反復）は confidence を下げて区別する

使い方:
    python3 pattern_analyzer.py
"""

import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

VERSION = "1.0"
STATE = "Experimental"

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "01_Knowledge" / "08_Decision_Log"
INSIGHT_PATH = LOG_DIR / "insight_log.json"
DECISION_PATH = LOG_DIR / "decision_log.json"
OUTPUT_PATH = LOG_DIR / "pattern_log.json"

# ---- パラメータ（調整可能） ----
SIM_THRESHOLD = 0.35       # クラスタ所属のコサイン類似度しきい値（0.25〜0.42で感度検証済み・2026-07-06）
MIN_CONVERSATIONS = 3      # Pattern認定: 異なる会話での最少出現数
VERBATIM_THRESHOLD = 0.90  # これ以上の平均類似度は「定型文」とみなす
NGRAM_SIZES = (2, 3)       # 文字n-gram


def normalize(text: str) -> str:
    """HTML・URL・記号ゆらぎを除去して比較用テキストを作る。"""
    text = unicodedata.normalize("NFKC", str(text))
    text = re.sub(r"<[^>]+>", " ", text)          # HTMLタグ
    text = re.sub(r"https?://\S+", " ", text)     # URL
    text = re.sub(r"[\s、。・…‥「」『』（）()\"'“””“]+", "", text)
    return text.strip()


def ngrams(text: str) -> Counter:
    c = Counter()
    for n in NGRAM_SIZES:
        for i in range(len(text) - n + 1):
            c[text[i:i + n]] += 1
    return c


def cosine(a: Counter, b: Counter, idf: dict) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    num = sum(a[g] * b[g] * idf.get(g, 1.0) ** 2 for g in common)
    na = math.sqrt(sum((v * idf.get(g, 1.0)) ** 2 for g, v in a.items()))
    nb = math.sqrt(sum((v * idf.get(g, 1.0)) ** 2 for g, v in b.items()))
    return num / (na * nb) if na and nb else 0.0


def load_items():
    items = []
    insights = json.load(open(INSIGHT_PATH, encoding="utf-8"))["insights"]
    for x in insights:
        items.append({
            "text": x.get("内容", ""),
            "type": x.get("タイプ", "不明"),
            "brand": x.get("関連ブランド", "全社"),
            "category": x.get("関連カテゴリ", "その他"),
            "importance": x.get("重要度", "低"),
            "dt": x.get("日時", ""),
            "cid": x.get("Conversation ID", ""),
            "source": "insight",
        })
    decisions = json.load(open(DECISION_PATH, encoding="utf-8"))["decisions"]
    for x in decisions:
        items.append({
            "text": x.get("判断内容", ""),
            "type": "経営判断",
            "brand": x.get("関連ブランド", "全社"),
            "category": x.get("関連カテゴリ", "その他"),
            "importance": x.get("重要度", "低"),
            "dt": x.get("日時", ""),
            "cid": x.get("Conversation ID", ""),
            "source": "decision",
        })
    for it in items:
        it["norm"] = normalize(it["text"])
    return [it for it in items if len(it["norm"]) >= 8]


def build_idf(vecs):
    df = Counter()
    for v in vecs:
        for g in set(v):
            df[g] += 1
    n = len(vecs)
    return {g: math.log((n + 1) / (d + 1)) + 1.0 for g, d in df.items()}


def cluster(items):
    """タイプ内で greedy クラスタリング（代表ベクトルとの類似度で所属判定）。"""
    by_type = defaultdict(list)
    for it in items:
        by_type[it["type"]].append(it)

    clusters = []
    for typ, group in by_type.items():
        vecs = [ngrams(it["norm"]) for it in group]
        idf = build_idf(vecs)
        assigned = []  # list of dict(members=[idx], vec=Counter)
        order = sorted(range(len(group)), key=lambda i: -len(group[i]["norm"]))
        for i in order:
            best, best_sim = None, 0.0
            for cl in assigned:
                sim = cosine(vecs[i], cl["vec"], idf)
                if sim > best_sim:
                    best, best_sim = cl, sim
            if best is not None and best_sim >= SIM_THRESHOLD:
                best["members"].append(i)
                # 代表ベクトルを逐次更新（和）
                best["vec"] = best["vec"] + vecs[i]
            else:
                assigned.append({"members": [i], "vec": Counter(vecs[i])})
        for cl in assigned:
            members = [group[i] for i in cl["members"]]
            clusters.append({"type": typ, "members": members,
                             "vecs": [vecs[i] for i in cl["members"]], "idf": idf})
    return clusters


def avg_pairwise_sim(cl):
    v, idf = cl["vecs"], cl["idf"]
    if len(v) < 2:
        return 0.0
    sims, cnt = 0.0, 0
    for i in range(len(v)):
        for j in range(i + 1, len(v)):
            sims += cosine(v[i], v[j], idf)
            cnt += 1
    return sims / cnt if cnt else 0.0


STOPWORDS = set("こと それ これ ため よう もの ください います おります いたします 思って 場合 よろしく お願い".split())


def keywords(texts, k=3):
    words = Counter()
    for t in texts:
        for w in re.findall(r"[ァ-ヴー]{3,}|[一-龠々]{2,}|[A-Za-z][A-Za-z .]{2,}", t):
            w = w.strip()
            if w not in STOPWORDS:
                words[w] += 1
    return [w for w, _ in words.most_common(k)]


def month_span(dts):
    ds = sorted(d for d in dts if d)
    if len(ds) < 2:
        return 0
    f = datetime.strptime(ds[0][:10], "%Y-%m-%d")
    l = datetime.strptime(ds[-1][:10], "%Y-%m-%d")
    return (l - f).days


def build_patterns(clusters):
    patterns = []
    for cl in clusters:
        members = cl["members"]
        cids = {m["cid"] for m in members if m["cid"]}
        if len(cids) < MIN_CONVERSATIONS:
            continue

        dts = [m["dt"] for m in members if m["dt"]]
        span_days = month_span(dts)
        verbatim = avg_pairwise_sim(cl) >= VERBATIM_THRESHOLD

        # confidence: 出現会話数 × 期間 × 定型文減点
        n = len(cids)
        if verbatim:
            confidence = "low"   # 定型文由来の可能性。CEOレビューで判断
        elif n >= 6 and span_days >= 180:
            confidence = "high"
        elif n >= 4:
            confidence = "medium"
        else:
            confidence = "low"

        texts = [m["text"] for m in members]
        # 代表例: 長さの中央値に近いもの + 最初 + 最後（重複除去、最大3件）
        by_len = sorted(texts, key=len)
        reps, seen = [], set()
        for t in [by_len[len(by_len) // 2], texts[0], texts[-1]]:
            key = normalize(t)[:40]
            if key not in seen:
                seen.add(key)
                reps.append(t.strip()[:200])
        kw = keywords(texts)
        brand = Counter(m["brand"] for m in members).most_common(1)[0][0]
        category = Counter(m["category"] for m in members).most_common(1)[0][0]

        patterns.append({
            "pattern_id": None,  # 後で採番
            "pattern_name": f"{cl['type']}: {'・'.join(kw) if kw else normalize(texts[0])[:20]}",
            "type": cl["type"],
            "category": category,
            "brand": brand,
            "summary": min(texts, key=lambda t: abs(len(t) - 80)).strip()[:120],
            "evidence_count": len(members),
            "conversation_count": n,
            "first_seen": min(dts) if dts else None,
            "last_seen": max(dts) if dts else None,
            "source_ids": sorted(cids),
            "representative_examples": reps,
            "confidence": confidence,
            "verbatim_suspected": verbatim,
            "status": "draft",
            "needs_ceo_review": True,
        })

    patterns.sort(key=lambda p: (-p["conversation_count"], -p["evidence_count"]))
    for i, p in enumerate(patterns, 1):
        p["pattern_id"] = f"PTN-{i:03d}"
    return patterns


def main():
    items = load_items()
    clusters = cluster(items)
    patterns = build_patterns(clusters)

    out = {
        "meta": {
            "generator": f"Pattern Analyzer v{VERSION} [{STATE}]",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input": {"insights": INSIGHT_PATH.name, "decisions": DECISION_PATH.name,
                      "items_analyzed": len(items)},
            "params": {"sim_threshold": SIM_THRESHOLD,
                       "min_conversations": MIN_CONVERSATIONS,
                       "verbatim_threshold": VERBATIM_THRESHOLD},
            "note": "全Patternはdraft。CEOレビュー前にCORE_PRINCIPLES / EVOLVING_PRINCIPLES / Knowledge Releasedへ反映しないこと。",
            "total_patterns": len(patterns),
        },
        "patterns": patterns,
    }
    OUTPUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- 統計レポート ----
    print(f"Pattern Analyzer v{VERSION} [{STATE}]")
    print(f"分析対象: {len(items)}件 (insight+decision) / クラスタ: {len(clusters)}")
    print(f"Pattern総数(3会話以上): {len(patterns)}")
    for label, key in [("type別", "type"), ("category別", "category"),
                       ("brand別", "brand"), ("confidence別", "confidence")]:
        c = Counter(p[key] for p in patterns)
        print(f"\n[{label}]")
        for k, v in c.most_common():
            print(f"  {k}: {v}")
    print("\n[TOP10 (会話数順)]")
    for p in patterns[:10]:
        vb = " ※定型文疑い" if p["verbatim_suspected"] else ""
        print(f"  {p['pattern_id']} [{p['confidence']}] {p['pattern_name']} "
              f"(会話{p['conversation_count']}/証拠{p['evidence_count']}, "
              f"{(p['first_seen'] or '')[:7]}〜{(p['last_seen'] or '')[:7]}){vb}")
        print(f"      {p['summary'][:80]}")


if __name__ == "__main__":
    main()
