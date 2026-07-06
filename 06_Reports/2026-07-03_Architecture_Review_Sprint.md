# Architecture Review Sprint — 設計レビュー結果

日付: 2026-07-03
種別: 設計レビューのみ（コード変更・ファイル移動は未実施）
状態: CEOレビュー待ち
担当: AI（レビュー実施）/ CEO（承認）

---

## 1. Decision Logの配置統一

### 現状
- `08_Decision_Log/`（ルート）: decision_log.json(20件)・insight_log.json(382件)の実データあり
- `01_Knowledge/08_Decision_Log/`: README.mdのみ（データなし、フォーマット未定義のTODO状態）

### 推奨案: `01_Knowledge/08_Decision_Log/` へ統一

**理由**
1. CEOの方針「Knowledgeの一部として管理」と一致する
2. 既存の01_Knowledge/README.mdの構成表がすでに08_Decision_LogをKnowledge配下として定義しており、当初設計への回帰である
3. Phase 9でAgentが参照するルートを`01_Knowledge/`の1か所に集約できる（Agent設計が単純になる）
4. 移行先にデータがまだ無いため、いま統一するのが最も低コスト

**期待効果**: 知識の一元管理、Agent参照設計の単純化、バックアップ・権限管理の単一化

**メリット・デメリット・互換性**

| 観点 | 内容 |
|---|---|
| メリット | 上記の通り。旧ルートフォルダの混乱が解消 |
| デメリット | Extractor 2本のLOG_DIR変更が必要。ルート`08_Decision_Log/`の扱い（99_Archiveへ移動）に事前確認が必要 |
| 互換性 | JSON構造は無変更。パスのみ変更 = フォルダ構成変更 → メジャーVersion更新（Decision Extractor v2.0 / Insight Extractor v2.0）とCHANGELOG記録が必要 |

**リスク**: 移行中に片方のパスを参照する不整合。→ 実装Sprintで「コピー→スクリプト修正→検証→旧フォルダを99_Archiveへ」の順で実施すれば回避可能（削除は行わない）

**実行手順（実装Sprint案・未実施）**
1. 実データを`01_Knowledge/08_Decision_Log/`へコピー
2. decision_extractor.py / insight_extractor.py のLOG_DIRを変更（v2.0）
3. 再実行して出力一致を検証
4. ルート`08_Decision_Log/`を99_Archiveへ移動（CEO事前確認のうえ）
5. CHANGELOG・ROADMAP・関連README更新

**優先順位: 高**（Phase 6の前提。データが増える前に実施すべき）

---

## 2. Knowledge昇格フローの設計

### 前提
AIはKnowledgeへ直接書き込まない。必ずCEOレビューを経て正式Knowledgeへ昇格する。

### 提案: 3状態 + 却下の状態管理

```
Knowledge Draft（AI生成）
   ↓ CEOレビュー依頼（レビューキュー）
CEO Review（レビュー中）
   ↓ 承認 / 却下
Knowledge Released（正式Knowledge）   Rejected(却下理由を記録)
```

**設計詳細**

1. **書き込み先の分離**: AIが生成する下書きは `01_Knowledge/_drafts/` のみに置く。正式Knowledge（各カテゴリフォルダ直下）へはCEO承認後にKnowledge Writerが移動する。「_drafts以外へのAI書き込み禁止」をルール化（02_Rules）
2. **状態はファイル内フロントマターで管理**:
   ```
   status: draft | in_review | released | rejected
   source: Conversation ID / decision_log等の出典
   created: 日付 / reviewed: 日付 / reviewer: CEO
   ```
3. **レビューキュー**: `06_Reports/knowledge_review_queue.md` にDraft一覧（重要度順）を自動生成。CEOは承認/却下/修正指示を書き込むだけでよい
4. **Agentの参照範囲**: `status: released` のみ（デフォルト）。Draftは参照しない
5. **却下も資産化**: Rejectedは理由つきで保存（AIの生成精度改善の学習データになる）

**リスク**: CEOレビューがボトルネック化（Draft大量発生時）。→ 重要度「高」のみ先行レビュー、閾値以下は保留、の運用ルールで緩和

**優先順位: 高**（Phase 6 Knowledge Builderの中核仕様）

---

## 3. Pattern Analysisの追加検討

