# 01_Knowledge — NOMADO株式会社 知識ベース

> 目的: NOMADO株式会社の全知識を蓄積し、FUKUDA AIの全エージェントが判断の根拠として参照する。
> 原則: 推測で埋めない。出典・日付を明記する。不足はTODOで残す。

## Version
Knowledge Information Architecture v1.0（2026-07-06 設計・以下IA）

## 最終更新日
2026-07-06

---

# Knowledge Information Architecture v1.0

数千件規模になってもAIが高速に検索・参照できることを目的とした構造設計。
**Knowledge Builder v1.0以降のすべての生成はこの構造に従う。**

## 1. 検索の基本設計（索引ファースト）

AIは全ファイルを読まない。**必ず索引 → 本文の2段階で参照する。**

```
1. 01_Knowledge/knowledge_index.json を読む（全Knowledgeのメタ情報一覧）
2. Category / Brand / Status / キーワードで絞り込む
3. 該当するKnowledgeファイルだけを開く
```

- `knowledge_index.json` はKnowledge Builderが自動生成・再生成する（手動編集禁止）
- AgentはStatus: released のみを参照対象とする（KNOWLEDGE_PROMOTION_RULES準拠）
- 将来拡張: 件数が1,000件を超えたらカテゴリ別索引への分割、意味検索（埋め込み）の導入を検討（TODO）

## 2. カテゴリ体系（11分類）

| コード | カテゴリ | 物理フォルダ | 内容 |
|---|---|---|---|
| BRD | ブランド | 01_Brands | ブランド思想・世界観・表現ルール（自社ブランドごとにサブフォルダ） |
| PRD | 商品 | 02_Products | 商品仕様・素材・製法・価格・開発判断 |
| EVT | 催事 | 05_Events | 催事場・売上実績・出店判断・設営 |
| SLS | 営業 | 10_Sales | 取引先・卸・見積・商談知識 |
| MKT | マーケティング | 04_Marketing | 広告・SEO・SNS・EC運営 |
| MFG | 製造 | 07_Operations | 工場・職人・リードタイム・品質管理 |
| CS | 顧客対応 | 03_Customers | 顧客理解・対応方針・レビュー |
| FIN | 財務 | 06_Finance | 資金繰り・粗利・コスト構造 |
| LGL | 法務 | 11_Legal | 知財・契約・規約 |
| AI | AI | 12_AI | FUKUDA AI自身の運用知識 |
| SOP | SOP | ../04_SOP | 手順書（物理はルート04_SOP。索引には含める） |

- 10_Sales / 11_Legal / 12_AI はKnowledge Builder v1.0の初回実行時に作成する（既存フォルダは変更・削除しない）
- 08_Decision_Log（ログ原本）と09_ChatGPT_Archive（アーカイブ）は「Knowledgeの供給源」であり、索引の対象外
- AI生成のdraftは `01_Knowledge/_drafts/` に置き、CEO承認後に各カテゴリへ移動する（昇格フロー）

## 3. Knowledge ID体系

```
KN-<カテゴリコード>-<連番4桁>   例: KN-EVT-0001（駅系催事の売上実績）
```

- IDは一度発番したら再利用しない（rejectedになっても欠番として残す）
- ファイル名 = `KN-EVT-0001_駅系催事の売上実績.md`（ID + 短いタイトル）

## 4. 共通フォーマット（全Knowledge必須）

Markdownファイル + YAMLフロントマターで管理する。

```markdown
---
knowledge_id: KN-EVT-0001
title: 駅系催事の売上実績
category: 催事          # 11分類のいずれか
brand: 全社             # 全社 / SUNNY NOMADO / so u / Dr.Nomado / （支援先名）
summary: 駅系催事場の平均売上は30万円。判断の土台となる実績数値。
related_principle: [EP-005]
related_lesson: [LSN-003]
related_pattern: []
evidence: [Conversation ID / 出典文書 / 日付]
last_reviewed: 2026-07-06
version: v1.0
status: released        # draft / in_review / released / rejected
reviewer: CEO
---

## Body
（本文。事実・数値・文脈。推測は書かない）
```

- **Related Principle/Lesson/Pattern** で学習サイクルとの双方向リンクを保つ（EPの運用記録にも反映可能になる）
- **Evidence** は必須。出典のないKnowledgeは作らない（AI_CHARTER第2条）
- ブランド支援案件のKnowledgeは brand にクライアント名を入れ、所有者を混同しない（COMPANY_PROFILE 3-B）

## 5. knowledge_index.json 仕様

```json
{
  "meta": {"generated_at": "...", "generator": "Knowledge Builder vX.X", "total": 0},
  "knowledge": [
    {"knowledge_id": "KN-EVT-0001", "title": "...", "category": "催事",
     "brand": "全社", "summary": "...", "status": "released",
     "path": "05_Events/KN-EVT-0001_駅系催事の売上実績.md",
     "related_principle": ["EP-005"], "last_reviewed": "2026-07-06"}
  ]
}
```

## 6. 既存構成との対応

| フォルダ | 内容 | IA上の位置づけ |
|---|---|---|
| 01_Brands〜07_Operations | 既存カテゴリフォルダ | §2の通りカテゴリへ対応（変更なし） |
| 08_Decision_Log | Insight/Decision/Pattern/Lesson/Principleログ | 供給源（索引対象外） |
| 09_ChatGPT_Archive | 過去ログ | 供給源（索引対象外） |
| _drafts | AI生成draft置き場 | Builder初回実行時に作成 |

---

## 関連機能
- Knowledge Builder v1.0（Phase 6・次Sprint）— 本IAに従って生成・索引再生成を担当
- ChatGPT Importer v1.1 [Released]（09_ChatGPT_Archive を入力とする）

## 依存関係
上位文書: [KNOWLEDGE_PROMOTION_RULES](../02_Rules/KNOWLEDGE_PROMOTION_RULES.md) / [ARCHITECTURE.md](../00_MASTER/ARCHITECTURE.md)（③Knowledge Layer）

## 今後のTODO
- Knowledge Builder v1.0の実装（承認済みLesson 11件の転記から開始）
- 1,000件超え時の索引分割・意味検索の導入検討
