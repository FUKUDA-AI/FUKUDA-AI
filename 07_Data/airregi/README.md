# 07_Data/airregi — Airレジ Connector v1.0（POS売上データ）

Version: 設計書 v1.3（**airregi_importer.py v1.0 [Experimental] 実装済み・テスト9ケース合格 2026-07-07**）
最終更新日: 2026-07-07
状態: 稼働可（設計v1.1/v1.2 CEO承認済み・実装テスト合格。**実運用active化はCEO操作待ち**）

## 使い方

```
1. Airレジ管理画面からCSVエクスポート → raw/店舗別・催事別サブフォルダ/ へ置く
2. python3 airregi_importer.py          # 取込+索引更新
   python3 airregi_importer.py --check  # 文字コード・type判別・列マッピング確認のみ（書き込みなし）
```
対象Dataset: **DS-POS-0001**（Airレジ・status: draft・[../datasets/dataset_registry.json](../datasets/dataset_registry.json)）
関連文書: [../CONNECTOR_ARCHITECTURE.md](../CONNECTOR_ARCHITECTURE.md) / [../DATA_SOURCE_DESIGN.md](../DATA_SOURCE_DESIGN.md) §追補 / [../events/README.md](../events/README.md)（照合先）/ [../../06_Reports/2026-07-07_Airregi_Sample_CSV_Column_Report.md](../../06_Reports/2026-07-07_Airregi_Sample_CSV_Column_Report.md)（列名確認レポート・CEO回答の根拠）

> 目的: Airレジ（POS）の売上CSVを **SalesRecord** へ正規化し、催事実績（EventRecord）と照合して
> 催事AI・CEO補佐AIの判断材料（催事別/商品別売上）にする。
> KN-EVT-0001（駅系平均30万）の定量検証・EP-005（実績+今年の条件）・Result実績照合（Result Layer §9-4）の入力源。
> 将来、催事・店舗・EC等の複数チャネル売上を統合分析できる構造を前提とする。

---

## 1. Layer宣言（ARCHITECTURE §4必須事項）

| 項目 | 内容 |
|---|---|
| 属するLayer | Connector Layer + Importer Layer（パイプライン上流・Data Layerへの供給） |
| 参照するLayer | 07_Data/airregi/raw/（投入CSV・読み取り専用）/ 07_Data/events/index.json（照合・読み取り専用）/ 07_Data/datasets/dataset_registry.json（status確認・読み取り専用） |
| 更新するLayer | **07_Data/airregi/normalized/ と index.json のみ**（書込ホワイトリスト。他への書込はPermissionErrorで拒否する設計） |

## 2. 方式（Connector部）

- **手動CSVエクスポート方式**（認証・API接続なし。「置くだけ」方式で接続コスト最小）
- 文字コード: **Shift_JIS前提 + 自動判別**（CEO回答#8）。デコード試行順: UTF-8(BOM) → Shift_JIS → UTF-8。全て失敗した場合は取込まずCEOへ報告（データは壊さない）
- raw/は読み取り専用（AIは変更・削除しない。処理済み管理はindex.json側で行い、ファイル移動もしない）

### 2-1. 店舗・催事情報の取得 = サブフォルダ方式（CEO回答#1・v1.2確定）

CSV自体に店舗・催事情報がないため、**raw/直下の店舗別・催事別サブフォルダ**で識別する。

```
07_Data/airregi/raw/
  2026-05_◯◯催事/
    売上集計_20260501-20260531.csv
    商品別売上_20260501-20260531.csv
```

| ルール | 内容 |
|---|---|
| 取得 | サブフォルダ名から event_name / store_name を取得する。サブフォルダ名の原文は source_subfolder へ必ず保存（事実） |
| 割当 | サブフォルダ名の名称部分がEventRecord（催事名/会場名・正規化後）と**完全一致**した場合のみ event_name / event_ref へ確定。それ以外は**推測せずnull**とし、index.jsonの「店舗/催事 未確定リスト」へ載せてCEO確認へ回す |
| 直置き | raw/直下（サブフォルダなし）のCSVは event_name / store_name = null + CEO確認行き |
| 現サンプル2件 | **event_name / store_name 未確定として null 扱いで進める**（CEO指示） |

### 2-2. dataset_type（CSV種類を固定しない・ヘッダー判別）

