#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOS Importer v1.0 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト

FOS-data.json（正本・Source of Truth）を読み取り専用で取り込み、
TaskRecordへ正規化して 07_Data/fos/ に保存する。
Morning Brief（CEO Assistant）のDecision候補・タスク・期限の入力元。

フロー: FOS-data.json → 【FOS Importer（本機能）】 → TaskRecord → Morning Brief → Decision候補

重要ルール:
・JSONのみ読む（FOS.htmlは読まない・解析しない）
・FOS原本への書き込み禁止（読み取り専用。タスク完了・削除・変更はCEO確認後のみ=そもそも本ツールは書かない）
・内容はKnowledgeへ直接渡さない（Data Layer保存→意味づけされたものだけLearning Cycleへ）
・書き込み先は 07_Data/fos/ のみ
・冪等（内容ハッシュが同じなら再取込しない）

使い方:
    python3 fos_importer.py            # 取込 + index.json更新
    python3 fos_importer.py --check    # 読込と件数確認のみ（書き込みなし）
"""

import hashlib
import json
import sys
from datetime import datetime, date
from pathlib import Path

VERSION = "1.0"
STATE = "Experimental"

BASE_DIR = Path(__file__).resolve().parent
FOS_PATH = BASE_DIR / "FOS" / "FOS-data.json"          # 正本（読み取り専用）
OUT_DIR = BASE_DIR / "07_Data" / "fos"                  # 書き込みはここのみ
SNAP_DIR = OUT_DIR / "snapshots"
INDEX_PATH = OUT_DIR / "index.json"
PENDING_PATH = BASE_DIR / "10_AI_Memory" / "PENDING.md"  # 同期レポート用（読み取りのみ）


def load_fos():
    if not FOS_PATH.exists():
        raise FileNotFoundError(f"FOS-data.jsonが見つからない: {FOS_PATH}")
    raw = FOS_PATH.read_text(encoding="utf-8")
    return json.loads(raw), hashlib.md5(raw.encode()).hexdigest()[:12]


def build_records(fos, today):
    """FOS-data.json → TaskRecord群。推測せず、無い項目はnull。"""
    projects = {p["id"]: p for p in fos.get("projects", [])}
    records = []

    def project_of(pid):
        p = projects.get(pid, {})
        return p.get("name"), p.get("category"), p.get("scores", {})

    # 1) tasks → TaskRecord
    for t in fos.get("tasks", []):
        pname, pcat, scores = project_of(t.get("projectId"))
        records.append({
            "record_id": f"FOS-task-{t['id']}",
            "source_type": "task",
            "title": t.get("title"),
            "project": pname, "category": t.get("category") or pcat,
            "status": "完了" if t.get("done") else "未完了",
            "priority": scores.get("todayScore"),
            "urgency": scores.get("urgency"),
            "due_date": None, "overdue": False,
            "decision_candidate": False, "brief_candidate": not t.get("done"),
        })

    # 2) projects.nextAction → TaskRecord（進行中プロジェクトの次の一手）
    for p in fos.get("projects", []):
        if p.get("nextAction"):
            records.append({
                "record_id": f"FOS-next-{p['id']}",
                "source_type": "next_action",
                "title": f"{p.get('name')}: {p['nextAction']}",
                "project": p.get("name"), "category": p.get("category"),
                "status": p.get("status"),
                "priority": p.get("scores", {}).get("todayScore"),
                "urgency": p.get("scores", {}).get("urgency"),
                "due_date": None, "overdue": False,
                "decision_candidate": False,
                "brief_candidate": p.get("status") == "進行中",
                "stop_reason": p.get("stopReason") or None,
                "waiting_other": p.get("waitingOther") or None,
            })

    # 3) staffRequests → Decision候補（判断が明示的に求められている）
    for s in fos.get("staffRequests", []):
        if s.get("status") in ("resolved", "done"):
            continue
        records.append({
            "record_id": f"FOS-req-{s['id']}",
            "source_type": "staff_request",
            "title": f"【要判断】{s.get('projectName')}: {s.get('decisionNeeded') or s.get('problem')}",
            "project": s.get("projectName"), "category": "スタッフ相談",
            "status": s.get("status"),
            "priority": 90,  # 人が返事を待っている（憲法: 人を待たせない）
            "urgency": 90,
            "due_date": None, "overdue": False,
            "decision_candidate": True, "brief_candidate": True,
            "options": {"A": s.get("optionA"), "B": s.get("optionB"),
                        "スタッフ推奨": s.get("recommended"), "提案": s.get("staffProposal")},
        })

    # 4) improvements → Brief候補（低優先）
    for i in fos.get("improvements", []):
        if i.get("status") in ("done", "rejected"):
            continue
        records.append({
            "record_id": f"FOS-imp-{i['id']}",
            "source_type": "improvement",
            "title": f"改善案: {i.get('idea')}",
            "project": projects.get(i.get("projectId"), {}).get("name"),
            "category": "改善", "status": i.get("status"),
            "priority": 40 if i.get("urgency") == "high" else 20,
            "urgency": None, "due_date": None, "overdue": False,
            "decision_candidate": True, "brief_candidate": False,
            "reason": i.get("reason"),
        })

    # 5) events → 期限つき予定 + 期限切れ検知
    for e in fos.get("events", []):
        due = e.get("date")
        overdue = bool(due and due < today)
        records.append({
            "record_id": f"FOS-evt-{e['id']}",
            "source_type": "event",
            "title": e.get("title"),
            "project": e.get("project"), "category": "予定",
            "status": "期限切れ" if overdue else "予定",
            "priority": 80 if overdue else 60,
            "urgency": None,
            "due_date": f"{due} {e.get('time') or ''}".strip(),
            "overdue": overdue,
            "decision_candidate": overdue,  # 期限切れは判断（実施/延期/中止）が必要
            "brief_candidate": True,
        })

    for r in records:
        r["imported_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        r["importer_version"] = f"v{VERSION}"
    # priority順ソート（降順・None末尾）
    records.sort(key=lambda r: -(r["priority"] or 0))
    return records


def pending_sync_report(records):
    """FOSと10_AI_Memory/PENDINGの同期状況（読み取りのみ・レポートだけ）。"""
    pending_text = PENDING_PATH.read_text(encoding="utf-8") if PENDING_PATH.exists() else ""
    fos_decisions = [r for r in records if r["decision_candidate"]]
    in_pending = sum(1 for r in fos_decisions
                     if r["title"][:15] in pending_text or (r.get("project") or "") in pending_text)
    return {
        "fos_decision_candidates": len(fos_decisions),
        "pending_overlap_estimate": in_pending,
        "note": "FOS=CEO操作面 / PENDING=AI記録面。差分の取り込みはBrief経由でCEO確認後のみ",
    }


def sprint_sync(fos):
    """Sprint同期: FOSのprojects状態を集計（FUKUDA AIのSprintとの突合材料）。"""
    from collections import Counter
    return {
        "project_status": dict(Counter(p.get("status", "不明") for p in fos.get("projects", []))),
        "active_projects": [p["name"] for p in fos.get("projects", []) if p.get("status") == "進行中"],
    }


def main():
    check_only = "--check" in sys.argv
    today = date.today().isoformat()
    fos, content_hash = load_fos()
    records = build_records(fos, today)

    from collections import Counter
    by_type = Counter(r["source_type"] for r in records)
    decisions = [r for r in records if r["decision_candidate"]]
    overdue = [r for r in records if r["overdue"]]

    print(f"FOS Importer v{VERSION} [{STATE}]（正本: FOS-data.json / HTMLは読まない）")
    print(f"読込: projects {len(fos.get('projects', []))} / tasks {len(fos.get('tasks', []))} / "
          f"staffRequests {len(fos.get('staffRequests', []))} / improvements {len(fos.get('improvements', []))} / events {len(fos.get('events', []))}")
    print(f"TaskRecord: {len(records)}件 {dict(by_type)}")
    print(f"Decision候補: {len(decisions)}件 / 期限切れ: {len(overdue)}件")
    for r in records[:8]:
        od = " ⚠期限切れ" if r["overdue"] else ""
        dc = " ★判断" if r["decision_candidate"] else ""
        print(f"  [{r['priority'] or '-'}]{dc}{od} ({r['source_type']}) {str(r['title'])[:55]}")

    if check_only:
        print("--check: 書き込みなしで終了")
        return

    # 冪等: 同一ハッシュのスナップショットは再保存しない
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SNAP_DIR.mkdir(exist_ok=True)
    snap_path = SNAP_DIR / f"{today}_{content_hash}.json"
    if not snap_path.exists():
        snap_path.write_text(json.dumps(fos, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"スナップショット保存: {snap_path.name}")
    else:
        print("スナップショット: 同一内容のため保存スキップ（冪等）")

    index = {
        "meta": {"generator": f"FOS Importer v{VERSION} [{STATE}]",
                 "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "source": "FOS/FOS-data.json（正本・読み取り専用）",
                 "content_hash": content_hash,
                 "note": "Morning Brief・Agent参照用。Knowledge直行禁止。タスク操作はCEO確認後のみ",
                 "total": len(records)},
        "summary": {"by_type": dict(by_type),
                    "decision_candidates": len(decisions),
                    "overdue": len(overdue),
                    "sprint_sync": sprint_sync(fos),
                    "pending_sync": pending_sync_report(records)},
        "records": records,
    }
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"index.json更新: {len(records)}件 → Morning Brief参照可能")


if __name__ == "__main__":
    main()
