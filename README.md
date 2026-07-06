# FUKUDA AI — NOMADO AI Operating System

## 目的
NOMADO株式会社の経営を支援する「福田AI」を構築する。長期運用を前提としたソフトウェア開発プロジェクトとして運用する。

## Version
- プロジェクト: Phase 5まで完了（ROADMAP.md参照）
- Architecture: v1.0
- Development Standard: v1.0

## 最終更新日
2026-07-03

## 開発標準（概要）
全開発は [00_MASTER/DEVELOPMENT_STANDARD.md](00_MASTER/DEVELOPMENT_STANDARD.md) に従う。

- 全機能はVersionを持ち、更新時はCHANGELOGを必ず同時更新する
- 機能の状態は [Released] / [Experimental] / [Deprecated]。正式運用はReleasedのみ
- 既存ファイルの無断削除・上書き禁止。破壊的変更は事前確認。一時ファイルのみ削除可
- Sprint開発。Sprint終了時に完成物・Version・CHANGELOG・ROADMAP・次Sprint・レビュー結果を更新
- 命名は [NAMING_CONVENTION.md](00_MASTER/NAMING_CONVENTION.md) に従う
- 機能追加より長期運用品質を優先する

## Architecture v1.0
```
Conversation → Conversation Index → Insight → Decision
→ Lessons Learned → CEO Principles → Knowledge → AI Agents
```

## 実装済み機能

| 機能 | Version | 状態 | 実行方法 |
|---|---|---|---|
| ChatGPT Importer | v1.1 | Released | `python3 chatgpt_importer.py` |
| Conversation Index | v1.0 | Released | （Importerが生成） |
| Decision Extractor | v1.0 | Experimental | `python3 decision_extractor.py [--rebuild]` |
| Insight Extractor | v1.0 | Experimental | `python3 insight_extractor.py [--rebuild]` |

## フォルダ構成

| フォルダ | 内容 |
|---|---|
| 00_MASTER | 開発標準・変更履歴・ロードマップ・経営哲学 |
| 01_Knowledge | 知識ベース（ChatGPTアーカイブ含む） |
| 02_Rules | AIエージェントの運用ルール |
| 03_Agents | AIエージェント定義（Phase 9） |
| 04_SOP | 標準作業手順 |
| 05_Projects | 個別プロジェクト |
| 06_Reports | 分析・定期レポート |
| 07_Data | 構造化データ（Index等） |
| 08_Decision_Log | 経営判断・経営知見ログ |
| 99_Archive | アーカイブ（削除の代わりに移動） |

## 依存関係
Pythonスクリプトはプロジェクトルートに置き、共通処理を相互importしている（chatgpt_importer → decision_extractor → insight_extractor の順に依存）。

## 今後のTODO
- Phase 4/5のCEOレビューとReleased昇格
- Phase 6: Knowledge Builder（Knowledge Writer v1.0）の設計
