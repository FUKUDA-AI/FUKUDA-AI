#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CEO Assistant v1.1 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト

CEO補佐AI（03_Agents/CEO_ASSISTANT.md）の機械部分。
Morning Briefの材料収集・ルール適用・骨組み生成・Decision Log Draft生成を担う。

ハイブリッド方式（CEO承認 2026-07-06）:
    機械（本スクリプト）: 情報収集 / released・verified Knowledge確認 / PENDING確認 /
                          候補抽出 / スコアリング / Brief骨組み生成 / Decision Log Draft生成
    FUKUDA AI（LLM）:     判断3件の推奨文・理由の言語化 / 最終検査 / CEOへの提示

Layer: ⑤Agent Layer（参照: ①〜④ / 書込: ホワイトリスト3か所のみ）

重要ルール（AI_CHARTER / CEO_ASSISTANT.md準拠）:
・AIは実行しない。判断材料のみ提示する
・Draft Knowledgeは通常判断に使わない（released / verified のみ参照）
・Decision Log本体（decision_log.json）には書かない。Draftはdecision_log_draft.jsonのみ
・書き込み先はWRITE_WHITELISTの3か所のみ（コードで強制）
・同日複数回実行は追記型（YYYY-MM-DD.md → _2.md → _3.md…）。上書き禁止
・既存ファイルを削除しない

使い方:
    python3 ceo_assistant.py            # Morning Brief骨組み生成 + Draft生成
    python3 ceo_assistant.py --check    # Reader検証のみ（書き込みなし）
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

VERSION = "1.3.1"
STATE = "Experimental"
# v1.2 (2026-07-07): FOS接続 — 07_Data/fos/index.json（FOS Importer出力）から
# Decision候補・期限切れ・優先タスクをBrief判断候補へ統合（Sprint 13）
# v1.3 (2026-07-07): FOS Operating Rule v1.0〜v1.2 CEO承認後の実装 —
# 並び順v1.2（期限切れ→S→待ち人→A→期限3日→priority高）/【main】見出し表示 /
# 未分類・未設定のCEO確認行 / review_after_days初期値提案（S30/A14/B7・確定はCEO）/
# Brief「⏰ 結果確認待ち」セクション（expected vs actual比較欄）/ Draft5項目保存
#
# 実装済みの設計メモ（旧TODO v1.3・Sprint 14.1）:
# - decision_needed=YES を最優先の判断候補として扱う（現行のsource_type判定を置換）
# - decision_type_main を判断見出しの【】に表示（subは必要時のみ併記）
# - 未入力のdecision_type は「未分類」とし、BriefでCEOへ分類確認を提示（AIは推測確定しない）
# - Decision Log Draft起票時に decision_type_main / sub を両方保存
# - 既存FOS-data.jsonに項目がない場合は null（未分類）として互換動作（壊さない）
#
# 実装済みの設計メモ（旧TODO v1.3追補・Sprint 14.2）:
# - Brief判断候補の並び順: 期限切れ → decision_importance=S（原則必載）→ waiting_person
#   → importance=A → 期限3日以内 → priority高（priority=急ぎ度 / importance=経営重要度は別軸）
# - Brief新セクション「⏰ 結果確認待ち」: review_after_days経過の判断を自動掲載し、
#   expected_result と actual_result（CEO記入欄）を並べて提示 → 成功/失敗/継続観察の判定 → Result Record化
# - Decision Log Draft起票時に decision_importance / expected_result / review_after_days も保存（計5項目）
# - importance未入力=「未設定」としてCEOへ確認。expected_resultは推測しない。
#   review_after_days未入力はimportance初期値（S30/A14/B7/Cなし）を提案表示のみ・確定はCEO
# - Knowledge化時は Related Decision Metadata（main/sub/importance/expected_result）を保持
#   （将来のEvidence Scorer・Verified昇格条件が重要度別・分類別の成功率を参照する前提）

BASE_DIR = Path(__file__).resolve().parent
BRIEF_DIR = BASE_DIR / "06_Reports" / "morning_brief"
DRAFT_LOG_PATH = BASE_DIR / "01_Knowledge" / "08_Decision_Log" / "decision_log_draft.json"
MEMORY_DIR = BASE_DIR / "10_AI_Memory"

