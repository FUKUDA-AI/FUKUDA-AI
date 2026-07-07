# 07_Data — 構造化データ（Data Layer）

## 目的
パイプラインが生成する構造化データ（Index等）と、外部データソースの実績データを格納する**事実の保管庫**。不変・出典つき・索引ファースト。

## 設計文書（本フォルダが正）
- [CONNECTOR_ARCHITECTURE.md](CONNECTOR_ARCHITECTURE.md) — Connector→Importer→Learning Cycleの4層設計・共通スキーマ・8 Importer（v1.0 Draft）
- [DATA_SOURCE_DESIGN.md](DATA_SOURCE_DESIGN.md) — 10データソース別の取得範囲・優先順位・段階分け（v1.0 Draft）

## Version
v1.3（Dataset Registry v1.0を追加・Spreadsheet Registryを統合・Sprint 14.5）

## 最終更新日
2026-07-07

## 関連機能
- ChatGPT Importer v1.1 [Released] → `chatgpt_index.json`（Conversation Index v1.0、3,323件）

## 依存関係
- 入力: 01_Knowledge/09_ChatGPT_Archive のZIP
- 出力先として利用: Decision Extractor / Insight Extractor（Indexのメタ情報を参照）

## 使用方法
```
python3 chatgpt_importer.py   # プロジェクトルートで実行
```
再実行時は既存Indexとマージ。詳細はプロジェクトルートREADME参照。

## 稼働中の取込機能
- **Events Importer v1.0 [Experimental]**（2026-07-06〜）: `events/raw/` のExcel/CSV → EventRecord正規化 + `events/index.json`。詳細は [events/README.md](events/README.md)

## 稼働中の取込機能（続き）
- **FOS Importer v1.0 [Experimental]**（2026-07-07〜）: `FOS/FOS-data.json`（正本・読み取り専用）→ TaskRecord → `fos/index.json`。Morning Brief接続済み（CEO Assistant v1.2）

## Dataset Registry（v1.0設計・Sprint 14.5・全データソース共通の台帳）
- `datasets/DATASET_REGISTRY.md` + `dataset_registry.json` — **あらゆるデータソースの台帳**（23項目・source_type 18種: google_sheets/excel/csv/json/fos_json/shopify/meta_ads/gmail/google_calendar/notion/airtable/sqlite/postgresql/chatgpt_export/claude_conversation/gemini_conversation/meeting_transcript/other）。稼働中3ソース（FOS/ChatGPT/催事）をdraft登録済み
- **AI Conversation Source**: ChatGPT/Claude/Geminiの会話は共通の**ConversationRecord**（16項目）へ正規化してLearning Cycleへ統合（そのままKnowledge化禁止）
- ルール: **未登録Datasetは読まない / AIは編集しない（read_only=true初期値）/ 個人情報・顧客・契約・財務=sensitivity high / Knowledge直行禁止（Dataset→Connector→Importer→Data Layer→Learning Cycle）**
- `spreadsheets/`（Sprint 14.4）はDataset Registryへ統合済み・互換のため保持（削除禁止）

## 今後のTODO
- ~~催事・発注・在庫・Shopify・Meta広告データの取り込み設計~~ ✅ 2026-07-06 設計完了（上記2文書）
- ~~催事Connector+Events Importer~~ ✅ 2026-07-06 v1.0実装（データ投入は次Sprint）
- v1.1実装続き: Claude Importer → Sheets → Shopify
- ChatGPT Importer v2.0（Connector/Importer分離・共通スキーマ移行。chatgpt_index.jsonは互換変換・削除しない）
