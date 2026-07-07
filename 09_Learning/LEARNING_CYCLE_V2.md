# LEARNING_CYCLE_V2 — Learning Cycle v2.0 設計書

Version: v2.0設計（Sprint 9・設計のみ・実装なし）
最終更新日: 2026-07-06
状態: Draft（CEOレビュー待ち。承認後に実装Sprint・Architecture版数更新）
関連: [../00_MASTER/ARCHITECTURE.md](../00_MASTER/ARCHITECTURE.md)（v1.3）/ [../02_Rules/KNOWLEDGE_PROMOTION_RULES.md](../02_Rules/KNOWLEDGE_PROMOTION_RULES.md)

> v1.3の学習サイクルは「過去のChatGPT会話」から学んだ。
> v2.0は**CEOの日々の判断（Decision Log）そのもの**から学ぶ。
> Morning Briefで判断するたびにFUKUDA AIが賢くなる、閉じたループをつくる。

---

## 1. Learning Cycle v2.0 全体図

```
【入力】 Decision Log（CEO確定判断・判断理由・却下理由・根拠EP/KN）
   ↓ ① Insight Generator v2.0（判断から学びの種を抽出。理由未記入の判断からは作らない）
Insight Draft（09_Learning/insights/）
   ↓ ② Pattern Generator v2.0（意味的グルーピング・反復の検出・既存との重複判定）
Pattern Draft（09_Learning/patterns/）
   ↓ ③ Knowledge Generator v2.0（Knowledge IA形式へ変換・Evidence連鎖を封入）
Knowledge Draft（01_Knowledge/_drafts/）
   ↓ ④ Knowledge Review Queue（06_Reports/・CEOが承認/却下/保留）
【CEO Review】← 唯一の昇格ゲート
   ↓ 承認
Released Knowledge（Agent参照可能）
   ↓ ⑤ 実運用（利用実績の記録: Brief・Agent判断での参照）
Verified Candidate Queue（06_Reports/・機械判定で候補入り）
   ↓ ⑥【CEOのみ】Verified昇格
Verified Knowledge（会社標準）
   ↘ すべての段階の生成物・却下理由が次の学習の入力に還流
```

v1.3サイクル（会話→Insight→…→Principle→EP）は**並存**する。v2.0はDecision Log起点のKnowledge育成ルートを追加し、Verified段階までを閉じる。

## 2. Insight Generator v2.0

| 項目 | 設計 |
|---|---|
| 入力 | decision_log.json（**confirmed/確定のみ**）+ Morning BriefのCEOコメント・「AIへの気付き」欄 |
| 抽出対象 | ①判断理由に含まれる基準・思想（承認理由）②**却下理由**（何をしないか＝最も価値の高い学び）③保留理由（判断に必要だった不足情報） |
| 生成しないもの | 判断理由が「理由未記入」のdecision（**推測禁止**）/ 既存EP・CORE・Knowledgeの言い換えにすぎないもの（重複判定§7） |
| 出力 | Insight Draft（09_Learning/insights/insight_draft_log.json）: insight_id / type（承認基準・却下基準・不足情報）/ 内容 / source_decisions[] / evidence / status: draft |
| Evidence | 元Decision ID + 日付 + Brief番号（必須。無ければ生成しない） |
| 実行タイミング | 週次（週次レビューの前工程）+ 手動 |

## 3. Pattern Generator v2.0

| 項目 | 設計 |
|---|---|
| 入力 | Insight Draft（v2.0）+ 既存insight_log（v1.3・会話由来）— **両ルートを横断して反復を数える** |
| グルーピング | 意味的類似（v1.0の文字n-gramから開始し、意味解析へ強化）。件数集計ではない |
| Pattern認定 | 同一の判断・思想が **異なる日・異なる文脈で3回以上**（同日の同案件の反復は1回と数える） |
| 出力 | Pattern Draft（09_Learning/patterns/pattern_draft_log.json）: pattern_id / 内容 / 出現回数 / 初出〜最新 / source_insights[] / evidence連鎖 / status: draft |
| 特記 | CEO却下理由のパターン（「事実だけでは原則にならない」等）は**Generator改善ルール候補**としても出力する（学習の学習） |

## 4. Knowledge Generator v2.0

| 項目 | 設計 |
|---|---|
| 入力 | Pattern Draft（3回以上の反復あり）+ 実績データの確定事実（07_Data。例: 催事データから「会場Xの平均日商」） |
| 出力 | Knowledge Draft（01_Knowledge/_drafts/・**Knowledge IA v1.0の13項目フォーマット**・KN-xxx採番） |
| 変換ルール | Pattern→「判断の学び」型KN / 実績データ→「事実・数値」型KN（事実と学びを混ぜない） |
| Evidence | source_pattern → source_insights → source_decisions の**連鎖を全て封入**（KNから元判断まで遡れる） |
| 禁止 | Released領域への直接書込（_draftsのみ）/ Evidenceなし生成 / 推測による補完 |

