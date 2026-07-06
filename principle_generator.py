#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Principle Generator v1.0 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト

CEO承認済みのLessonを「どんな場面でも使える判断原則（Principle）」へ抽象化し、
principle_log.json に保存する。

Architecture v1.3 上の位置づけ:
    Lesson → 【Principle（本機能）】 → CEO Review → Evolving Principles → Core Principles

Layer: ②Principles Layerへの供給ライン（Principle層）
参照: 01_Knowledge/08_Decision_Log/lesson_log.json（読み取りのみ。status: released中心）
更新: 01_Knowledge/08_Decision_Log/principle_log.json（新規出力のみ）

重要ルール（KNOWLEDGE_PROMOTION_RULES.md準拠）:
・全Principleは status: draft / needs_ceo_review: true
・AIはCORE_PRINCIPLESへ勝手に昇格させない
・EVOLVING_PRINCIPLESへの登録もCEO Review後の反映Sprintでのみ行う

抽象化方式（v1.0）:
・CEOレビュー済みLessonに対する「キュレーション済み抽象化ルール」（本ファイル内 CURATED_RULES）
・ルール未定義の承認済みLessonは汎用テンプレートでdraft化（confidence: low）
・rejectedのLessonからはPrincipleを生成しない
・in_review（hold）のLessonはCEOコメントの再整理方針がある場合のみ、それに沿って生成

Generator改善ルール（CEOレビュー 2026-07-06 追加。次回生成時に必ず適用）:
1. Principleは「特定商品の知識」ではなく、会社全体で再利用できる普遍的な判断原則まで抽象化する
2. 特定ブランドだけで成立するものは、すぐにPrincipleへせず反復実績（複数ブランド・複数場面）を確認してから再提案する
3. 「事実」だけでは原則にならない（例: 作業スペースに費用がかかる → NG。売上だけでなく利益・ブランド価値・運営負荷・将来性の総合判断 → OK）

再提案TODO（次回実行時のCURATED_RULES候補）:
・PRN-010改め:「経営判断は売上だけでなく、利益・ブランド価値・運営負荷・将来性を総合的に判断する」（CEO再整理指示・要根拠Lessonの拡充）
・PRN-009: SUNNY NOMADO / so u / MIRAI UP / 今後のブランドで「職人の目と実物で判断」が反復されたら
  「最終品質は数値だけでなく、職人の経験・感性・実物確認を含めて判断する」として再提案（CEO成長方針）

使い方:
    python3 principle_generator.py