### 結論: 追加を推奨。「Insight/Decision → Pattern → Lessons Learned → CEO Principles」の流れは適切

**理由**
1. Insight 382件は粒度が細かく、そのままLessons Learnedへ進むと単発の思いつきと反復された信念を区別できない
2. 「繰り返し出る」ことこそが福田恭平の本質的な考え方の証拠。頻度・期間の定量化はPattern層でしかできない
3. CEO Principlesは「反復検証済みのパターン」から生成すべきで、生のInsightから直接生成するより精度が上がる

**Pattern Analyzer v1.0 設計案（未実装）**
- 入力: insight_log.json + decision_log.json
- 処理: タイプ×ブランド×カテゴリでグループ化 → キーワード類似度で文をクラスタリング → 出現回数・出現期間・代表例を集計
- パターン認定基準: 異なる会話で3回以上出現（閾値は調整可能に）
- 出力: `pattern_log.json`（パターン名 / タイプ / 出現回数 / 初出〜最新日付 / 代表例3件 / 関連Insight ID）
- 抽出対象: 考え方 / 成功要因 / 失敗要因 / ブランド思想 / 経営判断の5系統

**注意点（データ品質）**: 現Insightは「職人との考え」160件が最多だが、その多くは顧客向けメール定型文由来。頻度だけで集約すると定型文がパターン上位を占めるリスクがある。→ Pattern Analyzerに「定型文らしさ」の減点（同一宛先向け・敬語密度等）を入れる、またはPattern結果もCEOレビュー対象とする

**優先順位: 中**（Phase 6と並行設計可能。ROADMAPへ「Phase 5.5」または Phase 7の前段として組み込む）

---

## 4. AI Agent設計レビュー

### 結論: Agent はKnowledge参照専用（読み取り専用）を正式ルールとすることを推奨

**参照設計**

1. **読み取り専用の徹底**: AgentはKnowledgeを書き換えない。Agentが得た新しい知見は「Insight Draft」として提出し、通常の昇格フロー（§2）を通す。これによりKnowledgeの品質はCEOレビューが常に担保する
2. **参照優先順位**（Agentの判断根拠の階層）:
   ```
   00_MASTER（CEO_PRINCIPLES / BUSINESS_PHILOSOPHY）
   → 02_Rules（行動ルール）
   → 01_Knowledge（status: releasedのみ）
   → 07_Data(実績データ)
   ```
3. **スコープ定義**: 各Agent定義ファイル（03_Agents）に参照するKnowledgeフォルダを明記する（例: 催事AI → 05_Events / 08_Decision_Log / 03_Customers）。全Agentが全Knowledgeを読む設計は精度と保守性を下げる
4. **出力先の限定**: Agentの成果物は06_Reports（レポート）と01_Knowledge/_drafts（知見の下書き）のみ
5. **フィードバックループ**: Agent提案の採用/却下をCEOが記録 → Decision Logに蓄積 → Pattern → Principlesが改善される循環を作る（Architecture v1.1に反映）

**リスク**: 参照専用にするとAgentの応答に最新情報が反映されにくい。→ 07_Data（実績データ）は常時最新を参照可とし、「解釈・思想」だけを昇格制にすることで両立

**優先順位: 中**（Phase 9の前提仕様として文書化のみ先行）

---

## 5. Architectureレビュー

### v1.0の評価

**不足している層**
1. **Pattern Analysis層**（§3の通り）
2. **CEO Review Gate**（人間の承認ゲートが図に存在しない。§2の通り）
3. **Data Source層の明示**: 現状はConversationのみだが、将来のShopify・Meta広告・Sheets・催事・発注データの入口が図にない
4. **フィードバックループ**: Agents→Insightへ戻る循環がない（一方通行のままだとAIが成長しない）

**構造上の問題**: v1.0は「Insight→Decision」と直列だが、実装上は両者ともConversation Indexから並列に抽出しており、図と実装が不一致。v1.1で並列表記に修正すべき

