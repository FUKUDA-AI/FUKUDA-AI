# CHANGELOG.md — 変更履歴

記録項目: Version / 日付 / 対象機能 / 変更内容 / 変更理由 / 互換性 / 担当

新しい変更を上に追記する。

---

## 2026-07-06（v1.0.0後・v1.1に向けて）

### Knowledge Review Sprint v1.0（レビューキュー作成）
- **対象機能**: 06_Reports/KNOWLEDGE_REVIEW_QUEUE.md（新規・文書のみ）
- **変更内容**: Knowledge/SOP Draft 13件にAI推奨（approve 12 / hold 1 / reject 0）・根拠EP/Lesson/Pattern・Evidence・反映先・CEO判断欄を付与したレビュー表を作成
- **変更理由**: Draft released化前のCEOレビュー運用（KNOWLEDGE_PROMOTION_RULES §4）
- **互換性**: 新規文書のみ。Released化・Draft移動は未実施（全13件draftのまま）
- **担当**: CEO（判断・これから）/ AI（キュー作成）

### Knowledge Builder v1.0 [Experimental]
- **対象機能**: knowledge_builder.py（新規）
- **変更内容**: CEO承認済み（released）Lesson 10件をKnowledge IA v1.0に従いKnowledge Draft 10件（01_Knowledge/_drafts/・KN-xxx形式・YAMLフロントマター13項目・Evidence必須）へ転記。SOP化候補3件を04_SOP/_drafts/へ生成（so u顧客対応・ODM見積対応・催事設営チェックリスト）。knowledge_index.json（13件）をフロントマタースキャンから自動生成
- **変更理由**: Phase 6実装（CEO指示Sprint）。※CEO指示は「11件」だがLSN-011のHold修正により対象は10件
- **互換性**: 新規ファイルのみ。Released Knowledge（カテゴリフォルダ直下）への書き込みなし。全Draftはstatus: draft / needs_ceo_review: true・Agent参照不可
- **担当**: CEO（承認方針）/ AI（実装）

# 🎂 NOMADO AI Operating System v1.0.0 [Released] — 2026-07-06

**この日をFUKUDA AIの誕生日として記録する。**
「会社の経営思想を学び続けるAI」の確かな出発点（CEO宣言）。今後はv1.1、v1.2…と育てていく。

- **Gitタグ**: `v1.0.0`（コミット f838519・タグメッセージに誕生日を記録）
- **v1.0.0に含まれるもの**:
  - 00_MASTER最上位文書群11文書（憲法 / 経営哲学 / 会社情報 / ビジョン / IDENTITY / CORE / EVOLVING / AI憲章 / 開発標準 / ROADMAP / CHANGELOG）
  - Architecture v1.3 — 学習サイクル: Conversation → Insight/Decision → Pattern → Lesson → Principle → CEO Review → EVOLVING → CORE（+ AI Memory横断層・5層構造）
  - パイプライン実装: ChatGPT Importer v1.1 / Conversation Index v1.0 / Insight・Decision Extractor v2.0 / Pattern Analyzer v1.0 / Lesson Generator v1.0 / Principle Generator v1.0
  - **EVOLVING_PRINCIPLES EP-001〜008**（CEO承認済み・運用中）— 学習サイクルの初回一巡の成果
  - Knowledge昇格ルール v1.0 / Knowledge Information Architecture v1.0 / AI Memory Layer v1.0
- **Git管理外**: 01_Knowledge/09_ChatGPT_Archive（1.8GBの生データ。正本はフォルダ内に存置）
- **次**: v1.1に向けてKnowledge Builder v1.0（Phase 6）から

---

## 2026-07-06

### Knowledge Information Architecture v1.0 [Released]
- **対象機能**: 01_Knowledge/README.md（全面改訂）/ ARCHITECTURE.md / ROADMAP.md
- **変更内容**: 数千件対応のKnowledge構造を設計 — ①索引ファースト検索（knowledge_index.json → 本文の2段階参照）②11カテゴリ（ブランド/商品/催事/営業/マーケティング/製造/顧客対応/財務/法務/AI/SOP）と物理フォルダ対応 ③ID体系 KN-<カテゴリ>-<連番> ④共通フォーマット13項目（YAMLフロントマター）⑤学習サイクルとの双方向リンク（Related Principle/Lesson/Pattern）⑥Evidence必須
- **変更理由**: Knowledge Builder v1.0実装前の構造正式化（CEO指示）
- **互換性**: 既存フォルダは変更なし。10_Sales / 11_Legal / 12_AI / _drafts はBuilder初回実行時に新規作成
- **担当**: CEO（方針）/ AI（設計）

