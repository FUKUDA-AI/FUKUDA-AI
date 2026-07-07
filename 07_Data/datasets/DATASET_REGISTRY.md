# DATASET_REGISTRY v1.0 — データセット台帳（全データソース共通）

Version: v1.0（Sprint 14.5・設計のみ）
最終更新日: 2026-07-07
状態: **Released（CEO一括承認 2026-07-07）** — DS-AI-0001 / DS-AI-0002 / DS-EVT-0001 をCEO確認によりactive化。**以後、未登録Datasetは読まない**（登録・変更はCEO確認後のみ・AIはdraft提案まで）
正本データ: [dataset_registry.json](dataset_registry.json)（本mdは説明書・人間用ビュー）
前身: [../spreadsheets/SPREADSHEET_REGISTRY.md](../spreadsheets/SPREADSHEET_REGISTRY.md)（Sprint 14.4・**Google SheetsはDatasetの一種として本台帳へ統合**。旧フォルダは互換のため保持・削除禁止）

> **目的**: FUKUDA AIが扱う**あらゆるデータソース**（Sheets・Excel・CSV・JSON・FOS・Shopify・Meta・AI会話…）を1つの台帳で管理する。
> どのデータが・どこにあり・誰のもので・どのConnector/Importerが・何に使ってよいかを登録してから読む。**未登録のDatasetは読まない。**

---

## 1. Registryの項目（23項目）

| 項目 | 内容 | 例 |
|---|---|---|
| dataset_id | 一意ID（DS-{domain略号}-{連番}） | DS-EVT-0001 |
| name | データセット名（人間が呼ぶ名前） | 催事売上管理表2026 |
| description | 何が入っているか1〜2行 | 催事ごとの売上・客数・経費 |
| source_type | §2の18候補から | google_sheets |
| source_location | 所在（SheetsID / パス / URL / DB名） | FOS/FOS-data.json |
| owner | 所有者・管理者 | CEO / スタッフ名 |
| data_domain | データ領域（催事/売上/在庫/発注/受注/顧客対応/商品/マーケティング/財務/法務/AI/その他） | 催事 |
| related_agent | 主担当Agent（CEO補佐/催事/発注・在庫/so u/SUNNY NOMADO/営業/広告・SEO/資金繰り/商品企画/秘書AI） | 催事AI |
| related_brand | 関連ブランド（自社/支援の区別を維持） | so u / 全社 |
| update_frequency | 更新頻度 | 日次 / 週次 / 催事ごと |
| data_sensitivity | low / mid / **high**（個人情報・顧客・契約・財務・原価はhigh） | high |
| pii_level | none / low / **high** | none |
| access_rule | 誰が読めるか | CEO+担当Agent |
| read_only | AIの読み取り専用か（**初期値: 必ずtrue**） | true |
| allowed_use | 使ってよい用途 | 催事実績の分析・Brief判断材料 |
| forbidden_use | 禁止用途（Knowledge直行は全Dataset共通で禁止） | 対外共有・個人特定 |
| connector_name | 担当Connector | FOS Connector |
| importer_name | 担当Importer | fos_importer.py |
| record_schema | 正規化先の共通スキーマ | TaskRecord / EventRecord / ConversationRecord |
| related_knowledge | 関連KN ID | KN-EVT-0001 |
| related_decision_type | 関連する判断分類（FOS 13分類） | 催事・イベント |
| last_reviewed | CEOが台帳内容を最後に確認した日 | 2026-07-07 |
| status | active / paused / archived / draft | draft |

## 2. source_type候補（24・Sprint 14.6で7種追加）

google_sheets / excel / csv / json / fos_json / **shopify / makeshop / hapilogi / logiec / flam / airregi / airpay**（14.6追加）/ meta_ads / gmail / google_calendar / notion / airtable / sqlite / postgresql / **chatgpt_export / claude_conversation / gemini_conversation / meeting_transcript** / other

## 2-1. Commerce / Logistics / POS拡張（v1.0・Sprint 14.6・7ソースdraft登録）

| Dataset | 取得したい情報 | 主担当Agent（他の利用Agent） | record_schema |
|---|---|---|---|
| **Shopify**（DS-SLS-0001） | EC注文・商品別売上・顧客情報・在庫・返品・決済状況・広告流入元 | CEO補佐AI（発注在庫/資金繰り/SUNNY NOMADO/so u） | OrderRecord |
| **MakeShop**（DS-SLS-0002） | 旧EC注文・商品別売上・顧客情報・過去実績・移行前データ | CEO補佐AI（同上） | OrderRecord |
| **はぴロジ**（DS-LOG-0001） | 出荷状況・在庫・入荷・返品・配送遅延・倉庫差異 | 発注・在庫AI（CEO補佐） | ShipmentRecord |
| **logiec**（DS-LOG-0002） | 物流連携データ・出荷指示・在庫連携・注文連携・エラー履歴 | 発注・在庫AI（CEO補佐） | ShipmentRecord |
| **FLAM**（DS-INV-0001） | 在庫・受注・発注・仕入・売上・商品マスタ・取引先 | 発注・在庫AI（CEO補佐） | InventoryRecord |
| **Airレジ**（DS-POS-0001） | 催事売上・店舗売上・商品別売上・日別売上・レジ実績・決済方法別売上 | 催事AI（CEO補佐/SUNNY NOMADO） | SalesRecord |
| **Airペイ**（DS-FIN-0001） | 決済実績・入金予定・決済手数料・カード/QR/電子マネー別売上・未入金/差異 | 資金繰りAI（CEO補佐） | PaymentRecord |

