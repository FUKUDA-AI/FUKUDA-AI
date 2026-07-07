# CHANGELOG.md — 変更履歴

記録項目: Version / 日付 / 対象機能 / 変更内容 / 変更理由 / 互換性 / 担当

新しい変更を上に追記する。

---

## 2026-07-06（v1.0.0後・v1.1に向けて）

### FOS Importer v1.0 [Experimental] + CEO Assistant v1.2（Sprint 13: FOS Connector）
- **対象機能**: fos_importer.py（新規）/ 07_Data/fos/（index.json+snapshots）/ ceo_assistant.py v1.2
- **変更内容**: FOS-data.json（正本・読み取り専用・HTMLは読まない）→TaskRecord 34件へ正規化（tasks18/next_action11/staff_request1/improvements2/events2）。**Decision候補生成**（staffRequestsの要判断・期限切れevent・improvements=5件）、**期限切れ検知**（2件検出）、priority順ソート、PENDING同期レポート、Sprint同期（projects状態集計）、--check、冪等（内容ハッシュでスナップショット重複回避）。CEO Assistant v1.2でBrief判断候補へ統合（期限切れが最上位・スタッフ相談は「人が待っている」加点）
- **変更理由**: Sprint 13（FOS-data.json配置完了を受けた実装）
- **互換性**: FOS原本無変更を検証済み。書込は07_Data/fos/のみ。Knowledge直行なし（Data Layer経由）
- **担当**: CEO（配置・仕様）/ AI（実装）

### FOS設計変更: FOS-data.jsonを正本（Source of Truth）へ（CEO指示）
- **対象機能**: DATA_SOURCE_DESIGN.md 1-11 / CONNECTOR_ARCHITECTURE.md 4-9 / 07_Data/README / ROADMAP / PENDING
- **変更内容**: FOSの正本をFOS.html→**FOS-data.json**へ変更（HTMLは表示用補助・解析対象外）。フロー: FOS-data.json→FOS Importer→TaskRecord→Morning Brief→Decision候補。理由: Importer簡単・HTML解析不要・Brief反映容易・将来API化容易
- **変更理由**: CEO指示（2026-07-06）
- **互換性**: 設計のみ。配置待ち（推奨: FOS/FOS-data.json・PENDING #9更新済み）。初回接続時にJSONスキーマの項目対応をCEOと確認
- **担当**: CEO（決定）/ AI（設計反映）

### FOS を正式データソースへ追加（設計・CEO指示）
- **対象機能**: DATA_SOURCE_DESIGN.md（1-11追加・優先順位0番）/ CONNECTOR_ARCHITECTURE.md（FOS Connector・FOS Importer 4-9・TaskRecordスキーマ・07_Data/fos/）/ AGENT_COLLABORATION.md（共有データ追加）/ ROADMAP / PENDING
- **変更内容**: FOS（FUKUDA Operating System・日次運用ボードHTML）を最優先データソースとして登録。取得: 今日やること・未完了/完了タスク・Sprint・PENDING・期限・優先度・Decision候補・Brief候補。ルール: 読み取り専用開始・原本無変更・タスク完了/削除はCEO確認後のみ・内容はKnowledge直行禁止（Data Layer→意味づけ後にLearning Cycle）
- **変更理由**: CEO指示（FOSはMorning Brief・タスク・Sprint・PENDING管理の入力元）
- **互換性**: 設計のみ。**実装前提: FOS.htmlが別セッション出力フォルダにあり現在アクセス不可 → プロジェクト内移設（推奨: FOS/FOS.html）が要CEO作業（PENDING #9）**
- **担当**: CEO（指示・移設）/ AI（設計・登録）

### Result Layer v1.0 設計 [Draft・CEOレビュー待ち]（Sprint 12・設計のみ）
- **対象機能**: 09_Learning/RESULT_LAYER_DESIGN.md（新規・コードなし）/ ARCHITECTURE.md（§5追記）
- **変更内容**: Decision→Action→Result→Insightの閉ループを設計 — Result Record 13項目（decision_id遡及リンク・Evidence必須・learning_ready機械判定）、**成功/失敗/継続観察の判定と要因分析はCEOのみ（AIは推測しない。機械は数値・日付・出典の転記だけ）**、入力3経路（Brief結果確認欄/実績データ照合/週次棚卸し）、失敗Resultを最重要学習素材に、Verified条件の深化（利用実績→**成功Resultで検証された**利用実績へ・失敗根拠のKNは昇格せず見直し）
- **変更理由**: Sprint 12（CEO指示・設計のみ）
- **互換性**: 新規文書のみ。実装は承認後（保存先: 07_Data/results/）
- **担当**: CEO（方針・レビュー）/ AI（設計）

