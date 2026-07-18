#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CEO Assistant v2.1 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト

CEO補佐AI（03_Agents/CEO_ASSISTANT.md）の機械部分。
Morning Briefの材料収集・ルール適用・骨組み生成・Decision Log Draft生成を担う。

ハイブリッド方式（CEO承認 2026-07-06）:
    機械（本スクリプト）: 情報収集 / released・verified Knowledge確認 / PENDING確認 /
                          候補抽出 / スコアリング / Brief骨組み生成 / Decision Log Draft生成
    FUKUDA AI（LLM）:     一言・判断の推奨文・②③④の言語化 / 最終検査（一言=①先頭一致・30行以内）/ CEOへの提示

Layer: ⑤Agent Layer（参照: ①〜④ / 書込: ホワイトリスト3か所のみ）

重要ルール（AI_CHARTER / CEO_ASSISTANT.md準拠）:
・AIは実行しない。判断材料のみ提示する（AI ActionsもCEO承認まで・実行はDraft/取込/生成）
・Draft Knowledgeは通常判断に使わない（released / verified のみ参照）
・Decision Log本体（decision_log.json）には書かない。Draftはdecision_log_draft.jsonのみ
・書き込み先はWRITE_WHITELISTの3か所のみ（コードで強制）
・同日複数回実行は追記型（YYYY-MM-DD.md → _2.md → _3.md…）。上書き禁止
・既存ファイルを削除しない・FOSは変更しない

使い方:
    python3 ceo_assistant.py            # Morning Brief骨組み生成 + Draft生成（「おはよう」で起動）
    python3 ceo_assistant.py --check    # Reader検証のみ（書き込みなし）
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

VERSION = "2.1.1"
STATE = "Experimental"
# v2.1.1 (2026-07-18・Brief v2.1 実装Sprint 4「要約精度改善」):
# ④会社の状態を company_attention() で強化 — 期限切れ/未入金・請求/スタッフ待ち・相談/催事搬入直前/
# 結果確認期限/未接続 を根拠つきで機械検出しlevel順に列挙（LLMが1〜3行に要約する材料）。推測しない=事実のみ。
# 未接続ソースの実数値化は各Connector接続時に順次（本Sprintは判定ルールの土台）。
# v2.1 (2026-07-18・Brief v2.1「Less is More」実装Sprint 2・CEO承認済み設計):
# Briefを5ブロックへ圧縮 — 💬AIから一言（①先頭と一致）/ ①今日の判断（原則1件・最大3件）/
# ②AIからの提案（FOS Review・6観点・最大3件厳選）/ ③AI Actions（ai_ready=yes・最大5件・承認制）/
# ④会社の状態（1〜3行要約・数字を並べない）。条件付き表示: 催事（あった日のみ）/ 結果確認（期限到来のみ）/
# 緊急（発生時のみ最上部）。Briefから削除: 今日やらないこと / AI開発案件 / 次に決めること / Event常設表
# （→Dashboard・ログ・条件付きへ移動。情報は消えない=隠す勇気）。30行以内ガード。
# 評価基準は「CEOが5分で今日の判断を終えられるか」。不変: 推測禁止・FOS書換禁止・実行はDraft/取込/生成まで。
# v1.6 (2026-07-11・CEO訂正): Event Statusの情報源=催事スケジュール（Google Sheets「18期催事管理」
# DS-EVT-0002・event_schedule_importer.py・毎朝取込）。表示は「出店決定」のみ（v2.1で条件付き表示へ移行）。
# v1.4 (2026-07-11・CEO指示): 判断候補の生成源をFOS（実業データ）のみに変更。AI開発タスクはAI開発レポートへ分離。
# v1.3 (2026-07-07): FOS Operating Rule v1.0〜v1.2実装（Decision Metadata・並び順・結果確認待ち・Draft5項目）。
# v1.2 (2026-07-07): FOS接続（07_Data/fos/index.json → 判断候補統合・Sprint 13）。

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
    if path.exists() and BRIEF_DIR.resolve() in path.parents and "_draft" not in path.parts:
        raise PermissionError(f"上書き禁止: {path} は既に存在（追記型命名を使うこと）")
    # _draft/（前夜下書き）は上書き可（毎晩/当朝に再生成する下書き置き場・確定版はmorning_brief直下）
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


