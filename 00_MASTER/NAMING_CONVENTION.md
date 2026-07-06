# NAMING_CONVENTION.md — 命名規則

Version: v1.0
最終更新日: 2026-07-03
状態: Released

---

## 1. フォルダ

- 形式: `NN_PascalCase` または `NN_Snake_Case`（番号2桁 + アンダースコア + 名称）
- 例: `00_MASTER` / `01_Knowledge` / `07_Data` / `08_Decision_Log`
- 番号はパイプライン・重要度順を表す。既存番号の変更は互換性影響ありとして扱う

## 2. Pythonスクリプト

- 形式: `snake_case.py`、役割がわかる「対象_動作」型
- 例: `chatgpt_importer.py` / `decision_extractor.py` / `insight_extractor.py`
- 将来例: `knowledge_writer.py` / `lessons_generator.py`
- 1スクリプト = 1機能。共通処理は既存モジュールからimportする
- スクリプト冒頭のdocstringに機能名・Version・目的・使い方を記載する

## 3. JSONデータ

- 形式: `対象_内容.json`（snake_case）
- 例: `chatgpt_index.json` / `decision_log.json` / `insight_log.json`
- 構造: 必ず `meta`（generated_at / total件数 / note）+ 本体配列 の2層とする
- 日時は `YYYY-MM-DD HH:MM` 形式で統一

## 4. Markdown文書

- マスター文書: `UPPER_SNAKE_CASE.md`（例: `DEVELOPMENT_STANDARD.md` / `CEO_PRINCIPLES.md`）
- フォルダ説明: `README.md`（各フォルダに1つ）
- 通常文書: 内容がわかる日本語または英語名。日付を含む場合は `YYYY-MM-DD_名称.md`

## 5. 機能名・Agent名

- 機能名: 英語の「対象 + 役割」型（例: ChatGPT Importer / Decision Extractor / Knowledge Writer / Knowledge Curator）
- Agent名: 「領域 + Agent」型（例: Finance Agent / 催事AI / so uブランドAI）
- 表記は初出時に必ずVersionを添える（例: Insight Extractor v1.0）

## 6. Version

- 形式: `vX.Y`
  - **X（メジャー）**: 互換性に影響する変更（データ構造変更・フォルダ構成変更・出力形式変更）
  - **Y（マイナー）**: 互換性を保つ改善（精度向上・速度改善・機能追加）
- 初版は v1.0。v0.x は設計中・未検証を意味する
- Version更新時は CHANGELOG.md を必ず同時更新する（[DEVELOPMENT_STANDARD.md](DEVELOPMENT_STANDARD.md) §2）

## 7. Release状態表記

- README・CHANGELOG内では `[Released]` / `[Experimental]` / `[Deprecated]` の角括弧表記で統一する
