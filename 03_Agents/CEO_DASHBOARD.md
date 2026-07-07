# CEO_DASHBOARD — CEO Dashboard v1.0（設計書）

Version: v1.0（Sprint 15.1設計 → **CEO承認 2026-07-07**）/ 実装: dashboard_generator.py v1.0（Sprint 15.2・§9のv1.1段階に相当・稼働中）
最終更新日: 2026-07-07
状態: Released（設計CEO承認済み。生成機能はExperimental・実運用検証中）
起動方法: `python3 fos_importer.py && python3 ceo_assistant.py`（Brief発行後）→ `python3 dashboard_generator.py` → 06_Reports/dashboard/YYYY-MM-DD.md（追記型）
Layer: ⑤Agent Layer（CEO補佐AIの表示面。参照: ①〜④+07_Data / 書込: なし=**読み取り専用**）
関連: [CEO_ASSISTANT.md](CEO_ASSISTANT.md) / [../06_Reports/CEO_MORNING_BRIEF_DESIGN.md](../06_Reports/CEO_MORNING_BRIEF_DESIGN.md) / [../07_Data/datasets/DATASET_REGISTRY.md](../07_Data/datasets/DATASET_REGISTRY.md) / [../07_Data/results/README.md](../07_Data/results/README.md)

> FUKUDA AIを「Morning Brief中心」から、CEOが毎朝最初に見る**経営コックピット**へ進化させる。
> **Morning BriefはCEO Dashboardの一部**になる。

---

## 0. 基本思想（CEOの朝の順番）

```
① 会社の状態を確認する      → Company Health / Today's Dashboard
② 今日判断することを決める  → Morning Brief（判断3件）
③ 過去判断の結果を確認する  → Result Review
```

この順番で経営する。Dashboardはこの3ステップを1枚で完結させる。

## 1. 画面構成（6セクション）

| # | セクション | 一言 | 生成元 |
|---|---|---|---|
| 1 | **Company Health** | 会社の健康を100点で | Dataset（将来自動） |
| 2 | **Today's Dashboard** | 今日の状況一覧 | Dataset |
| 3 | **Morning Brief** | 今日の判断（既存Brief統合） | FOS+Memory+Knowledge |
| 4 | **Result Review** | 過去判断の結果確認 | Result Recorder |
| 5 | **Dataset Status** | データ接続の状態 | Dataset Registry |
| 6 | **AI Learning Status** | 学習サイクルの状況 | Learning各ログ |

## 2. Company Health（100点満点）

| 構成 | 配点（v1.0案） | 見るもの | データ源 |
|---|---|---|---|
| 売上 | 20 | 目標/前年比の進捗 | Airレジ・Shopify・MakeShop |
| 利益 | 15 | 粗利率の維持（CORE第2条②） | FLAM・会計 |
| 現金 | 15 | 入金予定と残高の見通し（CORE第2条①） | Airペイ・会計 |
| 在庫 | 10 | 過剰/欠品の少なさ | FLAM・はぴロジ |
| 出荷 | 10 | 遅延ゼロか | はぴロジ・logiec |
| 未対応 | 10 | 人を待たせていないか（憲法） | FOS（waiting_person） |
| 期限 | 10 | 期限超過ゼロか | FOS（overdue） |
| Learning | 10 | 学習サイクルが回っているか | Learning Status（§7） |

- **将来的にはDatasetから自動計算**する。v1.0時点で接続済みなのはFOS系のみのため、**未接続項目はスコア対象外とし、接続済み項目だけで按分表示**（例:「Health 78/100（算定対象30点分）」）
- **AIは数値を推測して埋めない**。データが無い項目は「未接続」と表示する

## 3. Today's Dashboard（今日の状況一覧）

| 表示 | データ源 | 段階 |
|---|---|---|
| 本日の売上 / 催事売上 / EC売上 | Airレジ / Shopify / MakeShop | v2.0（接続後） |
| 受注件数 / 出荷件数 / 未出荷 | Shopify・FLAM / はぴロジ・logiec | v2.0 |
| 入金予定 | Airペイ・Shopify | v2.0 |
| スタッフ待ち | FOS（staffRequests・waiting_person） | **v1.1（接続済み）** |
| 期限超過 | FOS（overdue） | **v1.1（接続済み）** |
| 本日予定 | FOS（events）・Google Calendar | **v1.1（FOS分）** |