### EVOLVING登録Sprint v1.0（EVOLVING_PRINCIPLES v0.2）
- **対象機能**: 00_MASTER/EVOLVING_PRINCIPLES.md / principle_log.json / ARCHITECTURE.md
- **変更内容**: CEO承認済みPrinciple 8件（PRN-001〜008）をEP-001〜008としてEVOLVING_PRINCIPLES.mdへ登録（Status: active・各EPに根拠Principle/Lesson/Pattern・採用日・CORE昇格候補・昇格条件・運用記録欄を付与）。学習サイクル図をv1.3へ更新。principle_logへEP対応（registered_as）を記録。Hold 2件（PRN-009継続観察・PRN-010再整理待ち）は登録せず本文書のHold欄で管理
- **変更理由**: CEO Review承認結果の正式反映（CEO指示Sprint）
- **互換性**: EPは「現在有効な判断原則」だがCOREではない。CORE昇格は継続運用+複数ブランド有効性確認+CEO承認のみ（AIは昇格不可）
- **担当**: CEO（承認）/ AI（登録）

### COMPANY_PROFILE ブランド分類の修正（Version変更なし）
- **対象機能**: 00_MASTER/COMPANY_PROFILE.md
- **変更内容**: ブランド・プロジェクトを「3-A 自社ブランド（SUNNY NOMADO / so u / Dr.Nomado®ほか）」と「3-B ブランド支援・共同プロジェクト（クライアントブランド・共同開発・ロゴデザイン・ブランディング・商品企画・ODM/OEM等）」の2分類へ修正。MIRAI UPはブランド所有者=株式会社ベルタ、NOMADOはブランド設計・ロゴデザイン・商品企画の支援として明記。「AIはブランド所有者・支援会社・共同プロジェクトを混同しない」を追記
- **担当**: CEO（指示）/ AI（修正）

### Principle Review結果の反映（status更新・Version変更なし）
- **対象機能**: principle_log.json / PRINCIPLE_REVIEW_QUEUE.md / principle_generator.py（コメントのみ）
- **変更内容**: CEO判断を反映 — PRN-001〜008: released（Approve）/ PRN-009: in_review（継続観察: 複数ブランドでの反復確認後に「最終品質は数値+職人の経験・感性・実物確認」として成長させる）/ PRN-010: in_review（「経営判断は売上だけでなく利益・ブランド価値・運営負荷・将来性を総合判断」へ再整理し再提案）。Generator改善ルール3項（普遍性・反復実績・事実≠原則）をprinciple_generator.py docstringへ追記
- **変更理由**: CEOレビュー結果（KNOWLEDGE_PROMOTION_RULES §4の即時反映）
- **互換性**: statusとコメントのみ。EVOLVING_PRINCIPLESへの登録は未実施（次Sprint）
- **担当**: CEO（判断）/ AI（反映）

### Principle Review Sprint v1.0（レビューキュー作成）
- **対象機能**: 06_Reports/PRINCIPLE_REVIEW_QUEUE.md（新規・文書のみ）
- **変更内容**: Principle 10件にAI推奨（approve 8 / hold 1 / reject 1）・推奨理由・根拠Lesson/Pattern・反映先候補・CEO判断欄を付与したレビュー表を作成。「事実だけでは原則にならない」基準を明記
- **変更理由**: Principle層のCEOレビュー運用（KNOWLEDGE_PROMOTION_RULES §4）
- **互換性**: 新規文書のみ。EVOLVING / CORE / Knowledgeへの反映なし・全件draftのまま
- **担当**: CEO（判断・これから）/ AI（キュー作成）

