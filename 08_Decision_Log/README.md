# 08_Decision_Log — 経営判断・経営知見ログ【旧保存先】

> **【2026-07-06 CEO決定】正式保存先は `01_Knowledge/08_Decision_Log/` へ移行した。本フォルダは今後使用しない。**
> Extractor v2.0化完了（2026-07-06）により、全スクリプトの出力先は正式保存先へ変更済み。
> 本フォルダのデータは削除せず存置。**99_Archive/への移動を提案中（CEO承認待ち）。**

## 目的
ChatGPTログから抽出した「経営判断（Decision）」と「経営知見（Insight）」を、Conversation全文を保存せずログとして管理する。

## Version
- Decision Extractor v1.0 [Experimental] → `decision_log.json`（20件）
- Insight Extractor v1.0 [Experimental] → `insight_log.json`（382件）

## 最終更新日
2026-07-03

## 関連機能
Decision Extractor / Insight Extractor（いずれもプロジェクトルートの.py）

## 依存関係
- 入力: 01_Knowledge/09_ChatGPT_Archive/_extracted/ と 07_Data/chatgpt_index.json
- 前提: chatgpt_importer.py を先に実行しておくこと

## 使用方法
```
python3 decision_extractor.py [--rebuild]
python3 insight_extractor.py [--rebuild]
```
無印は既存ログとマージ、`--rebuild` はゼロから再構築。

## 今後のTODO
- [Experimental] → [Released] 昇格のためのCEOレビュー
- 重要度「高」会話の意味解析による抽出漏れ改善（Phase 5次Sprint）
- Knowledge Builder（Phase 6）への接続