"""

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

VERSION = "1.0"
STATE = "Experimental"

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "01_Knowledge" / "08_Decision_Log"
LESSON_PATH = LOG_DIR / "lesson_log.json"
OUTPUT_PATH = LOG_DIR / "principle_log.json"
TODAY = datetime.now().strftime("%Y-%m-%d")

# ---------------------------------------------------------------
# キュレーション済み抽象化ルール（CEOレビュー2026-07-06の結果を反映）
# 1ルール = 1Principle。source_lessons のLessonが根拠。
# ---------------------------------------------------------------
CURATED_RULES = [
    {
        "title": "ブランドは売るものではなく、人の歩みを豊かにするために存在する",
        "summary": "すべてのブランド・商品・発信は「歩みゆたかに」を最上位思想とし、作り手の情熱とストーリーを大切に形にする。売ることではなく、人の歩みを豊かにすることを目的とする（CEO: 会社・ブランド・AIすべての最上位思想）。",
        "source_lessons": ["LSN-001"], "source_patterns": ["PTN-001"],
        "category": "ブランド", "brand": "全社", "confidence": "high",
    },
    {
        "title": "お客様の想いは、必ず作り手まで届ける",
        "summary": "お客様から預かった想い（手紙・言葉・背景）は、販売側で止めず必ず職人・作り手まで共有する。想いが届いた上でのものづくりが、最速・最良の納品につながる（so uの標準対応）。",
        "source_lessons": ["LSN-002"], "source_patterns": ["PTN-002"],
        "category": "so u", "brand": "全社", "confidence": "high",
    },
    {
        "title": "一人のお客様のために、通常を超える対応を惜しまない",
        "summary": "目の前の一人に最上を尽くす（憲法第3条）。必要であれば通常は行わない特別な製作体制を整える。数ではなく一人に向かうことが、ブランドの信頼をつくる。",
        "source_lessons": ["LSN-005"], "source_patterns": ["PTN-004"],
        "category": "so u", "brand": "全社", "confidence": "medium",
    },
    {
        "title": "安くするのではなく、工夫によってお客様へ還元する",
        "summary": "値引きで選ばれることを良しとしない（憲法第5条）。DX・改善・工夫でコストを下げ、その分をお客様へ還元する。お客様のためを考え抜いた結果として会社が残る（CEO: 最終的に安くするのではなく、工夫でお客さんに還元）。",
        "source_lessons": ["LSN-016", "LSN-004"], "source_patterns": ["PTN-003"],
        "category": "経営", "brand": "全社", "confidence": "medium",
        "note": "LSN-004/PTN-003はhold中。CEOコメント「DXによってお客様へ還元する思想として再整理」に沿って生成",
    },
    {
        "title": "判断は過去実績の数値を基準に持ちつつ、今年の条件・環境・在庫・市場変化を含めて行う",
        "summary": "実績数値（例: 駅系催事の平均売上30万）は判断の土台として必ず参照する。ただし前年実績だけで判断せず、今年の条件・環境・在庫・市場変化を重ねて最終判断する。",
        "source_lessons": ["LSN-003"], "source_patterns": [],
        "category": "催事", "brand": "全社", "confidence": "medium",
    },
    {
        "title": "失敗は謝罪で終わらせず、プロセスの見直しへ昇華させる",
        "summary": "事故・失敗が起きたら、個別の謝罪・対処で終わらせず、必ず事前準備プロセス・チェックリストの見直しへつなげる。仕組みでの再発防止だけが「継続」を守る。",
        "source_lessons": ["LSN-023"], "source_patterns": [],
        "category": "催事", "brand": "全社", "confidence": "medium",
    },
    {
        "title": "品質は時間と反復で確保し、確保できるまで世に出さない・価格を約束しない",
        "summary": "試作と修正の反復に時間を惜しまない。自信を持てる品質に達してから世に出す（憲法第8条の四問）。品質が確定する前に価格を約束しない。",
        "source_lessons": ["LSN-018", "LSN-014"], "source_patterns": [],
        "category": "商品企画", "brand": "全社", "confidence": "medium",
    },
    {
        "title": "商品は、使い手の身体と課題の観察から設計する",
        "summary": "商品開発は「何が売れるか」ではなく「使い手の身体・暮らしのどんな課題を解決するか」から始める（例: 足圧を正常な位置に戻すための高硬度インソール設計）。",
        "source_lessons": ["LSN-009"], "source_patterns": [],
        "category": "商品企画", "brand": "全社", "confidence": "low",
    },
    {
        "title": "仕上がりの良し悪しは、職人の目と実物の雰囲気で決める",
        "summary": "仕様・データだけで決めず、職人の美的判断と実物の雰囲気を基準にする（例: 彫刻は点彫りのほうが良い雰囲気）。craftsmanshipを主語にする（憲法第6条）。",
        "source_lessons": ["LSN-007"], "source_patterns": [],
        "category": "so u", "brand": "全社", "confidence": "low",
    },
    {
        "title": "出店・企画の判断には、売上見込みだけでなく付帯コストを含める",
        "summary": "催事・出店・企画の採算判断には、売上見込みに加えてスペース費・作業費などの付帯コストを必ず織り込む。",
        "source_lessons": ["LSN-011"], "source_patterns": [],
        "category": "催事", "brand": "全社", "confidence": "low",
    },
]


def main():
    data = json.load(open(LESSON_PATH, encoding="utf-8"))
    lessons = {l["lesson_id"]: l for l in data["lessons"]}

    # 検証: ルールが参照するLessonの存在と状態
    principles = []
    used = set()
    for rule in CURATED_RULES:
        for lid in rule["source_lessons"]:
            l = lessons.get(lid)
            assert l, f"{lid} が見つからない"
            assert l["status"] != "rejected", f"{lid} はrejected（Principle生成不可）"
            used.add(lid)
        principles.append(rule)

    # フォールバック: released済みでルール未定義のLesson → 汎用抽象化（low）
    for lid, l in lessons.items():
        if l["status"] == "released" and lid not in used:
            principles.append({
                "title": f"（要抽象化）{l['title']}",
                "summary": f"{l['summary']}（キュレーションルール未定義のためLesson文のまま。CEOレビューで抽象化方針を指示してください）",
                "source_lessons": [lid], "source_patterns": l.get("related_patterns", []),
                "category": l["category"], "brand": l["brand"], "confidence": "low",
            })

    out_list = []
    for i, p in enumerate(principles, 1):
        out_list.append({
            "principle_id": f"PRN-{i:03d}",
            "title": p["title"],
            "summary": p["summary"],
            "source_lessons": p["source_lessons"],
            "source_patterns": p["source_patterns"],
            "category": p["category"],
            "brand": p["brand"],
            "confidence": p["confidence"],
            **({"note": p["note"]} if p.get("note") else {}),
            "status": "draft",
            "needs_ceo_review": True,
            "created_at": TODAY,
            "updated_at": TODAY,
        })

    out = {
        "meta": {
            "generator": f"Principle Generator v{VERSION} [{STATE}]",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input": {"lessons": LESSON_PATH.name,
                      "released_lessons": sum(1 for l in lessons.values() if l["status"] == "released")},
            "note": "全Principleはdraft。CEO Review後にEVOLVING_PRINCIPLESへ登録する。AIはCORE_PRINCIPLESへ昇格させない。",
            "total_principles": len(out_list),
        },
        "principles": out_list,
    }
    OUTPUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Principle Generator v{VERSION} [{STATE}]")
    print(f"Principle総数: {len(out_list)}")
    for label in ("category", "brand", "confidence"):
        print(f"\n[{label}別]")
        for k, v in Counter(p[label] for p in out_list).most_common():
            print(f"  {k}: {v}")
    print("\n[一覧]")
    for p in out_list:
        print(f"  {p['principle_id']} [{p['confidence']}] ({p['category']}) {p['title']}")


if __name__ == "__main__":
    main()
