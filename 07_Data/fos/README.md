# 07_Data/fos — FOS TaskRecord（Data Layer）

## 目的
FOS-data.json（正本・CEOの操作面）を正規化したTaskRecordの保管庫。Morning Brief・Agentの参照元。

## Version
FOS Importer v1.0 [Experimental]（2026-07-07〜稼働）

## 最終更新日
2026-07-07

## 構成

| 場所 | 内容 | ルール |
|---|---|---|
| `index.json` | TaskRecord全件+サマリー（Decision候補・期限切れ・Sprint/PENDING同期レポート） | Importerのみ再生成。手動編集禁止 |
| `snapshots/` | FOS-data.jsonの取込時スナップショット（日付+内容ハッシュ。同一内容は保存しない） | 削除しない |

## 使用方法

```
python3 fos_importer.py          # 取込+索引更新（Brief発行前に実行）
python3 fos_importer.py --check  # 読込確認のみ
```

## TaskRecordデータ辞書

| フィールド | 内容 |
|---|---|
| record_id | FOS-{task/next/req/imp/evt}-{FOS内ID} |
| source_type | task / next_action / staff_request / improvement / event |
| title / project / category / status | タスク内容と帰属 |
| priority / urgency | FOSのtodayScore/urgency由来。priority降順でソート済み |
| due_date / overdue | 期限と期限切れ検知（eventsのみ） |
| decision_candidate | Brief判断候補フラグ（staff_request・期限切れ・改善案） |
| brief_candidate | Brief掲載候補フラグ |
| options | staff_requestの選択肢・スタッフ推奨（あればBriefがほぼ完成形になる） |
| decision_needed（v1.1設計） | YES / NO（FOS Operating Rule §4-1の基準。CEO入力） |
| decision_type_main / sub（v1.1設計） | 13分類の2階層（main必須・sub任意=null可）。Decision Log→Result→Knowledgeへ一気通貫 |
| decision_importance（v1.2設計） | S / A / B / C（経営重要度・§4-3。**priority=急ぎ度とは別軸**。S=Brief必載） |
| expected_result（v1.2設計） | 判断時に期待する結果1行（§4-4）。Result Recordでactual_resultと比較 |
| review_after_days（v1.2設計） | 結果確認までの日数（§4-5。初期値S30/A14/B7/Cなし）。経過でBrief「結果確認待ち」へ |

**既存データ互換（v1.1〜v1.2）**: 既存FOS-data.jsonに decision_needed / decision_type / decision_importance / expected_result / review_after_days の項目がない場合、Importerは **null（未分類/未設定）** として扱い壊さない。未分類・未設定のdecision候補はBriefでCEOへ確認を提示。AIは推測で分類・重要度・期待結果を確定しない（review_after_daysの初期値提案のみ可・確定はCEO）

## ルール（FOS Operating Rule v1.2準拠 → 正: [../../FOS/README.md](../../FOS/README.md)）

- FOS原本は読み取り専用。**タスクの完了化・削除・変更はCEO操作のみ**（AIは書かない）
- 内容はKnowledge直行禁止（本フォルダ=Data Layer → 意味づけされたものだけLearning Cycleへ）
- FOS=CEOの操作面 / 10_AI_Memory/PENDING=AIの記録面。同一案件の二重管理をしない
