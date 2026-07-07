# RESULT_LAYER_DESIGN — Result Layer v1.0 設計書

Version: v1.0設計（Sprint 12）→ **実装第1段 稼働（Sprint 15・2026-07-07: result_recorder.py v1.0 = 実装計画§9の1〜3。Result Draft 2件生成・Brief接続済み）**
最終更新日: 2026-07-07
状態: 実装開始（残り: §9の4 実績データ照合・5 Insight Generator v1.1）
関連: [LEARNING_CYCLE_V2.md](LEARNING_CYCLE_V2.md) / [../02_Rules/KNOWLEDGE_PROMOTION_RULES.md](../02_Rules/KNOWLEDGE_PROMOTION_RULES.md)

> これまでの学習は「CEOが**何を**判断したか」から学んでいた。
> Result Layerは「その判断が**どうなったか**」から学ぶ。
> 判断と結果が揃って初めて、学びは検証済みになる。

---

## 1. 全体フロー

```
Decision（CEO確定判断・Decision Log）
   ↓ 実行
Action（誰が・いつ・何をしたか）
   ↓ 時間経過・事実の発生
Result（結果の記録 — 07_Data/results/result_log.json）
   │  成功 / 失敗 / 継続観察 の3分類
   │  ★AIはResultを推測しない。CEO記入 or 07_Data実績データの事実のみ
   ↓ Learning Ready = true のResultだけが学習対象
Insight（Insight Generator v1.1が「結果つきの学び」を生成）
   ↓ 以降は既存Learning Cycle（Pattern → Knowledge → CEO Review → …）
```

## 2. Result Record 仕様

保存先: `07_Data/results/result_log.json`（事実の記録=Data Layer。索引ファースト）

| 項目 | 内容 | 記入者 |
|---|---|---|
| result_id | RES-xxxx（採番） | 機械 |
| decision_id | 元Decisionの指紋/ID（**必須・遡及リンク**） | 機械 |
| action_date | 実行した日 | CEO / 実績データ |
| result_date | 結果が判明した日 | CEO / 実績データ |
| status | **成功 / 失敗 / 継続観察** の3分類のみ | **CEOのみ**（AIは分類しない） |
| outcome | 何が起きたかの事実記述 | CEO / 実績データ |
| 数値結果 | 売上・利益・件数等（あれば。出典必須） | 実績データ優先 |
| 成功要因 | CEOの分析（成功時。空欄可） | CEO |
| 失敗要因 | CEOの分析（失敗時。空欄可） | CEO |
| 想定との差異 | 判断時の期待効果（Brief記載）と実績の差 | CEO + 機械（期待効果を自動転記して比較材料に） |
| evidence | 出典（EventRecord ID / TransactionRecord ID / CEO記入・日付） | 機械（**必須。無ければLearning Ready不可**） |
| reviewer | CEO（結果の確定者） | CEO |
| learning_ready | true / false（学習投入可否。status確定+evidence完備でtrue） | 機械判定 |

## 3. Resultの入力経路（AIは推測しない）

| 経路 | 例 | 自動化度 |
|---|---|---|
| ① CEO記入 | Morning Briefの「結果確認」欄（§5）に一言記入 | 手動（v1.0） |
| ② 実績データ照合 | 催事出店判断 → 07_Data/events/の該当EventRecord（会場+期間一致）から売上・日商を自動転記 | 半自動（v1.1・**数値の転記のみ**。成功/失敗の判定はしない） |
| ③ 定期棚卸し | 週次レビューで「結果待ちDecision一覧」を提示 → CEOがまとめて記入 | 手動（v1.0） |

**鉄則**: 機械が書けるのは事実（数値・日付・出典）だけ。**成功/失敗/継続観察の判定と要因分析はCEOのみ**。判定のないResultは learning_ready = false のまま学習に使われない。

## 4. Learning Cycleへの接続

- **Insight Generator v1.1（将来拡張）**: learning_ready=trueのResultを読み、Decisionと突合して「結果つきInsight」を生成
  - 成功Result → type: 成功要因（「この判断はこの理由で成功した」— Evidenceに数値つき）
  - 失敗Result → type: 失敗要因（**最も価値の高い学び**。判断理由と失敗要因の差分が判断基準の改善点）
  - 継続観察 → 生成しない（結果が出るまで待つ）
- 結果つきInsightはPattern Generator以降を通常どおり流れる。**「成功が3回反復した判断基準」は最強のKnowledge/Principle候補**になる
- 想定との差異が大きいResultは、根拠にしたEP/KNの見直し候補としてCEOへ報告（原則の反証データ）

## 5. Morning Briefとの接続

- Briefに「🔁 結果確認（最大2件）」セクションを追加（v1.2で）: result_date未記入のDecisionのうち、実行から一定期間（目安2週間）経過したものを提示 → CEOが「成功/失敗/継続観察+一言」を記入（判断3件とは別枠・軽量）
- 判断時の「期待効果」をResult Recordへ自動転記 → 結果記入時に「想定との差異」が一目で分かる
- 判断→結果→学びの一巡がBrief上で完結する（判断した朝と、結果を振り返る朝が同じ1枚の作法）

## 6. Decision Logとの接続

- Decision Log側に `result_id` の逆リンクを追記（結果が記録されたDecisionが分かる）
- 「結果待ちDecision」の抽出条件: confirmed + 実行系の判断 + result未記録
- 記録・報告系の判断（文書承認等）は結果追跡の対象外とする（対象フラグ `trackable` をDecision確定時に付与）

## 7. Knowledgeとの接続

- 成功Result（特に数値つき）はKnowledge Draftの最上級Evidence（「使われて、効いた」証拠）
- 失敗Resultは該当Knowledgeの改訂Draft・SOP見直し（EP-006: 失敗はプロセスの見直しへ）のトリガー
- Result由来の事実数値（催事売上等）はKnowledgeの定量更新に使う（例: KN-EVT-0001の平均30万の検証・更新）

## 8. Verified条件との関係

Knowledge Lifecycle（released → verified）の判定材料が強化される。

| Verified Candidate判定（現行） | Result Layer導入後の強化 |
|---|---|
| released後180日以上 | 変更なし |
| 利用実績3回以上（参照された） | **+ 参照した判断のResultが「成功」であること**（参照されただけでなく、効いた証拠） |
| 矛盾・訂正ゼロ | **+ 失敗Resultに紐づいていない**（失敗の根拠になったKnowledgeは昇格せず見直しへ） |

→ Verifiedの意味が「長く使われた」から「**長く使われ、結果で検証された**」へ深化する。EP→CORE昇格も同様に、EPを根拠にした判断の成功Resultが昇格の証拠になる。

## 9. 実装計画（承認後）

1. result_log.json スキーマ+Result Recorder（CEO記入の構造化保存・書込は07_Data/results/のみ）
2. 結果待ちDecision抽出（trackableフラグ+週次一覧）
3. Brief「結果確認」セクション（ceo_assistant v1.2）
4. 実績データ照合（Events Importer連携・数値転記のみ）
5. Insight Generator v1.1（結果つきInsight生成）

## 変更履歴

| 日付 | 版 | 内容 |
|---|---|---|
| 2026-07-06 | v1.0設計 | 初版（Sprint 12・設計のみ。Decision→Action→Result→Insightの閉ループ設計） |
