# CHANGELOG.md — 変更履歴

記録項目: Version / 日付 / 対象機能 / 変更内容 / 変更理由 / 互換性 / 担当

新しい変更を上に追記する。

---

## 2026-07-06（v1.0.0後・v1.1に向けて）

### Result Layer v1.1 [Draft・CEOレビュー待ち]（Sprint 15.3・設計のみ）
- **対象機能**: 09_Learning/RESULT_LAYER_V11.md（新規）/ ARCHITECTURE.md §5（Result Layer項更新）
- **変更内容**: Resultを2層構造へ拡張 — ①**Action Result**（実行できたか: 成功/失敗/延期/保留・実行日・Evidence必須・実行直後に判定）②**Business Result**（経営として成功か: 成功/失敗/継続観察・評価日・expected/actual・数値=利益/売上/ROI・定性=ブランド価値/顧客満足/運営負荷・成功/失敗要因・Evidence必須）③**Learning Rule**: Insight GeneratorはBusiness Resultのみ学習対象。Action Resultは実行率分析/運営改善/SOP改善用 ④**Dashboard**: Result Review→Action Review+Business Reviewに分割 ⑤**Knowledge**: Decision/Action Result/Business Resultの3種Evidence保持 ⑥**CEO Rule**: 両Resultの確定はCEOのみ・AIは推測しない ⑦既存result_log 2件は削除せず互換読み替え（確定はCEO確認後）
- **変更理由**: Sprint 15.3（CEO指示・設計のみ。「実行できた」と「経営的に成功した」の分離=Learning Cycle精度向上）
- **互換性**: コード無変更。実装はResult Recorder v1.1+Insight Generator v1.1として次Sprint以降
- **担当**: CEO（レビュー・両Result確定）/ AI（設計）

### Result初号確定 — RES-0001/0002（CEO判定 2026-07-07）
- **対象機能**: 07_Data/results/{result_draft_log.json, result_log.json, index.json} / result_recorder.py（watching状態の再掲対応）/ PENDING #11
- **変更内容**: **FUKUDA AI初のResult確定** — RES-0001 工場打ち合わせ: **継続観察**（認識合わせ実施・詳細成果は今後確認。Evidence: 実施+メモ後日。learning_ready=false・watchingとしてBrief再掲継続）/ RES-0002 催事搬入確認: **成功**（会期開始に支障なく完了。Evidence: 搬入完了+会期影響なし。**learning_ready=true=学習投入可能な初のResult**）。判定・文言はすべてCEO記入（AIは転記のみ）。想定との差異は「expected_result未記録のため評価なし」と事実記載
- **変更理由**: CEO判定指示（Dashboard初号のResult Review経由）
- **互換性**: Decision Log本体無変更・Draft保持（削除なし）
- **担当**: CEO（判定）/ AI（転記・確定操作）

### Dashboard Generator v1.0 [Experimental]（Sprint 15.2・実装）
- **対象機能**: dashboard_generator.py（新規）/ 06_Reports/dashboard/（新規・追記型YYYY-MM-DD.md + _state.json）/ CEO_DASHBOARD.md（承認反映・起動方法追記）
- **変更内容**: CEO Dashboard v1.0設計（CEO承認済み）の実装 — 接続済みデータのみで6セクションを1枚生成。①Company Health: 接続済み3項目（未対応10・期限10・Learning10=30点分）を機械的算定式（待ち/超過1件毎-5・released有無+直近7日Decision）で按分表示・未接続70点分は対象外と明示 ②Today's Dashboard: FOS由来3項目表示・売上系は「未接続」表示（推測しない）③Morning Brief統合: 当日Brief原文を転記（⏰セクションは§4へ集約・重複排除。生成はしない）④Result Review: 07_Data/results/index.json参照（期待vs実績記入欄・判定はCEOのみ）⑤Dataset Status: Registry 10件（ACTIVE/WARNING/ERROR/DRAFT・最終同期・機械的判定のみ）⑥AI Learning Status: 6段階件数+今日の増分（_state.json比較）+Evidence付与率
- **テスト**: --check→本実行→再実行（追記型: _2.md生成・上書きなし・内容は増分基準行以外同一=決定的）/ 書込制限（dashboard/外拒否・既存md上書き拒否）— 全合格。初号発行済み（Health 15/30・Result確認待ち2件）
- **変更理由**: Sprint 15.2（CEO指示・実装Sprint）
- **互換性**: 全入力読み取り専用・既存ファイル無変更・削除なし。DashboardからKnowledge生成なし
- **担当**: CEO（承認・判定記入）/ AI（実装・テスト）