CSV種類は設計に固定埋め込みしない。**dataset_type** として扱い、Importerが**CSVヘッダー（列名シグネチャ）から判別**する。

```
raw/のCSV → 文字コード判別 → ヘッダー読取 → 判別テーブルと照合 → 一致typeとして正規化
                                                  ↓ 一致なし
                                        取込まない（unknown）・CEOへ報告 + 新type登録draftを提案
```

- **dataset_type判別テーブル**が唯一の判別根拠（実体: [dataset_type_table.json](dataset_type_table.json)・コード本体から分離）。新しいCSV種類は**テーブルへの1行追加（CEO確認後）だけで対応**する。設計・コード構造の変更は不要（テストT9で実証済み）
- テーブルへの登録・変更はCEO確認後のみ（AIは判別根拠を推測で追加しない）
- チャネル初期値（CEO確定 2026-07-07）: **channel="event"** / store_name=null / event_name=null（テーブルdefaults定義・店舗/催事名確定後に更新可能）

### 2-3. dataset_type判別テーブル（v1.2確定・サンプル実測に基づく）

| dataset_type | 判別シグネチャ（ヘッダー） | 集計単位 | 確定根拠 |
|---|---|---|---|
| **daily_sales** | 先頭列「集計期間」かつ「売上」「会計数」を含む（10列） | 1行=1営業日 | サンプル実測 2026-07-07 |
| **product_sales** | 先頭列「商品名」かつ「販売総売上」「粗利総額」を含む（14列・「構成比%」4回重複=**位置ベースマッピング**） | 1行=1商品の期間集計 | サンプル実測 2026-07-07 |
| （unknown） | 上記に一致しないヘッダー | — | 取込まずCEOへ報告 |

- **payment_sales（決済方法別）は初期typeから除外**（CEO回答#3）。将来サンプル取得時にテーブル1行追加で対応
- 取引明細（ジャーナル）も未登録（粒度過剰・PIIリスク。必要時に新typeとして検討）

## 3. データ辞書（SalesRecord・v1.2で35項目に確定）

| フィールド | 内容 | 読み取れない場合 |
|---|---|---|
| record_id | SLS-xxxxxxxxxx（source_file+サブフォルダ+日付/期間+商品+端末のハッシュ・冪等） | — |
| source | "airregi" 固定 | — |
| channel | 販売チャネル: 催事 / 店舗 / EC / その他（チャネルマッピング表=CEO確認済み対応表から機械判定。表に無ければnull） | null |
| event_name / store_name | §2-1サブフォルダ方式で取得（完全一致のみ確定・推測しない） | null |
| terminal_id | レジ端末ID（現行CSVには無し=null。将来の複数端末運用用） | null |
| business_date | 営業日（YYYY-MM-DD）。daily_salesのみ（「集計期間」列から） | null |
| **period_start / period_end** | 期間集計の開始日・終了日（**CEO回答#2**）。product_salesはファイル名の `_YYYYMMDD-YYYYMMDD` から取得。daily_salesはnull | null |
| dataset_type | daily_sales / product_sales / …（§2-3判別テーブルの値） | 必須 |
| product_name / product_code / **product_id** | 商品名 / 商品コード（サンプルでは空=null）/ Airレジ内部ID（**CEO承認#5**） | null |
| category / **tax_type** | カテゴリー / 税区分（**CEO承認#5**） | null |
| qty / **return_qty** | 販売数量 / 返品数量（**CEO承認#5**） | null |
| gross_sales / discount / net_sales | 売上・割引額・純売上。**Airレジ出力値をそのまま保存**（税込/税抜・割引前/後の推測禁止・CEO回答#4）。net_salesは現行CSVに対応列なし=null（導出しない） | null |
| **gross_profit** | 粗利総額（**CEO承認#5**・原価系=sensitivity high・対外共有禁止） | null |
| payment_method | 決済方法（payment系type用・初期typeでは未使用=null） | null |
| **cash_sales / non_cash_sales** | 現金支払合計額 / 現金その他支払合計額（**CEO承認#5**・daily_salesの2区分内訳） | null |
| receipt_count / **customer_count** | 会計数 / 客数（**CEO承認#5**） | null |
| event_ref | 照合済みEventRecord ID（EVT-xxx）。§4のルールで完全一致のみ自動リンク | null |
| **sales_definition** | 売上金額の定義。**当面 "unknown" 固定**（CEO回答#4。将来Airレジ仕様確認後に更新） | "unknown" |
| **raw_fields** | 元CSV行の**未マッピング列すべて**を列名→値で保持（**CEO回答#6**）。会計単価・客単価・構成比%（重複列は位置サフィックス: 構成比%_1〜_4）・バーコード等はここへ。**Record本体には保存しない** | {} |
| source_subfolder | raw/内サブフォルダ名の原文（§2-1・事実として必ず保存） | null（直置き時） |
| notes / source_file | メモ・元ファイル名 | null / 必須 |
| imported_at / importer_version / pii_filtered | 取込記録（共通必須3項目） | 必須 |

