# CURRENT_STATE — AI作業記憶

最終更新: 2026-07-06（更新者: AI）

## 現在位置

- **Phase**: 7 Lessons Learned / Principle（Experimental運用中）
- **直近Sprint**: EVOLVING登録Sprint v1.0 — **EP-001〜008運用開始**（EVOLVING_PRINCIPLES.md v0.2）。学習サイクル（Conversation→…→Principle→CEO Review→EVOLVING）が初めて一巡した。2026-07-06
- **次の着手可能作業**: Knowledge Builder v1.0（Phase 6）— **Knowledge IA v1.0（01_Knowledge/README.md）設計済み**。11カテゴリ・KN-xxx ID・共通フォーマット13項目・knowledge_index.json索引に従って実装する
- **Architecture**: **v1.2（正式・00_MASTER/ARCHITECTURE.md）**

## 実装済み機能（詳細はCHANGELOGを正とする）

| 機能 | Version | 状態 |
|---|---|---|
| ChatGPT Importer | v1.1 | Released |
| Conversation Index | v1.0 | Released（3,323件） |
| Insight Extractor | v2.0 | Experimental（382件） |
| Decision Extractor | v2.0 | Experimental（20件） |
| Pattern Analyzer | v1.0 | Experimental（4件・全draft） |
| Lesson Generator | v1.0 | Experimental（23件・レビュー済み: released11/rejected11/hold1） |
| Principle Generator | v1.0 | Experimental（10件・全draft） |
| AI Memory Layer | v1.0 | Released |
| Architecture | v1.3 | Released（Principle層新設） |
| Architecture | v1.2 | Released（ARCHITECTURE.md） |
| Knowledge昇格ルール | v1.0 | Released（02_Rules/KNOWLEDGE_PROMOTION_RULES.md） |
| 00_MASTER文書群（11文書） | v0.x | Draft・CEOレビュー待ち |

## 保存先ルール（重要）

- Decision / Insight / Pattern の正式保存先: `01_Knowledge/08_Decision_Log/`（Extractor v2.0で出力先変更済み）
- ルート `08_Decision_Log/` は不使用。99_Archive移動を提案中（CEO承認待ち）

## 次に行う作業

[NEXT.md](NEXT.md) を参照。最優先はCEOレビュー（PENDING.md）の消化とLesson Generator設計。