### CEO Review修正: LSN-011 Approve→Hold
- **対象機能**: lesson_log.json / principle_log.json
- **変更内容**: LSN-011（作業スペース費用）をreleased→in_reviewへ変更（CEO修正指示）。理由:「事実だけでは会社の原則にならない」。根拠にしていたPRN-010へnoteを付与（採否はPrincipleレビューで判断）
- **変更理由**: AIの確認質問に対するCEO回答
- **互換性**: statusとnoteのみ変更
- **担当**: CEO（判断）/ AI（反映）

### CEO Review結果の反映（status更新）
- **対象機能**: 01_Knowledge/08_Decision_Log/pattern_log.json / lesson_log.json
- **変更内容**: CEO記入済みレビューキュー（docx）に基づき、27件のstatusを更新（released 14 / rejected 11・理由つき / in_review 2）。reviewed・reviewer・rejected_reason / hold_reasonを付与
- **変更理由**: KNOWLEDGE_PROMOTION_RULES §4「CEOの承認・却下があったとき、AIは即時に対象ファイルの状態を更新する」
- **互換性**: statusフィールドのみ更新。本文・構造は無変更（更新前バックアップ取得済み）
- **担当**: CEO（判断）/ AI（反映）

### Principle Generator v1.0 [Experimental]
- **対象機能**: principle_generator.py（新規）
- **変更内容**: CEO承認済みLesson（released 11件 + hold 1件のCEO再整理方針）から、再利用可能な判断原則10件を抽象化生成し 01_Knowledge/08_Decision_Log/principle_log.json へ出力。全件 status: draft / needs_ceo_review: true。抽象化はキュレーションルール方式（CEOレビュー結果・CEOコメントを反映）+ 未定義Lesson用フォールバック
- **変更理由**: Architecture v1.3のPrinciple層実装（CEO指示Sprint）
- **互換性**: 新規ファイルのみ。rejectedのLessonからは生成しない
- **担当**: CEO（仕様・レビュー）/ AI（実装）

### Architecture v1.3 [Released]
- **対象機能**: 00_MASTER/ARCHITECTURE.md
- **変更内容**: Principle層をLessonとCEO Reviewの間に新設。CEO ReviewをEvolvingの前に配置（Lesson→Principle→CEO Review→Evolving→Core）。Principle層の定義とLesson→Principle抽象化例3件を記載
- **変更理由**: Lessonは「出来事からの学び」であり、CORE昇格には「どんな場面でも使える判断原則」への抽象化が必要（CEOレビューでの気付き）
- **互換性**: v1.2からの追加のみ。既存層の変更なし
- **担当**: CEO（設計）/ AI（文書化）

### CEO Review Sprint v1.0（レビューキュー作成）
- **対象機能**: 06_Reports/CEO_REVIEW_QUEUE.md（新規・文書のみ）
- **変更内容**: Pattern 4件 + Lesson 23件（計27件）にAI推奨（approve 13 / reject 11 / hold 3）と推奨理由・反映先候補・CEO判断欄を付与したレビュー表を作成。優先TOP10を先頭に配置
- **変更理由**: CEOレビューの効率化（KNOWLEDGE_PROMOTION_RULES §4のレビュー運用）。AIは承認せず、全27件はdraftのまま
- **互換性**: 新規文書のみ。pattern_log / lesson_log / Principles / Knowledgeへの変更なし
- **担当**: CEO（判断・これから）/ AI（キュー作成）

### Lesson Generator v1.0 [Experimental]
- **対象機能**: lesson_generator.py（新規）
- **変更内容**: Pattern（4件）+ Insight（成功要因/失敗要因/学び/改善案・重要度中以上・ノイズ除去/近接統合後）+ 判断理由つきDecisionから、再利用可能な形に抽象化したLesson 23件を生成し 01_Knowledge/08_Decision_Log/lesson_log.json へ出力。全件 status: draft / needs_ceo_review: true・必須18項目つき
- **変更理由**: Architecture v1.2のLesson層実装（CEO指示Sprint）。KNOWLEDGE_PROMOTION_RULES.md準拠
- **互換性**: 新規ファイルのみ。既存に影響なし。pattern_analyzer.pyの正規化・類似度関数を再利用
- **担当**: CEO（仕様）/ AI（実装）

