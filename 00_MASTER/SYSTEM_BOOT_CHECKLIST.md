# SYSTEM_BOOT_CHECKLIST v1.0 — Task開始前チェックリスト

**運用チェック専用（設計書ではない）。** Claude CodeがTask開始前に最低限確認する。
読込ルールの正本は [SYSTEM_BOOT.md](SYSTEM_BOOT.md)。

```
□ SYSTEM_BOOT読込      （BIOS＝読込ルールを把握したか）
□ MASTER読込           （必読10文書。矛盾時は読込順の小さい文書が正）
□ Memory読込           （CURRENT_STATE / NEXT / PENDING のみ。Version・Phase・SprintはCURRENT_STATEで確認）
□ Agent決定            （このTaskに必要なAgentは1つだけ読んだか）
□ Knowledge取得        （knowledge_index.json経由・released/verifiedのみ・draft禁止）
□ Data取得             （必要なindexのみ・事実のみ・意味づけ禁止）
□ AI_CHARTER確認       （実行しない・CEOが唯一の承認ゲート・書込先制限）
□ 推測禁止確認         （不足データは「不足」と明示してCEOへ確認する準備があるか）
□ Evidence確認         （生成・昇格・提案に根拠IDを付けられるか）
□ Task開始
```

## 使い方

- 毎Task開始前に上から順に確認する（数十秒で終わる粒度を維持する）
- チェックできない項目が1つでもあれば、Taskを開始せずCEOへ確認する
- 本ファイルは増やしすぎない（10項目を超える追加はCEO承認後のみ）

## 変更履歴

| 日付 | 版 | 内容 |
|---|---|---|
| 2026-07-07 | v1.0 | 初版作成（Sprint 14.3.1・SYSTEM_BOOT v1.1のBIOS化に伴う運用チェックリスト新設） |
