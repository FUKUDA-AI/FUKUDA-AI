# PATTERN_GENERATOR_PLAN — Pattern Generator v1.0 実装計画

Version: 計画v1.0（Sprint 11・計画のみ・コード未着手）
最終更新日: 2026-07-06
状態: Draft（CEO確認待ち → 承認後に実装）
上位設計: [LEARNING_CYCLE_V2.md](LEARNING_CYCLE_V2.md) §3
学習フロー上の位置: Insight Draft → 【Pattern Draft（本機能）】 → Knowledge Generator → CEO Review

---

## 1. 入力

| 入力 | 場所 | 用途 |
|---|---|---|
| Insight Draft（v2.0・CEO判断由来） | 09_Learning/insights/insight_draft_log.json（現在10件） | 主入力 |
| 既存Insight Log（v1.3・会話由来） | 01_Knowledge/08_Decision_Log/insight_log.json（382件） | **横断カウント**（同じ思想が会話とCEO判断の両方に現れたら強い反復証拠） |
| 既存Pattern Log | 同 pattern_log.json（PTN-001〜004） | 重複判定（既存Patternの強化先） |
| EVOLVING_PRINCIPLES / CORE | 00_MASTER | 重複判定（既にEP/CORE化済みの思想は新Pattern化しない） |
| 却下記録 | lesson/principle/pattern各logのrejected+理由 | **再提案防止**（CEO却下済みと同型は生成しない） |

## 2. 出力

`09_Learning/patterns/pattern_draft_log.json` — Pattern Draft（全件 status: draft / needs_ceo_review: true）

```json
{
  "pattern_id": "PTN2-001",
  "type": "判断 | 失敗 | 成功 | 思想",
  "内容": "反復している判断・思想の記述（構成Insightの共通部のみ。推測で一般化しない）",
  "occurrence_count": 3,
  "distinct_days": ["2026-07-06", "2026-07-13", "..."],
  "contexts": ["催事", "商品企画", "..."],
  "source_insights": ["INS2-001", "..."],
  "evidence_chain": {"insights": [...], "decisions": [...], "dates": [...]},
  "related_existing": ["EP-005（類似だが閾値未満）等の参考リンク"],
  "status": "draft", "needs_ceo_review": true,
  "created_at": "...", "generator_version": "v1.0"
}
```

## 3. Pattern認定条件

1. **異なる日 × 異なる文脈で3回以上**
   - 「異なる日」= Insightのevidence（decision_dates）の**日付部分**が3日以上に分散
   - 「異なる文脈」= 関連カテゴリ（催事/商品企画/経営…）または案件が異なる
   - **同日同案件の反復は1回として数える**（同じBriefの複数判断で同じ理由が出ても1カウント）
2. 横断カウント: v2.0 Insight（CEO判断由来）とv1.3 Insight（会話由来）の類似グループは出現を合算。ただし**CEO判断由来を1件以上含むこと**を必須とする（会話だけのパターンはv1.3ルートの管轄）
3. type分類: 却下基準→「失敗（やらない）」、承認基準→「判断/成功」、思想語彙（歩みゆたかに等）→「思想」

## 4. 重複判定（LEARNING_CYCLE_V2 §7の3層を実装）

1. **同一**: source_insights構成が既存Patternと同じ → 生成しない（冪等・処理済み指紋管理）
2. **類似（強化）**: 既存Pattern（PTN/PTN2）と意味類似 ≧ 閾値 → 新規作成せず既存のoccurrence_count・evidence_chainを強化
3. **既昇格**: EP-001〜008・CORE18条と類似 ≧ 閾値 → 新Pattern化せず**EP運用記録の候補**として別出力（「EP-xxxがまた使われた」証拠 → CORE昇格材料）
4. **却下照合**: rejected記録（理由つき）と類似 → 生成しない。ただしCEOの「再整理して再提案」指示つき（PRN-010改等）は指示に従い生成対象
- 類似度: 初期実装は文字n-gram TF-IDF（pattern_analyzer.py共通ロジック再利用・実績あり）。閾値は0.35〜0.80をデータで検証して決定

## 5. Evidence構造（必須・連鎖）

```
Pattern Draft
 └─ source_insights[]（INS2-xxx）
     └─ source_decisions[]（Decision指紋）
         └─ 日時・Brief番号・根拠EP/KN
```
- Patternから元のCEO判断まで**2ホップで遡れる**ことを保証
- Evidenceが欠けたInsight（理論上存在しないが）はPattern構成から除外
- distinct_days / contexts を機械検証してから認定（自己申告でなく計算で担保）

## 6. 実装順序

1. Reader（v2.0 insights + v1.3 insights + 既存patterns + EP/CORE + 却下記録の読込）
2. 類似グルーピング（共通ロジック再利用）+ 異なる日・文脈の機械検証
3. 重複判定4種（同一・強化・既昇格・却下照合）
4. Pattern Draft生成・保存（09_Learning/patterns/のみ書込・冪等）
5. テスト: 合成Insightデータで「3日3文脈→認定」「同日反復→1カウント」「EP類似→運用記録候補行き」「却下類似→非生成」を検証
6. 実データ実行 → 文書更新（CHANGELOG/README/Memory）

## 7. リスク

| リスク | 緩和策 |
|---|---|
| **データ不足**: v2.0 Insightは現在10件・全て2026-07-06 → 「異なる日3回以上」を満たすPatternは**初回実行では0件の見込み**（正直な予測） | 仕様どおり0件で正しい。日々のBrief運用で自然に蓄積される。横断カウント（v1.3の382件）により早期に成立するPatternもあり得る |
| 文字n-gram類似の限界（言い換えを見逃す/偽陽性） | 閾値をデータ検証で調整。Pattern DraftはCEOレビュー必須なので偽陽性は却下で学習データ化 |
| 却下照合の過剰マッチ（正当な新提案まで抑制） | 却下類似は「生成しない」ではなく「抑制理由つきでログに記録」し、CEOが月次で確認できるようにする |
| v1.3とv2.0のInsightスキーマ差異 | Reader層で共通形式へ変換（本体ファイルは無変更） |
| 同日判定の粒度（日時 vs 案件） | v1.0は「日付+カテゴリ」で機械判定。案件同一性の精密判定はv1.1 |

## 8. CEOへ確認すべきこと

1. 横断カウントの必須条件「CEO判断由来を1件以上含む」でよいか（会話由来だけでもPattern化を許すか）
2. 初回実行が0件の見込みである点の了承（データ蓄積が前提の設計であり、実装は将来への投資）

## 変更履歴

| 日付 | 版 | 内容 |
|---|---|---|
| 2026-07-06 | 計画v1.0 | Sprint 11実装計画（コード未着手・CEO確認待ち） |
