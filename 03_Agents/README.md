# 03_Agents — AIエージェント定義

## 目的
専門AI（CEO補佐 / so u / SUNNY NOMADO / 催事 / 発注・在庫 / 営業 / 広告・SEO / 資金繰り / 商品企画 / 秘書）の定義・プロンプト・設定を管理する。

## Version
Agent Design v1.0（設計完了・実装は未着手）

## 最終更新日
2026-07-06

## 構成

- [AGENT_DESIGN.md](AGENT_DESIGN.md) — **10エージェント設計書 v1.0**（目的/役割/入出力/参照Knowledge・Principle/判断基準/連携/CEO確認事項/禁止事項/v1.0・v2.0スコープ）。CEOレビュー待ち
- [AGENT_COLLABORATION.md](AGENT_COLLABORATION.md) — **OS連携設計書 v1.0**（情報フロー3層・起点トリガー・CEO報告経路・共有/書換禁止データ・CEO必須確認8分類・日次/週次/月次フロー・典型シナリオ6件）。CEOレビュー待ち
- [CEO_ASSISTANT.md](CEO_ASSISTANT.md) — **CEO補佐AI v1.0 [Experimental]**（FUKUDA AI初の稼働Agent・Morning Brief専用。起動: CEOが「Morning Brief」と発話）
- 他Agent個別定義は実装Sprint（Phase 9）で「領域 + Agent」型の命名（NAMING_CONVENTION.md §5）で追加する

## 共通原則（AGENT_DESIGN.md §0を正とする）

- Layer: ⑤Agent Layer。①〜④を参照し、書き込みは06_Reports・01_Knowledge/_draftsのみ
- 参照スタック: 00_MASTER → EP → 02_Rules → Knowledge（releasedのみ・索引経由）→ 07_Data
- 実行はしない（対外送信・支払・発注等はすべてDraft提示 → CEO実行）
- 実装優先順位: ① CEO補佐AI ② 催事AI ③ so u AI

## 依存関係
- 前提: Knowledge Draft 13件のreleased化（Knowledge Review進行中）
- 参照: 01_Knowledge / 02_Rules / 00_MASTER / 10_AI_Memory

## 今後のTODO
- AGENT_DESIGN.mdのCEOレビュー
- CEO補佐AI v1.0の実装Sprint（Agent定義フォーマット確定を含む）