### CEO Dashboard v1.0 [Released・CEO承認 2026-07-07]（Sprint 15.1・設計のみ）
- **対象機能**: 03_Agents/CEO_DASHBOARD.md（新規）/ ARCHITECTURE.md §7 / CEO_ASSISTANT.md（Brief統合の注記）
- **変更内容**: 経営コックピットを設計 — 6セクション: ①**Company Health**（100点満点: 売上20/利益15/現金15/在庫10/出荷10/未対応10/期限10/Learning10。将来Dataset自動計算・未接続項目は按分表示・AIは推測して埋めない）②**Today's Dashboard**（売上/受注/出荷/入金予定/スタッフ待ち/期限超過/本日予定 — FOS分はv1.1で表示可）③**Morning Brief統合**（判断3件→やらないこと→レビュー待ち→Decision Draft。生成ルールはCEO_ASSISTANT.mdが正）④**Result Review**（Result Recorder接続: 結果確認待ち・期待vs実績・差分・判定=CEOのみ）⑤**Dataset Status**（Registry接続: ACTIVE/WARNING/ERROR/未登録+最終同期・機械的判定のみ）⑥**AI Learning Status**（Decision〜Verified件数・今日の増分・Evidence Score平均は将来/当面はEvidence付与率）
- **重要ルール**: Dashboard読み取り専用・AIは書き換えない・Dataset→Brief→Decision Log→Learningから生成・DashboardからKnowledgeを作らない
- **変更理由**: Sprint 15.1（CEO指示・設計のみ。「Morning Brief中心」→「経営コックピット」へ）
- **互換性**: Brief生成ロジック無変更（表示面の統合のみ）。実装はdashboard_generator.py v1.1として次Sprint以降
- **担当**: CEO（方針・レビュー）/ AI（設計）

### Result Recorder v1.0 [Experimental]（Sprint 15・実装）
- **対象機能**: result_recorder.py（新規）/ 07_Data/results/（新規: result_draft_log.json・result_log.json・index.json・README.md）/ ceo_assistant.py v1.3.1（Result Reader追加・結果確認待ち統合）/ RESULT_LAYER_DESIGN.md（実装開始へ状態更新）
- **変更内容**: Result Layer初実装 — ①decision_log.json（読み取りのみ）から結果待ちDecision抽出（trackable条件明記: 結果=完了/実行済み・開発/記録系除外）②Action Record（事実のみ: date/actor/what）+ Result Draft生成（status=**CEO判定待ち**・outcome/数値/要因は全てCEO記入欄）③Metadata引き継ぎ（decision_type main/sub・importance・expected_result・review_after_days・無ければnull）④Evidence必須構造（result_evidenceが入るまでlearning_ready=false）⑤index.json→Brief「⏰ 結果確認待ち」接続（ceo_assistant v1.3.1）⑥確定はCEO確認後にresult_log.jsonへ（AIは判定・確定しない）
- **Result Draft**: 2件生成（RES-0001 工場打ち合わせ / RES-0002 催事搬入確認 — PENDING #11のResult初号候補）
- **テスト**: --check → 本実行 → 再実行（冪等: 新規0件）/ 書込ホワイトリスト検証（results/外への書込をPermissionErrorで拒否）/ Brief統合テスト（一時領域: RES 2件掲載・CEO判定欄・expected未入力表示）— 全合格
- **変更理由**: Sprint 15（CEO指示・実装Sprint）
- **互換性**: Decision Log本体無変更・既存ファイル削除なし。旧判断はメタ項目null（未入力と表示・推測しない）
- **担当**: CEO（判定・確定）/ AI（実装・テスト）

