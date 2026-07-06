#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Knowledge Builder v1.0 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト

CEO承認済み（status: released）のLessonを、Knowledge Information Architecture v1.0
（01_Knowledge/README.md）に従って Knowledge Draft へ転記し、knowledge_index.json を生成する。

Architecture v1.3 上の位置づけ: ③Knowledge Layerへの供給（Knowledge Draft生成）
参照: 01_Knowledge/08_Decision_Log/lesson_log.json / principle_log.json（読み取りのみ）
更新: 01_Knowledge/_drafts/（KN Draft）/ 04_SOP/_drafts/（SOP Draft）/ 01_Knowledge/knowledge_index.json

重要ルール（KNOWLEDGE_PROMOTION_RULES.md準拠）:
・対象はstatus: releasedのLessonのみ（rejected / hold / in_review は対象外）
・生成物は全て status: draft / needs_ceo_review: true（正式Knowledgeではない）
・AIはReleased Knowledge（各カテゴリフォルダ直下）へ直接書き込まない
・Evidenceのない Knowledge は作成しない
・索引はフロントマターのスキャンから自動再生成（手動編集禁止）

使い方:
    python3 knowledge_builder.py
"""

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

VERSION = "1.1"
STATE = "Experimental"
# v1.1 (2026-07-06): 索引走査に04_SOP（released SOP）を追加。released済みLessonのDraft再生成を防止

BASE_DIR = Path(__file__).resolve().parent
K_DIR = BASE_DIR / "01_Knowledge"
LESSON_PATH = K_DIR / "08_Decision_Log" / "lesson_log.json"
PRINCIPLE_PATH = K_DIR / "08_Decision_Log" / "principle_log.json"
DRAFT_DIR = K_DIR / "_drafts"
SOP_DRAFT_DIR = BASE_DIR / "04_SOP" / "_drafts"
INDEX_PATH = K_DIR / "knowledge_index.json"
TODAY = datetime.now().strftime("%Y-%m-%d")

# 索引スキャン対象（カテゴリフォルダ + drafts。ログ・アーカイブは対象外）
SCAN_DIRS = [
    "01_Brands", "02_Products", "03_Customers", "04_Marketing", "05_Events",
    "06_Finance", "07_Operations", "10_Sales", "11_Legal", "12_AI", "_drafts",
]

# ---------------------------------------------------------------
# Lesson → Knowledge 変換マップ（v1.0はキュレーション方式）
# カテゴリコード: BRD/PRD/EVT/SLS/MKT/MFG/CS/FIN/LGL/AI/SOP
# ---------------------------------------------------------------
LESSON_MAP = {
    "LSN-001": dict(cat="BRD", brand="全社",
        title="ブランド発信の核 — 歩みゆたかに×作り手の情熱・ストーリー",
        body="全ブランドの紹介文・発信は「歩みゆたかに」の想いと、作り手の情熱・歴史・ストーリーを大切にした丁寧なものづくりを軸に語る。2024-08〜2026-04の6会話で一貫して反復された、実際に使われてきた表現・思想である。"),
    "LSN-002": dict(cat="CS", brand="so u",
        title="so u標準対応 — お客様の手紙を職人と共有し最速でお手元へ",
        body="so uでは、お客様からの手紙・想いを必ず職人と共有し、ご希望の内容で一日でも早くお手元へ届くよう心を込めて製作する。CEO承認済みのso u標準対応（2023-06〜2026-07の5会話で反復）。",
        sop=dict(title="so u顧客対応プロセス — 手紙共有・最速納品", body="1. お客様から手紙・想い・背景を預かる\n2. 内容を職人へ必ず共有する（販売側で止めない）\n3. ご希望内容で製作し、一日でも早い納品を目指す\n4. 進捗をお客様へ丁寧に連絡する")),
    "LSN-003": dict(cat="EVT", brand="全社",
        title="駅系催事の売上実績 — 平均30万円",
        body="駅関係の催事場（東武浅草EKIMISE・ラスカ平塚改札横スペース等）の売上実績は平均30万円。催事出店判断の土台となる実績数値。判断時はEP-005（過去実績+今年の条件で判断）に従い、当年の条件・環境を重ねて評価する。"),
    "LSN-005": dict(cat="CS", brand="so u",
        title="so u特別製作体制 — 一人のお客様のための通常外対応",
        body="お客様のために、通常は行わない特別な製作体制を整えた実績がある（3会話で反復）。供養の心を込め、職人が一点一点製作する。EP-003（一人のために通常を超える対応）の実践記録。"),
    "LSN-007": dict(cat="PRD", brand="so u",
        title="so u彫刻仕様 — 点彫りの方が良い雰囲気",
        body="so uの彫刻は「点」で彫刻したほうが良い雰囲気に仕上がる（職人・実物確認による知見）。仕上がり判断の参考知見。関連: PRN-009（hold・継続観察中）。"),
    "LSN-009": dict(cat="PRD", brand="Dr.Nomado",
        title="Dr.Nomadoインソール設計思想 — 足圧の正常化",
        body="足圧を正常な位置に戻し姿勢を正すため、かかとと三点足の部分をしっかり固定する構造が必要と判断し、高硬度インソールを開発した。使い手の身体・課題の観察から設計するEP-008の実例。"),
    "LSN-014": dict(cat="SLS", brand="全社",
        title="ODM見積対応 — 試作を経ない価格提示はしない",
        body="技術的には試作の反復で要望に近づけられるが、品質とデザインの確保には複数回の試作が必要なため、試作前に具体的な価格を確定提示しない。見積・商談の標準対応（EP-007の実践）。",
        sop=dict(title="ODM見積対応プロセス — 試作と価格提示", body="1. 要望をヒアリングし、技術的な実現可能性を回答する\n2. 品質・デザイン確保に試作が必要な旨を説明する\n3. 試作前の確定価格提示はしない（概算の場合は前提条件を明記）\n4. 試作を経て品質確定後に正式見積を提示する")),
    "LSN-016": dict(cat="EVT", brand="全社",
        title="催事場実績 — JR浦和駅の反応が良好",
        body="最近の催事で反応が良かった場所としてJR浦和駅の実績がある。催事場選定の判断材料（KN-EVT-0001の平均売上30万とあわせて参照）。"),
    "LSN-018": dict(cat="PRD", brand="SUNNY NOMADO",
        title="マルチカラーシリーズ開発 — 修正反復による品質確保",
        body="新作マルチカラーシリーズはサンプルに何度もの修正を繰り返し、時間をかけた結果、品質・デザインともに自信を持って紹介できる水準に到達した。EP-007（品質は時間と反復で確保）の実例。"),
    "LSN-023": dict(cat="EVT", brand="全社",
        title="催事設営の教訓 — 事故を受けた事前準備プロセスの見直し",
        body="催事設営作業で事故が発生した教訓から、設営作業の事前準備プロセスを徹底的に見直す。個別の謝罪で終わらせず、チェックリスト化により再発を仕組みで防止する（EP-006の実例）。",
        sop=dict(title="催事設営チェックリスト（事前準備）", body="1. 設営前に会場条件（スペース・電源・搬入経路・安全上の制約）を確認する\n2. 設営作業の手順と役割分担を事前に文書化する\n3. 什器・備品の固定と安全確認を設営完了時に実施する\n4. 事故・ヒヤリハットが起きたら本チェックリストを必ず更新する（EP-006）\n（TODO: 実際の設営手順の詳細はCEO・現場確認のうえ拡充する）")),
}


def ep_links(principles, lesson_id):
    eps, prns = [], []
    for p in principles:
        if lesson_id in p.get("source_lessons", []):
            if p.get("registered_as"):
                eps.append(p["registered_as"])
            prns.append(p["principle_id"])
    return eps, prns


def frontmatter(d):
    lines = ["---"]
    for k, v in d.items():
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(v)}]")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    d = {}
    for line in m.group(1).split("\n"):
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        d[k.strip()] = v
    return d


def existing_lesson_refs():
    """カテゴリフォルダ・SOPに既にKnowledge化済みのLesson IDを収集（再生成防止）。"""
    refs = set()
    scan = [(K_DIR / d) for d in SCAN_DIRS if d != "_drafts"] + [BASE_DIR / "04_SOP"]
    for folder in scan:
        if not folder.exists():
            continue
        for f in folder.rglob("KN-*.md"):
            fm = parse_frontmatter(f.read_text(encoding="utf-8"))
            if fm:
                for lid in fm.get("related_lesson", []):
                    refs.add(lid)
    return refs


def build_drafts():
    lessons = {l["lesson_id"]: l for l in json.load(open(LESSON_PATH, encoding="utf-8"))["lessons"]}
    principles = json.load(open(PRINCIPLE_PATH, encoding="utf-8"))["principles"]
    DRAFT_DIR.mkdir(exist_ok=True)
    SOP_DRAFT_DIR.mkdir(parents=True, exist_ok=True)

    seq = Counter()
    kn_files, sop_files, skipped = [], [], []
    done = existing_lesson_refs()

    for lid, spec in LESSON_MAP.items():
        if lid in done:
            skipped.append(f"{lid}（Knowledge化済み）")
            continue
        l = lessons.get(lid)
        if not l or l["status"] != "released":
            skipped.append(f"{lid}（status: {l['status'] if l else '不明'}）")
            continue
        evidence = l.get("source_ids", [])
        if not evidence:
            skipped.append(f"{lid}（Evidenceなし）")
            continue

        eps, prns = ep_links(principles, lid)
        seq[spec["cat"]] += 1
        kid = f"KN-{spec['cat']}-{seq[spec['cat']]:04d}"
        fm = {
            "knowledge_id": kid, "title": spec["title"], "category": spec["cat"],
            "brand": spec["brand"], "summary": spec["body"][:60] + "…",
            "related_principle": eps, "related_lesson": [lid],
            "related_pattern": l.get("related_patterns", []),
            "evidence": evidence + [f"lesson_log.json/{lid}（CEO承認 2026-07-06）"],
            "last_reviewed": TODAY, "version": "v0.1",
            "status": "draft", "needs_ceo_review": "true",
        }
        path = DRAFT_DIR / f"{kid}_{re.sub(r'[/ 　]', '_', spec['title'])[:30]}.md"
        path.write_text(frontmatter(fm) + f"\n\n## Body\n\n{spec['body']}\n", encoding="utf-8")
        kn_files.append(path)

        if spec.get("sop"):
            seq["SOP"] += 1
            sid = f"KN-SOP-{seq['SOP']:04d}"
            sfm = dict(fm)
            sfm.update({"knowledge_id": sid, "title": spec["sop"]["title"],
                        "category": "SOP", "summary": spec["sop"]["title"]})
            spath = SOP_DRAFT_DIR / f"{sid}_{re.sub(r'[/ 　]', '_', spec['sop']['title'])[:30]}.md"
            spath.write_text(frontmatter(sfm) + f"\n\n## 手順\n\n{spec['sop']['body']}\n", encoding="utf-8")
            sop_files.append(spath)

    return kn_files, sop_files, skipped


def build_index():
    entries = []
    scan = [(K_DIR / d) for d in SCAN_DIRS] + [BASE_DIR / "04_SOP"]  # 04_SOPはrglobで_drafts含む
    for folder in scan:
        if not folder.exists():
            continue
        for f in sorted(folder.rglob("KN-*.md")):
            fm = parse_frontmatter(f.read_text(encoding="utf-8"))
            if not fm or "knowledge_id" not in fm:
                continue
            entries.append({
                "knowledge_id": fm["knowledge_id"], "title": fm.get("title", ""),
                "category": fm.get("category", ""), "brand": fm.get("brand", ""),
                "summary": fm.get("summary", ""), "status": fm.get("status", ""),
                "path": str(f.relative_to(BASE_DIR)),
                "related_principle": fm.get("related_principle", []),
                "last_reviewed": fm.get("last_reviewed", ""),
            })
    out = {
        "meta": {"generator": f"Knowledge Builder v{VERSION} [{STATE}]",
                 "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "note": "AgentはStatus: releasedのみ参照可。draftは通常判断に使わない。",
                 "total": len(entries)},
        "knowledge": entries,
    }
    INDEX_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return entries


def main():
    kn, sop, skipped = build_drafts()
    entries = build_index()
    print(f"Knowledge Builder v{VERSION} [{STATE}]")
    print(f"Knowledge Draft: {len(kn)}件 / SOP Draft: {len(sop)}件 / 索引: {len(entries)}件")
    if skipped:
        print("対象外:", "; ".join(skipped))
    for label in ("category", "brand"):
        print(f"\n[{label}別]")
        for k, v in Counter(e[label] for e in entries).most_common():
            print(f"  {k}: {v}")
    print("\n[一覧]")
    for e in entries:
        print(f"  {e['knowledge_id']} [{e['status']}] ({e['brand']}) {e['title']}")


if __name__ == "__main__":
    main()
