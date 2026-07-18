#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Night Build v1.0 [Experimental] — NOMADO株式会社 FUKUDA AI プロジェクト（Brief v2.1 実装Sprint 3）

夜間準備思想（CEO_MORNING_BRIEF_V2_DESIGN §3-2）:
    「朝に生成する」のではなく「朝には完成している」。
    夜（AI）: 取込 → 同期 → Dashboard更新 → Result更新 → FOSレビュー → Morning Brief下書き
    朝（CEO）: 「おはよう」 → 表示だけ（お待ちしていました）

本スクリプトは上記パイプラインを順に実行し、
  ①各ステップの完了報告（=💬AIから一言の材料。実行事実のみ・推測しない）
  ②Brief下書き（ceo_assistant.py --draft → 06_Reports/morning_brief/_draft/）
を残す。**各ステップは失敗しても止めず、異常として記録して続行する**
（例: 催事スケジュール取込はネットワークが要るため、オフライン環境では失敗を記録し継続）。

不変ルール（AI_CHARTER準拠）: 読み取り・生成・整理まで。対外送信・支払・発注・FOS変更はしない。
各ステップのスクリプト自身が自分の書込ホワイトリストを持つ（本体は順序制御と報告のみ）。

使い方:
    python3 night_build.py            # 夜間パイプライン実行 + 下書き生成
    python3 night_build.py --dry      # 実行順の確認のみ（サブプロセスを起動しない）

スケジュール化（CEOのMac・任意。過渡期は手動 or「おはよう」時生成でも可）:
    launchd/cron で毎晩 `cd <repo> && /usr/bin/python3 night_build.py` を実行（例は CEO_ASSISTANT.md）。
    ※このリポジトリはCEOのMac上で動かす前提（催事取込のネットワークが必要なため）。
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

VERSION = "1.0"
STATE = "Experimental"
BASE_DIR = Path(__file__).resolve().parent
DRAFT_DIR = BASE_DIR / "06_Reports" / "morning_brief" / "_draft"

# パイプライン定義（順序が重要: 取込→Result→Dashboard→Brief下書き）。
# ceo_assistantはFOS index・催事・Resultを読むため必ず最後。存在しないスクリプトはskip。
STEPS = [
    ("FOS取込",            "fos_importer.py",            []),
    ("催事スケジュール取込", "event_schedule_importer.py", []),   # 要ネットワーク（失敗時は最新スナップショットにフォールバック）
    ("Result更新",         "result_recorder.py",         []),
    ("Dashboard更新",      "dashboard_generator.py",     []),
    ("Brief下書き生成",     "ceo_assistant.py",           ["--draft"]),  # 必ず最後
]

STEP_TIMEOUT = 120  # 秒/ステップ


def run_step(label, script, args):
    p = BASE_DIR / script
    if not p.exists():
        return {"label": label, "script": script, "status": "skip", "summary": "スクリプトなし"}
    try:
        r = subprocess.run([sys.executable, str(p)] + args, cwd=str(BASE_DIR),
                           capture_output=True, text=True, timeout=STEP_TIMEOUT)
        out = [l for l in (r.stdout or "").splitlines() if l.strip()]
        err = [l for l in (r.stderr or "").splitlines() if l.strip()]
        ok = (r.returncode == 0)
        return {"label": label, "script": script,
                "status": "ok" if ok else "fail",
                "returncode": r.returncode,
                "summary": (out[-1][:140] if out else ""),
                "error": ("" if ok else (err[-1][:200] if err else f"exit {r.returncode}"))}
    except subprocess.TimeoutExpired:
        return {"label": label, "script": script, "status": "error",
                "error": f"タイムアウト（{STEP_TIMEOUT}s超）"}
    except Exception as e:  # noqa: BLE001 — 夜間は止めない。異常として記録し継続
        return {"label": label, "script": script, "status": "error", "error": str(e)[:200]}