**将来ボトルネック**
1. CEOレビュー容量（最大の制約。重要度順キューで緩和 — §2）
2. 全件再走査方式: 現在3,349会話の全走査は数秒だが、データソース追加後は増分処理（前回処理済みIDのスキップ)が必要になる
3. ルールベース抽出の精度上限（成功要因2件・学び1件は明らかに取りこぼし。重要度「高」会話の意味解析による第2段階抽出が将来必要）
4. スクリプト間のimport連鎖（importer→decision→insight）。機能が増えると壊れやすい → 実装Sprintで共通モジュール化を検討

**保守性・拡張性・Version管理**: Development Standard v1.0の施行で基盤は整備済み。ArchitectureをROADMAP内でなく独立文書`00_MASTER/ARCHITECTURE.md`として管理することを追加提案（変更履歴を追いやすくする）

### Architecture v1.1 設計案（CEO承認後に採用）

```
【Data Sources】
 Conversation(ChatGPT) │ 将来: Shopify / Meta広告 / Sheets / メール / 催事 / 発注・在庫
        ↓ Import
【Index層】 Conversation Index (07_Data)
        ↓ Extract（並列）
【抽出層】 Insight ・ Decision
        ↓ 集約
【Pattern層】 Pattern Analysis（新設）
        ↓ 生成
【知見層】 Lessons Learned → CEO Principles（いずれもDraft）
        ↓
【承認ゲート】 CEO Review（新設・人間）
        ↓ 昇格
【Knowledge層】 Knowledge Released（AIは直接書き込み不可）
        ↓ 参照専用
【Agent層】 AI Agents
        ↓ 提案・レポート(06_Reports)
        └──→ 新Insight Draftとして抽出層へ戻る（フィードバックループ・新設）
```

v1.0からの変更点: Insight/Decisionの並列化、Pattern層追加、CEO Review Gate追加、Data Source層明示、フィードバックループ追加。

---

## 推奨実施順序（次の実装Sprint案）

| 順 | 項目 | 優先順位 | 備考 |
|---|---|---|---|
| 1 | Decision Log配置統一（§1） | 高 | Extractor v2.0化・CHANGELOG更新を含む |
| 2 | Architecture v1.1の正式採用 + ARCHITECTURE.md作成（§5） | 高 | ROADMAP・README同期更新 |
| 3 | Knowledge昇格フローのルール文書化（§2） | 高 | 02_Rulesへ。Knowledge Writer v1.0の仕様確定 |
| 4 | Pattern Analyzer v1.0（§3） | 中 | 定型文対策を仕様に含める |
| 5 | Agent参照ルールの文書化（§4） | 中 | 実装はPhase 9 |

本レビューはすべて設計のみであり、コード・既存ファイル・フォルダへの変更は行っていない。CEOレビュー後、承認された項目から実装Sprintを開始する。

---

# 追記（2026-07-03）: AI Memory Layer 設計

CEO承認済みの§1〜5に加え、実装Sprint前の追加設計としてAI Memory Layerを設計する。本追記も設計のみ（コード・フォルダ変更なし）。

## 6. AI Memory Layer

### 概念定義

| | Knowledge | AI Memory |
|---|---|---|
| 内容 | 会社の知識（ブランド・顧客・判断基準） | AIの作業記憶（開発状態・未完了・再開位置） |
| 性質 | 恒久的資産。蓄積し続ける | 現在状態のみ。常に上書き更新される |
| 書き込み | CEOレビュー必須（昇格フロー） | AIが直接更新可（レビュー不要） |
| 参照者 | AI Agents（判断の根拠） | AI自身（作業の継続）+ CEO（進捗確認） |
| 失われた場合 | 経営資産の損失 | ROADMAP/CHANGELOGから再構築可能 |

MemoryはKnowledgeを書き換えず、Knowledgeの内容を複製しない。Version状況等の一次情報はCHANGELOG/READMEにあり、Memoryは「現在どこにいるか」への参照だけを持つ（二重管理の防止）。

### 保存先の提案: `10_AI_Memory/`

```
10_AI_Memory/
├── README.md          目的・更新ルール
├── CURRENT_STATE.md   現在の状態（唯一の再開起点）
└── PENDING.md         保留事項・CEOレビュー待ち一覧
```

- 番号10とするのはKnowledge（01）と明確に分離し、パイプライン成果物（07/08）とも区別するため
- ファイルは最小2つに固定。Memoryが肥大化したら設計ミスとみなす（状態は常に要約可能なはず）
- 過去状態の履歴は保持しない（必要ならSprint終了時点のスナップショットを99_Archiveへ）

