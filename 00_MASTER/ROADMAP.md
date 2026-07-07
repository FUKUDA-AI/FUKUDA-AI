# ROADMAP.md — 開発ロードマップ

Version: v1.0
最終更新日: 2026-07-03

管理項目: Phase / 目的 / 現在の状態 / 次Sprint / 完了条件 / 依存関係

---

## Phase一覧

| Phase | 名称 | 状態 |
|---|---|---|
| 1 | Foundation | ✅ 完了 |
| 2 | ChatGPT Import System | ✅ 完了 |
| 3 | Conversation Index | ✅ 完了 |
| 4 | Insight Extraction | 🔶 Experimental運用中 |
| 5 | Decision Extraction | 🔶 Experimental運用中 |
| 5.5 | Pattern Analysis | 🔶 Experimental運用中（2026-07-06〜） |
| 6 | Knowledge Builder | ⬜ 未着手（次Phase） |
| 7 | Lessons Learned | 🔶 Experimental運用中（2026-07-06〜） |
| 8 | CEO Principles | ⬜ 未着手 |
| 9 | AI Agents | ⬜ 未着手 |
| 10 | NOMADO AI Operating System | ⬜ 未着手 |

---

## Phase詳細

### Phase 1: Foundation ✅
- **目的**: フォルダ構成・マスター文書・開発標準の整備
- **現在の状態**: 完了（Development Standard v1.0 施行）
- **完了条件**: フォルダ構成確定、DEVELOPMENT_STANDARD / CHANGELOG / ROADMAP / NAMING_CONVENTION / README整備
- **依存関係**: なし

### Phase 2: ChatGPT Import System ✅
- **目的**: ChatGPTエクスポートZIPの継続的取り込み
- **現在の状態**: ChatGPT Importer v1.1 [Released]
- **完了条件**: ZIP検出→展開→分類→Index生成が再実行可能 ✅
- **依存関係**: Phase 1

### Phase 3: Conversation Index ✅
- **目的**: 全会話のメタ情報化（カテゴリ・重要度・概要）
- **現在の状態**: Conversation Index v1.0 [Released]、3,323件
- **完了条件**: 07_Data/chatgpt_index.json 生成、統計出力 ✅
- **依存関係**: Phase 2

### Phase 4: Insight Extraction 🔶
- **目的**: 経営上の気付き・仮説・学び等9タイプの抽出
- **現在の状態**: Insight Extractor v1.0 [Experimental]、382件抽出済み
- **次Sprint**: 抽出精度の検証（CEOレビュー）、成功要因・学びタイプの抽出率改善
- **完了条件**: CEOレビューで精度承認 → Released昇格
- **依存関係**: Phase 3

### Phase 5: Decision Extraction 🔶
- **目的**: 経営判断のみの抽出・ログ化
- **現在の状態**: Decision Extractor v1.0 [Experimental]、20件抽出済み
- **次Sprint**: 抽出漏れの検証（重要度「高」会話の意味解析による第2段階抽出の検討）
- **完了条件**: CEOレビューで精度承認 → Released昇格
- **依存関係**: Phase 3

### Phase 5.5: Pattern Analysis 🔶
- **目的**: 意味的に同一の判断・思想・成功/失敗要因のグルーピング（学習サイクルのPattern層）
- **現在の状態**: Pattern Analyzer v1.0 [Experimental]、4件抽出（全件draft・CEOレビュー待ち）
- **次Sprint**: Pattern 4件のCEOレビュー、データ増加後の再実行、意味解析ベースへの強化
- **完了条件**: CEOレビューで精度承認 → Released昇格
- **依存関係**: Phase 4, 5

### Phase 6: Knowledge Builder ✅（初回サイクル完了）
- **目的**: 承認済みLesson等を 01_Knowledge へ構造化して転記
- **現在の状態**: **Released Knowledge 12件誕生（2026-07-06）**。Knowledge Builder v1.1（冪等性検証済み）。hold 1件（KN-SOP-0003・実運用で成熟後に昇格）
- **次Sprint**: 新規Lesson承認時の随時実行。KN-SOP-0003の実運用と成熟判断
- **Knowledge Lifecycle**: Draft→Released→**Verified（会社標準）**の三段階を設計済み（2026-07-06・02_Rules準拠）。Verified昇格はCEOのみ。初回昇格候補の提案は運用実績蓄積後（目安: 2027-01以降）
- **完了条件**: 転記・索引再生成が再実行可能 ✅、AgentがReleasedのみ索引経由で参照できる ✅（released 12件）
- **依存関係**: Knowledge IA v1.0（完了）、Phase 7のCEOレビュー結果（完了）