### Decision Extractor v2.0 / Insight Extractor v2.0 [Experimental]
- **対象機能**: decision_extractor.py / insight_extractor.py
- **変更内容**: 出力先（LOG_DIR）をルート08_Decision_Log/から正式保存先 01_Knowledge/08_Decision_Log/ へ変更。抽出ロジックは無変更
- **変更理由**: CEO決定「正式なDecision/Insight/Patternの保存先は01_Knowledge/08_Decision_Log/」の完全実施
- **互換性**: フォルダ構成変更のためメジャー更新。--rebuild再実行で出力一致を検証済み（decision 20件・insight 382件・内容完全一致）。ルート08_Decision_Log/は不使用（データ存置・99_Archive移動はCEO承認待ちの提案）
- **担当**: CEO（決定）/ AI（実装・検証）

### Architecture v1.2 [Released]
- **対象機能**: 00_MASTER/ARCHITECTURE.md（新規）
- **変更内容**: Architecture v1.2を正式採用。パイプライン（Data Sources → Import → Index → Insight/Decision → Pattern → Lesson → Evolving → CEO Review → Core → Knowledge Draft → Released → AI Agents）、AI Memory横断層、5層構造、新機能追加時の必須記載3点を1文書に集約
- **変更理由**: CEO承認済み設計（2026-07-03 Architecture Review + 2026-07-06学習サイクル承認）の正式化
- **互換性**: Development Standard §9のv1.0記載は本文書が上書きする（以後ARCHITECTURE.mdを正とする）
- **担当**: CEO（承認）/ AI（文書化）

### Knowledge昇格ルール v1.0 [Released]
- **対象機能**: 02_Rules/KNOWLEDGE_PROMOTION_RULES.md（新規）
- **変更内容**: draft → in_review → released / rejected の状態管理、AI書き込み先の限定（_drafts / 06_Reports）、CEO Review唯一の承認ゲート、Rejected資産化、AgentのReleased限定参照、Draft不使用の7原則を文書化
- **変更理由**: Lesson Generator実装前に昇格ルールを正式化するため（CEO指示Sprint）
- **互換性**: 新規文書のみ
- **担当**: CEO（方針）/ AI（文書化）

### AI Memory Layer v1.0 [Released]
- **対象機能**: 10_AI_Memory/（新規フォルダ）
- **変更内容**: CURRENT_STATE.md（現在Phase・Sprint・Version・実装済み機能・次作業）/ NEXT.md（次Sprint）/ PENDING.md（CEOレビュー待ち・保留）/ README.md を新規作成。Session Start Protocol（00_MASTER → AI Memory → Knowledge → Task）を定義
- **変更理由**: 新しいセッションでもFUKUDA AIが前回の状態から再開できるようにするため（CEO指示Sprint）
- **互換性**: 新規フォルダのみ。MemoryはKnowledgeを複製せず作業状態のみ保持。信頼順位はCHANGELOG/ROADMAP（正）> Memory
- **担当**: CEO（仕様）/ AI（実装）

### Pattern Analyzer v1.0 [Experimental]
- **対象機能**: pattern_analyzer.py（新規）
- **変更内容**: Insight/Decision Logから意味的グルーピング（文字n-gram TF-IDF + コサイン類似度、しきい値0.35、定型文減点あり）で「異なる会話で3回以上出現」のPatternを抽出し、01_Knowledge/08_Decision_Log/pattern_log.json へ出力（4件・全件status: draft / needs_ceo_review: true）
- **変更理由**: 学習サイクル（Insight/Decision → Pattern → Lesson → EVOLVING → CEO Review → CORE）のPattern層実装（CEO指示Sprint）
- **互換性**: 新規ファイルのみ。既存に影響なし
- **担当**: CEO（仕様）/ AI（実装）

### Decision Log 正式保存先の移行（コピー）
- **対象機能**: 01_Knowledge/08_Decision_Log/
- **変更内容**: insight_log.json / decision_log.json をルート08_Decision_Log/から正式保存先へコピー（削除なし）。両READMEに新旧の位置づけを明記
- **変更理由**: CEO決定「正式なDecision/Insight/Patternの保存先は01_Knowledge/08_Decision_Log/」
- **互換性**: Extractor 2本は現在もルートへ出力する（v2.0での出力先変更は未実施・要Sprint）。当面は再実行後に手動コピーが必要
- **担当**: CEO（決定）/ AI（実施）