### CURRENT_STATE.md フォーマット案

```markdown
# CURRENT_STATE — AI作業記憶
最終更新: YYYY-MM-DD HH:MM（更新者: AI）

## 現在位置
- Phase: （例）Phase 6 Knowledge Builder
- Sprint: （例）実装Sprint #1「Decision Log配置統一」
- Sprint目標: 
- Architecture: v1.x

## 未完了Task
- [ ] （Taskと現在の進行状態）

## 保留事項
- （PENDING.mdの要約 + リンク）

## CEOレビュー待ち
- （文書名とリンク）

## 次回開始位置
- 次のセッションで最初に着手すべき作業を1〜3行で明記

## Version状況（参照のみ）
- 詳細は 00_MASTER/CHANGELOG.md を正とする
```

### 7. Architecture v1.2 のレビューと推奨図

CEO提示のv1.2候補は「Knowledge Released → AI Memory → AI Agents」と直列だが、AI MemoryはKnowledgeを変換する工程ではなく、**全工程の状態を横から保持する層**である。直列に置くと「MemoryがKnowledgeの下流成果物」と誤読され、Knowledgeとの分離原則と矛盾する。

**推奨: v1.2ではMemoryを並走レイヤーとして表記する**

```
【Data Sources】 Conversation │ 将来: Shopify / Meta広告 / Sheets / メール…
        ↓ Import                                    ┌─────────────────┐
【Index層】   Conversation Index (07_Data)           │  AI Memory      │
        ↓ Extract（並列）                            │  (10_AI_Memory) │
【抽出層】   Insight ・ Decision                     │                 │
        ↓ 集約                                      │ ・現在Sprint     │
【Pattern層】 Pattern Analysis                       │ ・未完了Task     │
        ↓ 生成                                      │ ・保留事項       │
【知見層】   Lessons Learned → CEO Principles        │ ・レビュー待ち    │
        ↓                                           │ ・次回開始位置    │
【承認ゲート】 CEO Review（人間）                     │                 │
        ↓ 昇格                                      │ 全層の進行状態を │
【Knowledge層】 Knowledge Released                   │ 保持（内容は     │
        ↓ 参照専用                                   │ 保持しない）     │
【Agent層】  AI Agents ──────────────────────────→ 参照（作業状態）
        └→ 提案(06_Reports) → Insight Draftへ還流    └─────────────────┘
```

- AI Agentsは **Knowledge（会社の知識）とMemory（作業状態)の両方を参照**するが、役割が異なる
- MemoryはKnowledge・Index・ログの内容を一切書き換えない（読み取り + 自フォルダのみ書き込み）
- CEO案の直列表記でも実運用は可能なため、表記の最終判断はCEOレビューに委ねる

### 8. Session Resume 設計

目的: 新しいチャットセッションでもAIが途中から開発を再開できること。

**再開プロトコル（セッション開始時にAIが実施）**
1. `10_AI_Memory/CURRENT_STATE.md` を読む（現在位置・次回開始位置）
2. `10_AI_Memory/PENDING.md` を読む（保留・レビュー待ち）
3. `00_MASTER/ROADMAP.md` と `CHANGELOG.md` で整合性を確認（Memoryが古い場合はROADMAP/CHANGELOGを正とし、Memoryを修正してから作業開始）
4. 「次回開始位置」から作業を再開し、CEOに現在地を1〜2行で報告する

**信頼順位**: CHANGELOG/ROADMAP（正） > Memory（作業用キャッシュ）。矛盾時は必ず正を優先する。

### 9. Memory更新ルール

**Sprint終了時に必ずセットで更新（Sprint Close 3点セット + README）**
1. Memory更新（CURRENT_STATE.md / PENDING.md）
2. ROADMAP更新
3. CHANGELOG更新（Version変更があった場合）

**Sprint途中でも即時更新するイベント**
- CEOの承認・却下・方針指示があったとき
- 作業がブロックされ保留になったとき
- セッションが長くなり中断の可能性があるとき（次回開始位置の更新）

このルールはDEVELOPMENT_STANDARD.md §8（Sprint開発）への追記事項として、実装Sprintで反映する（今回は未変更）。

---

