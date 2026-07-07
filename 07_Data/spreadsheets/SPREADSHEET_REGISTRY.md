# SPREADSHEET_REGISTRY v1.0 — スプレッドシート台帳

> **📢 Sprint 14.5でDataset Registryへ統合されました。**
> 新しい登録・参照はすべて [../datasets/DATASET_REGISTRY.md](../datasets/DATASET_REGISTRY.md) + dataset_registry.json（source_type: google_sheets）で行ってください。
> 本フォルダは移行前の互換フォルダとして保持します（削除禁止）。本md・jsonの設計内容はDataset Registryに継承済み（19項目→23項目へ拡張: +source_location / connector_name / importer_name / record_schema）。

Version: v1.0（Sprint 14.4・設計のみ → Sprint 14.5でDataset Registryへ統合）
最終更新日: 2026-07-07
状態: Superseded（後継: 07_Data/datasets/。登録はCEO/スタッフの申告 or Connector接続時）
正本データ: [spreadsheet_registry.json](spreadsheet_registry.json)（本mdは説明書・人間用ビュー）

> **目的**: Google Sheets / スプレッドシートをFUKUDA AIが迷わず扱えるようにする台帳。
> どのシートが・何のデータで・誰のもので・どのAgentが・何に使ってよいかを登録してから読む。**未登録のシートは読まない。**

---

## 1. Registryの項目（19項目）

| 項目 | 内容 | 例 |
|---|---|---|
| spreadsheet_id | Google SheetsのID（URLの/d/〜/の部分）またはファイル名 | 1AbC...xyz |
| name | シート名（人間が呼ぶ名前） | 催事売上管理表2026 |
| description | 何が入っているか1〜2行 | 催事ごとの売上・客数・経費 |
| owner | 所有者・管理者 | CEO / スタッフ名 |
| data_domain | データ領域（§2の12候補から） | 催事 |
| related_agent | 主担当Agent（§3の10候補から） | 催事AI |
| related_brand | 関連ブランド（自社/支援の区別を維持） | so u / SUNNY NOMADO / 全社 |
| source_type | google_sheets / excel / csv | google_sheets |
| update_frequency | 更新頻度 | 催事ごと / 週次 / 日次 |
| data_sensitivity | low / mid / **high**（§4参照） | high |
| pii_level | none / low / **high**（個人情報の有無） | none |
| access_rule | 誰が読めるか | CEO+担当Agent |
| read_only | AIの読み取り専用か（**初期値: 必ずtrue**） | true |
| allowed_use | 使ってよい用途 | 催事実績の分析・Brief判断材料 |
| forbidden_use | 使ってはならない用途 | 対外共有・Knowledge直行・個人特定 |
| related_knowledge | 関連KN ID | KN-EVT-0001 |
| related_decision_type | 関連する判断分類（FOS 13分類・main/sub） | 催事・イベント |
| last_reviewed | CEOが台帳内容を最後に確認した日 | 2026-07-07 |
| status | active / paused / archived | active |

## 2. data_domain候補（12）

催事 / 売上 / 在庫 / 発注 / 受注 / 顧客対応 / 商品 / マーケティング / 財務 / 法務 / AI / その他

## 3. related_agent候補（10）

CEO補佐AI / 催事AI / 発注・在庫AI / so u AI / SUNNY NOMADO AI / 営業AI / 広告・SEO AI / 資金繰りAI / 商品企画AI / 秘書AI

## 4. Spreadsheet Rule（AIの制約）

1. **AIはスプレッドシートを勝手に編集しない**（最初は全シートread_only=true。書き込み解禁はCEO承認のみ）
2. **個人情報・財務・原価・顧客情報を含むものは data_sensitivity=high**（pii_levelも併せて設定。high×highはPENDINGでCEO確認後にのみ参照）
3. **Knowledgeへ直行禁止**。必ず次の順番を守る:
   `Spreadsheet → Connector → Importer → Data Layer（07_Data）→ Learning Cycle`
4. 未登録のシートは読まない（発見したら台帳への登録をCEOへ提案する。AIが勝手に登録・確定しない）
5. registry.jsonの登録・変更はCEO確認後のみ（AIはdraft提案まで）

## 5. 運用フロー

```
CEO/スタッフがシートを申告（or Connector接続時に発見）
  → AIがregistry項目のdraftを作成（19項目・不明はnull）
  → CEOが確認・確定（last_reviewed記入）
  → Sheets Connector（v1.1予定）が read_only で取込
  → 07_Data/spreadsheets/ へスナップショット保存 → index化 → Learning Cycleへ
```

## 変更履歴

| 日付 | 版 | 内容 |
|---|---|---|
| 2026-07-07 | v1.0 | 初版作成（Sprint 14.4・設計のみ。登録0件・Sheets Connector実装前の台帳設計） |
