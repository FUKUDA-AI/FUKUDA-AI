# CEO_ASSISTANT_IMPL_PLAN — CEO Assistant v1.1 実装計画

Version: 計画v1.0（Sprint 7・計画のみ・コード未着手）
最終更新日: 2026-07-06
状態: Draft（CEO確認待ち → 承認後に実装開始）
対象設計書: CEO_ASSISTANT.md / CEO_MORNING_BRIEF_DESIGN.md / AGENT_COLLABORATION.md

---

## 0. 実装方式（重要な設計判断）

**ハイブリッド方式**を提案する。

```
ceo_assistant.py（機械）: 情報収集・ルール適用・材料集約・骨組み生成・Draft保存
        ↓ brief_input（判断候補・スコア・根拠つき材料）
FUKUDA AI本体（LLM）: 推奨文・理由・リスクの言語化、最終検査、CEOへの提示
```

理由: Reader群・絞り込みルール・保存は機械化で毎回確実になるが、「判断3件の推奨と理由」の文章品質はスクリプトだけでは出せない。機械が事実とルールを担保し、LLMが言葉を担う分業が、AI_CHARTER（推測しない・根拠を示す）と品質を両立する。

## 1. 実装対象ファイル（新規1本）

`ceo_assistant.py`（プロジェクトルート・CEO Assistant v1.1 [Experimental]）
単一ファイル内に6機能をモジュール関数として実装（import連鎖の防止・Development Standard準拠）。

| # | 機能 | 内容 |
|---|---|---|
| 1 | Released Knowledge Reader | knowledge_index.json → **status: released / verifiedのみ**抽出。本文はKN-ID指定で遅延読込 |
| 2 | CORE / EVOLVING Principles Reader | CORE_PRINCIPLES.md（18条）とEVOLVING_PRINCIPLES.md（EP-001〜008・active）のパース |
| 3 | AI Memory Reader | CURRENT_STATE / NEXT の現在地・次作業の抽出 |
| 4 | PENDING Reader | PENDING.mdの表をパースし、未完了項目を優先度つきで抽出（完了行は除外） |
| 5 | Morning Brief Generator | 判断候補のスコアリング（Brief設計書§5の6ルール）→最大3件選定→5セクション骨組み生成→ `06_Reports/morning_brief/YYYY-MM-DD.md` 保存 |
| 6 | Decision Log Draft Generator | CEO判断の記録案を `01_Knowledge/08_Decision_Log/decision_log_draft.json` へ保存（**本体decision_log.jsonには書かない**。確定はCEO承認後の別操作） |

## 2. 新規作成するファイル

- ceo_assistant.py（上記）
- 06_Reports/morning_brief/YYYY-MM-DD.md（実行ごとの出力）
- 01_Knowledge/08_Decision_Log/decision_log_draft.json（Draft置き場・本体と分離）

## 3. 更新するファイル（実装完了時）

- 03_Agents/CEO_ASSISTANT.md（v1.0→v1.1: 起動方法に`python3 ceo_assistant.py`を追記）
- 03_Agents/README.md / 00_MASTER/CHANGELOG.md / ROADMAP.md / 10_AI_Memory一式
- 既存ファイルの削除・破壊的変更は一切なし

## 4. 読み込むファイル（読み取り専用）

00_MASTER全文書（特にCORE/EVOLVING/AI_CHARTER）/ 10_AI_Memory 3ファイル / 01_Knowledge/knowledge_index.json + released本文 / 04_SOP（released SOP）/ 01_Knowledge/08_Decision_Log/decision_log.json（前日判断の確認）/ 06_Reportsのレビューキュー

## 5. 出力するファイル（書込先ホワイトリスト・これ以外into書き込まない実装にする）

- `06_Reports/morning_brief/` （Brief）
- `01_Knowledge/08_Decision_Log/decision_log_draft.json` （Draft）
- `10_AI_Memory/` （状態更新）

## 6. 実装順序

1. Reader 4種（Knowledge / Principles / Memory / PENDING）+ 単体検証
2. 判断候補の集約とスコアリング（絞り込み6ルールの実装）
3. Morning Brief Generator（骨組み生成・保存・冪等: 同日再実行は上書き確認）
4. Decision Log Draft Generator
5. 統合実行（`python3 ceo_assistant.py` 一発でbrief_input+骨組みまで）
6. 実運用テスト: 第2号Briefを本仕組みで発行し、手動版（第1号）と品質比較
7. 文書更新（CEO_ASSISTANT.md v1.1・CHANGELOG・ROADMAP・Memory）

## 7. リスク

| リスク | 緩和策 |
|---|---|
| Markdown表のパース脆弱性（PENDING等の形式変更で壊れる） | 寛容なパーサ+失敗時は「読めない」と正直に報告（推測で補わない） |
| 機械生成文の品質不足 | ハイブリッド方式（§0）。機械は骨組みまで、言語化はLLM |
| 判断3件の選定が機械的すぎる | スコアは提案扱い。LLM工程とCEOの差し替え指示で補正（Brief設計§7） |
| Draftログと本体ログの二重管理 | ファイル分離+「確定=CEO承認後にマージ」の手順を関数化 |
| 書込先の逸脱 | 出力パスをホワイトリスト定数化し、それ以外への書込をコードで禁止 |

## 8. Version更新

- **必要**: ceo_assistant.py 新規 → CEO Assistant **v1.1 [Experimental]**（新機能追加）
- CEO_ASSISTANT.md v1.0 → v1.1（マイナー更新・起動方法追記）
- CHANGELOG記録・README同期（Development Standard §1・§2）

## 9. CEOへ確認すべきこと

1. **Decision Log Draftの保存先**: 指示は「08_Decision_Log/」だが、ルート08_Decision_Log/は廃止済み（CEO決定 2026-07-06）。**正式保存先 `01_Knowledge/08_Decision_Log/decision_log_draft.json` でよいか**
2. **ハイブリッド方式（§0）の承認**: 機械=材料とルール、LLM=言語化。完全スクリプト生成を希望する場合は品質低下を許容いただく必要がある
3. 同日に複数回実行した場合の扱い: 上書きでよいか、第2版として別名保存か（推奨: 追記型 `YYYY-MM-DD_2.md`）

## 変更履歴

| 日付 | 版 | 内容 |
|---|---|---|
| 2026-07-06 | 計画v1.0 | Sprint 7実装計画（コード未着手・CEO確認待ち） |
