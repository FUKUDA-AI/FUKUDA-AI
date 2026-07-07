# RESULT_LAYER_V11 — Result Layer v1.1 設計書（2層構造）

Version: v1.1設計（Sprint 15.3・設計のみ・コードなし）
最終更新日: 2026-07-07
状態: Draft（CEOレビュー待ち）
前版: [RESULT_LAYER_DESIGN.md](RESULT_LAYER_DESIGN.md)（v1.0・Result Recorder v1.0で実装済み）

> **「実行できたか」と「経営的に成功したか」は別物である。**
> 工場打ち合わせは実施できた（実行=成功）。しかし納期遅延・品質問題・利益悪化なら経営=失敗。逆もある。
> v1.1はResultをこの2層に分け、Learning Cycleの精度を上げる。

---

## 1. 全体フロー（v1.1）

```
Decision（CEO確定判断）
   ↓ 実行
Action（誰が・いつ・何をしたか）
   ↓
【Action Result】  「判断したことを実行できたか」   … 実行の成否
   ↓ 時間経過・事実の発生
【Business Result】「その判断は経営として成功だったか」… 経営の成否
   ↓ learning_ready=true のBusiness Resultのみ
Insight → Pattern → Knowledge（既存Learning Cycle）
```

**実例（Result初号・v1.0からの読み替え）**:

| | Action Result | Business Result |
|---|---|---|
| RES-0001 工場打ち合わせ | **成功**（打ち合わせ実施・認識合わせ完了） | **継続観察**（納期・品質・生産結果はこれから） |
| RES-0002 催事搬入確認 | **成功**（会期開始に支障なく搬入完了） | **継続観察へ読み替え可**（催事全体の売上成果は会期終了後） |

→ v1.0では1つのstatusに押し込めていた「実行は済んだが結果待ち」が、v1.1では自然に表現できる。

## 2. Action Result（実行結果）

**目的**: 「判断したことを実行できたか」

| 項目 | 内容 |
|---|---|
| action_result_id | ARES-xxxx |
| decision_fingerprint | 元Decisionへの遡及リンク（必須） |
| **status** | **成功 / 失敗 / 延期 / 保留**（4分類・**CEOのみ確定**） |
| 実行日 | action_date |
| what | 何を実行したか（事実） |
| actor | 実行者 |
| **Evidence** | 実行の事実（FOS完了記録・CEO記入+日付。**必須**） |

- 判定時期: 実行直後（review_after_daysを待たない。「やったか」はすぐ分かる）
- 延期/保留が続く判断は**実行率の問題**としてBriefに再掲する

## 3. Business Result（経営結果）

**目的**: 「その判断は経営として成功だったか」

| 項目 | 内容 |
|---|---|
| business_result_id | BRES-xxxx |
| action_result_id / decision_fingerprint | 遡及リンク（必須） |
| **status** | **成功 / 失敗 / 継続観察**（3分類・**CEOのみ確定**） |
| 評価日 | result_date（判断日+review_after_daysが目安） |
| expected_result | 判断時の期待（FOS Metadataから引き継ぎ） |
| actual_result | 実際に起きたこと（CEO記入/実績データ） |
| **数値** | 利益 / 売上 / ROI（出典必須・実績データ優先） |
| **定性** | ブランド価値 / 顧客満足 / 運営負荷（CEO評価） |
| 成功要因 / 失敗要因 | CEOの分析（AIは書かない） |
| **Evidence** | 実績データID（EventRecord/SalesRecord等）/ CEO記入+日付（**必須**） |
| learning_ready | status確定（成功/失敗）+ Evidence完備で機械がtrue化 |

- CORE第2条の優先順位（現金化→粗利→ブランド→顧客満足→効率→資産化）と評価軸を揃える

## 4. Learning Rule（v1.1・学習対象の分離）

| Result | 学習での扱い |
|---|---|
| **Business Result** | **Insight Generatorの唯一の学習対象**（成功→成功要因Insight / 失敗→失敗要因Insight=最重要 / 継続観察→生成しない） |
| **Action Result** | Insight生成には**使わない**。用途: ①**実行率分析**（判断のうち何%が実行されたか・延期/保留の傾向）②**運営改善**（実行が遅れる判断の型の発見）③**SOP改善**（失敗した実行の手順見直し・EP-006準拠） |

→ 「実行できた」だけの事実が経営の学びとして昇格することを防ぐ（Learning Cycleの精度向上）。

## 5. Dashboard変更（CEO_DASHBOARD.md §5の分割）

Result Reviewを2つに分割する。

| セクション | 内容 |
|---|---|
| **④-1 Action Review** | 実行待ち/実行済みの判断一覧・実行率・延期/保留の再掲（判定: 成功/失敗/延期/保留） |
| **④-2 Business Review** | 評価期日が来た判断のexpected vs actual・数値・判定（成功/失敗/継続観察）・継続観察中リスト |

## 6. Knowledge Rule（3種Evidence）

Knowledge（KN-xxx）は以下の3種のEvidenceを保持する。

| Evidence | 内容 | 意味 |
|---|---|---|
| Decision Evidence | 根拠にした判断（decision_fingerprint） | 「どの判断から生まれた知識か」 |
| Action Result Evidence | ARES-xxxx | 「その判断は実行されたか」 |
| Business Result Evidence | BRES-xxxx | 「実行されて、**効いたか**」（Verified昇格の最上級証拠） |

- Verified昇格条件（KNOWLEDGE_PROMOTION_RULES）は将来「Business Result Evidence=成功が付いていること」を要件に加える（v1.0設計§8の強化を2層で精密化）

## 7. CEO Rule

- **Action Result / Business Result どちらもCEOのみが確定する。AIは推測しない**
- AIが書けるのは: 事実の転記（実行日・出典）・引き継ぎ（expected_result等）・記入欄の準備・期日の検知のみ

## 8. Result Recorder変更点（v1.1実装時・今回はコード変更なし）

1. Draft生成を2段化: 実行検知→**Action Result Draft**（即時判定依頼）→ 確定後に**Business Result Draft**（review_after_days経過で判定依頼）
2. result_draft_log.json / result_log.json のレコードに `layer: action | business` を追加（**既存2件は削除せず互換読み替え**: RES-0001→ARES成功+BRES継続観察 / RES-0002→ARES成功+BRES継続観察or成功=CEO確認）
3. index.jsonのcheck_dueを Action待ち / Business待ち に分離（Dashboard §④-1/④-2の参照元）
4. ceo_assistant / dashboard_generator の表示分割（§5）
5. Insight Generator v1.1: learning_ready=trueの**Business Resultのみ**読む

## 9. 移行方針（既存データ互換）

- 既存result_log.json 2件は削除・書き換えしない。v1.1実装時にlayerフィールドを解釈で補う読み替え表を持つ（正本は既存記録のまま）
- RES-0002の「成功」は**Action Result=成功**として読み替え、Business Result（催事売上の成果）は会期終了後にCEOが別途判定 — 読み替えの確定はCEO確認後

## 変更履歴

| 日付 | 版 | 内容 |
|---|---|---|
| 2026-07-07 | v1.1設計 | 初版（Sprint 15.3・設計のみ。Action Result / Business Resultの2層化・Learning Rule分離・Dashboard分割・Knowledge 3種Evidence） |