### Phase 7: Lessons Learned / Principle 🔶
- **目的**: 教訓（Lesson）の生成と、判断原則（Principle）への抽象化
- **現在の状態**: Lesson Generator v1.0 [Experimental]（23件・CEOレビュー済み: released 11 / rejected 11 / hold 1）、Principle Generator v1.0 [Experimental]（10件・全draft・CEOレビュー待ち）
- **次Sprint**: ~~Principleレビュー・EVOLVING登録~~ ✅完了（EP-001〜008運用開始・運用記録蓄積中）。**次回Principle Generator実行時にPRN-010改「経営判断は売上だけでなく、利益・ブランド価値・運営負荷・将来性を総合的に判断する」を再提案**（CEO指示 2026-07-06・Brief#2判断3）
- **完了条件**: CEOレビューで精度承認 → Released昇格
- **依存関係**: Phase 5.5（Pattern）。Phase 6（Knowledge Builder）とは並行可

### Phase 8: CEO Principles ⬜
- **目的**: Decision / Lessons から福田恭平の判断基準を体系化（CEO_PRINCIPLES.mdへ反映）
- **現在の状態**: 未着手
- **完了条件**: CEO Principles Generator v1.0 [Released]、CEO承認
- **依存関係**: Phase 7

### Phase 9: AI Agents 🔶
- **目的**: 専門AI（CEO補佐・so u・SUNNY NOMADO・催事・発注在庫・営業・広告SEO・資金繰り・商品企画・秘書）の構築
- **現在の状態**: Agent Design + Collaboration完成。**CEO補佐AI v1.0定義済み（2026-07-06・CEO_ASSISTANT.md・FUKUDA AI初の稼働Agent・Morning Brief専用）**
- **次Sprint**: ~~Morning Brief第1号~~ ✅発行済み。**CEO Assistant v1.1実装済み（ceo_assistant.py・2026-07-06）**。次: 催事AI・so u AIの定義、催事データ接続（v1.1）
- **完了条件**: 各Agent v1.0がKnowledgeを参照して提案（理由・期待効果・リスク・優先順位・実行手順つき）できる
- **依存関係**: Knowledge Draft 13件のreleased化（レビュー進行中）