## 推奨実施順序（改訂版・実装Sprint案）

| 順 | 項目 | 優先順位 | 備考 |
|---|---|---|---|
| 1 | AI Memory Layer構築（`10_AI_Memory/`作成 + 初期状態記入） | 高 | 最初に作ると以降のSprint進捗がすべて記録される |
| 2 | Decision Log配置統一（§1） | 高 | Extractor v2.0化・CHANGELOG更新を含む |
| 3 | Architecture v1.2の正式採用 + ARCHITECTURE.md作成（§5・§7） | 高 | v1.1を経ずv1.2を直接採用 |
| 4 | Knowledge昇格フローのルール文書化（§2） | 高 | 02_Rulesへ。Knowledge Writer v1.0の仕様確定 |
| 5 | Pattern Analyzer v1.0（§3） | 中 | 定型文対策を仕様に含める |
| 6 | Agent参照ルールの文書化（§4・§7） | 中 | Knowledge+Memoryの参照区分を含める |

追記分もCEOレビュー待ち。承認後、順序1から実装Sprintを開始する。

---

# 追記2（2026-07-03）: AI Operating System Core Architecture（5層構造）

CEO指示により、FUKUDA AI（NOMADO AI Operating System）の最上位アーキテクチャを以下の5層構造として定義する。本追記も設計のみ（コード変更なし・Version番号未変更）。CEOレビュー後に正式採用する。

## 10. Core Architecture — 5層構造

```
① Identity Layer      AIは誰か・何のために存在するか
        ↓ 規定する
② Principles Layer    AIがどのように判断するか
        ↓ 判断基準を与える
③ Knowledge Layer     会社の正式な知識資産（CEOレビュー済みのみ）
        ↓ 判断材料を与える          ④ Memory Layer（並走）
⑤ Agent Layer         実行するAI ←── AI自身の作業記憶
```

### ① Identity Layer — 存在定義

| 項目 | 内容 |
|---|---|
| 役割 | AIは誰か、何のために存在するかを定義する |
| 対象文書 | BUSINESS_PHILOSOPHY.md / PROJECT_VISION.md / AI_CHARTER.md（未作成・TODO） |
| 更新権限 | CEOのみ |
| 参照 | 全Layer・全Agentが暗黙の前提として参照 |

### ② Principles Layer — 判断定義

| 項目 | 内容 |
|---|---|
| 役割 | AIがどのように判断するかを定義する |
| 対象 | CEO_PRINCIPLES.md / Decision Rules（02_Rules配下・今後整備） |
| 更新権限 | CEO承認必須（CEO Principles GeneratorのDraftも昇格フロー経由） |
| 参照 | Agent Layerが判断時に必ず参照 |

### ③ Knowledge Layer — 知識資産

| 項目 | 内容 |
|---|---|
| 役割 | 会社の正式な知識資産。CEOレビュー済みのみ保存 |
| 対象 | 01_Knowledge（Draft → Review → Released の状態管理、本レビュー§2） |
| 更新権限 | Knowledge昇格フローのみ。AI直接書き込みは_draftsに限定 |
| 参照 | Agent LayerがReleasedのみ参照 |

### ④ Memory Layer — 作業記憶

| 項目 | 内容 |
|---|---|
| 役割 | AI自身の作業記憶。Knowledgeを複製しない |
| 保持内容 | 現在のSprint / 現在のPhase / 未完了Task / 保留事項 / 次回開始位置 のみ |
| 対象 | 10_AI_Memory/CURRENT_STATE.md / PENDING.md（本レビュー§6） |
| 更新権限 | AIが直接更新可（レビュー不要）。他Layerへの書き込み不可 |

### ⑤ Agent Layer — 実行

| 項目 | 内容 |
|---|---|
| 役割 | Knowledge と Memory を参照して実行するAI |
| 対象 | 03_Agents配下の各Agent（Phase 9） |
| 制約 | **Knowledgeを書き換えない**。Knowledge更新は昇格フローのみ。成果物は06_Reports / 01_Knowledge/_drafts に限定 |
| 参照 | ①②を判断の前提、③を判断材料、④を作業状態として参照 |

### 5層と既存パイプライン（v1.2）の関係