**Agent別の主用途**: CEO補佐AI=売上異常/在庫異常/入金予定/出荷遅延/利益低下/今日判断すべきこと。催事AI=Airレジ・催事別/商品別売上・次回催事判断。発注・在庫AI=FLAM/はぴロジ/logiec/Shopify/MakeShop。資金繰りAI=Airペイ・Shopify・MakeShop入金/売上予定/決済手数料。SUNNY NOMADO AI=Shopify/MakeShop/Airレジ/商品別売上。so u AI=Shopify/MakeShop/顧客対応/受注状況。

**EC・物流・POS・決済系の追加ルール（Sprint 14.6）**:
1. **最初はすべて読み取り専用。AIは注文・出荷・返金・決済・在庫変更を実行しない**（AI_CHARTER第1条）
2. 顧客情報・住所・電話番号・メール・決済情報を含むため **data_sensitivity=high / pii_level=high が原則**（参照はCEO確認後・個人特定禁止・PIIはImporterでフィルタ）
3. Knowledge直行禁止: `Dataset → Connector → Importer → Data Layer → Learning Cycle`

## 3. AI Conversation Source（ChatGPT / Claude / Gemini・v1.0新設）

ChatGPT・Gemini・Claudeの会話は**AI Conversation Source**として扱い、**すべて同じConversationRecord形式に正規化**する。どのAIで話しても、FUKUDA AIのLearning Cycleへ統合される。

```
ChatGPT Export        → ChatGPT Connector → ChatGPT Importer ┐
Claude Conversation   → Claude Connector  → Claude Importer  ├→ ConversationRecord → Learning Cycle
Gemini Conversation   → Gemini Connector  → Gemini Importer  ┘
```

### ConversationRecord共通項目（16）

| 項目 | 内容 |
|---|---|
| conversation_id | 一意ID（source_ai + 元ID） |
| source_ai | chatgpt / claude / gemini |
| title | 会話タイトル |
| created_at / updated_at | 会話の開始・最終更新日時 |
| participants | 参加者（CEO / スタッフ / AI名） |
| messages | 発言列（role + content。PIIフィルタ後） |
| summary | 会話の要約（Importerが機械生成・推測で断定しない） |
| decision_candidates | 判断らしき箇所の候補（確定はExtractor→CEO） |
| insight_candidates | 気付きらしき箇所の候補（同上） |
| related_project | 関連プロジェクト（不明はnull） |
| related_brand | 関連ブランド（不明はnull） |
| data_sensitivity | low / mid / high |
| pii_level | none / low / high |
| imported_at | 取込日時 |
| status | imported / processed / archived |

### AI会話の重要ルール

1. **AI会話はそのままKnowledgeにしない。** 必ず次の順に通す:
   `ConversationRecord → Insight → Decision → Pattern → Lesson → Knowledge Draft → CEO Review → Released`
2. **個人情報・顧客情報・契約・財務を含む会話は data_sensitivity=high / pii_level=high**
3. ChatGPT・Gemini・Claudeで形式を分けない（Importerの入口だけ別・出口は共通ConversationRecord）
4. 既存のchatgpt_index.json（3,323件）はChatGPT Importer v2.0でConversationRecordへ互換変換（削除しない）

## 4. Dataset Rule（AIの制約・Spreadsheet Ruleを継承）

1. **AIはDatasetを勝手に編集しない**（全Dataset read_only=true初期値。解禁はCEO承認のみ）
2. **未登録のDatasetは読まない**（発見したら登録draftをCEOへ提案。AIが勝手に確定しない）
3. **Knowledgeへ直行禁止**: `Dataset → Connector → Importer → Data Layer（07_Data）→ Learning Cycle`
4. sensitivity=high × pii=high はCEO確認後にのみ参照
5. registry.jsonの登録・変更はCEO確認後のみ（AIはdraft提案まで）

## 5. 運用フロー

```
CEO/スタッフがDatasetを申告（or Connector接続時に発見）
  → AIが23項目のdraftを作成（不明はnull）
  → CEOが確認・確定（last_reviewed記入・status: draft→active）
  → 担当Connectorが read_only で取込 → Importerが record_schema へ正規化
  → 07_Data/ へ保存・index化 → Learning Cycleへ
```

## 変更履歴

| 日付 | 版 | 内容 |
|---|---|---|
| 2026-07-07 | v1.0 | 初版作成（Sprint 14.5・設計のみ。Spreadsheet Registry v1.0を上位概念化・AI Conversation Source＝ConversationRecord共通形式を新設・稼働中3ソースをdraft登録） |
| 2026-07-07 | v1.0（CEO承認） | Sprint 14系一括承認・DS-AI-0001/0002・DS-EVT-0001 active化 |
| 2026-07-07 | v1.1相当（Sprint 14.6・設計のみ） | Commerce/Logistics/POS拡張 — source_type 7種追加（shopify/makeshop/hapilogi/logiec/flam/airregi/airpay）・7ソースdraft登録（全てread_only・sensitivity/pii原則high）・record_schema 5種追加（Order/Shipment/Inventory/Sales/PaymentRecord） |