### 3-1. 確定マッピング表（サンプル実測・v1.2）

**daily_sales（売上集計CSV・10列）**

| CSV列 | SalesRecord |
|---|---|
| 集計期間 | business_date（YYYYMMDD→YYYY-MM-DD） |
| 売上 | gross_sales（Airレジ出力値そのまま・sales_definition="unknown"） |
| 会計数 | receipt_count |
| 客数 | customer_count |
| 商品数 | qty |
| 現金支払合計額 | cash_sales |
| 現金その他支払合計額 | non_cash_sales |
| 割引額 | discount |
| 会計単価・客単価 | raw_fieldsのみ（本体保存なし） |

**product_sales（商品別売上CSV・14列・位置ベース）**

| CSV列 | SalesRecord |
|---|---|
| 商品名 | product_name（集約行・レジ袋等も事実として取込・除外しない） |
| カテゴリー | category |
| 税区分 | tax_type |
| 販売総売上 | gross_sales（同上・"unknown"） |
| 粗利総額 | gross_profit |
| 販売商品数 | qty |
| 返品商品数 | return_qty |
| 商品ID | product_id |
| 商品コード | product_code |
| （ファイル名 _YYYYMMDD-YYYYMMDD） | period_start / period_end |
| 構成比%×4・バーコード | raw_fieldsのみ（構成比%_1〜_4） |

### 3-2. 欠損日の扱い（CEO回答#7）

daily_salesは**期間内に売上があった日だけ出力されている可能性がある**（サンプル: ファイル名5/1〜5/31・中身10日分=意図どおり）。**欠損日を0円として補完しない**（存在する行だけを事実として保存。集計時も「データのある日」の集計であることをindex.jsonへ明記）。

## 4. 催事照合（events連携・本Connectorの中核）

```
SalesRecord（business_date または period + store_name/source_subfolder）
  × EventRecord（start_date〜end_date + venue/event_name）
```

| 条件 | 動作 |
|---|---|
| 日付が会期内 かつ 会場名/催事名一致（正規化後の完全一致） | event_refへ自動リンク + event_nameへEventRecordの催事名を転記 |
| 部分一致 等 | **リンクしない**。index.jsonの「照合候補」へ提示（確定はCEO） |
| 一致なし | event_ref=null（推測しない） |

- 会場名の正規化: 空白/全半角/「店」「会場」等の接尾辞ゆらぎのみ吸収(意味的な推測マッチはしない)
- 照合結果はSalesRecord側にのみ記録（**EventRecord原本は変更しない**）

## 5. フォルダ構成

| 場所 | 内容 | ルール |
|---|---|---|
| `raw/` | AirレジエクスポートCSV。**店舗別・催事別サブフォルダに置く**（§2-1） | 変更・削除禁止（読み取り専用） |
| `normalized/` | SalesRecord（1 CSV行グループ=1 JSON） | Importerのみ生成 |
| `index.json` | 索引+サマリー（チャネル別/日別/催事別売上・商品TOP・照合候補・**店舗/催事 未確定リスト**・未対応type報告） | Importerのみ再生成 |

## 6. 運用ルール（Dataset Rule準拠）