パイプライン（Import → Extract → Pattern → 知見 → 承認 → Knowledge）は、③Knowledge Layerへ知識を供給する**製造ライン**であり、5層構造はその成果物を含むシステム全体の**静的構造**である。両者は矛盾せず補完関係にある。

### 新機能追加時の必須記載事項

今後、新しい機能・Agent・スクリプトを追加する際は、設計文書とREADMEに以下を必ず明記する。

1. **どのLayerに属するか**（①〜⑤のいずれか。パイプライン工程の場合は「③への供給ライン」等）
2. **どのLayerを参照するか**
3. **どのLayerを更新するか**（更新権限の範囲内であること）

この3点が明記されていない機能追加は、Development Standard違反としてレビューで差し戻す。

### 実装Sprintへの影響

- 本5層構造は既存の推奨実施順序（改訂版）と整合しており、順序変更は不要
- AI_CHARTER.md（①の未作成文書）の作成を実装Sprint候補に追加する
- 正式採用時にARCHITECTURE.md（§5提案）へ5層構造とv1.2パイプラインの両方を記載し、Architecture Versionを更新する（採用まで現状維持）

---

# 追記3（2026-07-06）: 00_MASTER 最上位文書の再編設計

CEO指示により、AIが毎回読み込む最上位文書（00_MASTER）の構成と読込順序を定義する。本追記も設計のみ（コード変更・ファイル作成/移動なし・Version番号未変更）。CEOレビュー後に実装Sprintで反映する。

## 11. 00_MASTER 文書構成（設計）

```
00_MASTER/
├── 00_CONSTITUTION.md        会社・ブランド憲法
├── BUSINESS_PHILOSOPHY.md    会社とは
├── PROJECT_VISION.md         目標
├── IDENTITY.md               AIとは
├── CORE_PRINCIPLES.md        不変の経営判断
├── EVOLVING_PRINCIPLES.md    成長する経営判断
├── AI_CHARTER.md             AIの法律
├── DEVELOPMENT_STANDARD.md   開発標準
├── ROADMAP.md                開発計画
└── CHANGELOG.md              変更履歴
```

### 読込順序（AIがセッション開始時に必ずこの順で読む）

| 順 | 文書 | 役割 | Layer |
|---|---|---|---|
| 1 | 00_CONSTITUTION.md | 会社・ブランド憲法 | ① Identity |
| 2 | BUSINESS_PHILOSOPHY.md | 会社とは | ① Identity |
| 3 | PROJECT_VISION.md | 目標 | ① Identity |
| 4 | IDENTITY.md | AIとは | ① Identity |
| 5 | CORE_PRINCIPLES.md | 不変の経営判断 | ② Principles |
| 6 | EVOLVING_PRINCIPLES.md | 成長する経営判断 | ② Principles |
| 7 | AI_CHARTER.md | AIの法律 | ① Identity / ② Principles |
| 8 | DEVELOPMENT_STANDARD.md | 開発標準 | 運用 |
| 9 | ROADMAP.md | 開発計画 | 運用 |
| 10 | CHANGELOG.md | 変更履歴 | 運用 |

順序の設計意図: 「会社の存在（1〜3）→ AIの存在（4）→ 判断基準（5〜6）→ AIの制約（7）→ 運用ルール（8〜10）」。抽象度の高い順に読むことで、下位文書の解釈が常に上位文書に拘束される。矛盾時は番号の小さい文書を正とする。

### CEO_PRINCIPLES.md の役割分離（将来）

CEO_PRINCIPLES.md は CORE_PRINCIPLES.md / EVOLVING_PRINCIPLES.md の2文書へ分離する。

| | CORE_PRINCIPLES | EVOLVING_PRINCIPLES |
|---|---|---|
| 性質 | 不変。CEOが直接確定した判断基準 | 成長する。学習サイクルから生成される仮説段階の基準 |
| 更新権限 | CEOのみ | AIがDraft追記可（CEOレビュー前提） |
| Agent参照時の扱い | 絶対遵守 | 参考（COREと矛盾する場合はCOREを優先） |

**分離の理由 — 学習サイクルの実現（正式Architecture・CEO承認 2026-07-06）**