### Commerce/Logistics/POS Dataset Expansion v1.0 [Released（設計登録として承認 2026-07-07。実接続はsource_location・認証・エクスポート方法確認後にactive化）]（Sprint 14.6・設計のみ）
- **対象機能**: 07_Data/datasets/DATASET_REGISTRY.md（§2-1新設）+ dataset_registry.json（7件draft追加・total 10）/ DATA_SOURCE_DESIGN.md / CONNECTOR_ARCHITECTURE.md（Connector 6種追加）/ ARCHITECTURE.md §1
- **変更内容**: EC・物流・POS・決済系を正式登録 — ①source_type 7種追加（shopify/makeshop/hapilogi/logiec/flam/airregi/airpay・計24種）②7 Dataset draft登録: DS-SLS-0001 Shopify（EC注文・商品別売上・顧客・在庫・返品・決済・広告流入元）/ DS-SLS-0002 MakeShop（旧EC・過去実績・移行前データ）/ DS-LOG-0001 はぴロジ（出荷・在庫・入荷・返品・配送遅延・倉庫差異）/ DS-LOG-0002 logiec（物流連携・出荷指示・在庫/注文連携・エラー履歴）/ DS-INV-0001 FLAM（在庫・受注・発注・仕入・売上・商品マスタ・取引先）/ DS-POS-0001 Airレジ（催事/店舗/商品別/日別売上・決済方法別）/ DS-FIN-0001 Airペイ（決済実績・入金予定・手数料・未入金/差異）③record_schema 5種新設（OrderRecord/ShipmentRecord/InventoryRecord/SalesRecord/PaymentRecord）④Agent用途マップ（CEO補佐=売上/在庫/入金/出荷遅延/利益異常、催事=Airレジ、発注在庫=FLAM/はぴロジ/logiec/EC、資金繰り=Airペイ/EC入金、SUNNY NOMADO・so u=EC/商品別売上/受注）
- **重要ルール**: 全て読み取り専用開始・**AIは注文/出荷/返金/決済/在庫変更を実行しない**・data_sensitivity/pii_level原則high（顧客情報・住所・電話・メール・決済情報を含むため）・Knowledge直行禁止
- **変更理由**: Sprint 14.6（CEO指示・設計のみ）
- **互換性**: 既存Dataset 3件（active）は無変更。コードなし・Connector/Importerは未実装（v1.1〜v1.2で実装）
- **担当**: CEO（方針・レビュー・active化）/ AI（設計・draft登録）

### FOS Metadata実装 — FOS Importer v1.2 / CEO Assistant v1.3 [Experimental]（Implementation Mode）
- **対象機能**: fos_importer.py v1.2 / ceo_assistant.py v1.3
- **変更内容**: Sprint 14系承認済み設計の実装 — ①Importer: Decision Metadata 6項目をTaskRecordへ透過（項目なし=null・推測で埋めない）・decision_needed=YESを判断候補の第一条件に・index.jsonサマリーへimportance別/main別集計+「結果確認待ち」抽出（decision_log.json読み取りのみ）②Assistant: Brief並び順v1.2（期限切れ→S→待ち人→A→期限3日→priority高・スコア段階制）・【main】見出し表示・未分類/未設定のCEO確認行（1タップ記入）・review_after_days初期値提案（S30/A14/B7・確定はCEO）・Brief新セクション「⏰ 結果確認待ち」（expected_result vs actual_result比較欄+成功/失敗/継続観察）・Decision Log Draftへメタ5項目保存
- **テスト**: Importer実行（34件・全メタnull互換・冪等確認）+ Assistantユニットテスト5/5合格（スコア・並び順・Brief生成・Draft保存・上書き禁止。一時領域でのみ書込・本番Brief未発行）
- **変更理由**: CEO一括承認（2026-07-07）による実装指示
- **互換性**: 既存FOS-data.json無変更で動作（現データは全件「未分類/未設定」と表示=正常）。既存index.json/draft構造は項目追加のみ
- **担当**: CEO（承認）/ AI（実装・テスト）

### Sprint 14系 CEO一括承認（2026-07-07）
- **承認対象**: FOS Operating Rule v1.0〜v1.2 / SYSTEM_BOOT v1.3 / SYSTEM_BOOT_CHECKLIST v1.0 / Current Mode / Dataset Registry v1.0 / AI Conversation Connectors設計 → **すべてDraft→Released**
- **Dataset active化**: DS-AI-0001（FOS）/ DS-AI-0002（ChatGPT）/ DS-EVT-0001（催事）— last_reviewed=2026-07-07。**以後、未登録Datasetは読まない**
- **Mode移行**: Planning → **Implementation**（CURRENT_STATE.md更新）