# ---- 書き込み先ホワイトリスト（これ以外への書き込みはコードが拒否する） ----
WRITE_WHITELIST = [BRIEF_DIR, DRAFT_LOG_PATH, MEMORY_DIR]


def safe_write(path: Path, text: str):
    """ホワイトリスト外への書き込みを拒否し、既存ファイルの上書きを禁止する（Memoryのみ更新可）。"""
    path = path.resolve()
    allowed = any(str(path).startswith(str(w.resolve())) for w in WRITE_WHITELIST)
    if not allowed:
        raise PermissionError(f"書き込み禁止: {path} はホワイトリスト外")
    if path.exists() and BRIEF_DIR.resolve() in path.parents:
        raise PermissionError(f"上書き禁止: {path} は既に存在（追記型命名を使うこと）")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ================================================================
# Reader群（すべて読み取り専用）
# ================================================================

def read_released_knowledge():
    """1. Released Knowledge Reader — released/verifiedのみ返す。draftは返さない。"""
    idx = json.load(open(BASE_DIR / "01_Knowledge" / "knowledge_index.json", encoding="utf-8"))
    usable = [k for k in idx["knowledge"] if k["status"] in ("released", "verified")]
    excluded = len(idx["knowledge"]) - len(usable)
    return {"usable": usable, "excluded_count": excluded}


def read_principles():
    """2. CORE / EVOLVING Principles Reader"""
    core_text = (BASE_DIR / "00_MASTER" / "CORE_PRINCIPLES.md").read_text(encoding="utf-8")
    core = re.findall(r"^\d+\. (.+)$", core_text, re.M)
    ev_text = (BASE_DIR / "00_MASTER" / "EVOLVING_PRINCIPLES.md").read_text(encoding="utf-8")
    eps = re.findall(r"^\| (EP-\d+) \| (.+?) \|", ev_text, re.M)
    return {"core_count": len(core), "core": core,
            "eps": [{"id": e[0], "title": e[1].strip()} for e in eps]}


def read_memory():
    """3. AI Memory Reader — CURRENT_STATE / NEXTの要点"""
    out = {}
    for name in ("CURRENT_STATE", "NEXT"):
        p = MEMORY_DIR / f"{name}.md"
        text = p.read_text(encoding="utf-8") if p.exists() else ""
        out[name] = [l.strip("- ").strip() for l in text.split("\n")
                     if l.strip().startswith("- **") or l.strip().startswith("- ")][:15]
    return out


def read_result_due():
    """Result Reader（v1.3.1）— 07_Data/results/index.json（Result Recorder出力・読み取りのみ）。
    Brief「⏰ 結果確認待ち」の参照元。判定（成功/失敗/継続観察）はCEOのみ。"""
    p = BASE_DIR / "07_Data" / "results" / "index.json"
    if not p.exists():
        return []
    idx = json.load(open(p, encoding="utf-8"))
    return idx.get("check_due", [])


def read_fos():
    """FOS Reader（v1.2）— 07_Data/fos/index.json（Data Layer経由・FOS原本は読まない）。"""
    p = BASE_DIR / "07_Data" / "fos" / "index.json"
    if not p.exists():
        return None
    idx = json.load(open(p, encoding="utf-8"))
    return {
        "records": idx["records"],
        "decisions": [r for r in idx["records"] if r.get("decision_candidate")],
        "overdue": [r for r in idx["records"] if r.get("overdue")],
        "summary": idx.get("summary", {}),
        "generated_at": idx["meta"].get("generated_at"),
    }


IMPORTANCE_DEFAULT_REVIEW = {"S": 30, "A": 14, "B": 7}  # C=原則なし（FOS Rule §4-5）


def deadline_within(r, days=3):
    """due_dateが今日からdays日以内か（期限切れは別加点のため除く）。"""
    from datetime import date, timedelta
    d = str(r.get("due_date") or "")[:10]
    try:
        dd = date.fromisoformat(d)
    except ValueError:
        return False
    return date.today() <= dd <= date.today() + timedelta(days=days)


