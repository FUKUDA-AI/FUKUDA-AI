# 10_AI_Memory — AI作業記憶（Memory Layer）

## 目的
新しいセッションでもFUKUDA AIが前回の状態から再開できるようにする。
MemoryはKnowledgeを複製せず、**現在の作業状態だけ**を保持する（常に上書き更新・履歴は持たない）。

## Version
AI Memory Layer v1.0 [Released]

## 最終更新日
2026-07-06

## 構成（3ファイル固定）

| ファイル | 内容 |
|---|---|
| [CURRENT_STATE.md](CURRENT_STATE.md) | 現在Phase・現在Sprint・現在Version・実装済み機能・次に行う作業 |
| [NEXT.md](NEXT.md) | 次Sprintで行う作業 |
| [PENDING.md](PENDING.md) | CEOレビュー待ち・未確定事項・保留事項 |

## Session Start Protocol（参照順）

```
1. 00_MASTER（README.mdの読込順11文書）
2. AI Memory（本フォルダ: CURRENT_STATE → NEXT → PENDING）
3. Knowledge（01_Knowledge・statusがreleasedのもの）
4. Task（当該セッションの作業）
```

## 更新ルール

- **Sprint終了時に必ず更新**: CURRENT_STATE / NEXT / PENDING + ROADMAP + CHANGELOG（Sprint Close 3点セット）
- **即時更新イベント**: CEOの承認・却下・方針指示 / 作業ブロック / セッション中断の可能性
- **信頼順位**: CHANGELOG・ROADMAP（正） > Memory（作業用キャッシュ）。矛盾時はMemoryを修正してから作業開始
- 書き込みはAIが直接行ってよい（CEOレビュー不要）。ただし本フォルダ以外への書き込みには使わない

## 依存関係
- 参照: 00_MASTER/ROADMAP.md / CHANGELOG.md（一次情報。Memoryは複製しない）
- Layer: ④Memory Layer（5層構造）。全層の進行状態を保持し、内容は保持しない