### Dataset Registry + AI Conversation Connectors v1.0 [Released・CEO承認 2026-07-07]（Sprint 14.5・設計のみ）
- **対象機能**: 07_Data/datasets/（新規: DATASET_REGISTRY.md + dataset_registry.json）/ 07_Data/spreadsheets/（Supersededへ・誘導追記・削除禁止）/ 07_Data/README.md / DATA_SOURCE_DESIGN.md / CONNECTOR_ARCHITECTURE.md / ARCHITECTURE.md §1 / SYSTEM_BOOT.md v1.3（Data Rule）
- **変更内容**: ①**Dataset Registry**: Spreadsheet Registryを全データソース共通台帳へ上位概念化 — 23項目（19項目+source_location/connector_name/importer_name/record_schema）・source_type 18種（google_sheets/excel/csv/json/fos_json/shopify/meta_ads/gmail/google_calendar/notion/airtable/sqlite/postgresql/chatgpt_export/claude_conversation/gemini_conversation/meeting_transcript/other）。未登録Datasetは読まない・read_only=true初期値・登録確定はCEOのみ。稼働中3ソース（DS-AI-0001 FOS / DS-AI-0002 ChatGPT / DS-EVT-0001 催事）をdraft登録 ②**AI Conversation Source**: ChatGPT/Gemini/Claudeの会話を共通**ConversationRecord（16項目: conversation_id/source_ai/title/created_at/updated_at/participants/messages/summary/decision_candidates/insight_candidates/related_project/related_brand/data_sensitivity/pii_level/imported_at/status）**へ正規化。**そのままKnowledge化禁止**（ConversationRecord→Insight→Decision→Pattern→Lesson→Knowledge Draft→CEO Review→Released）。個人情報・顧客・契約・財務を含む会話=sensitivity high/pii high
- **変更理由**: Sprint 14.5（CEO指示・設計のみ）
- **互換性**: Spreadsheet Registry設計は破壊せず継承（旧フォルダ保持・READMEで誘導）。chatgpt_index.json（3,323件）はv2.0で互換変換・削除しない。コードなし
- **担当**: CEO（方針・レビュー・登録確定）/ AI（設計・draft提案）

### Current Mode + Spreadsheet Registry v1.0 [Draft・CEOレビュー待ち]（Sprint 14.4・設計のみ）
- **対象機能**: 10_AI_Memory/CURRENT_STATE.md（Current Mode欄新設）/ 00_MASTER/SYSTEM_BOOT.md v1.2（Mode別読込ルール）/ 07_Data/spreadsheets/（新規: SPREADSHEET_REGISTRY.md + spreadsheet_registry.json）/ ARCHITECTURE.md §6 / 07_Data/README.md / DATA_SOURCE_DESIGN.md §1-3 / CONNECTOR_ARCHITECTURE.md
- **変更内容**: ①**Current Mode**: 作業モード6種（Review=書込禁止 / Planning=コード変更禁止 / Implementation / Operation / Analysis / Emergency=最小読込で止血）。Mode値はCURRENT_STATE.mdのみが正本（BIOSは持たない）・Mode別読込ルールはSYSTEM_BOOT §Mode別読込ルール ②**Spreadsheet Registry**: 19項目台帳（id/name/description/owner/data_domain 12候補/related_agent 10候補/related_brand/source_type/update_frequency/data_sensitivity/pii_level/access_rule/read_only/allowed_use/forbidden_use/related_knowledge/related_decision_type/last_reviewed/status）。**未登録シートは読まない・AIは編集しない（read_only=true初期値）・個人情報/財務/原価/顧客情報=high・Knowledge直行禁止（Spreadsheet→Connector→Importer→Data Layer→Learning Cycle）**。登録・変更はCEO確認後のみ
- **変更理由**: Sprint 14.4（CEO指示・設計のみ。Sheets Connector v1.1実装の前提）
- **互換性**: 既存の読込シーケンス・Rule無変更（Modeは範囲をさらに絞る追加規約）。DATA_SOURCE_DESIGNの保存先を07_Data/sheets/→spreadsheets/へ統一。コードなし・登録0件
- **担当**: CEO（方針・レビュー・登録確定）/ AI（設計・draft提案）