def read_event_schedule():
    """Event Schedule Reader（v1.6）— 07_Data/event_schedule/index.json。未取込はNone（推測しない）。"""
    p = BASE_DIR / "07_Data" / "event_schedule" / "index.json"
    if not p.exists():
        return None
    return json.load(open(p, encoding="utf-8"))


def read_result_due():
    """Result Reader（v1.3.1）— 07_Data/results/index.json（読み取りのみ）。判定はCEOのみ。"""
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
    """FOSのDecision候補をBrief判断候補形式へ変換（FOS Rule v1.2 §6準拠）。
    並び順: 期限切れ → importance=S（原則必載）→ 人が待っている → A → 期限3日以内 → priority高"""
    cands = []
    for r in (fos["decisions"] if fos else []):
        if r.get("brief_candidate") is False:   # v2.1: improvements等（brief_candidate=False）は今日の判断に出さない（金曜レビュー/別枠）
            continue
        imp = r.get("decision_importance")      # None=未設定（AIは推測しない）
        main = r.get("decision_type_main")      # None=未分類
        waiting = (r["source_type"] == "staff_request" or bool(r.get("waiting_person"))
                   or bool(r.get("consultation")))
        score = (r.get("priority") or 50)
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
    """4. PENDING Reader — 未完了項目（Briefには出さない・v1.4。件数のみ利用）"""
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
# 候補抽出・選定（Brief v2.1 §①）
# ================================================================

def select_v21(cands):
    """v2.1: 判断は原則1件。S（重要度S）または期限切れが複数あるときのみ最大3件。
    candsはscore降順である前提。選外はBriefに出さない（索引・Draftログに残る=隠す勇気）。"""
    if not cands:
        return [], []
    forced = [c for c in cands if c.get("urgent") or "重要度S" in c.get("priority", "")]
    n = max(1, min(3, len(forced)))
    return cands[:n], cands[n:]


def fos_review(fos, max_items=3):
    """v2.1 ②AIからの提案: Brief生成前のFOSレビュー。機械で検出できる観点のみ返す（提案のみ・FOSは変更しない）。
    検出: 完了忘れ(期限切れ) / 重複(同一タイトルの未完了タスク) / 待ち(相談・スタッフ)。
    順番・今日やらなくてよい・AIでできる の定性観点はLLMが補う（Briefにプレースホルダ）。
    戻り値: (表示分リスト, 検出総数)"""
    from collections import Counter
    recs = fos["records"] if fos else []
    proposals = []
    for r in (fos["overdue"] if fos else []):
        proposals.append({"観点": "完了忘れ",
                          "text": f"「{r['title']}」が期限切れです。済んでいれば完了化を（アプリ操作）",
                          "根拠": f"due {r.get('due_date') or '-'}"})
    titles = [r["title"] for r in recs
              if r.get("source_type") == "task" and r.get("status") == "未完了" and r.get("title")]
    for title, cnt in Counter(titles).items():
        if cnt > 1:
            proposals.append({"観点": "重複",
                              "text": f"「{title}」が{cnt}件重複しています。1件に統合できます",
                              "根拠": f"未完了タスク×{cnt}"})
    for r in recs:
        if r.get("consultation"):
            proposals.append({"観点": "待ち",
                              "text": f"相談「{r['title']}」が待ち状態です。回答すれば前に進みます",
                              "根拠": "consultation（人を待たせない・憲法）"})
    return proposals[:max_items], len(proposals)