def fos_candidates(fos):
    """FOSのDecision候補をBrief判断候補形式へ変換（v1.3・FOS Rule v1.2 §6準拠）。
    並び順: 期限切れ → importance=S（原則必載）→ 人が待っている → A → 期限3日以内 → priority高"""
    cands = []
    for r in (fos["decisions"] if fos else []):
        imp = r.get("decision_importance")      # None=未設定（AIは推測しない）
        main = r.get("decision_type_main")      # None=未分類
        waiting = r["source_type"] == "staff_request" or bool(r.get("waiting_person"))
        score = (r.get("priority") or 50)       # priority=急ぎ度（最下位の判定条件）
        if r.get("overdue"):
            score += 100000                     # 1. 期限切れ
        if imp == "S":
            score += 50000                      # 2. S=原則必載
        if waiting:
            score += 20000                      # 3. 人が待っている
        if imp == "A":
            score += 10000                      # 4. A
        if deadline_within(r):
            score += 5000                       # 5. 期限3日以内
        cands.append({
            "no": r["record_id"],
            "item": f"【{main or '未分類'}】{r['title']}",
            "place": f"FOS（{r['source_type']}）",
            "priority": f"重要度{imp}" if imp else "重要度未設定",
            "score": score, "urgent": bool(r.get("overdue")),
            "fos": r,
        })
    return cands


def read_pending():
    """4. PENDING Reader — 未完了項目を優先度つきで抽出（完了・打ち消し線は除外）"""
    p = MEMORY_DIR / "PENDING.md"
    if not p.exists():
        return []
    items = []
    for line in p.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"\| (\S+) \| (.+?) \| (.+?) \| (.+?) \|$", line.strip())
        if not m:
            continue
        no, item, place, prio = (x.strip() for x in m.groups())
        if no in ("#",) or "---" in no:
            continue
        if "~~" in item or "✅" in item or prio == "完了":
            continue
        items.append({"no": no, "item": re.sub(r"\*\*", "", item),
                      "place": place, "priority": prio})
    return items


# ================================================================
# 候補抽出・スコアリング（Brief設計書§5の6ルール）
# ================================================================

PRIORITY_SCORE = {"最高": 100, "高": 70, "中": 40, "低": 15}


def score_candidates(pending):
    cands = []
    for it in pending:
        base = 15
        for key, val in PRIORITY_SCORE.items():
            if key in it["priority"]:
                base = val
                break
        urgent = bool(re.search(r"緊急|事故|支払不能|クレーム", it["item"]))
        deadline = bool(re.search(r"期限|今日|本日|明日|締切", it["item"]))
        waiting = bool(re.search(r"お客様|職人|取引先|待ち(?!キュー)", it["item"]))
        ceo_task = "CEO作業" in it["item"] or "【CEO", it["item"][:5]
        # v1.3: FOS候補とスケール統一（緊急=期限切れ相当 > 待ち人 > 期限）
        score = base + (100000 if urgent else 0) + (20000 if waiting else 0) + (5000 if deadline else 0)
        cands.append({**it, "score": score, "urgent": urgent})
    return sorted(cands, key=lambda c: -c["score"])


def select_top3(cands):
    """観察・低優先は選外。最大3件。"""
    active = [c for c in cands if "観察" not in c["priority"]]
    return active[:3], active[3:] + [c for c in cands if "観察" in c["priority"]]


# ================================================================
# 5. Morning Brief Generator（骨組み）
# ================================================================

def next_brief_path(today: str) -> Path:
    """追記型命名: YYYY-MM-DD.md → _2.md → _3.md…（上書き禁止）"""
    p = BRIEF_DIR / f"{today}.md"
    n = 1
    while p.exists():
        n += 1
        p = BRIEF_DIR / f"{today}_{n}.md"
    return p


