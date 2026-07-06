# 07_Data — 構造化データ（Data Layer）

## 目的
パイプラインが生成する構造化データ（Index等）と、外部データソースの実績データを格納する**事実の保管庫**。不変・出典つき・索引ファースト。

## 設計文書（本フォルダが正）
- [CONNECTOR_ARCHITECTURE.md](CONNECTOR_ARCHITECTURE.md) — Connector→Importer→Learning Cycleの4層設計・共通スキーマ・8 Importer（v1.0 Draft）
- [DATA_SOURCE_DESIGN.md](DATA_SOURCE_DESIGN.md) — 10データソース別の取得範囲・優先順位・段階分け（v1.0 Draft）

## Version
v1.1（Connector Architecture設計を追加）

## 最終更新日
2026-07-06

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

## 今後のTODO
- ~~催事・発注・在庫・Shopify・Meta広告データの取り込み設計~~ ✅ 2026-07-06 設計完了（上記2文書）
- v1.1実装: 催事Connector+Events Importer → Claude Importer → Sheets → Shopify
- ChatGPT Importer v2.0（Connector/Importer分離・共通スキーマ移行。chatgpt_index.jsonは互換変換・削除しない）
