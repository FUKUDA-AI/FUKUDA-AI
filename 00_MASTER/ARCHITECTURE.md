# ARCHITECTURE — FUKUDA AI / NOMADO AI Operating System

Architecture Version: **v1.3**（2026-07-06 正式採用・CEO承認）
最終更新日: 2026-07-06
状態: Released

> 本書はシステム全体の正式Architectureを定める唯一の文書である。
> Architecture変更時は本書とCHANGELOGを必ず更新する（Development Standard §9の記載はv1.0時点のものであり、以後は本書を正とする）。

---

## 1. パイプライン（Architecture v1.3）

```
【Data Sources】 ChatGPT / Claude / Gemini / 会議 / Gmail / Calendar / Drive / Sheets / Shopify / MakeShop / はぴロジ / logiec / FLAM / Airレジ / Airペイ / Meta / 催事 / 発注・在庫 / 会計
        ↓ Connector Layer（認証・取得・生データ搬入。読み取り専用。**接続先は07_Data/datasets/のDataset Registryに登録済みのもののみ**・Sprint 14.5）
        ↓ Importer Layer（AI別・ソース別に分離。共通スキーマへ正規化・PIIフィルタ。**AI会話=ChatGPT/Claude/Geminiは共通ConversationRecordへ統一**）
                 （設計: 07_Data/CONNECTOR_ARCHITECTURE.md + DATA_SOURCE_DESIGN.md + datasets/DATASET_REGISTRY.md。外部データはKnowledge直行禁止）
        ↓ Import        （現行: chatgpt_importer.py v1.1＝Connector+Importer一体型。v2.0で分離）
【Index】        Conversation Index    （07_Data/chatgpt_index.json）
        ↓ Extract（並列）
【抽出層】       Insight ・ Decision   （Extractor v2.0 → 01_Knowledge/08_Decision_Log/）
        ↓ 集約
【Pattern】      Pattern Analysis      （pattern_analyzer.py v1.0 → pattern_log.json）
        ↓ 生成
【Lesson】       Lessons Learned       （lesson_generator.py v1.0 → lesson_log.json）
        ↓ 抽象化
【Principle】    Principle             （principle_generator.py v1.0 → principle_log.json）★v1.3新設
        ↓
【承認ゲート】   CEO Review            （人間。全昇格の唯一の関門）
        ↓ 登録
【Evolving】     EVOLVING_PRINCIPLES   （00_MASTER・現在有効な判断原則。EP-001〜008運用中 2026-07-06〜）
        ↓ 昇格（CEOのみ）
【Core】         CORE_PRINCIPLES       （00_MASTER・不変の判断基準）
        ↓
【Knowledge】    Knowledge Draft → CEO Review → Released → 実運用 → Verified（会社標準・CEOのみ昇格）
                 （01_Knowledge。AIは_draftsのみ書込可。Lifecycle: 02_Rules/KNOWLEDGE_PROMOTION_RULES.md §1）
        ↓ 参照専用
【Agent】        AI Agents             （03_Agents・Phase 9）
        └→ 提案・レポート(06_Reports) → 新Insight Draftとして抽出層へ還流（フィードバックループ）
```

### Principle層とは（v1.3新設）

Lessonは「この出来事から何を学んだか」であり、そのままCORE_PRINCIPLESへ昇格させるには抽象度が足りない。
Principleは、Lessonを**「どんな場面でも使える判断原則」**へ抽象化したものである。

| 例 | Lesson | Principle |
|---|---|---|
| 1 | 催事は前年売上だけで判断すると失敗する | 判断は前年実績だけでなく、今年の条件・環境・在庫・市場変化を含めて行う |
| 2 | 職人へお客様の手紙を共有した | お客様の想いは必ず作り手まで届ける |
| 3 | 歩みゆたかに | ブランドは売るものではなく、人の歩みを豊かにするために存在する |

昇格の詳細ルールは [../02_Rules/KNOWLEDGE_PROMOTION_RULES.md](../02_Rules/KNOWLEDGE_PROMOTION_RULES.md) を正とする。

## 2. AI Memory Layer（横断層）

AI Memory（`10_AI_Memory/`）は上記パイプラインの**工程ではなく**、全工程の進行状態を横から保持する**横断的な作業記憶**である。

| | Knowledge | AI Memory |
|---|---|---|
| 内容 | 会社の知識（恒久資産） | AIの作業状態（現在のみ） |
| 書き込み | CEOレビュー必須 | AIが直接更新可 |
| 失われた場合 | 経営資産の損失 | ROADMAP/CHANGELOGから再構築可能 |

MemoryはKnowledgeを**複製せず**、以下だけを保持する。

- 現在のPhase
- 現在のSprint
- 未完了Task
- 保留事項
- 次回開始位置

信頼順位: CHANGELOG / ROADMAP（正）> Memory（作業用キャッシュ）。

