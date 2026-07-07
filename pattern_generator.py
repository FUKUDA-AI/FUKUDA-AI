#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pattern Generator v1.0 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト

Insight Draft（CEO判断由来 v2.0）と会話由来Insight（v1.3）を横断し、
反復している判断・失敗・成功・思想を検出して Pattern Draft を生成する。

学習フロー上の位置: Insight Draft → 【Pattern Draft（本機能）】 → Knowledge Generator → CEO Review

Pattern成立条件（CEO承認 2026-07-06・4条件すべて必須）:
1. CEO判断由来Insight（v2.0）を1件以上含む
2. 異なる日が含まれる（distinct_days >= 2）
3. 異なる文脈が含まれる（distinct_contexts >= 2）
4. EvidenceからDecisionまで遡れる（v2.0構成分のevidence連鎖完備）
+ 出現3回以上（同日同案件・同文脈は1回として数える）

重要ルール:
・推測禁止（内容は構成Insightの代表文。一般化の言い換えをしない）
・Patternはdraftのみ。CEO承認なしにKnowledge/Principle/EP/COREへ昇格しない
・CEO却下済み類似は再提案しない（抑制理由をログに記録。再整理指示つきのみ例外）
・EP/CORE類似は新Pattern化せず「EP運用記録候補」として別出力
・書き込み先は 09_Learning/patterns/ のみ。既存ファイル削除禁止
・冪等（構成Insightの指紋で重複排除）

使い方:
    python3 pattern_generator.py            # 生成 + pattern_draft_log.json 更新
    python3 pattern_generator.py --check    # 入力とグルーピングの確認のみ（書き込みなし）