### Pattern Generator v1.0 [Experimental]（Sprint 11実装）
- **対象機能**: pattern_generator.py（新規）/ 09_Learning/patterns/pattern_draft_log.json
- **変更内容**: Insight横断（v2.0 CEO判断由来10件+v1.3会話由来382件）の反復検出を実装。Pattern成立はCEO承認4条件（v2由来1件以上・異なる日・異なる文脈・Decision遡及可能）+出現3回以上（同日同文脈=1回）を**機械検証**。重複判定: 既存Pattern類似は非生成、EP/CORE類似はEP運用記録候補へ、**CEO却下済み類似は再提案しない**（再整理指示つきのみ例外・抑制理由をログ記録）。書込は09_Learning/patterns/のみ・冪等
- **変更理由**: Sprint 11（CEO承認2点を反映した実装）
- **互換性**: 新規のみ。初回実行: **Pattern Draft 0件**（設計どおり: v2.0 Insightが1日分のため「異なる日」条件を満たす群が無い）。抑制1件（hold解消判断とDX還元Insightの群・異なる日待ち）。合成データテスト5ケース+冪等性検証合格
- **担当**: CEO（条件承認）/ AI（実装）

### Pattern Generator v1.0 実装計画 [Draft・CEO確認待ち]（Sprint 11・計画のみ）
- **対象機能**: 09_Learning/PATTERN_GENERATOR_PLAN.md（新規・コードなし）
- **変更内容**: Insight Draft→Pattern Draftの実装計画 — 認定条件（**異なる日×異なる文脈で3回以上・同日同案件は1回**・機械検証）、v1.3会話由来Insightとの横断カウント（CEO判断由来1件以上を必須）、重複判定4種（同一冪等/類似は既存強化/EP・CORE類似はEP運用記録候補へ/**CEO却下済みは再提案しない**）、Evidence連鎖（Pattern→Insight→Decision 2ホップ遡及保証）、リスク明示（初回実行はデータ1日分のため0件の見込み=正直な予測）
- **変更理由**: Sprint 11（CEO指示・設計と実装計画のみ）
- **互換性**: 新規文書のみ
- **担当**: CEO（確認・これから）/ AI（計画）

### Insight Generator v1.0 [Experimental]（Sprint 10・Learning Cycle v2.0第一コンポーネント）
- **対象機能**: insight_generator.py（新規）/ 09_Learning/insights/insight_draft_log.json
- **変更内容**: Decision LogからInsight Draftを自動生成 — 入力は**CEO確定判断のみ**（会話からの機械抽出分20件は対象外として除外）、判断理由未記入からは生成しない（推測禁止）、結果から承認基準/却下基準/保留・不足情報を分類、既存Insight・EPとの意味類似判定（≧0.80は新規作成せず既存Evidence強化）、Evidence必須（Decision指紋・日時・根拠EP/KN封入）、冪等（処理済み指紋管理・再実行で重複ゼロを検証）、書込は09_Learning/insights/のみ
- **変更理由**: Sprint 10（CEO指示・コード実装）
- **互換性**: 新規のみ。decision_log本体は無変更。初回実行: 確定判断10件→Insight Draft 10件（承認基準9・保留1）
- **担当**: CEO（指示）/ AI（実装）

### Learning Cycle v2.0 設計 [Draft・CEOレビュー待ち]（Sprint 9）
- **対象機能**: 09_Learning/（新規フォルダ）LEARNING_CYCLE_V2.md + README.md / ARCHITECTURE.md（§5参照追記）
- **変更内容**: Decision Log起点の自動学習を設計 — Insight Generator v2.0（確定判断の理由・**却下理由**から抽出。理由未記入からは作らない）/ Pattern Generator v2.0（異なる日・文脈で3回以上・v1.3会話ルートと横断）/ Knowledge Generator v2.0（Evidence連鎖封入・IA準拠）/ 昇格条件表（Released=CEO Review・Verified=CEOのみ・候補入り機械判定は180日+利用実績3回+矛盾ゼロ）/ 重複判定3層（同一・類似は既存強化・却下照合）/ Brief・Decision Log・Knowledge連携 / Agent反映（released化で全Agentへ即時反映+将来の週次ダイジェスト・提案採否の還流学習）
- **変更理由**: Sprint 9（CEO指示・設計のみ・コードなし）
- **互換性**: 新規文書のみ。v1.3サイクルと並存。Architecture版数は承認時にv1.4へ
- **担当**: CEO（方針・レビュー）/ AI（設計）

### Events Importer v1.0 [Experimental]（Sprint 8: Events Connector）
- **対象機能**: events_importer.py（新規）/ 07_Data/events/（raw・normalized・index.json）
- **変更内容**: 催事実績（Excel/CSV）の共通データ基盤を実装 — 列名ゆらぎ吸収マッピング、EventRecord正規化（12項目+取込記録）、読めないセルはnull（推測禁止）、日数・日商のみ算術導出（derived_fields明記）、冪等（record_idで重複排除）、元データ無変更・読み取り専用。index.jsonにサマリー（総件数・平均売上・会場一覧）を生成しMorning Brief・催事AI・CEO補佐AIが参照可能
- **変更理由**: Sprint 8（v1.1データ接続の一番手・DATA_SOURCE_DESIGN優先順位1位）
- **互換性**: 新規のみ。テスト合格（正規化3件・null処理・導出・冪等性・本番raw/空で0件index）
- **担当**: CEO（仕様）/ AI（実装）

### Morning Brief第2号 CEO判断反映
- **対象機能**: pattern_log / lesson_log / decision_log_draft / decision_log / EVOLVING_PRINCIPLES / Brief#2
- **変更内容**: ①Git+GitHub Push完了を確認・記録（CEO実施・origin接続確認済み）②PTN-003/LSN-004をhold解消→released（EP-004への再整理完了が根拠）③LSN-011/PRN-010はhold継続とし、「経営判断は売上だけでなく、利益・ブランド価値・運営負荷・将来性を総合的に判断する」を次回Principle候補として再提案指示を記録 ④Decision Log Draft 3件を確定し本体へ反映（合計30件）⑤EP-004運用記録を追記
- **変更理由**: Brief#2へのCEO記入（v1.1ハイブリッド方式の初回フルサイクル完走: 機械生成→LLM言語化→CEO判断→Draft確定→本体反映→EP記録）
- **互換性**: statusと記録のみ。削除なし
- **担当**: CEO（判断）/ CEO Assistant v1.1（反映）

### CEO Assistant v1.1 [Experimental]（Sprint 7実装）
- **対象機能**: ceo_assistant.py（新規）/ 03_Agents/CEO_ASSISTANT.md v1.1 / CEO_ASSISTANT_IMPL_PLAN.md
- **変更内容**: Morning Brief生成の機械工程を実装 — ①Released Knowledge Reader（released/verifiedのみ・draft除外を機械的に保証）②CORE/EVOLVING Principles Reader ③AI Memory Reader ④PENDING Reader（完了行除外）⑤Brief Generator（6ルールスコアリング・最大3件選定・追記型YYYY-MM-DD_n.md・上書き禁止）⑥Decision Log Draft Generator（decision_log_draft.json専用・本体へ書かない）。書込先3か所のホワイトリストをコードで強制（逸脱・上書きの拒否をテストで検証済み）
- **変更理由**: Sprint 7（CEO承認3点: 正式Draft保存先/ハイブリッド方式/追記型を反映）
- **互換性**: 新規ファイルのみ。既存削除なし。ルート08_Decision_Log/は不使用（既存データ存置）
- **担当**: CEO（方式承認）/ AI（実装）

### 🎂 Morning Brief第1号 発行・CEO判断反映（FUKUDA AI初の日次運用）
- **対象機能**: 06_Reports/morning_brief/2026-07-06.md / 00_MASTER思想文書8本 / 設計6文書 / decision_log.json / EVOLVING_PRINCIPLES.md
- **変更内容**: CEO補佐AI v1.0が第1号Briefを発行し、CEO判断を反映 — ①**設計6文書をReleased化**（Agent Design / Collaboration / Data Source / Morning Brief / Connector / CEO補佐AI定義）②**思想文書8本をv1.0（正式版）へ昇格**（憲法〜AI_CHARTER。FUKUDA AIの人格が正式確定）③Decision Log 7件確定（本日の全CEO判断・根拠EP/KN付き）④**EP-001〜008へ初回運用記録**（Knowledge Review・Brief判断での使用実績=CORE昇格の証拠の蓄積開始）
- **変更理由**: Morning Brief第1号へのCEO記入（判断1: 承認 / 判断2: 承認 / 判断3: Git作業はCEOがこれから実行）
- **互換性**: 版数とstatusのみ更新。内容変更なし
- **担当**: CEO（判断）/ CEO補佐AI v1.0（発行・反映）

### CEO補佐AI v1.0 [Experimental・Draft]
- **対象機能**: 03_Agents/CEO_ASSISTANT.md（新規）/ AGENT_DESIGN.md / README.md
- **変更内容**: FUKUDA AI初のAgent定義 — Morning Brief専用。参照順序（00_MASTER→Memory→released/verified Knowledge→レビューキュー→実績→CEO当日情報）、生成手順6段階、出力5セクション、書込先3か所限定、禁止事項7条（実行しない・draft不参照・推測しない・4件以上載せない・判断先取りしない・保留案件の再提示ルール等）、Brief後の記録義務（EP運用記録・Knowledge利用実績=Verified昇格の証拠）
- **変更理由**: Phase 9 STEP6（CEO指示Sprint・設計のみ・コードなし。FUKUDA AI本体が本定義に従い動作）
- **互換性**: 新規文書のみ
- **担当**: CEO（方針・レビュー）/ AI（定義）

### Knowledge Lifecycle設計（Verified状態の追加・設計のみ）
- **対象機能**: 02_Rules/KNOWLEDGE_PROMOTION_RULES.md v1.1 / ARCHITECTURE.md / 01_Knowledge/README.md
- **変更内容**: Knowledgeの状態遷移に**verified（会社標準Knowledge）**を追加設計 — Draft→CEO Review→Released→実運用で継続利用→Verified。昇格はCEOのみ（AIは候補提案まで。目安: released後6か月以上・複数回の有効利用・矛盾なし）。Agent参照はreleased/verified、矛盾時はverified優先。verifiedも事実が変われば改訂・降格（CEOのみ）
- **変更理由**: PrincipleのEVOLVING→CORE二段階と同じ検証構造をKnowledgeにも適用（CEO指示）
- **互換性**: 設計のみ。既存Knowledge 13件の状態は変更なし（released 12 / in_review 1のまま）
- **担当**: CEO（方針）/ AI（設計）

### 🎉 Knowledge Release Sprint v1.0 — 初のReleased Knowledge誕生
- **対象機能**: 01_Knowledge各カテゴリ / 04_SOP / knowledge_index.json / knowledge_builder.py v1.1
- **変更内容**: CEO承認12件をreleased化しカテゴリフォルダへ配置（01_Brands 1 / 02_Products 3 / 03_Customers 2 / 05_Events 3 / 10_Sales 1【新設】/ 04_SOP 2）。KN-SOP-0003はhold（in_review・実運用で成熟後に昇格）。索引再生成（released 12 / in_review 1）。**AgentはこのReleased 12件を参照可能になった（FUKUDA AI初の正式Knowledge）**
- **変更理由**: CEOレビュー結果の反映（Approve 12 / Hold 1 / Reject 0）
- **互換性**: 元Draftは削除せず移動記録スタブとして保持。Knowledge Builder v1.1（索引走査に04_SOPを追加・released済みLessonの再生成防止=冪等性検証済み）
- **担当**: CEO（承認）/ AI（反映）

### Connector Architecture v1.0 [Draft・CEOレビュー待ち]
- **対象機能**: 07_Data/CONNECTOR_ARCHITECTURE.md（新規）/ ARCHITECTURE.md（Connector/Importer層明記）/ 07_Data/README.md / ROADMAP.md
- **変更内容**: 全情報源（ChatGPT/Claude/Gemini/会議/Gmail/Calendar/Drive/Sheets/Shopify/Meta/催事）を「Connector→Importer→Learning Cycle」へ統一する4層設計。層の役割と禁止事項、共通レコードスキーマ5種（Conversation/Transaction/Event/Metric/Document）、Connector 8種、AI別に分離したImporter 8種（ChatGPT/Claude/Gemini/Meeting/Gmail/Calendar/Shopify/Meta）、07_Dataフォルダ構成、運用ルール6条（読取専用・冪等・PIIフィルタ・独立Version・統合索引）
- **変更理由**: Phase 10 STEP5（CEO指示Sprint・設計のみ・コードなし）
- **互換性**: 既存chatgpt_importer.py v1.1は一体型のまま稼働継続。v2.0で分離（chatgpt_index.jsonは互換変換・削除しない）
- **担当**: CEO（方針・レビュー）/ AI（設計）

### CEO Morning Brief Design v1.0 [Draft・CEOレビュー待ち]
- **対象機能**: 06_Reports/CEO_MORNING_BRIEF_DESIGN.md（新規）/ AGENT_COLLABORATION.md（日次フロー詳細化）
- **変更内容**: 日次運用の設計 — 毎朝の確認情報6種、Agent別3行ミニレポート、CEO補佐AIの統合6手順、1枚テンプレート（最重要判断3件/今日やらないこと/注意5領域/レビュー待ち/次の判断/AI提案/Decision Log候補/CEO入力欄）、3件絞り込みルール6条、緊急アラート条件5種、Decision Log記録項目、日次→週次→月次の接続、v1.1（手動）/v1.2（半自動）/v2.0（自動発行）段階分け。CEO所要時間5分以内の設計
- **変更理由**: Phase 10 STEP4（CEO指示Sprint・設計のみ・コードなし）
- **互換性**: 新規文書のみ
- **担当**: CEO（方針・レビュー）/ AI（設計）

### Data Source Design v1.0 [Draft・CEOレビュー待ち]
- **対象機能**: 07_Data/DATA_SOURCE_DESIGN.md（新規）/ ARCHITECTURE.md / ROADMAP.md / AGENT_COLLABORATION.md（参照追記）
- **変更内容**: 外部10データソース（Shopify/Drive/Sheets/Gmail/Calendar/Meta広告/Instagram/催事売上/発注在庫/会計）の接続設計 — 各ソース10項目（取得情報/利用Agent/判断用途/更新頻度/CEO確認/保存先/Knowledge化基準/個人情報注意）+ 共通ルール6条（外部データのKnowledge直行禁止・07_Data経由・読み取り専用開始・発信/削除のCEO確認必須等）+ 接続優先順位 + v1.1/v1.2/v2.0段階分け
- **変更理由**: Phase 10 STEP3（CEO指示Sprint・設計のみ・コードなし）
- **互換性**: 新規文書のみ
- **担当**: CEO（方針・レビュー）/ AI（設計）

### Agent Collaboration v1.0 [Draft・CEOレビュー待ち]
- **対象機能**: 03_Agents/AGENT_COLLABORATION.md（新規）/ 03_Agents/README.md（更新）
- **変更内容**: 10AgentのOS連携設計 — 情報フロー3層（現場→資源→中枢→CEO+還流）、トリガー別起点、CEO報告の一本化（CEO補佐AI窓口+緊急直訴ルート）、共有データ6種・書換禁止データ7種、CEO必須確認8分類、日次/週次/月次フロー、典型シナリオ6件（催事出店/so u対応/在庫不足/新商品/広告改善/事故対応）
- **変更理由**: Phase 9 STEP2（CEO指示Sprint・設計のみ・コードなし）
- **互換性**: 新規文書のみ
- **担当**: CEO（方針・レビュー）/ AI（設計）

### Agent Design v1.0 [Draft・CEOレビュー待ち]
- **対象機能**: 03_Agents/AGENT_DESIGN.md（新規）/ 03_Agents/README.md（更新）
- **変更内容**: 10エージェント（CEO補佐/so u/SUNNY NOMADO/催事/発注・在庫/営業/広告・SEO/資金繰り/商品企画/秘書）の設計書を作成。各Agent12項目（目的/役割/入出力/参照Knowledge・Principle/判断基準/連携/CEO確認/禁止事項/v1.0・v2.0スコープ）+ 全Agent共通設計（参照スタック・行動制約・判断基準）+ 連携マップ + 実装優先順位（①CEO補佐 ②催事 ③so u）
- **変更理由**: Phase 9の設計フェーズ（CEO指示Sprint・設計のみ・コードなし）
- **互換性**: 新規文書のみ。Agent実装なし
- **担当**: CEO（方針・レビュー）/ AI（設計）

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