### SYSTEM_BOOT v1.1 [Draft・CEOレビュー待ち]（Sprint 14.3.1・設計のみ）
- **対象機能**: 00_MASTER/SYSTEM_BOOT.md（v1.1）/ 00_MASTER/SYSTEM_BOOT_CHECKLIST.md（新規）/ README.md / ARCHITECTURE.md §6 / 10_AI_Memory/CURRENT_STATE.md
- **変更内容**: v1.0のCEOレビュー反映 — ①**BIOS化**: 役割を「何を・どの順で・どのルールで読むかの定義」に限定（設計書ではない・「唯一読むファイル」表現を廃止・読込シーケンスの定義者として明記）②**Version管理分離**: Current Version/Phase/SprintをSYSTEM_BOOTから削除し、**CURRENT_STATE.mdを唯一の正本に**（SYSTEM_BOOTはほとんど変更されないBIOSになる）③**SYSTEM_BOOT_CHECKLIST.md新設**: Task開始前の運用チェック10項目（□SYSTEM_BOOT→□MASTER→□Memory→□Agent決定→□Knowledge→□Data→□AI_CHARTER→□推測禁止→□Evidence→□Task開始。設計書ではない）
- **変更理由**: Sprint 14.3.1（CEOレビュー・設計のみ）
- **互換性**: 読込シーケンス・各Rule・禁止事項は変更なし。CURRENT_STATEにVersion管理セクション追加（既存内容は保持）
- **担当**: CEO（レビュー・方針）/ AI（設計）

### SYSTEM_BOOT v1.0 [Draft・CEOレビュー待ち]（Sprint 14.3・設計のみ）
- **対象機能**: 00_MASTER/SYSTEM_BOOT.md（新規・起動時に最初に読む唯一のファイル）/ 00_MASTER/README.md（Session Start Protocolの入口をSYSTEM_BOOTへ）/ ARCHITECTURE.md（§6起動プロトコル追記・章番号繰下げ）
- **変更内容**: 起動時最小読込を設計 — ①必読10文書（AI_CHARTER→PHILOSOPHY→CEO_PRINCIPLES（=CORE/EVOLVING）→ARCHITECTURE→DATA_SOURCE→CONNECTOR→AGENT_DESIGN→COLLABORATION）②Knowledge Rule（索引経由・released/verifiedのみ・draft禁止）③Data Rule（事実のみ・意味づけ禁止・Knowledge直行禁止）④Learning Rule（Decision→…→Verified・Result推測禁止・Evidence必須）⑤Agent Rule（必要な1Agentのみ）⑥FOS Rule（JSON正本・AI変更禁止）⑦Memory Rule（CURRENT_STATE/NEXT/PENDINGのみ）⑧Token Rule（全ファイル読込禁止・全文検索禁止）⑨禁止事項7つ ⑩起動シーケンス7段。Current Version/Phase/SprintはSprint完了時にAIが更新・本文変更はCEO承認のみ
- **変更理由**: Sprint 14.3（CEO指示・設計のみ。トークン消費を抑えFUKUDA AIを長期運用するため）
- **互換性**: 既存の11文書読込順は「矛盾時の優先順位」として存続（README.mdに明記）。コードなし
- **担当**: CEO（方針・レビュー）/ AI（設計）

### FOS Decision Metadata v1.2 [Draft・CEOレビュー待ち]（Sprint 14.2・設計のみ・Result Layer接続の前提設計）
- **対象機能**: FOS/README.md v1.2 / 07_Data/fos/README.md / CEO_ASSISTANT.md / fos_importer.py・ceo_assistant.py（TODOコメントのみ・ロジック無変更）
- **変更内容**: 判断メタデータに3項目追加 — ①**decision_importance S/A/B/C**（経営重要度。priority=作業の急ぎ度と分離。S=方針・数十万円以上・新ブランド・人事・契約法務・大投資・撤退・不可逆 → **原則Brief必載**）②**expected_result**（判断時の期待結果。Result Recordへ引き継ぎactual_resultと差分比較）③**review_after_days**（結果確認日数。初期値S30/A14/B7/Cなし・催事/発注/広告は実務調整可。経過でBrief「結果確認待ち」へ自動掲載）④テンプレート14項目化 ⑤Brief並び順: 期限切れ→S→待ち人→A→期限3日→priority高 ⑥Decision Logへ5項目保存・Knowledge化時はRelated Decision Metadata保持 ⑦AIはimportance/expected_resultを推測確定しない（未入力=未設定→CEOへ確認。review_after_daysのみ初期値提案可・確定はCEO）
- **変更理由**: Sprint 14.2（CEO指示・設計のみ。Result Recorder v1.0実装前の前提設計 — Evidence Scorer・Verified昇格条件が重要度別・分類別の成功率を参照する接続点）
- **互換性**: 既存FOS-data.json無変更・項目なしはnull/未設定互換。コードはTODOのみ（実装はfos_importer v1.2 / ceo_assistant v1.3として次Sprint）
- **担当**: CEO（基準・レビュー）/ AI（設計）