## 4. Morning Brief（Dashboard内へ統合）

既存のMorning Brief（CEO Assistant v1.3.1が生成）を**Dashboardのセクション3として表示**する。生成ロジック・ルールは変更しない（CEO_ASSISTANT.mdが正）。

表示順: **今日の判断3件 → 今日やらないこと → レビュー待ち → Decision Draft**
（Briefの「⏰結果確認待ち」セクションは§5 Result Reviewへ移す＝重複表示しない）

## 5. Result Review（Result Recorder接続）

生成元: `07_Data/results/index.json`（Result Recorder v1.0・稼働済み）

| 表示 | 内容 |
|---|---|
| 結果確認待ち | check_dueリスト（RES-xxxx・判断・確認予定日） |
| 期待結果 | expected_result（判断時の期待。未入力は「未入力」表示） |
| 実績 | actual_result / outcome（CEO記入） |
| 差分 | 期待 vs 実績の比較欄 |
| 判定 | **成功 / 失敗 / 継続観察 — CEOのみが記入**（AIは推測しない） |

## 6. Dataset Status（Dataset Registryから取得）

生成元: `07_Data/datasets/dataset_registry.json` + 各index.jsonの生成時刻

| 表示列 | 内容 |
|---|---|
| Dataset | FOS / Shopify / Airレジ / FLAM / はぴロジ / logiec / Meta / ChatGPT / Claude / Gemini / Google Sheets … |
| 状態 | **ACTIVE**（active+同期正常）/ **WARNING**（同期が更新頻度を超えて古い）/ **ERROR**（読込失敗）/ **未登録**（registryにない=読まない） |
| 最終同期日時 | 各Importerのindex.json `generated_at` |

- 状態判定は機械的ルールのみ（推測しない）: registry.status × 最終同期の経過時間 × 直近実行の成否

## 7. AI Learning Status（Learning Cycle状況）

生成元: decision_log / insight_draft_log / pattern_draft_log / knowledge_index ほか各ログ（読み取りのみ）

| 表示 | 内容 |
|---|---|
| 件数 | Decision / Insight / Pattern / Knowledge / Released / Verified の各件数 |
| 今日増えた件数 | 前日index比の差分（+n表示） |
| Evidence Score平均 | **将来（Evidence Scorer実装後）**。それまでは「Evidence付与率」（evidence有り件数/全件）で代替表示 |

## 8. 重要ルール

1. **Dashboardは読み取り専用。** AIはDashboardを起点にデータを書き換えない（CEO記入欄への記入はCEOのみ）
2. 生成の流れ: **Dataset → Morning Brief → Decision Log → Learning** の順に読み取って組み立てる（この4系統以外から作らない）
3. **DashboardからKnowledgeを作らない**（表示は表示。学びは必ずLearning Cycle経由）
4. データが無い項目は「未接続」「未入力」と表示し、**AIは推測して埋めない**
5. 書込が発生するのはCEOの判断・判定の記入だけであり、その反映は既存フロー（Decision Log Draft / Result Draft→CEO確認後確定）に従う

## 9. 実装段階（承認後）

| 段階 | 内容 |
|---|---|
| v1.1 | dashboard_generator.py — **接続済みデータのみ**（FOS・results・registry・knowledge_index・Learning各ログ）で§3の一部+§4〜7を1枚のmd生成（06_Reports/dashboard/YYYY-MM-DD.md・追記型・上書き禁止）。Morning Brief生成と同時実行 |
| v1.2 | Airレジ・Shopify接続後: Today's Dashboardの売上系・Health Score部分算定 |
| v2.0 | 全Dataset接続: Health Score 100点満点の完全自動計算・異常アラート |

## 変更履歴

| 日付 | 版 | 内容 |
|---|---|---|
| 2026-07-07 | v1.0 | 初版作成（Sprint 15.1・設計のみ。6セクション構成・Morning BriefのDashboard統合・読み取り専用原則） |