def generate_brief(materials, selected, dropped, path: Path, brief_no: str):
    know = materials["knowledge"]
    lines = [
        f"# CEO Morning Brief — {materials['today']}（{brief_no}）",
        "",
        f"発行: CEO Assistant v{VERSION} [{STATE}]（機械骨組み {materials['now']}）+ FUKUDA AI（言語化）",
        f"参照: released/verified Knowledge {len(know['usable'])}件（draft {know['excluded_count']}件は除外）/ "
        f"CORE {materials['principles']['core_count']}条 / EP {len(materials['principles']['eps'])}件 / PENDING {materials['pending_count']}件",
        "",
        "---",
        "",
        "## 🔴 今日の判断（最大3件）",
        "",
    ]
    if not selected:
        lines.append("（本日、判断が必要な案件はありません）")
    for i, c in enumerate(selected, 1):
        urgent_mark = "🚨【緊急】" if c["urgent"] else ""
        lines += [
            f"### {i}. {urgent_mark}{c['item']}",
            f"- 出典: {c['no']}（{c['place']}）/ {c['priority']} / スコア: {c['score']}",
        ]
        fr = c.get("fos")
        if fr is not None:  # v1.3: Decision Metadata表示（FOS Rule v1.2）
            imp, main, sub = fr.get("decision_importance"), fr.get("decision_type_main"), fr.get("decision_type_sub")
            exp, rad = fr.get("expected_result"), fr.get("review_after_days")
            lines.append(f"- 分類: main={main or '未分類'} / sub={sub or '-'} / 重要度: {imp or '未設定'} / 期待結果: {exp or '未入力'}")
            if main is None or imp is None:
                lines.append("- ⚠ CEO確認（1タップ）: 未入力の分類/重要度を記入 → main=______ / importance=[ S / A / B / C ]")
            if rad is not None:
                lines.append(f"- 結果確認: 判断から{rad}日後（Brief「結果確認待ち」に自動掲載）")
            elif imp in IMPORTANCE_DEFAULT_REVIEW:
                lines.append(f"- 結果確認（AI提案・確定はCEO）: {IMPORTANCE_DEFAULT_REVIEW[imp]}日後（importance {imp}の初期値）[ 採用 / 変更: __日 ]")
        lines += [
            "- 推奨: <!-- LLM: 推奨案・理由・期待効果・リスク・実行手順・根拠EP/KNをここに記述 -->",
            "- CEO判断: [ 承認 / 却下 / 保留 ] ______",
            "",
        ]
    lines += ["## ⛔ 今日やらないこと", ""]
    if dropped:
        for c in dropped:
            lines.append(f"- {c['item']}（優先度: {c['priority']}・スコア{c['score']}で選外）")
    else:
        lines.append("- なし")
    due = materials.get("result_check_due") or []
    lines += ["", "## ⏰ 結果確認待ち（Result Layer入口・判定はCEOのみ）", ""]
    if due:
        for d in due:
            lines += [
                f"- **{d.get('判断')}**（判断日 {d.get('判断日')} / 確認予定 {d.get('確認予定日')} / 分類 {d.get('decision_type_main') or '未分類'} / 重要度 {d.get('decision_importance') or '未設定'}）",
                f"  - expected_result: {d.get('expected_result') or '未入力'}",
                "  - actual_result（CEO記入）: ______",
                "  - 判定: [ 成功 / 失敗 / 継続観察 ] ______",
            ]
    else:
        lines.append("- なし（review_after_days経過の判断はありません）")
    lines += [
        "",
        "## 📋 レビュー待ち",
        "",
        f"- PENDING未完了: {materials['pending_count']}件（本Briefの判断候補に反映済み）",
        "",
        "## ⏭ 次に決めること",
        "",
        "<!-- LLM: NEXT.md・文脈から近づいている判断を記述 -->",
        "",
        "## 📝 Decision Log Draft",
        "",
        f"- 本Briefの判断結果は decision_log_draft.json へDraft起票済み（CEO記入後に本体へ確定反映）",
        "",
        "---",
        f"*機械工程: 収集・候補抽出・スコアリング・骨組み生成（v{VERSION}）。言語化・検査: FUKUDA AI。実行系の提案はありません。*",
    ]
    safe_write(path, "\n".join(lines))
    return path


# ================================================================
# 6. Decision Log Draft Generator（本体には書かない）
# ================================================================

