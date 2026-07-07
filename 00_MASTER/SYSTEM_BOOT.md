# FUKUDA AI — SYSTEM_BOOT v1.1

**SYSTEM_BOOTは、FUKUDA AIが最初に読む「起動ガイド（BIOS）」である。**

SYSTEM_BOOT自身は設計書ではない。SYSTEM_BOOTの役割は、

- 何を読むか
- 何を読まないか
- どの順番で読むか
- どのルールで読むか

を決めることだけである。SYSTEM_BOOTだけ読んで終わるのではなく、
**SYSTEM_BOOT → MASTER → Memory → 必要Agent → 必要Knowledge → 必要Data → Task開始** という読込シーケンスを定義するBIOSとして機能する。

> **Version・Phase・Sprint・Current Modeは [../10_AI_Memory/CURRENT_STATE.md](../10_AI_Memory/CURRENT_STATE.md) を参照する。**
> SYSTEM_BOOTはVersion情報・現在のMode値を保持しない（正本はCURRENT_STATE.mdのみ）。本ファイルは読込ルールだけを管理し、ほとんど変更されない。本文変更はCEO承認後のみ。

---

## Repository Structure

```
00_MASTER/     最上位文書（思想・原則・開発標準）← 本ファイルはここ
01_Knowledge/  正式知識（knowledge_index.json経由のみ・08_Decision_Log含む）
02_Rules/      昇格ルール（KNOWLEDGE_PROMOTION_RULES）
03_Agents/     Agent定義書（必要なAgentだけ読む）
04_SOP/        標準手順書
06_Reports/    Brief・レビューキュー・レポート
07_Data/       Data Layer（事実のみ。fos/ events/ 等）
09_Learning/   Learning Cycle v2.0（insights/ patterns/ 設計書）
10_AI_Memory/  AI作業記憶（CURRENT_STATE / NEXT / PENDING）
FOS/           FOS-data.json（正本・読み取り専用）+ 運用ルール
*.py           Importer・Generator群（ルート直下）
```

## 読む順番（必ず読む・この順）

| 順 | 文書 |
|---|---|
| 1 | [AI_CHARTER.md](AI_CHARTER.md) |
| 2 | [BUSINESS_PHILOSOPHY.md](BUSINESS_PHILOSOPHY.md) |
| 3 | CEO_PRINCIPLES →（役割分離済み・実体は4と5を読む） |
| 4 | [CORE_PRINCIPLES.md](CORE_PRINCIPLES.md) |
| 5 | [EVOLVING_PRINCIPLES.md](EVOLVING_PRINCIPLES.md) |
| 6 | [ARCHITECTURE.md](ARCHITECTURE.md) |
| 7 | [../07_Data/DATA_SOURCE_DESIGN.md](../07_Data/DATA_SOURCE_DESIGN.md) |
| 8 | [../07_Data/CONNECTOR_ARCHITECTURE.md](../07_Data/CONNECTOR_ARCHITECTURE.md) |
| 9 | [../03_Agents/AGENT_DESIGN.md](../03_Agents/AGENT_DESIGN.md) |
| 10 | [../03_Agents/AGENT_COLLABORATION.md](../03_Agents/AGENT_COLLABORATION.md) |

上記以外の思想文書（00_CONSTITUTION / IDENTITY / COMPANY_PROFILE / PROJECT_VISION等）は、**判断の最終審（憲法第5条「歩みゆたかに」）やブランド・会社事実の確認が必要なTaskのときだけ読む**。矛盾時は00_MASTER/README.mdの読込順の小さい文書を正とする。

## Knowledge Rule

- Knowledgeは **knowledge_index.json 経由のみ**参照する（索引→必要なKN本文だけ開く）
- 使用できるのは **released / verified のみ。draftは禁止**
- Knowledge全文検索・全KNファイル読込は禁止

## Data Rule

- Data Layer（07_Data）は**事実のみ**。意味づけは禁止
- Knowledgeへ直接渡さない（必ずLearning Cycle経由）
- 各Dataはindex（07_Data/fos/index.json等）から読み、rawやsnapshotsは必要時のみ
- **外部Datasetは 07_Data/datasets/dataset_registry.json に登録済みのもののみ読む**（未登録は読まない・read_only・v1.3追加）

## Learning Rule

```
Decision → Action → Result → Insight → Pattern → Knowledge → Released → Verified
```