## 3. 5層構造（静的構造）

| 層 | 名称 | 対象 | 更新権限 |
|---|---|---|---|
| ① | Identity Layer | 00_CONSTITUTION / BUSINESS_PHILOSOPHY / PROJECT_VISION / IDENTITY / AI_CHARTER | CEOのみ |
| ② | Principles Layer | CORE_PRINCIPLES / EVOLVING_PRINCIPLES / 02_Rules | CEO承認必須（EVOLVINGへの仮説追記のみAI可） |
| ③ | Knowledge Layer | 01_Knowledge（draft → released）。構造は**Knowledge Information Architecture v1.0**（01_Knowledge/README.md: 11カテゴリ・KN-xxx ID・共通フォーマット・knowledge_index.json索引ファースト検索）に従う | 昇格フローのみ。AI直接書込は_drafts限定 |
| ④ | Memory Layer | 10_AI_Memory | AI直接更新可（他層への書込不可） |
| ⑤ | Agent Layer | 03_Agents | Released Knowledgeのみ参照。Knowledge書換禁止 |

パイプライン（§1）は③へ知識を供給する製造ライン、5層構造はその成果物を含む静的構造であり、両者は補完関係にある。

## 4. 新機能追加時の必須記載事項

新しい機能・Agent・スクリプトの設計文書とREADMEには以下を必ず明記する（未記載はレビューで差し戻し）。

1. どのLayerに属するか
2. どのLayerを参照するか
3. どのLayerを更新するか

## 5. Learning Cycle v2.0（設計済み・CEOレビュー待ち・未採用）

Decision Log起点の自動学習ルート（Decision Log → Insight → Pattern → Knowledge Draft → CEO Review → Released → Verified Candidate → Verified）を設計済み。詳細は [../09_Learning/LEARNING_CYCLE_V2.md](../09_Learning/LEARNING_CYCLE_V2.md)。Insight Generator v1.0 / Pattern Generator v1.0は先行実装済み。承認・実装時にArchitecture v1.4として正式採用する（それまで本書はv1.3のまま）。

### Result Layer（設計済み・CEOレビュー待ち・未採用）

判断の**結果**から学ぶ層: Decision → Action → Result（成功/失敗/継続観察・**判定はCEOのみ・AIは推測しない**）→ 結果つきInsight → 既存サイクルへ。Verified判定を「使われた」から「使われて効いた」へ深化させる。詳細は [../09_Learning/RESULT_LAYER_DESIGN.md](../09_Learning/RESULT_LAYER_DESIGN.md)。v1.4採用時にLearning Cycle v2.0と併せて正式化する。

## 6. SYSTEM_BOOT（起動ガイド=BIOS・v1.1設計 2026-07-07・Sprint 14.3/14.3.1）

起動時は [SYSTEM_BOOT.md](SYSTEM_BOOT.md) から読込を開始する。SYSTEM_BOOTは設計書ではなく、**「何を・どの順で・どのルールで読むか」だけを定義するBIOS**であり、Version情報を保持しない（**Version・Phase・Sprintの正本は 10_AI_Memory/CURRENT_STATE.md**）。

```
SYSTEM_BOOT → MASTER（必読10文書）→ Memory（CURRENT_STATE/NEXT/PENDINGのみ）
→ 必要Agent（1つ）→ 必要Knowledge（索引経由・released/verifiedのみ）→ 必要Data（該当indexのみ）→ Task開始
```

Task開始前の最終確認は [SYSTEM_BOOT_CHECKLIST.md](SYSTEM_BOOT_CHECKLIST.md)（運用チェック専用・10項目）。
**Current Mode（v1.2・Sprint 14.4）**: 作業モード6種（Review/Planning/Implementation/Operation/Analysis/Emergency）でModeごとに読込範囲をさらに絞る。Mode値の正本はCURRENT_STATE.md・Mode別読込ルールの正本はSYSTEM_BOOT.md。
目的はトークン消費の抑制と長期運用: **全ファイル読込禁止・Knowledge全文検索禁止・Agentごとに最小読込**。5層構造（§3）に対する読み方の規約であり、層の定義・更新権限は変えない。

## 7. Version履歴

| Version | 日付 | 内容 |
|---|---|---|
| v1.0 | 2026-07-03 | 直列パイプライン（Development Standard §9） |
| v1.2 | 2026-07-06 | Insight/Decision並列化・Pattern層・Lesson層・Evolving/Core分離・CEO Review Gate・Knowledge Draft/Released分離・フィードバックループ・AI Memory横断層・5層構造を正式採用（v1.1を経ず直接採用） |
| v1.3 | 2026-07-06 | **Principle層をLessonとCEO Reviewの間に新設**（Lessonの抽象化 → 判断原則化）。CEO ReviewをEvolvingの前に配置（Principle承認後にEVOLVING登録、Core昇格はCEOのみ） |
