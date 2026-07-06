# 07_Data/events — 催事実績データ（Events Connector v1.0）

## 目的
催事実績の共通データ基盤。Morning Brief・催事AI・CEO補佐AIが参照する。

## Version
Events Importer v1.0 [Experimental]

## 最終更新日
2026-07-06

## 構成

| 場所 | 内容 | ルール |
|---|---|---|
| `raw/` | 元データ（Excel .xlsx/.xlsm / CSV）。**ここにファイルを置くだけでよい** | **変更・削除禁止（読み取り専用）** |
| `normalized/` | EventRecord（1催事=1 JSON） | Importerのみが生成 |
| `index.json` | 全レコードの索引+サマリー（総件数・平均売上・会場一覧） | Importerのみが再生成。手動編集禁止 |

## 使用方法

```
1. raw/ へ催事実績のExcel/CSVを置く（ファイル名は自由）
2. python3 events_importer.py        # 取込+索引更新
   python3 events_importer.py --check  # 列マッピングの確認のみ
```

## データ辞書（EventRecord）

| フィールド | 内容 | 読み取れない場合 |
|---|---|---|
| record_id | EVT-xxxxxxxxxx（ファイル名+催事名+会場+開始日のハッシュ・冪等） | — |
| event_name / brand / venue | 催事名・ブランド・会場 | null |
| start_date / end_date | 開始日・終了日（YYYY-MM-DD。年不明の日付は推測せずnull） | null |
| sales / profit | 売上・利益 | null（例: 「abc」等の非数値はnull） |
| days / daily_sales | 日数・日商。**元データに無い場合のみ算術導出**（日数=終了-開始+1、日商=売上÷日数）し、derived_fieldsに明記 | null |
| yoy | 前年比（105% → 1.05） | null |
| notes / source_file | メモ・データ元ファイル名 | null / 必須 |
| imported_at / importer_version / pii_filtered | 取込記録 | 必須 |

## 認識される列名（ゆらぎ吸収）
催事名/イベント名・ブランド・会場/会場名/場所・開始日/初日/開催日・終了日/最終日・売上/売上高/売上金額・利益/粗利・日商/日販・日数・前年比/昨対・メモ/備考。未対応の列は無視し実行時に報告（データは壊さない）。

## 今後のTODO
- 過去催事データの投入（次Sprint）→ KN-EVT-0001（駅系平均30万）の定量検証
- 複数シートのExcel対応（v1.1）
- 会場マスタ（駅系/百貨店/SC等の分類）の整備
