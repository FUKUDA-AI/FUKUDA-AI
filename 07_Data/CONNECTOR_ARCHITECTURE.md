# CONNECTOR_ARCHITECTURE — Connector Architecture v1.0

Version: v1.0（設計のみ・実装なし）
最終更新日: 2026-07-06
状態: Released（CEO承認 2026-07-06・Morning Brief第1号・判断1）
関連文書: [DATA_SOURCE_DESIGN.md](DATA_SOURCE_DESIGN.md)（ソース別の取得範囲・優先順位）/ [../00_MASTER/ARCHITECTURE.md](../00_MASTER/ARCHITECTURE.md)

> 目的: ChatGPT / Claude / Gemini / Google Drive / Gmail / Calendar / Sheets / Shopify / Meta / 催事データ —
> **すべての情報源を「Connector → Importer → Learning Cycle」の一本の道に統一する。**
> どこから来た情報でも、同じ形に正規化され、同じ学習サイクルを通り、同じ昇格フローでしかKnowledgeにならない。

---

## 1. 4層の役割

```
【Connector Layer】 外の世界とつなぐ（認証・取得・生データ搬入）
        ↓ 生データ（無加工）を 07_Data/_inbox/<source>/ へ
【Importer Layer】  共通スキーマへ正規化（ソース別・AI別に分離）
        ↓ 正規化レコード + 索引を 07_Data/<domain>/ へ
【Data Layer】      事実の保管庫（07_Data。不変・出典つき・索引ファースト）
        ↓ Learning Cycle（Insight→Decision→Pattern→Lesson→Principle→CEO Review）
【Knowledge Layer】 意味づけされた学びの資産（01_Knowledge。昇格フロー経由のみ）
```

| 層 | 役割 | やらないこと |
|---|---|---|
| **Connector** | 認証・接続・差分取得・生データの搬入（読み取り専用）。接続状態の監視 | データの解釈・加工・削除。外部への書き込み（CEO確認なしの送信・変更は全面禁止） |
| **Importer** | 生データ→共通スキーマへの正規化・重複排除・個人情報フィルタ・索引生成 | 意味づけ（学びの抽出はLearning Cycleの仕事）。Knowledgeへの直接書き込み |
| **Data** | 正規化された事実の保管（不変）。取込日時・出典の記録。ドメイン別索引 | 事実の書き換え。解釈の混入 |
| **Knowledge** | CEOレビュー済みの学び・判断根拠（released）の保管 | 生データ・数値の保管（それはData層） |

**鉄則**: 層を飛ばさない。ConnectorからKnowledgeへ直行するデータは存在しない。

## 2. 共通レコードスキーマ（Importerの出力形式）

| スキーマ | 用途 | 主なフィールド |
|---|---|---|
| **ConversationRecord** | AI会話・会議・メールのやりとり | record_id / source（chatgpt/claude/gemini/meeting/gmail）/ title / created_at / participants / summary / category / importance / 原文参照 |
| **TransactionRecord** | 売上・注文・発注 | record_id / source / date / channel / brand / product / qty / amount / cost |
| **EventRecord** | 催事・予定 | record_id / source / venue / period / sales / expenses / notes |
| **MetricRecord** | 広告・EC指標 | record_id / source / date / campaign / spend / clicks / cv |
| **DocumentRecord** | 文書（Drive等） | record_id / source / title / doc_type / summary / 原本リンク |

- ConversationRecordは**どのAI由来でも同一形式** → Insight/Decision Extractorがsourceを問わず一括処理できる（Learning Cycleの入口の統一）
- 全レコード共通: `imported_at` / `importer_version` / `pii_filtered: true/false` を必ず持つ

## 3. Connector一覧

> **Dataset Registry（v1.0・Sprint 14.5）**: 全Connectorの接続先は事前に [datasets/DATASET_REGISTRY.md](datasets/DATASET_REGISTRY.md) へ登録する（未登録Datasetは読まない・read_only=true初期値）。
> **AI Conversation Source**: ChatGPT / Claude / Gemini の会話Importerは、入口は別・**出口は共通のConversationRecord（16項目・DATASET_REGISTRY.md §3）**に統一する。どのAIで話してもLearning Cycleへ統合される。そのままKnowledge化は禁止（ConversationRecord→Insight→Decision→Pattern→Lesson→Knowledge Draft→CEO Review→Released）。