### FOS Decision Metadata v1.1 [Draft・CEOレビュー待ち]（Sprint 14.1・設計のみ）
- **対象機能**: FOS/README.md v1.1 / 07_Data/fos/README.md / CEO_ASSISTANT.md / fos_importer.py・ceo_assistant.py（TODOコメントのみ・ロジック無変更）
- **変更内容**: 判断メタデータを設計 — ①**decision_needed**（YES条件9種: 5万円以上・待ち人・方針/ブランド影響・契約法務・在庫発注・催事出店・例外対応・変更コスト高 / NO条件5種。YES=Brief最優先候補）②**decision_type main/sub 2階層**（13分類・main必須・sub任意=null。FOS→Brief→Decision Log→Result→Knowledgeまで一気通貫し分類別の判断傾向・成功率が集計可能に）③入力テンプレートへ3項目追加 ④AIは分類を推測確定しない（未入力=未分類→BriefでCEOへ確認）⑤既存FOS-data.jsonは無変更・項目なしはnull互換
- **変更理由**: Sprint 14.1（CEO指示・設計のみ）
- **互換性**: 既存データ・コードのロジック無変更（TODOコメントのみ）。実装はfos_importer v1.1 / ceo_assistant v1.3として次Sprint
- **担当**: CEO（基準・レビュー）/ AI（設計）

### FOS Operating Rule v1.0 [Draft・CEOレビュー待ち]（Sprint 14・設計のみ）
- **対象機能**: FOS/README.md（新規・運用ルール本体）/ 07_Data/fos/README.md（新規・データ辞書）/ CEO_ASSISTANT.md（参照追記）
- **変更内容**: FOS入力ルールを設計 — ①必ず入れるもの6種（CEO判断・待ち人・期限・お金・現場業務・Briefに出したいもの。**迷ったら入れる**）②入れなくてよいもの4種 ③FOS=CEO操作面/PENDING=AI記録面の分担（同一案件の二重管理禁止・境界例はFOS優先）④入力テンプレート9項目（Brief#3のso u相談を模範例として記載）⑤Brief掲載の機械判定6条件 ⑥Decision Log送付条件（判断のみ・作業完了は送らない）⑦Result Record送付条件（trackable判断・実行2週間後に結果確認）⑧運用の1日（朝Brief・日中入力・夕方完了化）
- **変更理由**: Sprint 14（Brief#3後のCEO指摘「FOSに入っていない重要タスクがある」を受けて）
- **互換性**: 設計のみ・コードなし。運用はCEOの入力習慣として開始
- **担当**: CEO（方針・レビュー・運用）/ AI（設計）

### Morning Brief第3号（FOS連携初号）発行・CEO判断反映
- **対象機能**: 06_Reports/morning_brief/2026-07-07.md / decision_log（33件）/ EVOLVING_PRINCIPLES（EP-005運用記録）/ PENDING / NEXT
- **変更内容**: FOS由来の判断3件をCEOが処理 — ①工場打ち合わせ: 済み（結果メモ後日=Result記録初号候補）②催事搬入確認: 済み ③so u発注量: **保留**（販売条件の前回比較+上限予算の確認後にB案方向で判断）。Decision Log 3件確定。**EP-005の運用記録に「CEOがEPをそのまま実践した初の実例」を記録**。確認事項2点をPENDING #10へ、FOS側への確認タスク追加をCEOへ推奨
- **変更理由**: Brief#3へのCEO記入（FOS→Brief→判断→記録のフルサイクル初完走）
- **互換性**: 記録のみ。**次Sprint予約: FOS入力ルール設計**（FOS外の重要タスク存在のCEO指摘による）
- **担当**: CEO（判断）/ CEO Assistant v1.2（反映）

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