### 00_MASTER 最上位文書群 v0.x [Draft・CEOレビュー待ち]
- **対象機能**: 00_MASTER（文書のみ・コード変更なし）
- **変更内容**: 新規作成 — 00_CONSTITUTION.md v0.2 / IDENTITY.md v0.1 / CORE_PRINCIPLES.md v0.2 / EVOLVING_PRINCIPLES.md v0.1 / AI_CHARTER.md v0.1。更新 — BUSINESS_PHILOSOPHY.md v0.2 / PROJECT_VISION.md v0.2 / COMPANY_PROFILE.md v0.3 / README.md（読込順11文書を定義）
- **変更理由**: House of Hachiemon Brand Constitutionと2025年会社案内を既存文書・ログと統合し、FUKUDA AIの人格・思想・判断基準を確立するため（CEO指示Sprint）
- **互換性**: 既存ファイルの削除なし。CEO_PRINCIPLES.mdはCORE / EVOLVINGへ役割分離（原本存置・アーカイブはCEO確認後）。文書IDをMASTER-01〜08（読込順ベース）へ変更
- **担当**: CEO（思想・承認）/ AI（文書化）

---

## 2026-07-03

### Development Standard v1.0
- **対象機能**: プロジェクト全体
- **変更内容**: DEVELOPMENT_STANDARD.md / CHANGELOG.md / ROADMAP.md / NAMING_CONVENTION.md を新規作成。各フォルダにREADME.mdを配置
- **変更理由**: 長期運用を前提としたソフトウェア開発プロジェクトへの移行
- **互換性**: 影響なし（既存データ・スクリプトに変更なし）
- **担当**: CEO（方針）/ AI（実装）

### Insight Extractor v1.0 [Experimental]
- **対象機能**: insight_extractor.py
- **変更内容**: 新規作成。経営上の気付き・仮説・学び・改善案・成功要因・失敗要因・ブランドへの考え・職人との考え・お客様理解の9タイプを抽出し 08_Decision_Log/insight_log.json へ出力（382件）
- **変更理由**: Decisionより緩い条件で経営知見を蓄積するため
- **互換性**: 新規ファイルのみ。既存に影響なし
- **担当**: AI

### Decision Extractor v1.0 [Experimental]
- **対象機能**: decision_extractor.py
- **変更内容**: 新規作成。確定表現（〜することにした、〜を決定 等）による経営判断のみ抽出し 08_Decision_Log/decision_log.json へ出力（20件）。疑問・仮定・願望・作業依頼文は除外
- **変更理由**: Conversation全文を保存せず経営判断のみをログ化するため
- **互換性**: 新規ファイルのみ。既存に影響なし
- **担当**: AI

### ChatGPT Importer v1.1 [Released]
- **対象機能**: chatgpt_importer.py
- **変更内容**: アーカイブフォルダを 09_ChatGPT_Archive → 01_Knowledge/09_ChatGPT_Archive へ変更
- **変更理由**: 実際のフォルダ構成に合わせるため
- **互換性**: フォルダ構成変更（旧パスは使用不可）
- **担当**: CEO（指示）/ AI（実装）

### Conversation Index v1.0 [Released]
- **対象機能**: 07_Data/chatgpt_index.json
- **変更内容**: test.zip（3,349会話）から3,323件のIndexを生成。タイトル・日時・カテゴリ（20分類）・重要度（高中低）・概要を保持
- **変更理由**: ChatGPTログの全体把握と後続抽出処理の基盤とするため
- **互換性**: 新規データ構造 v1.0
- **担当**: AI

### ChatGPT Importer v1.0 [Released → v1.1へ]
- **対象機能**: chatgpt_importer.py
- **変更内容**: 新規作成。ZIP検出→展開→分類→Conversation Index生成。再実行可能なマージ設計
- **変更理由**: ChatGPTエクスポートの継続的な取り込みシステム構築のため
- **互換性**: 新規
- **担当**: AI
