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