1. **読み取り専用**。レジ操作・取消・返金・値引の実行は一切しない
2. **Knowledge直行禁止**: `Airレジ → Connector → Importer → 07_Data/airregi/ → Learning Cycle` のみ
3. data_sensitivity=high / pii_level=high前提。gross_profit（原価系）は対外共有禁止。備考・自由記述欄はPIIフィルタ対象。顧客個人を特定できる列が発見された場合は取込対象から除外しCEOへ報告
4. 冪等（record_idで重複排除・再実行しても同一結果）
5. 集計サマリー（index.json）は機械的集計のみ。意味づけはLearning Cycleの仕事
6. dataset_type判別テーブル・チャネルマッピング表の登録/変更はCEO確認後のみ（AIはdraft提案まで）
7. 数値・定義の推測禁止: sales_definition="unknown"のまま扱い、税込/割引の解釈をAIが確定しない。欠損日0円補完禁止

## 7. CEO確認状況 + active化

CEO確認はすべて回答済み（2026-07-07）: #1 CSVの種類=2type確定 / #2 サンプルCSV=列マッピング確定 / #3 取得頻度=**催事終了時（event_end）**（日次運用は取込安定後に検討。registry `update_frequency` 反映済み）/ サンプル2件の店舗・催事名=**未確定のままnull**（後日サブフォルダ方式で整理）/ チャネル初期値=channel："event"。

**DS-POS-0001 = 設計上active候補**（CEO 2026-07-07）。**実運用active化（status: draft→active）はairregi_importer v1.0のテスト完了を受けたCEO操作のみ**で行う。

## 8. 実装状況（2026-07-07・v1.0実装済み）

- `airregi_importer.py v1.0 [Experimental]`（ルート直下・--check / 本実行 / --base=テスト用）
- テスト結果（9ケース全合格・2026-07-07）: ①--check（書込なし）②本実行=72件生成 ③再実行=新規0件（冪等）④書込ホワイトリスト=raw/・領域外へPermissionError ⑤催事照合=完全一致リンク/不一致null+未確定リスト（一時領域・模擬EventRecordで検証）⑥type判別=既知2type正常/未知ヘッダーunknown報告・取込なし ⑦文字コード=Shift_JIS・UTF-8自動判別 ⑧サブフォルダ/直置き=null+未確定リスト ⑨欠損日非補完（10日分のみ・0円行なし）。テーブル1行追加のみで新type取込（コード無変更）も実証
- **Dashboard接続済み（2026-07-07・dashboard_generator v1.1）**: Today's Dashboard（本日の売上/催事売上/商品TOP3/未確定ファイル数）+ Dataset Status（DS-POS-0001=ACTIVE・最終同期表示）。**DS-POS-0001はCEO承認によりactive化済み（2026-07-07）**。催事AI・Morning Brief本文への組み込みは次Sprint候補

## 変更履歴

| 日付 | 版 | 内容 |
|---|---|---|
| 2026-07-07 | v1.0 | 初版作成（Sprint 16・設計のみ。手動CSV方式・SalesRecord詳細定義・催事照合ルール・active化条件・実装/テスト計画） |
| 2026-07-07 | v1.1 | CEO指示の拡張性修正3点（設計のみ）— ①dataset_type化・ヘッダー判別・判別テーブル外部化 ②SalesRecord拡張: channel/event_name/store_name/terminal_id ③初回接続CEO確認3点（CSV種類・サンプルCSV・取得頻度）。**CEO承認 2026-07-07** |
| 2026-07-07 | v1.3 | 実装Sprint反映 — airregi_importer.py v1.0 [Experimental]実装・テスト9ケース合格・判別テーブル実体化（dataset_type_table.json）・取得頻度=催事終了時（registry反映）・チャネル初期値channel="event"・使い方追記。DS-POS-0001=設計上active候補（実運用active化はCEO操作） |
| 2026-07-07 | v1.2 | サンプルCSV列名確認+CEO回答8点の反映（設計のみ）— ①店舗/催事=サブフォルダ方式（完全一致のみ確定・現サンプルはnull扱い）②period_start/end追加（product_sales=期間集計・ファイル名から取得）③payment_salesを初期typeから除外 ④売上=Airレジ出力値そのまま・sales_definition="unknown" ⑤承認7項目追加（customer_count/cash_sales/non_cash_sales/tax_type/gross_profit/return_qty/product_id）→35項目 ⑥導出値はraw_fieldsのみ保持（本体保存なし・重複列は位置サフィックス）⑦欠損日0円補完禁止 ⑧Shift_JIS前提+UTF-8自動判別。判別テーブル2type確定（サンプル実測）・確定マッピング表新設 |