```
Conversation
   ↓
Insight
   ↓
Decision
   ↓
Pattern（同一思想・判断・学びが3回以上出現）
   ↓
Lesson
   ↓
EVOLVING_PRINCIPLES（仮説として蓄積）
   ↓
CEO Review（承認ゲート）
   ↓
CORE_PRINCIPLES（不変の基準へ昇格）
```

パイプラインv1.2の出口（Lessons → CEO Principles）を2段階化するもので、Knowledge昇格フロー（§2）と同じ「AI生成 → CEOレビュー → 正式化」の原則をPrinciples Layerにも適用する。②Principles Layerの構造が§2・§10と一貫する。

**Pattern層の定義（CEO決定）**: Patternは単なる件数集計ではなく、**意味的に同一の判断・思想・成功要因・失敗要因をグループ化する層**である。認定基準は「同一思想・判断・学びが異なる会話で3回以上出現」。この定義により、Pattern Analyzer（§3）は将来の重要コンポーネントとして位置づけられ、v1.0設計案のキーワード類似度クラスタリングは意味的グループ化の第一段階実装とし、将来的に意味解析ベースへ強化する。

**期待効果**: AIが学んだ判断基準を安全に蓄積できる（COREを汚染しない）／CEOレビュー対象がEVOLVINGの差分のみになりレビュー負荷が下がる／「反復検証済みか否か」が文書の所属で判別できる。

**リスク**: EVOLVINGが肥大化しノイズ化する → Pattern層の認定基準（3回以上出現）を通過したもののみEVOLVINGへ記載する運用で緩和。

### 既存ファイルの扱い（実装Sprint時の論点）

| 既存ファイル | 扱い |
|---|---|
| CEO_PRINCIPLES.md | CORE / EVOLVING へ分離後、99_Archiveへ（削除しない） |
| COMPANY_PROFILE.md | 存置・統合しない（CEO決定 2026-07-06）。00_CONSTITUTION＝会社の思想、COMPANY_PROFILE＝会社の事実情報で役割が異なる。会社概要・ブランド一覧・沿革・代表・事業内容・所在地など事実のみを管理する文書とする |
| NAMING_CONVENTION.md | DEVELOPMENT_STANDARD.md の下位文書として存置。毎回読込の対象外 |
| README.md | 00_MASTERの案内板として存置。読込順序の対象外 |
| 新規作成が必要 | 00_CONSTITUTION.md / IDENTITY.md / CORE_PRINCIPLES.md / EVOLVING_PRINCIPLES.md / AI_CHARTER.md |

AI_CHARTER.md は§10で「①の未作成文書」として既にSprint候補入りしており、本設計と整合する。

### 実行手順（実装Sprint案・未実施）

1. 00_CONSTITUTION.md / IDENTITY.md / AI_CHARTER.md をDraft作成（CEOレビュー）
2. CEO_PRINCIPLES.md を CORE / EVOLVING へ分離（現内容は全てCOREへ、EVOLVINGは空で開始）
3. COMPANY_PROFILE.md を事実情報のみの文書として整理（統合しない・存置）
4. README.md / Session Resumeプロトコル（§8）へ読込順序を反映
5. CHANGELOG記録・Version更新（フォルダ構成変更のためメジャー更新）

**優先順位: 高**（②Principles Layerの中核。ただしPhase 7 Lessons Learnedの完成前でも文書の器は先行作成可能）

---

# 追記4（2026-07-06）: CEOレビュー結果 — 追記3承認

追記3（00_MASTER再編設計）はCEOレビューにより**承認**された。修正指示は以下の2点（本追記で反映済み）。Version変更なし。

1. **COMPANY_PROFILE.md は存置・統合しない**: 00_CONSTITUTION＝会社の思想、COMPANY_PROFILE＝会社の事実情報（会社概要・ブランド一覧・沿革・代表・事業内容・所在地など）で役割が異なるため。
2. **学習サイクルを正式Architectureとして採用**: Conversation → Insight → Decision → Pattern → Lesson → EVOLVING_PRINCIPLES → CEO Review → CORE_PRINCIPLES。Pattern層は意味的グループ化の層（件数集計ではない）として正式にArchitectureへ追加。Pattern Analyzerは将来の重要コンポーネントとしてROADMAPへ登録。

ARCHITECTURE.md 正式作成時（実装Sprint順序3）には、5層構造・パイプラインv1.2に加えて本学習サイクルを記載すること。
