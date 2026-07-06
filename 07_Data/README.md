# 07_Data — 構造化データ

## 目的
パイプラインが生成する構造化データ（Index等）を格納する。今後、催事・発注・在庫・Shopify等の実績データもここへ蓄積する。

## Version
v1.0

## 最終更新日
2026-07-03

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
- 催事・発注・在庫・Shopify・Meta広告データの取り込み設計（Phase 10）