"""

import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from pattern_analyzer import normalize, ngrams, cosine, build_idf

VERSION = "1.0"
STATE = "Experimental"

BASE_DIR = Path(__file__).resolve().parent
V2_INSIGHT_PATH = BASE_DIR / "09_Learning" / "insights" / "insight_draft_log.json"
V13_INSIGHT_PATH = BASE_DIR / "01_Knowledge" / "08_Decision_Log" / "insight_log.json"
V13_PATTERN_PATH = BASE_DIR / "01_Knowledge" / "08_Decision_Log" / "pattern_log.json"
LESSON_PATH = BASE_DIR / "01_Knowledge" / "08_Decision_Log" / "lesson_log.json"
PRINCIPLE_PATH = BASE_DIR / "01_Knowledge" / "08_Decision_Log" / "principle_log.json"
EVOLVING_PATH = BASE_DIR / "00_MASTER" / "EVOLVING_PRINCIPLES.md"
CORE_PATH = BASE_DIR / "00_MASTER" / "CORE_PRINCIPLES.md"
OUT_DIR = BASE_DIR / "09_Learning" / "patterns"
OUT_PATH = OUT_DIR / "pattern_draft_log.json"

CLUSTER_TH = 0.35       # Insight同士のグルーピング閾値（v1.3 Pattern Analyzerで検証済みの値）
EXISTING_TH = 0.60      # 既存Pattern/EP/CORE/却下との類似判定閾値
# CEOの「再整理して再提案」指示（却下照合の例外。出典: Brief#2判断3 2026-07-06）
REPROPOSAL_ALLOWED = ["経営判断は売上だけでなく、利益・ブランド価値・運営負荷・将来性を総合的に判断"]


# ---------------- Readers（読み取り専用） ----------------

def load_v2_insights():
    if not V2_INSIGHT_PATH.exists():
        return []
    data = json.load(open(V2_INSIGHT_PATH, encoding="utf-8"))["insights"]
    out = []
    for i in data:
        dates = sorted({str(d)[:10] for d in i["evidence"].get("decision_dates", []) if d})
        out.append({"id": i["insight_id"], "route": "v2", "text": i["内容"],
                    "dates": dates, "context": i["evidence"].get("関連カテゴリ") or "経営",
                    "decisions": i.get("source_decisions", []), "type_hint": i.get("type", "")})
    return out


def load_v13_insights():
    if not V13_INSIGHT_PATH.exists():
        return []
    data = json.load(open(V13_INSIGHT_PATH, encoding="utf-8"))["insights"]
    return [{"id": f"v13@{i.get('Conversation ID','')[:8]}", "route": "v13",
             "text": i.get("内容", ""), "dates": [str(i.get("日時", ""))[:10]],
             "context": i.get("関連カテゴリ") or i.get("タイプ") or "その他",
             "decisions": [], "type_hint": i.get("タイプ", "")}
            for i in data if i.get("内容")]


def load_reference_texts():
    """既存Pattern / EP / CORE / 却下済み（理由つき）のテキスト群。"""
    refs = {"pattern": [], "principle": [], "rejected": []}
    if V13_PATTERN_PATH.exists():
        for p in json.load(open(V13_PATTERN_PATH, encoding="utf-8"))["patterns"]:
            refs["pattern"].append((p["pattern_id"], p.get("summary", p.get("pattern_name", ""))))
    for path, key, idk, txtk in [(LESSON_PATH, "lessons", "lesson_id", "summary"),
                                 (PRINCIPLE_PATH, "principles", "principle_id", "title")]:
        if path.exists():
            for x in json.load(open(path, encoding="utf-8"))[key]:
                if x.get("status") == "rejected":
                    refs["rejected"].append((x[idk], x.get(txtk, "")))
    for path in (EVOLVING_PATH, CORE_PATH):
        if path.exists():
            text = path.read_text(encoding="utf-8")
            for m in re.findall(r"^### (EP-\d+): (.+)$", text, re.M):
                refs["principle"].append((m[0], m[1].strip()))
            for m in re.findall(r"^\d+\. (.+)$", text, re.M):
                refs["principle"].append(("CORE", m.strip()))
    return refs


# ---------------- グルーピングと判定 ----------------

def cluster_insights(insights):
    """意味的類似でグルーピング（greedy・v1.3実績ロジック再利用）。"""
    vecs = [ngrams(normalize(i["text"])) for i in insights]
    idf = build_idf(vecs)
    groups = []
    for idx in range(len(insights)):
        placed = False
        for g in groups:
            if cosine(vecs[idx], vecs[g[0]], idf) >= CLUSTER_TH:
                g.append(idx)
                placed = True
                break
        if not placed:
            groups.append([idx])
    return [[insights[i] for i in g] for g in groups], idf


def occurrences(group):
    """出現回数: 同日・同文脈は1回として数える。"""
    occ = set()
    for m in group:
        for d in (m["dates"] or ["日付不明"]):
            occ.add((d, m["context"]))
    return occ


def qualifies(group):
    """CEO承認4条件 + 3回以上を機械検証。(合否, 理由)を返す。"""
    v2 = [m for m in group if m["route"] == "v2"]
    if not v2:
        return False, "CEO判断由来Insightを含まない"
    days = {d for m in group for d in m["dates"] if d and d != "日付不明"}
    if len(days) < 2:
        return False, f"異なる日が含まれない（{len(days)}日）"
    contexts = {m["context"] for m in group}
    if len(contexts) < 2:
        return False, f"異なる文脈が含まれない（{len(contexts)}文脈）"
    if any(not m["decisions"] for m in v2):
        return False, "v2構成分のEvidence（Decision遡及）不完全"
    occ = occurrences(group)
    if len(occ) < 3:
        return False, f"出現{len(occ)}回（3回未満）"
    return True, "成立"


def classify_type(group):
    hints = " ".join(m["type_hint"] + m["text"] for m in group)
    if re.search(r"却下|失敗|やらない", hints):
        return "失敗"
    if re.search(r"歩みゆたか|思想|ブランドへの考え|職人との考え", hints):
        return "思想"
    if re.search(r"成功", hints):
        return "成功"
    return "判断"


def check_existing(group_text, refs, idf_texts):
    """既存Pattern/EP・CORE/却下との類似チェック。(種別, 参照ID) or None。"""
    all_refs = ([("pattern", i, t) for i, t in refs["pattern"]]
                + [("principle", i, t) for i, t in refs["principle"]]
                + [("rejected", i, t) for i, t in refs["rejected"]])
    texts = [t for _, _, t in all_refs] + [group_text]
    vecs = [ngrams(normalize(t)) for t in texts]
    idf = build_idf(vecs)
    for k, (kind, rid, _) in enumerate(all_refs):
        if cosine(vecs[k], vecs[-1], idf) >= EXISTING_TH:
            if kind == "rejected" and any(a in group_text for a in REPROPOSAL_ALLOWED):
                continue  # 再整理指示つきの例外
            return kind, rid
    return None


def group_fingerprint(group):
    return hashlib.md5("|".join(sorted(m["id"] for m in group)).encode()).hexdigest()[:12]


# ---------------- main ----------------

def main():
    check_only = "--check" in sys.argv
    v2 = load_v2_insights()
    v13 = load_v13_insights()
    refs = load_reference_texts()
    insights = v2 + v13

    print(f"Pattern Generator v{VERSION} [{STATE}]")
    print(f"入力: v2.0 Insight {len(v2)}件 / v1.3 Insight {len(v13)}件 / "
          f"既存Pattern {len(refs['pattern'])} / EP・CORE {len(refs['principle'])} / 却下記録 {len(refs['rejected'])}")

    groups, _ = cluster_insights(insights)
    multi = [g for g in groups if len(g) >= 2]
    print(f"グルーピング: {len(groups)}群（2件以上: {len(multi)}群）")

    if OUT_PATH.exists():
        out = json.load(open(OUT_PATH, encoding="utf-8"))
    else:
        out = {"meta": {"generator": f"Pattern Generator v{VERSION} [{STATE}]",
                        "note": "Pattern Draft。全件draft・CEO承認なしにKnowledge/Principle/EP/COREへ昇格しない。",
                        "processed_fingerprints": []},
               "patterns": [], "suppressed": [], "ep_usage_candidates": []}
    processed = set(out["meta"].get("processed_fingerprints", []))

    new_patterns, suppressed, ep_usage = [], [], []
    for g in groups:
        v2_members = [m for m in g if m["route"] == "v2"]
        if not v2_members:
            continue  # CEO判断由来なしは検討対象外（v1.3ルート管轄）
        fp = group_fingerprint(g)
        if fp in processed:
            continue
        ok, reason = qualifies(g)
        rep = max(g, key=lambda m: len(m["text"]))
        if not ok:
            if len(g) >= 2:  # 単独Insightの不成立は静かにスキップ（ログ肥大防止）
                suppressed.append({"reason": f"条件未達: {reason}",
                                   "members": [m["id"] for m in g], "代表": rep["text"][:80]})
            processed.add(fp)  # 冪等: 同一構成の再評価をしない（構成が変われば指紋も変わり再評価される）
            continue
        hit = check_existing(rep["text"], refs, None)
        if hit:
            kind, rid = hit
            entry = {"members": [m["id"] for m in g], "代表": rep["text"][:80], "類似先": rid}
            if kind == "principle":
                entry["reason"] = f"EP/CORE類似（{rid}）→ EP運用記録候補へ"
                ep_usage.append(entry)
            elif kind == "rejected":
                entry["reason"] = f"CEO却下済み類似（{rid}）→ 再提案しない"
                suppressed.append(entry)
            else:
                entry["reason"] = f"既存Pattern類似（{rid}）→ 新規作成せず"
                suppressed.append(entry)
            processed.add(fp)
            continue

        occ = occurrences(g)
        days = sorted({d for m in g for d in m["dates"] if d})
        new_patterns.append({
            "pattern_id": None,
            "type": classify_type(g),
            "内容": rep["text"][:200],
            "occurrence_count": len(occ),
            "distinct_days": days,
            "contexts": sorted({m["context"] for m in g}),
            "source_insights": [m["id"] for m in g],
            "evidence_chain": {
                "insights": [m["id"] for m in g],
                "decisions": sorted({d for m in v2_members for d in m["decisions"]}),
                "dates": days,
            },
            "status": "draft", "needs_ceo_review": True,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "generator_version": f"v{VERSION}",
        })
        processed.add(fp)

    if check_only:
        print(f"成立見込み: {len(new_patterns)}件 / 抑制: {len(suppressed)} / EP運用候補: {len(ep_usage)}")
        print("--check: 書き込みなしで終了")
        return

    for p in new_patterns:
        p["pattern_id"] = f"PTN2-{len(out['patterns'])+1:03d}"
        out["patterns"].append(p)
    out["suppressed"] += suppressed
    out["ep_usage_candidates"] += ep_usage
    out["meta"]["processed_fingerprints"] = sorted(processed)
    out["meta"]["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out["meta"]["total_patterns"] = len(out["patterns"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"新規Pattern Draft: {len(new_patterns)}件（累計{len(out['patterns'])}件） / "
          f"抑制: {len(suppressed)}件 / EP運用記録候補: {len(ep_usage)}件")
    for p in out["patterns"]:
        print(f"  {p['pattern_id']} [{p['type']}] 出現{p['occurrence_count']}回 "
              f"{len(p['distinct_days'])}日 {len(p['contexts'])}文脈: {p['内容'][:60]}")
    if not new_patterns:
        print("→ 0件は設計どおり（Pattern成立には異なる日の反復蓄積が必要。日次運用で自然に育つ）")


if __name__ == "__main__":
    main()