def build_report(results, today, now):
    ok = sum(1 for r in results if r["status"] == "ok")
    bad = [r for r in results if r["status"] in ("fail", "error")]
    mark = {"ok": "✓", "fail": "✗", "error": "✗", "skip": "—"}
    lines = [
        f"# 🌙 Night Build 完了報告 — {today}", "",
        f"実行: Night Build v{VERSION} [{STATE}]（{now}）", "",
        f"結果: 成功 {ok}/{len(results)} ステップ / 異常 {len(bad)}件", "",
    ]
    for r in results:
        detail = r.get("summary") or r.get("error") or ""
        lines.append(f"- {mark[r['status']]} {r['label']}（{r['script']}）: {detail}")
    lines.append("")
    if bad:
        lines.append("⚠ 異常あり（翌朝の💬AIから一言で要言及・推測せず事実のみ）:")
        for r in bad:
            lines.append(f"  - {r['label']}: {r.get('error') or ''}")
    else:
        lines.append("異常なし。")
    lines += [
        "", "---",
        "*本報告は翌朝の💬AIから一言の材料（実行事実のみ）。Brief下書きは _draft/{date}.md に生成済み。*".replace("{date}", today),
        "*ネットワーク不可の環境では催事取込が失敗し得る（最新スナップショットで継続）。実接続はCEOのMacで担保。*",
    ]
    return "\n".join(lines), ok, bad


def main():
    dry = "--dry" in sys.argv
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Night Build v{VERSION} [{STATE}] — 夜間パイプライン（{now}）")
    if dry:
        for i, (label, script, args) in enumerate(STEPS, 1):
            exists = (BASE_DIR / script).exists()
            print(f"  {i}. {label} → {script} {' '.join(args)} {'' if exists else '(スクリプトなし=skip)'}")
        print("--dry: 実行しません")
        return

    def write_reports(results):
        """完了報告(md/json)を書く。ceo_assistant --draft がjsonを読み💬一言へ夜間サマリを載せるため、
        Brief下書き生成の"前"に一度書き、生成後にもう一度更新する（下書きが夜間結果を参照できる順序）。"""
        report_md, ok_, bad_ = build_report(results, today, now)
        (DRAFT_DIR / f"night_build_{today}.md").write_text(report_md, encoding="utf-8")
        (DRAFT_DIR / f"night_build_{today}.json").write_text(
            json.dumps({"date": today, "generated_at": now, "version": VERSION,
                        "ok": ok_, "total": len(results),
                        "anomalies": bad_, "steps": results},
                       ensure_ascii=False, indent=2), encoding="utf-8")
        return ok_, bad_

    results = []
    # データ工程（Brief下書きより前）。ここまでの結果を報告に書いてから下書きを作る。
    for label, script, args in STEPS[:-1]:
        print(f"  ▶ {label}（{script}）…", flush=True)
        res = run_step(label, script, args)
        results.append(res)
        print(f"    [{res['status']}] {res.get('summary') or res.get('error') or ''}")
    write_reports(results)  # ← ceo_assistant --draft がこのjsonを読む

    # 最後にBrief下書き（夜間サマリを💬一言に反映できる）
    label, script, args = STEPS[-1]
    print(f"  ▶ {label}（{script}）…", flush=True)
    res = run_step(label, script, args)
    results.append(res)
    print(f"    [{res['status']}] {res.get('summary') or res.get('error') or ''}")
    ok, bad = write_reports(results)  # 下書きステップも含めて最終更新

    print(f"\nNight Build 完了: 成功 {ok}/{len(results)} / 異常 {len(bad)}件")
    print(f"完了報告: {DRAFT_DIR / f'night_build_{today}.md'}")
    print(f"Brief下書き: {DRAFT_DIR / f'{today}.md'}")
    if bad:
        print("⚠ 異常:", ", ".join(f"{r['label']}({r.get('error','')[:40]})" for r in bad))
    print("→ 朝は「おはよう」= 下書きを表示（+当朝差分）。異常があれば一言で事実として伝える。")


if __name__ == "__main__":
    main()