def company_attention(fos, es, result_due, today):
    """v2.1.1 Sprint4: ④会社の状態の『注意点』を機械検出（根拠つき・level順）。
    推測しない=データにある事実のみ。level: high(お金・期限) > mid(待ち・催事・結果) > low(未接続)。"""
    import re
    from datetime import date as _d, timedelta as _td
    recs = fos["records"] if fos else []
    items = []
    # 1. 期限切れ（high）
    n_over = len(fos["overdue"]) if fos else 0
    if n_over:
        items.append({"level": "high", "観点": "期限切れ", "text": f"期限切れ {n_over}件", "根拠": "FOS overdue"})
    # 2. 入金・請求（未完了タスクのキーワード・high）
    for r in recs:
        t = r.get("title") or ""
        if r.get("status") == "未完了" and re.search(r"未入金|未回収|請求|滞納|未払", t):
            items.append({"level": "high", "観点": "入金", "text": f"入金/請求の確認: {t}", "根拠": r.get("record_id")})
    # 3. 待ち（相談・スタッフ待ち・mid）
    for r in recs:
        if r.get("consultation"):
            items.append({"level": "mid", "観点": "待ち", "text": f"相談待ち: {r.get('title')}", "根拠": "consultation"})
        elif r.get("source_type") == "next_action" and r.get("status") == "スタッフ待ち":
            items.append({"level": "mid", "観点": "待ち", "text": f"スタッフ待ち: {r.get('title')}", "根拠": r.get("record_id")})
    # 4. 催事搬入が3日以内（mid）
    if es and today:
        try:
            t0 = _d.fromisoformat(today)
            soon = (t0 + _td(days=3)).isoformat()
            for r in es.get("records", []):
                sd = r.get("setup_date")
                if r.get("confirmed") and sd and today <= sd <= soon:
                    items.append({"level": "mid", "観点": "催事", "text": f"催事搬入まもなく: {r.get('name')}（{sd}）", "根拠": "event_schedule"})
        except ValueError:
            pass
    # 5. 結果確認の期限到来（mid）
    if result_due:
        items.append({"level": "mid", "観点": "結果確認", "text": f"結果確認の期限到来 {len(result_due)}件", "根拠": "results"})
    # 6. 未接続（low・情報）
    items.append({"level": "low", "観点": "未接続", "text": "売上/在庫/入金の自動把握は未接続（Shopify等6ソース）", "根拠": "dataset_registry"})
    order = {"high": 0, "mid": 1, "low": 2}
    items.sort(key=lambda x: order[x["level"]])
    return items


def company_hints(fos, es=None, result_due=None, today=None):
    """v2.1 ④会社の状態の機械ヒント（LLMが1〜3行に要約する材料。数字の羅列はしない）。
    v2.1.1: 注意点（attention）を根拠つきで同梱。"""
    return {"overdue": len(fos["overdue"]) if fos else 0,
            "connected": "Airレジ・催事スケジュール",
            "unconnected": "Shopify / MakeShop / Airペイ / FLAM / はぴロジ / logiec",
            "attention": company_attention(fos, es, result_due or [], today)}


def events_today(es, today):
    """v2.1 条件付き催事: 本日/昨日に催事(出店決定)があれば1行リストを返す。無ければ[]（=非表示）。"""
    if not es:
        return []
    from datetime import date as _d, timedelta as _td
    try:
        t = _d.fromisoformat(today)
    except ValueError:
        return []
    ydays = {today, (t - _td(days=1)).isoformat()}
    out = []
    for r in es.get("records", []):
        if not r.get("confirmed"):
            continue
        s, e = r.get("start"), r.get("end")
        hit = (r.get("setup_date") in ydays or r.get("teardown_date") in ydays
               or s in ydays or e in ydays or (s and e and s <= today <= e))
        if hit:
            out.append(f"- {r['name']}（{r.get('vendor') or '-'}／日商予算{r.get('daily_budget_man') or '-'}万）")
    return out


