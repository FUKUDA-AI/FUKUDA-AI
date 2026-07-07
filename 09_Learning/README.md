# 09_Learning — Learning Cycle v2.0（学習サイクル作業領域）

## 目的
CEOの判断（Decision Log）からFUKUDA AIが自動で学ぶLearning Cycle v2.0の設計・生成物を管理する。
**Morning Briefで判断するたびにFUKUDA AIが賢くなる**閉ループの中間生成物置き場。

## Version
Learning Cycle v2.0（設計のみ・2026-07-06。実装はCEOレビュー後）

## 最終更新日
2026-07-06

## 構成（実装後）

| 場所 | 内容 | 状態 |
|---|---|---|
| [LEARNING_CYCLE_V2.md](LEARNING_CYCLE_V2.md) | 設計書（全体図・Generator3種・昇格条件・重複判定・連携） | Draft・CEOレビュー待ち |
| [RESULT_LAYER_DESIGN.md](RESULT_LAYER_DESIGN.md) | Result Layer設計（Decision→Action→Result→Insight。判定はCEOのみ） | Draft・CEOレビュー待ち（Sprint 12） |
| `insights/insight_draft_log.json` | Insight Draft（CEO確定判断由来） | **稼働中**（Insight Generator v1.0・`python3 insight_generator.py`） |
| `patterns/pattern_draft_log.json` | Pattern Draft（CEO承認4条件+3回以上を機械検証） | **稼働中**（Pattern Generator v1.0・`python3 pattern_generator.py`。初回0件=設計どおり） |

Knowledge Draftは従来どおり `01_Knowledge/_drafts/`、レビューキューは `06_Reports/` に生成する（既存フローと同じ場所・同じ作法）。

## 鉄則

- AIは勝手に昇格しない（Draft→ReleasedはCEO Review、Released→Verified CandidateはCEO承認のみ）
- ReleasedとVerifiedだけがAgentの参照対象
- 全生成物にEvidence連鎖必須（KNから元のCEO判断まで遡れる）
- 推測禁止（判断理由が未記入のDecisionからは学ばない）
- 却下されたものは再提案しない（却下理由は学習データとして保存）

## 依存関係
- 入力: 01_Knowledge/08_Decision_Log/decision_log.json（confirmedのみ）・Morning Brief CEO入力欄
- ルール: 02_Rules/KNOWLEDGE_PROMOTION_RULES.md / Knowledge IA v1.0
- 出力先: 01_Knowledge/_drafts/ / 06_Reports/（キュー2種）

## 今後のTODO
- 設計のCEOレビュー
- 実装Sprint（順序: Insight Generator → Review Queue自動生成 → Pattern → Knowledge Generator → Verified Candidate）