### Phase 10: NOMADO AI Operating System ⬜
- **目的**: 全Agent・全データ（10ソース）の統合運用
- **現在の状態**: **Data Source Design v1.0 完成（2026-07-06・07_Data/DATA_SOURCE_DESIGN.md・CEOレビュー待ち）**。接続実装は未着手
- **接続段階**: v1.1（催事売上・Sheets・Shopify）→ v1.2（発注在庫・会計・Meta広告・Drive）→ v2.0（Gmail・Calendar・Instagram）
- **日次運用**: CEO Morning Brief設計完了（2026-07-06・06_Reports/CEO_MORNING_BRIEF_DESIGN.md）。v1.1は手動運用で即開始可能
- **Connector Architecture v1.0 設計完了（2026-07-06・07_Data/CONNECTOR_ARCHITECTURE.md）**: 全情報源をConnector→Importer→Learning Cycleへ統一。Importer実装順: 催事/Events → Claude → Sheets → Shopify（v1.1）→ Meta/Gemini/Meeting/Drive + ChatGPT v2.0（v1.2）→ Gmail/Calendar（v2.0）
- **Events Importer v1.0 [Experimental] 実装済み（2026-07-06・Sprint 8）**: 初のデータ接続稼働。次Sprint=催事データ投入（raw/へExcel/CSV投入→取込→KN-EVT-0001の定量検証）
- **Learning Cycle v2.0 設計完了（2026-07-06・Sprint 9・09_Learning/）**: Decision Log起点の自動学習+Verifiedまでの閉ループ。採用時にArchitecture v1.4
- **Insight Generator v1.0 [Experimental] 実装済み（2026-07-06・Sprint 10）**: 初回実行でInsight Draft 10件（CEO確定判断由来）
- **Pattern Generator v1.0 [Experimental] 実装済み（2026-07-06・Sprint 11）**: 初回0件（設計どおり・日次運用で自然に育つ）。残り: Review Queue自動化 → Knowledge Gen → Verified Candidate
- **Result Layer v1.0 設計完了（2026-07-06・Sprint 12・09_Learning/RESULT_LAYER_DESIGN.md）**: 判断の結果から学ぶ層（成功/失敗/継続観察=CEOのみ判定）。承認後の実装順: Result Recorder → 結果待ち抽出 → Brief結果確認欄（ceo_assistant v1.2）→ 実績照合 → Insight Gen v1.1
- **FOS を正式データソースへ追加（2026-07-06・CEO指示・接続優先順位0番=最優先）**: 日次運用ボード。**正本=FOS-data.json（Source of Truth・JSON正本化 2026-07-06 CEO決定）、FOS.htmlは表示用補助**。フロー: FOS-data.json→FOS Importer→TaskRecord→Morning Brief→Decision候補。読み取り専用・原本無変更・タスク操作はCEO確認後のみ。~~配置待ち~~ ✅ **FOS Connector v1.0稼働（2026-07-07・Sprint 13）**: TaskRecord 34件・Decision候補5件・期限切れ検知2件・CEO Assistant v1.2でBrief接続済み
- **Dashboard Generator v1.0 実装（2026-07-07・Sprint 15.2）**: CEO Dashboard初号発行（06_Reports/dashboard/2026-07-07.md）— Health 15/30（按分・未接続70点分対象外）・Brief第3号統合・Result確認待ち2件・Dataset 10件・Learning 6段階+増分。追記型・書込制限・決定的生成のテスト全合格。毎朝の型: fos_importer → ceo_assistant → dashboard_generator
- **CEO Dashboard v1.0 設計完了（2026-07-07・Sprint 15.1・設計のみ→CEO承認済み）**: 経営コックピット（03_Agents/CEO_DASHBOARD.md）— CEOの朝の順番（①状態確認→②今日の判断→③結果確認）を1枚化。6セクション（Company Health 100点/Today's Dashboard/Morning Brief統合/Result Review/Dataset Status/AI Learning Status）。読み取り専用・DashboardからKnowledgeを作らない。実装はdashboard_generator v1.1（接続済みデータのみ）→v2.0（全Dataset自動計算）
- **Result Recorder v1.0 実装（2026-07-07・Sprint 15）**: Result Layer初実装 — decision_log（読取専用）→trackable抽出→Action Record+Result Draft（判定はCEOのみ・Evidence必須・Metadata引き継ぎ）→07_Data/results/→Brief「結果確認待ち」接続（ceo_assistant v1.3.1）。Draft 2件（工場打ち合わせ/催事搬入=Result初号候補）。テスト全合格（冪等・書込制限・Brief統合）。残り: 実績データ照合（§9-4）・Insight Generator v1.1（§9-5）
- **Sprint 14.6 CEO承認（2026-07-07）**: 7件draftは設計登録として承認。実接続はsource_location・認証・エクスポート方法の確認後にactive化
- **Commerce/Logistics/POS Dataset Expansion v1.0 設計完了（2026-07-07・Sprint 14.6・設計のみ）**: Dataset RegistryへEC/物流/POS/決済系7ソースをdraft登録（Shopify/MakeShop/はぴロジ/logiec/FLAM/Airレジ/Airペイ・source_type 7種追加・record_schema 5種新設）。全て読み取り専用（注文・出荷・返金・決済・在庫変更の実行禁止）・sensitivity/pii原則high・Knowledge直行禁止。接続優先: Airレジ（催事とセット・v1.1）→ Shopify（v1.1）→ FLAM/はぴロジ/logiec/Airペイ/MakeShop（v1.2）
- **Sprint 14系 CEO一括承認（2026-07-07）**: FOS Operating Rule v1.0〜v1.2 / SYSTEM_BOOT v1.3 / CHECKLIST / Current Mode / Dataset Registry（DS 3件active化）/ AI Conversation Connectors → **全てReleased**。→ Implementation Modeへ移行し **FOS Importer v1.2 + CEO Assistant v1.3実装済み**（Metadata透過・並び順v1.2・結果確認待ちセクション・Draft5項目保存。テスト5/5合格）
- **FOS Operating Rule v1.0 設計完了（2026-07-07・Sprint 14・FOS/README.md）**: 入れるもの6種/入れないもの4種・FOS/PENDING分担・入力テンプレート9項目・Brief/Decision/Result送付条件・運用の1日。CEOレビュー後に入力習慣として運用開始
- **FOS Decision Metadata v1.1 設計完了（2026-07-07・Sprint 14.1・設計のみ）**: decision_needed（YES条件9/NO条件5・YES=Brief最優先）+ decision_type main/sub 2階層（13分類・main必須・sub任意null可）。FOS→Brief→Decision Log→Result→Knowledgeまで同一分類が一気通貫（分類別の判断傾向・成功率を後から集計可能）。既存FOS-data.json無変更（項目なし=null互換）。実装はfos_importer v1.1 / ceo_assistant v1.3として次Sprint
- **Dataset Registry + AI Conversation Connectors v1.0 設計完了（2026-07-07・Sprint 14.5・設計のみ）**: Spreadsheet Registryを07_Data/datasets/の**Dataset Registry（全データソース共通台帳・23項目・source_type 18種）**へ上位概念化（Google Sheets=Datasetの一種・旧spreadsheets/は互換保持）。**ChatGPT/GeminiをAI Conversation Sourceとして正式接続対象に** — ChatGPT/Claude/Gemini会話は共通**ConversationRecord（16項目）**へ正規化しLearning Cycleへ統合（そのままKnowledge化禁止: ConversationRecord→Insight→Decision→Pattern→Lesson→Knowledge Draft→CEO Review→Released）。稼働中3ソース（FOS/ChatGPT/催事）をdraft登録
- **Current Mode + Spreadsheet Registry v1.0 設計完了（2026-07-07・Sprint 14.4・設計のみ）**: ①作業モード6種（Review/Planning/Implementation/Operation/Analysis/Emergency）— Mode値の正本=CURRENT_STATE.md・Mode別読込ルール=SYSTEM_BOOT.md v1.2 ②スプレッドシート台帳（07_Data/spreadsheets/・19項目・未登録シートは読まない・read_only=true初期値・sensitivity high基準・Knowledge直行禁止）。Sheets Connector（v1.1）実装の前提
- **SYSTEM_BOOT v1.0→v1.1 設計完了（2026-07-07・Sprint 14.3/14.3.1・設計のみ）**: 起動ガイド=**BIOS**（00_MASTER/SYSTEM_BOOT.md）。「何を・どの順で・どのルールで読むか」だけを定義（設計書ではない・Version情報を保持しない）。必読10文書・Knowledge/Data/Learning/Agent/FOS/Memory/Token Rule・禁止事項7つ・読込シーケンス。**Version管理の正本は10_AI_Memory/CURRENT_STATE.mdへ分離**。Task開始前チェックはSYSTEM_BOOT_CHECKLIST.md（10項目・運用専用）。全ファイル読込禁止によるトークン削減=長期運用の土台
- **FOS Decision Metadata v1.2 設計完了（2026-07-07・Sprint 14.2・設計のみ・Result Layer接続の前提設計）**: decision_importance S/A/B/C（priority=急ぎ度と分離・S=Brief必載）+ expected_result（Result Recordでactual_resultと差分比較）+ review_after_days（初期値S30/A14/B7/Cなし・経過でBrief「結果確認待ち」へ自動掲載）。テンプレート14項目化。Brief並び順: 期限切れ→S→待ち人→A→期限3日→priority高。Result Recorder v1.0・Evidence Scorer・Verified昇格条件が本メタデータへ接続する前提
- **完了条件**: 経営の意思決定サイクルにAI OSが常時組み込まれている状態
- **依存関係**: Phase 9