# ================================================================
# 5. Morning Brief Generator（v2.1・5ブロック + 条件付き）
# ================================================================

def next_brief_path(today: str) -> Path:
    """追記型命名: YYYY-MM-DD.md → _2.md → _3.md…（上書き禁止）"""
    p = BRIEF_DIR / f"{today}.md"
    n = 1
    while p.exists():
        n += 1
        p = BRIEF_DIR / f"{today}_{n}.md"
    return p


def draft_path(today: str) -> Path:
    """v2.1/Sprint3: 前夜Brief下書きの置き場（_draft/・上書き可）。「おはよう」時に表示+当朝差分の起点。"""
    d = BRIEF_DIR / "_draft"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{today}.md"


def read_night_build(today: str):
    """Night Build完了報告（_draft/night_build_YYYY-MM-DD.json）を読む。💬一言の「昨夜」材料（事実のみ）。
    無ければNone（推測しない）。"""
    p = BRIEF_DIR / "_draft" / f"night_build_{today}.json"
    if not p.exists():
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return None


def generate_brief(materials, selected, dropped, path: Path, brief_no: str):
    """v2.1 Brief。機械は骨組み+ヒント+プレースホルダを置き、LLMが一言・推奨・要約を言語化する。"""
    today = materials["today"]
    lines = [f"# CEO Operating Brief — {today}（{brief_no}）", ""]

    # 🚨 緊急（発生時のみ・最上部）
    urgent = [c for c in selected if c.get("urgent")]
    if urgent:
        lines += ["## 🚨 緊急", ""]
        lines += [f"- {c['item']}（{c['place']}）" for c in urgent]
        lines.append("")

    # 💬 AIから一言（最重要・①先頭と一致）
    top = selected[0]["item"] if selected else None
    night = materials.get("night")
    lines += ["## 💬 AIから一言", ""]
    if top:
        lines.append("<!-- LLM: 3-5行。挨拶 →（夜間の実施事実・異常有無があれば1行）→ 今日の中心判断（次の①先頭と必ず一致）→ 理由一言。事実のみ・演出なし・静けさと余白 -->")
        lines.append(f"（機械ヒント: 今日の中心判断=「{top}」）")
    else:
        lines.append("おはようございます。本日、FOSに判断が必要な案件はありません。落ち着いて進められる一日です。")
    if night:
        anom = night.get("anomalies") or []
        status = "異常なし" if not anom else f"異常{len(anom)}件（{', '.join(a.get('label', '') for a in anom)}）"
        lines.append(f"（夜間ビルド: 成功{night.get('ok')}/{night.get('total')}・{status}・{night.get('generated_at', '')}）")
    lines.append("")

    # ① 今日の判断（原則1件）
    lines += ["## ① 今日の判断（原則1件）", ""]
    if not selected:
        lines += ["- 判断が必要な案件はFOSにありません（判断させたいことはFOSへ入力）", ""]
    for i, c in enumerate(selected, 1):
        fr = c.get("fos") or {}
        imp, main = fr.get("decision_importance"), fr.get("decision_type_main")
        rad = fr.get("review_after_days")
        lines += [
            f"### {i}. {c['item']}",
            f"- 分類: main={main or '未分類'} / 重要度: {imp or '未設定'} / 出典: {c['place']}",
        ]
        if main is None or imp is None:
            lines.append("- ⚠ CEO確認（1タップ）: main=______ / importance=[ S / A / B / C ]")
        if rad is None and imp in IMPORTANCE_DEFAULT_REVIEW:
            lines.append(f"- 結果確認（AI提案・確定はCEO）: {IMPORTANCE_DEFAULT_REVIEW[imp]}日後 [ 採用 / 変更:__日 ]")
        lines += [
            "- 推奨: <!-- LLM: 推奨・理由・効果・リスク・手順・根拠EP/KN（5行以内） -->",
            "- CEO判断: [ 承認 / 却下 / 保留 ] ______",
            "",
        ]

    # ② AIからの提案（FOS Review・最大3件・提案のみ）
    reviews, review_total = materials.get("fos_review", ([], 0))
    lines += ["## ② AIからの提案（FOSは変更していません）", ""]
    for p in reviews:
        lines.append(f"- [{p['観点']}] {p['text']}（根拠: {p['根拠']}）")
    if review_total > len(reviews):
        lines.append(f"- ほか{review_total - len(reviews)}件は影響の大きい順に翌日以降へ（毎日3件ずつ整えます）")
    lines.append("<!-- LLM: 順番・今日やらなくてよい・AIでできる の観点で追加提案が1-2件あれば。無ければこの行は削除 -->")
    lines.append("")

    # ③ AI Actions（ai_ready=yes・承認制・最大5件）
    ai_actions = materials.get("ai_actions", [])
    lines += ["## ③ AI Actions（承認すればAIが実行・Draft/取込/生成まで）", ""]
    if ai_actions:
        for a in ai_actions[:5]:
            lines.append(f"[ ] {a.get('title')}（{a.get('project') or '-'}／出力: 06_Reports） CEO: [ 承認 / 不要 ]")
        if len(ai_actions) > 5:
            lines.append(f"- ほか{len(ai_actions) - 5}件（次点）")
    else:
        lines.append("- なし（ai_ready=yesのFOSタスクはありません。FOS Rule §4-6でタスクにai_readyを付けると自動掲載）")
    lines.append("")

    # ④ 会社の状態（1-3行要約・数字を並べない・v2.1.1 注意点検出）
    h = materials.get("company_hints", {})
    att = h.get("attention", [])
    real = [a for a in att if a.get("level") != "low"]
    lines += ["## ④ 会社の状態", ""]
    if real:
        lines.append("<!-- LLM: 1-3行で要約。「会社は正常です。注意点は_件— …」の形。重要な注意点のみ・数値の羅列や全項目リストは書かない（詳細はDashboard） -->")
    else:
        lines.append("<!-- LLM: 実質的な注意点なし→「会社は正常です」を1行。数値の羅列は書かない -->")
    lines.append("（機械ヒント・注意点: " + ("／".join(f"[{a['観点']}]{a['text']}" for a in att[:5]) if att else "なし") + "）")
    lines.append("")

    # 条件付き表示（出す条件があるときだけ現れる）
    ev = materials.get("event_today", [])
    if ev:
        lines += ["## 🎪 催事（本日/昨日）", ""] + ev + [""]
    due = materials.get("result_check_due") or []
    if due:
        lines += ["## ⏰ 結果確認待ち（判定はCEOのみ）", ""]
        for d in due:
            lines.append(
                f"- {d.get('判断')}（確認予定 {d.get('確認予定日') or '-'}）: "
                f"expected={d.get('expected_result') or '未入力'} / actual=______ / [ 成功 / 失敗 / 継続観察 ]")
        lines.append("")

    # footer
    content_lines = len([l for l in lines if l.strip()])
    lines += [
        "---",
        "*会社の詳細（売上・Dataset・Learning）はDashboard、AI開発はAI開発レポート、選外・レビュー待ちは各ログへ（情報は消えていません）。*",
        f"*発行: CEO Assistant v{VERSION} [{STATE}]（{materials['now']}）+ FUKUDA AI（言語化）。本文{content_lines}行（目安30行以内）。実行系の提案はありません。*",
    ]
    safe_write(path, "\n".join(lines))
    return path, content_lines


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
    DRAFT_LOG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(data["drafts"])