| Connector | 接続先 | 方式（想定) | 段階 |
|---|---|---|---|
| ChatGPT Connector | ChatGPTエクスポートZIP | 手動エクスポート→_inbox投入 → **ConversationRecord正規化（v2.0）** | 稼働中（v1.1一体型） |
| Claude Connector | Claude Code / Cowork会話ログ | エクスポート→_inbox投入 → **ConversationRecord正規化** | v1.1 |
| Gemini Connector | Geminiエクスポート | 手動エクスポート→_inbox投入 → **ConversationRecord正規化** | v1.2 |
| Meeting Connector | 会議録音・議事メモ | 文字起こしファイル→_inbox投入 | v1.2 |
| Google（Drive/Gmail/Calendar/Sheets）Connector | Google API | OAuth読み取り専用。**Sheetsは接続前にSpreadsheet Registry登録必須（07_Data/spreadsheets/・v1.0設計 Sprint 14.4。未登録シートは読まない・read_only=true初期値）** | Sheets=v1.1 / Drive=v1.2 / Gmail・Calendar=v2.0 |
| Shopify Connector | Shopify API | APIキー読み取り専用 → OrderRecord | v1.1 |
| MakeShop Connector（14.6追加） | MakeShop CSVエクスポート | ファイル投入 読み取り専用 → OrderRecord | v1.2 |
| はぴロジConnector（14.6追加） | はぴロジ CSV/API | 読み取り専用 → ShipmentRecord | v1.2 |
| logiec Connector（14.6追加） | logiec連携データ | 読み取り専用 → ShipmentRecord | v1.2 |
| FLAM Connector（14.6追加） | FLAM CSVエクスポート | 読み取り専用 → InventoryRecord | v1.2 |
| Airレジ Connector（14.6追加） | Airレジ CSVエクスポート | 読み取り専用 → SalesRecord（催事Connectorと連携・events照合） | **v1.1（催事とセット）** |
| Airペイ Connector（14.6追加） | Airペイ CSVエクスポート | 読み取り専用 → PaymentRecord | v1.2 |
| Meta Connector | Meta Marketing API | OAuth読み取り専用 | v1.2 |
| 催事データConnector | 手元Excel/Sheets | ファイル投入 or Sheets経由 | **v1.1最優先** |
| **FOS Connector**（2026-07-06追加・JSON正本） | **FOS-data.json**（正本・Source of Truth）。FOS.htmlは表示用補助 | ローカルJSON読み取り専用 | **✅稼働中**（2026-07-07・fos_importer.py v1.0） |

## 4. Importer設計（AIごと・ソースごとに分離）

### 4-1. ChatGPT Importer（既存v1.1 → v2.0で本Architectureへ適合）
- 入力: ChatGPTエクスポートZIP / 出力: ConversationRecord + conversation_index
- 現状はConnector+Importer一体型。v2.0でConnector層と分離し共通スキーマへ移行（既存chatgpt_index.json 3,323件は互換変換）

### 4-2. Claude Importer（新規・v1.1）
- 入力: Claude Code / Cowork のセッションログ（**FUKUDA AI自身の開発対話も学習源になる**）
- 出力: ConversationRecord（source: claude）
- 特記: 開発指示とビジネス判断が混在するため、カテゴリ分類で「開発」「経営判断」を分離

### 4-3. Gemini Importer（新規・v1.2）
- 入力: Geminiエクスポート / 出力: ConversationRecord（source: gemini）
- 特記: ChatGPT Importerの分類ロジックを共通モジュール化して再利用

### 4-4. Meeting Importer（新規・v1.2）
- 入力: 会議の文字起こし・議事メモ / 出力: ConversationRecord（source: meeting, participants付き）
- 特記: 発言者の同意なく個人評価に使わない。社外参加者の発言は要注意フラグ

### 4-5. Gmail Importer（新規・v2.0）
- 入力: 限定ラベルのメール / 出力: ConversationRecord（要約のみ・本文非保存）
- 特記: **個人情報フィルタ最強設定**（DATA_SOURCE_DESIGN 1-4準拠。訃報等の繊細情報の匿名化必須）

### 4-6. Calendar Importer（新規・v2.0）
- 入力: 業務用カレンダー / 出力: EventRecord（催事日程のみ保存・他は都度参照）