---

## Architecture v1.3（正式・現行）

2026-07-06に正式採用。詳細は [ARCHITECTURE.md](ARCHITECTURE.md) を正とする（パイプラインv1.3・Principle層新設・AI Memory横断層・5層構造）。

---

## 設計方針（2026-07-03設計 → 2026-07-06までに大半を正式化済み）

2026-07-03のArchitecture Review Sprintで設計。詳細は [06_Reports/2026-07-03_Architecture_Review_Sprint.md](../06_Reports/2026-07-03_Architecture_Review_Sprint.md) を参照。

### AI Operating System Core Architecture（5層構造）

全Agent設計の土台。新機能追加時は「属するLayer / 参照するLayer / 更新するLayer」の明記を必須とする。

| 層 | 名称 | 役割 | 対象 |
|---|---|---|---|
| ① | Identity Layer | AIは誰か・存在目的 | BUSINESS_PHILOSOPHY / PROJECT_VISION / AI_CHARTER(未作成) |
| ② | Principles Layer | どのように判断するか | CEO_PRINCIPLES / Decision Rules |
| ③ | Knowledge Layer | 会社の正式知識（Draft→Review→Released） | 01_Knowledge |
| ④ | Memory Layer | AIの作業記憶（Sprint/Task/再開位置のみ） | 10_AI_Memory(未作成) |
| ⑤ | Agent Layer | 実行AI（Knowledge書き換え禁止・参照専用） | 03_Agents |

