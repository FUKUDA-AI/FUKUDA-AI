# NEXT — 次Sprintで行う作業

最終更新: 2026-07-06（更新者: AI）

## 次Sprint候補（推奨順・2026-07-07更新）

0. ~~FOS入力ルール設計~~ ✅ 2026-07-07完了（FOS/README.md v1.0 → **v1.1 Decision Metadata追加済み**・CEOレビュー待ち）。**FOS外だった重要タスクのFOSへの入力はCEO作業**（テンプレート§5・11項目を使用）
1. so u発注量の再判断（PENDING #10の確認2点が揃い次第・次回Brief）
2. ~~FOS Decision Metadata実装Sprint~~ ✅ 2026-07-07完了（fos_importer v1.2 + ceo_assistant v1.3・テスト5/5合格）
3. **Result Recorder v1.0実装**（次の本命。v1.2メタデータ実装済み=前提が揃った。expected_result vs actual_result比較 → Evidence Scorer・Verified昇格条件へ接続）
4. CEO作業: FOSの既存タスクへdecision_needed / type / importance / expected_result / review_after_daysを入力（テンプレート§5・14項目）。入力後の初Briefで新メタデータが機能する
5. CEO作業: FOS上の完了済みタスク（工場打ち合わせ・催事搬入）の完了化（期限切れ誤検知の解消）

## 旧候補（消化済み多数・記録として保持）

1. ~~EVOLVING登録Sprint~~ ✅ 2026-07-06完了（EP-001〜008 active）
3. ~~Knowledge Builder v1.0~~ ✅ 2026-07-06完了（Draft13件生成）→ 次は**Knowledge ReviewSprint**（Draft 13件のCEOレビュー→承認分のreleased化・索引再生成）
4. Lesson/Principle Generator品質改善（却下理由11件を抽出フィルタへ反映）
5. ルート08_Decision_Log/の99_Archive移動（CEO承認後・AIは提案のみ）

## 前提・依存

- 1・2はKNOWLEDGE_PROMOTION_RULES.md（2026-07-06 Released）に準拠すること
- 3・4はCEOのレビュー・承認待ちであり、AIは勝手に実行しない（AI_CHARTER第3条・第6条）

## 完了済み（2026-07-06 正式化Sprint）

~~Extractor v2.0化~~ / ~~Architecture v1.2 + ARCHITECTURE.md~~ / ~~Knowledge昇格フロー文書化~~