# ================================================================
# main
# ================================================================

def main():
    check_only = "--check" in sys.argv
    draft_mode = "--draft" in sys.argv   # Sprint3: 前夜下書き（_draft/へ・decision_draftは起票しない・上書き可）
    today = datetime.now().strftime("%Y-%m-%d")

    knowledge = read_released_knowledge()
    principles = read_principles()
    memory = read_memory()
    pending = read_pending()
    fos = read_fos()
    es = read_event_schedule()

    print(f"CEO Assistant v{VERSION} [{STATE}]（Brief v2.1「Less is More」）")
    print(f"Knowledge: released/verified {len(knowledge['usable'])}件（draft等 {knowledge['excluded_count']}件を除外）")
    print(f"Principles: CORE {principles['core_count']}条 / EP {len(principles['eps'])}件")
    print(f"PENDING未完了: {len(pending)}件（Briefには出さない → AI開発レポートへ）")
    if fos:
        print(f"FOS: TaskRecord {len(fos['records'])}件 / Decision候補 {len(fos['decisions'])}件 / "
              f"期限切れ {len(fos['overdue'])}件（取込: {fos['generated_at']}）")
    else:
        print("FOS: 未接続（07_Data/fos/index.jsonなし → fos_importer.py実行で接続）")
    print(f"催事スケジュール: {'取込済み' if es else '未取込'} / 結果確認待ち: {len(read_result_due())}件")

    cands = fos_candidates(fos)
    cands.sort(key=lambda c: -c["score"])
    selected, dropped = select_v21(cands)                          # v2.1: 原則1件
    reviews = fos_review(fos)                                      # (表示分, 総数)
    ai_actions = (fos or {}).get("summary", {}).get("ai_action_records", []) if fos else []
    print(f"判断候補: {len(cands)}件 → 選定{len(selected)}件（v2.1原則1件）/ 選外{len(dropped)}件")
    print(f"FOS Review提案: {reviews[1]}件（表示{len(reviews[0])}件）/ AI Actions候補: {len(ai_actions)}件")
    for c in selected:
        print(f"  ★ [{c['score']}] {c['item'][:60]}")

    if check_only:
        print("--check: 書き込みなしで終了")
        return

    due = read_result_due() + (fos or {}).get("summary", {}).get("decision_metadata", {}).get("result_check_due", [])
    materials = {
        "today": today, "now": datetime.now().strftime("%H:%M"),
        "knowledge": knowledge, "principles": principles,
        "memory": memory, "pending_count": len(pending),
        "fos": fos, "event_schedule": es,
        "fos_review": reviews,
        "ai_actions": ai_actions,
        "company_hints": company_hints(fos, es, due, today),
        "event_today": events_today(es, today),
        "result_check_due": due,
        "night": read_night_build(today),   # Sprint3: 夜間ビルド完了報告（あれば💬一言の材料）
    }
    if draft_mode:
        path = draft_path(today)
        _, nlines = generate_brief(materials, selected, dropped, path, brief_no="前夜下書き")
        print(f"Brief下書き（v2.1・本文{nlines}行・_draft/）: {path}")
        print("→ 朝は「おはよう」で本下書きを表示（+当朝差分）。下書きではDecision Log Draftを起票しない（確定は朝）")
    else:
        path = next_brief_path(today)
        brief_no = "第" + (path.stem.split("_")[-1] if "_" in path.stem else "1") + "号"
        _, nlines = generate_brief(materials, selected, dropped, path, brief_no=brief_no)
        total = generate_decision_drafts(selected, path.name, today)
        print(f"Brief（v2.1・本文{nlines}行）: {path}")
        print(f"Decision Log Draft: {DRAFT_LOG_PATH.name}（累計{total}件）")
        print("→ 次工程: FUKUDA AI（LLM）が <!-- LLM: --> を言語化（一言=①先頭一致）・30行以内へ整えCEOへ提示")
    if nlines > 32:
        print(f"  ⚠ 30行目安を超過（{nlines}行）。LLM最終整理で圧縮すること")


if __name__ == "__main__":
    main()