### 4-7. Shopify Importer（新規・v1.1）
- 入力: Shopify API応答 / 出力: TransactionRecord（顧客は匿名化ID・氏名住所は取込前に除外）

### 4-8. Meta Importer（新規・v1.2）
- 入力: Meta広告レポート / 出力: MetricRecord（集計値のみ）

※ 催事データはSheets/Excel経由のため専用Importerは「Events Importer（v1.1）」として催事Connectorとセットで実装（EventRecord出力）。

### 4-9. FOS Importer（新規・v1.1・2026-07-06追加 / JSON正本化）
- 入力: **FOS-data.json（正本・Source of Truth。読み取り専用・原本を変更しない）**。FOS.htmlは表示用の補助データであり解析しない
- フロー: `FOS-data.json → FOS Importer → TaskRecord → Morning Brief → Decision候補`
- 出力: **TaskRecord**: record_id / title / status（今日やること・未完了・完了）/ sprint / pending_ref / due_date / priority / decision_candidate / brief_candidate / imported_at
- 保存先: 07_Data/fos/（スナップショット+正規化+索引）
- JSON正本の利点: Importer実装が単純・HTML解析不要・Brief反映が容易・将来API化しやすい（CEO決定理由）
- 特記: ①タスクの完了化・削除・変更はCEO確認後のみ（AIはFOSに書かない）②内容はKnowledge直行禁止（Data Layer→意味づけ後にLearning Cycle）③10_AI_Memory/PENDINGとの同期ルール（FOS=CEO操作面/PENDING=AI記録面）を実装時に定義 ④JSONスキーマは初回接続時にCEOと項目対応を確認してから実装（DATA_SOURCE_DESIGN §4準拠）

## 5. フォルダ構成（Data Layer）

```
07_Data/
├── _inbox/            Connectorの生データ搬入口（ソース別・処理済みは_processedへ）
├── conversations/     ConversationRecord + 統合索引（全AI・会議・メール横断）
├── transactions/      TransactionRecord（Shopify・卸）
├── events/            EventRecord（催事）
├── fos/               TaskRecord（FOS日次運用ボード。正本=FOS-data.json / HTML=補助・2026-07-06） 
├── metrics/           MetricRecord（広告・EC）
├── documents/         DocumentRecord索引（原本はDrive）
├── finance/           会計・資金繰り（アクセス限定）
└── chatgpt_index.json 既存索引（v2.0でconversations/へ統合予定・削除しない）
```

## 6. 運用ルール

1. Connectorは読み取り専用。外部への送信・変更・削除はCEO確認後のみ（AI_CHARTER準拠）
2. Importerは**冪等**（何度実行しても同じ結果。重複はrecord_idで排除）
3. 個人情報はImporter段階でフィルタし、`pii_filtered`を記録。フィルタ前の生データは_inboxに最小期間のみ保持
4. 各Connector/Importerは独立してVersion管理（例: Claude Importer v1.0 [Experimental]）。共通ロジックは共通モジュールへ（import連鎖の防止）
5. Learning Cycleは `07_Data/conversations/` の統合索引だけを見る（ソースが増えてもExtractorは変更不要）

## 7. 実装順（DATA_SOURCE_DESIGNの段階分けと同期）

| 段階 | 実装 |
|---|---|
| v1.1 | 催事Connector+Events Importer ✅ → **FOS Connector+Importer（2026-07-06追加・移設後即）** → Claude Importer → Sheets Connector → Shopify Connector+Importer |
| v1.2 | Meta / Gemini / Meeting / Drive の各Connector+Importer、ChatGPT Importer v2.0（共通スキーマ移行） |
| v2.0 | Gmail / Calendar（個人情報系・運用ルール成熟後） |

## 変更履歴

| 日付 | 版 | 内容 |
|---|---|---|
| 2026-07-06 | v1.0 | 初版作成（4層定義・共通スキーマ5種・Connector8種・Importer8種・運用ルール。設計のみ） |
| 2026-07-07 | v1.0追補（Sprint 14.6・設計のみ） | EC/物流/POS/決済系Connector 6種追加（MakeShop/はぴロジ/logiec/FLAM/Airレジ/Airペイ。全て読み取り専用・Dataset Registry登録必須）。出力スキーマにOrder/Shipment/Inventory/Sales/PaymentRecordを追加 |