### パイプライン v1.2候補

Insight/Decision並列化、Pattern Analysis層・CEO Review Gate・AI Memory並走レイヤー・フィードバックループを追加した構成。

### 00_MASTER 最上位文書の再編（**2026-07-06 実施済み・文書はCEOレビュー待ちDraft**）

2026-07-06のSprintで、House of Hachiemon Brand Constitution・2025年会社案内・既存文書（PHILOSOPHY / VISION / PROFILE / Index / Insight / Decision Log）を統合し、全11文書を作成・更新した。読込順はCEO指示により以下へ確定（COMPANY_PROFILEを3番に追加、旧10文書案から更新）。読込順の正式な記載場所は 00_MASTER/README.md。

1. 00_CONSTITUTION.md（会社・ブランド憲法）
2. BUSINESS_PHILOSOPHY.md（経営哲学）
3. COMPANY_PROFILE.md（会社の事実情報）
4. PROJECT_VISION.md（FUKUDA AIの目的と未来像）
5. IDENTITY.md（AIとは何者か）
6. CORE_PRINCIPLES.md（不変の経営判断）
7. EVOLVING_PRINCIPLES.md（成長する経営判断）
8. AI_CHARTER.md（AIの法律）
9. DEVELOPMENT_STANDARD.md（開発標準）
10. ROADMAP.md（開発計画）
11. CHANGELOG.md（変更履歴）

CEO_PRINCIPLES.mdはCORE / EVOLVINGへ役割分離済み（旧文書のアーカイブはCEO確認後）。矛盾時は読込順の小さい文書を正とする。

### 学習サイクル（正式Architecture・2026-07-06 CEO承認）

```
Conversation → Insight → Decision
→ Pattern（同一思想・判断・学びが3回以上出現）
→ Lesson → EVOLVING_PRINCIPLES → CEO Review → CORE_PRINCIPLES
```

Pattern層は件数集計ではなく、**意味的に同一の判断・思想・成功要因・失敗要因をグループ化する層**。これを実装する**Pattern Analyzerは将来の重要コンポーネント**であり、Phase 7 Lessons Learned・Phase 8 CEO Principlesの前提となる（各Phaseの仕様に反映）。

### 実装Sprint予定順序

1. AI Memory Layer構築（10_AI_Memory）→ ✅ 2026-07-06実施（v1.0 [Released]）
2. Decision Log配置統一 → ✅ 2026-07-06完了（Extractor v2.0化・出力一致検証済み。ルート08_Decision_Logの99_Archive移動はCEO承認待ち）
3. Architecture v1.2正式採用 + ARCHITECTURE.md作成 → ✅ 2026-07-06完了
4. Knowledge昇格フロー文書化（02_Rules/KNOWLEDGE_PROMOTION_RULES.md）→ ✅ 2026-07-06完了
5. ~~00_MASTER再編（CONSTITUTION / IDENTITY / AI_CHARTER作成、CORE / EVOLVING分離）~~ ✅ 2026-07-06実施（CEOレビュー待ち）
6. ~~Pattern Analyzer v1.0（**重要コンポーネント**・意味的グループ化）~~ ✅ 2026-07-06実施（v1.0 [Experimental]・Pattern 4件・CEOレビュー待ち）
7. Agent参照ルール文書化