- AIは**Resultを推測しない**（成功/失敗/継続観察の判定はCEOのみ）
- **Evidence必須**（Evidenceのない昇格・生成は無効）

## Agent Rule

- **必要なAgentだけ読む。全部読まない**
- Morning Brief → CEO_ASSISTANT.md のみ
- 催事Task → 催事AI（Event Agent）のみ
- so u Task → so u Agent のみ
- Agent横断が必要なときだけ AGENT_COLLABORATION.md の該当シナリオを参照

## FOS Rule

- **FOS-data.json = 正本（Source of Truth）**。HTMLは表示専用（読まない）
- 読み取り専用。**AIは変更禁止**（完了化・削除・変更はCEO操作のみ）
- 運用ルール・Decision Metadataの正: [../FOS/README.md](../FOS/README.md)

## Memory Rule

- 読むのは **CURRENT_STATE / NEXT / PENDING のみ**（10_AI_Memory）
- 過去のBrief・レポート・ログ全部は読まない（必要な1件だけ開く）

## Mode別読込ルール（v1.2追加）

**Current Modeの値はCURRENT_STATE.mdで確認**し、Modeに応じて読込範囲をさらに絞る。

| Mode | 読むもの | 制約 |
|---|---|---|
| **Review** | 対象文書のみ | **書き込み禁止** |
| **Planning** | SYSTEM_BOOT・MASTER・Memory・対象設計書 | コード変更禁止 |
| **Implementation** | SYSTEM_BOOT・MASTER・Memory・対象設計書・対象コード・CHANGELOG・ROADMAP | 開発標準に従い実装・テスト・CHANGELOG更新可 |
| **Operation** | SYSTEM_BOOT・MASTER・Memory・CEO_ASSISTANT・FOS・knowledge_index・必要Knowledgeのみ | Brief/FOS/Decision Logの日常運用のみ |
| **Analysis** | SYSTEM_BOOT・MASTER・Memory・07_Data・該当index・必要なCSV/JSONのみ | 事実のみ・意味づけ禁止（Data Rule準拠） |
| **Emergency** | **CURRENT_STATEと対象ファイルのみ** | 最小限の読込で止血。復旧後に通常Modeへ |

## Token Rule

- **必要なものだけ読む。全ファイル読込禁止**
- Knowledge全文検索禁止（索引経由）
- Agentごとに最小読込
- 大きいファイル（decision_log.json等）は集計・該当部分のみ参照

## 禁止事項

1. 推測禁止（不足データは「不足」と明示しCEOへ確認）
2. Evidenceなし禁止
3. Knowledge自動昇格禁止（released化はCEOのみ）
4. Verified自動昇格禁止（CEOのみ）
5. FOS変更禁止
6. Decision Log書換禁止（Draft経由・確定はCEO承認後）
7. Result推測禁止

## 起動シーケンス

```
SYSTEM_BOOT（本ファイル）
  ↓
MASTER（読む順番の10文書）
  ↓
Memory（CURRENT_STATE / NEXT / PENDING）
  ↓
必要Agent（Taskに応じて1つ）
  ↓
必要Knowledge（索引→released/verifiedの該当KNのみ）
  ↓
必要Data（該当indexのみ）
  ↓
Task開始
```

Task開始前の最終確認は [SYSTEM_BOOT_CHECKLIST.md](SYSTEM_BOOT_CHECKLIST.md)（運用チェック専用）を使う。

## 変更履歴

| 日付 | 版 | 内容 |
|---|---|---|
| 2026-07-07 | v1.0 | 初版作成（Sprint 14.3・設計のみ。起動時最小読込によるトークン削減・長期運用化） |
| 2026-07-07 | v1.1 | BIOS化（Sprint 14.3.1・設計のみ。役割を「読込ルールの定義」に限定・「唯一読むファイル」表現を廃止・Version/Phase/Sprint情報をCURRENT_STATE.mdへ分離・CHECKLIST参照追加） |
| 2026-07-07 | v1.2 | Mode別読込ルール追加（Sprint 14.4・設計のみ。Review/Planning/Implementation/Operation/Analysis/Emergency。Mode値はCURRENT_STATE.mdが正本・SYSTEM_BOOTは持たない） |
| 2026-07-07 | v1.3 | Data RuleへDataset Registry参照を追加（Sprint 14.5・設計のみ。未登録Datasetは読まない） |