def generate_decision_drafts(selected, brief_file: str, today: str):
    if DRAFT_LOG_PATH.exists():
        data = json.load(open(DRAFT_LOG_PATH, encoding="utf-8"))
    else:
        data = {"meta": {"note": "Decision Log Draft置き場。CEO承認後にdecision_log.json本体へ確定反映する（AIは本体へ直接書かない）",
                         "generator": f"CEO Assistant v{VERSION} [{STATE}]"}, "drafts": []}
    for c in selected:
        fr = c.get("fos") or {}
        data["drafts"].append({
            "draft_id": f"DLD-{today}-{len(data['drafts'])+1:02d}",
            "判断内容": c["item"],
            "判断理由": "（CEO記入待ち）",
            "結果": "（CEO判断待ち: 承認/却下/保留）",
            "関連カテゴリ": "経営", "重要度": c["priority"],
            # v1.3: Decision Metadata（FOS Rule v1.2 §7。未入力はnull=未分類/未設定・AIは確定しない）
            "decision_type_main": fr.get("decision_type_main"),
            "decision_type_sub": fr.get("decision_type_sub"),
            "decision_importance": fr.get("decision_importance"),
            "expected_result": fr.get("expected_result"),
            "review_after_days": fr.get("review_after_days"),
            "日時": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "source": f"Morning Brief {brief_file}",
            "status": "draft", "needs_ceo_review": True,
        })
    data["meta"]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["meta"]["total_drafts"] = len(data["drafts"])
    # DRAFT_LOG_PATHはホワイトリスト対象（追記更新のため直接書く）
    DRAFT_LOG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(data["drafts"])


# ================================================================
# main
# ================================================================

def main():
    check_only = "--check" in sys.argv
    today = datetime.now().strftime("%Y-%m-%d")

    knowledge = read_released_knowledge()
    principles = read_principles()
    memory = read_memory()
    pending = read_pending()
    fos = read_fos()

    print(f"CEO Assistant v{VERSION} [{STATE}]")
    print(f"Knowledge: released/verified {len(knowledge['usable'])}件（draft等 {knowledge['excluded_count']}件を除外）")
    print(f"Principles: CORE {principles['core_count']}条 / EP {len(principles['eps'])}件")
    print(f"PENDING未完了: {len(pending)}件")
    if fos:
        print(f"FOS: TaskRecord {len(fos['records'])}件 / Decision候補 {len(fos['decisions'])}件 / "
              f"期限切れ {len(fos['overdue'])}件（取込: {fos['generated_at']}）")
    else:
        print("FOS: 未接続（07_Data/fos/index.jsonなし → fos_importer.py実行で接続）")

    print(f"結果確認待ち（Result Recorder）: {len(read_result_due())}件")
    cands = score_candidates(pending) + fos_candidates(fos)
    cands.sort(key=lambda c: -c["score"])
    selected, dropped = select_top3(cands)
    print(f"判断候補: {len(cands)}件 → 選定{len(selected)}件 / 選外{len(dropped)}件")
    for c in selected:
        print(f"  ★ [{c['score']}] {c['item'][:60]}")

    if check_only:
        print("--check: 書き込みなしで終了")
        return

    materials = {"today": today, "now": datetime.now().strftime("%H:%M"),
                 "knowledge": knowledge, "principles": principles,
                 "memory": memory, "pending_count": len(pending),
                 # 結果確認待ち = Result Recorder（07_Data/results/）+ FOS index集計の統合（v1.3.1）
                 "result_check_due": read_result_due() +
                     (fos or {}).get("summary", {}).get("decision_metadata", {}).get("result_check_due", [])}
    path = next_brief_path(today)
    generate_brief(materials, selected, dropped, path, brief_no=path.stem.replace(today, "第" + (path.stem.split("_")[-1] if "_" in path.stem else "1") + "号"))
    total = generate_decision_drafts(selected, path.name, today)
    print(f"Brief骨組み: {path}")
    print(f"Decision Log Draft: {DRAFT_LOG_PATH.name}（累計{total}件）")
    print("→ 次工程: FUKUDA AI（LLM）が <!-- LLM: --> 箇所を言語化し、憲法・EP整合を検査してからCEOへ提示")


if __name__ == "__main__":
    main()