## 5. 昇格条件（段階別）

| 遷移 | 条件 | 決定者 |
|---|---|---|
| Decision → Insight Draft | 判断理由が記録されている | 機械（自動） |
| Insight → Pattern Draft | 異なる日・文脈で3回以上反復 | 機械（自動） |
| Pattern → Knowledge Draft | Evidence連鎖完備 + 重複判定通過 | 機械（自動） |
| **Knowledge Draft → Released** | **CEO Review（Knowledge Review Queue経由）** | **CEOのみ** |
| Released → Verified Candidate | 機械判定の目安: released後**180日以上** + **利用実績3回以上**（Brief/Agent判断での参照記録）+ 矛盾・訂正ゼロ | 機械（候補入りのみ） |
| **Verified Candidate → Verified** | **CEO承認** | **CEOのみ。AIは昇格しない** |

## 6. 必要Evidence（全段階必須）

- Insight: 元Decision ID・日付・Brief番号
- Pattern: source_insights[]（3件以上）・出現期間
- Knowledge: Evidence連鎖（pattern→insights→decisions）+ 出典データ（実績型はレコードID）
- Verified Candidate: 利用実績ログ（いつ・どの判断・どのBriefで参照されたか）
- **Evidenceのない生成物はどの段階でも作らない**（AI_CHARTER第2条）

## 7. 重複判定（3層）

1. **同一判定**: source ID・内容ハッシュが同じ → 生成しない（冪等）
2. **類似判定**: 既存のInsight/Pattern/KN/EP/COREと意味類似度が閾値超え → 新規作成せず**既存項目のEvidenceを強化**（evidence_count+1・最新日更新）。反復の証拠として蓄積され、Verified/CORE昇格の材料になる
3. **却下照合**: CEOがrejectしたものと同型 → 再提案しない（却下理由DBと照合）。ただし却下時に「再整理して再提案」指示があるものは指示に従う（例: PRN-010改）

## 8. Morning Briefとの連携

- CEO入力欄の「AIへの指示・気付き」→ Insight Draft候補として自動収集
- Knowledge Review Queue / Verified Candidate Queueの件数と最優先1件を「📋レビュー待ち」に表示
- 週次レビューでキューをまとめて消化（日次のCEO負荷を増やさない）
- Briefで使った根拠EP/KNの記録が§5の「利用実績」になる（**Briefを使うほどVerifiedが育つ**）

## 9. Decision Logとの連携

- 入力: status=confirmed のみ（Draft判断からは学ばない）
- 却下・保留の理由は最優先の学習素材（判断基準の輪郭は「やらない」側に現れる）
- 学習済みDecisionには `learned_at` を記録（再学習の重複防止・増分処理）
- CEO判断がEP運用記録と突合され、どのEPが実際に使われているかがCORE昇格判定の材料になる

## 10. Knowledgeとの連携

- 生成はKnowledge IA v1.0に完全準拠（カテゴリ11分類・KN-xxx・knowledge_index.json再生成）
- Released/Verifiedの利用実績を`usage_log`として記録（Verified Candidate判定の入力）
- Verifiedへ昇格したKNは矛盾するreleased KNより優先（Lifecycle準拠）。矛盾検出時はCEOへ報告

## 11. 将来Agent全体へ反映する方法

1. **即時反映（実装不要）**: 全Agentはknowledge_index.json経由でreleased/verifiedのみ参照する設計のため、**KNがreleasedになった瞬間、全Agentの判断根拠に自動で加わる**（再学習・再デプロイ不要）
2. **原則の反映**: EP/COREは00_MASTER参照のため同様に即時反映
3. **週次ダイジェスト（v2.1）**: 「今週増えたKnowledge・変わった原則」を各Agent向けに要約し、Agent定義の関連カテゴリごとに通知
4. **Agent提案の還流（v2.2）**: Agent提案の採否がDecision Logへ記録される → 本サイクルで学習 → **Agentの提案精度自体が学習対象になる**（採用率の低いAgentの改善点をPatternとして検出）
5. **矛盾の自動検出（v2.2）**: 新Verified/CORE と既存Agent定義・SOPの矛盾をスキャンしCEOへ報告

## 12. 実装順（承認後の実装Sprint案）

1. Insight Generator v2.0（Decision Log→Insight Draft。データが既に30件ある）
2. Knowledge Review Queue自動生成（既存キュー形式の機械化）
3. Pattern Generator v2.0（v1.3のpattern_analyzerを拡張・両ルート横断）
4. Knowledge Generator v2.0（knowledge_builderの汎用化）
5. 利用実績ログ + Verified Candidate Queue（180日ルールのため実稼働は2027-01以降）

## 変更履歴

| 日付 | 版 | 内容 |
|---|---|---|
| 2026-07-06 | v2.0設計 | 初版（Sprint 9・設計のみ。Decision Log起点の自動学習+Verifiedまでの閉ループ） |
