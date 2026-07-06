# KNOWLEDGE_PROMOTION_RULES — Knowledge昇格ルール

Version: v1.0
最終更新日: 2026-07-06
状態: Released
上位文書: [../00_MASTER/AI_CHARTER.md](../00_MASTER/AI_CHARTER.md) / [../00_MASTER/ARCHITECTURE.md](../00_MASTER/ARCHITECTURE.md)

> AIが生成した知見が正式Knowledgeになるまでの唯一のルートを定める。
> このルールに反する書き込み・昇格は、Development Standard違反として差し戻す。

---

## 1. 状態管理

```
draft（AI生成） → in_review（CEOレビュー中） → released（正式Knowledge）
                                             → rejected（却下・理由つきで保存）
```

## 2. 原則（7か条）

1. **Insight / Decision / Pattern / Lesson はすべて draft である。** 生成された時点では正式Knowledgeではない
2. **AIは正式Knowledgeへ直接書き込まない。** AIの書き込み先は `01_Knowledge/_drafts/` と `06_Reports/` に限定する（AI_CHARTER第5条）
3. **EVOLVING_PRINCIPLES もAIが勝手に CORE_PRINCIPLES へ昇格させない。** 昇格はCEOレビューのみ
4. **CEO Review を通過したものだけが released になる。** 承認ゲートはCEOただ一人
5. **Rejected も理由つきで残す。** 却下理由はAIの生成精度改善の学習データとして資産化する
6. **Agentは released のKnowledgeのみ参照する。**（ただし07_Dataの実績データは常時参照可。昇格制の対象は「解釈・思想」）
7. **DraftはAgentの通常判断に使わない。** Experimentalな出力・draft状態の知見を経営判断に直接使わない（Development Standard §4と同旨）

## 3. フロントマター（Knowledgeファイルの状態管理）

```yaml
status: draft | in_review | released | rejected
source: Conversation ID / pattern_id 等の出典
created: YYYY-MM-DD
reviewed: YYYY-MM-DD
reviewer: CEO
rejected_reason: （rejectedの場合のみ）
```

JSONログ（pattern_log.json等）では `status` / `needs_ceo_review` フィールドで同等の管理を行う。

## 4. レビュー運用

- レビュー依頼は `10_AI_Memory/PENDING.md` に一覧化する（重要度順）
- Draft大量発生時は重要度「高」のみ先行レビューし、閾値以下は保留とする（CEOレビューのボトルネック緩和）
- CEOの承認・却下があったとき、AIは即時に対象ファイルの状態とPENDING.mdを更新する

## 5. 対象範囲

| 対象 | draft置き場 | released置き場 |
|---|---|---|
| Insight / Decision / Pattern | 01_Knowledge/08_Decision_Log/*.json（status管理） | 同左（status: released） |
| Lesson（将来） | 01_Knowledge/_drafts/ | 01_Knowledge/該当カテゴリ |
| 判断基準の仮説 | 00_MASTER/EVOLVING_PRINCIPLES.md | 00_MASTER/CORE_PRINCIPLES.md（CEO改定のみ） |
| Agent提案の知見 | 01_Knowledge/_drafts/ | 昇格フロー経由 |
