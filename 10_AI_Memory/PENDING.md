# PENDING — CEOレビュー待ち・未確定事項・保留事項

最終更新: 2026-07-06（更新者: AI）

## CEOレビュー待ち

| # | 項目 | 場所 | 優先 |
|---|---|---|---|
| 1 | ~~00_MASTER思想文書8本のDraft承認~~ ✅ 2026-07-06 CEO承認・v1.0昇格済み（Brief#1判断2） | — | 完了 |
| 2 | ~~Pattern 4件 + Lesson 23件のレビュー~~ ✅ 2026-07-06 CEO記入済み・status反映済み | — | 完了 |
| 2b | ~~Principle 10件のレビュー~~ ✅ 2026-07-06 CEO判断済み（Approve8: PRN-001〜008 / Hold2: PRN-009継続観察・PRN-010再整理）→ **EVOLVING登録SprintがAI側の次作業** | — | 完了 |
| 2c | ~~PTN-003/LSN-004のhold解消~~ ✅ 2026-07-06 CEO承認・released化済み（Brief#2判断2） | — | 完了 |
| 2e | **PRN-010改「経営判断は売上だけでなく、利益・ブランド価値・運営負荷・将来性を総合的に判断する」を次回Principle Generator実行時に候補として再提案**（CEO指示・Brief#2判断3）。LSN-011はそれまでhold継続 | principle_generator.py TODO | 中 |
| 2d | ~~EVOLVING_PRINCIPLES.mdの学習サイクル図v1.3更新~~ ✅ 2026-07-06 EVOLVING登録Sprintで実施（CEO指示に含まれていたため） | — | 完了 |
| 2f | PRN-009の継続観察: SUNNY NOMADO / so u / MIRAI UP / 今後のブランドで「職人の目と実物で判断」の反復を確認したら再提案 | principle_log.json | 低（観察） |
| 2g | ~~Knowledge/SOP Draft 13件のレビュー~~ ✅ 2026-07-06 CEO判断・released化完了（released 12 / hold 1） | — | 完了 |
| 2i | KN-SOP-0003（催事設営チェックリスト）の実運用 → 数回運用し成熟したらReleased昇格をCEOへ提案 | 04_SOP/_drafts/ | 中（観察） |
| 2h | ~~設計6文書のレビュー~~ ✅ 2026-07-06 CEO一括承認・Released化済み（Brief#1判断1） | — | 完了 |
| 6 | ~~Gitロック解除+コミット~~ ✅ 2026-07-06 CEO実施・**GitHubへのPush完了**（origin: FUKUDA-AI/FUKUDA-AI） | — | 完了 |
| 3 | 旧CEO_PRINCIPLES.mdの99_Archive移動可否 | 00_MASTER/CEO_PRINCIPLES.md | 中 |
| 4 | ルート08_Decision_Log/の99_Archive移動可否（**Extractor v2.0完了済み・移動提案中**） | 08_Decision_Log/ | 中 |
| 5 | Insight/Decision Extractor のReleased昇格 | CHANGELOG参照 | 中 |

| 7 | **Learning Cycle v2.0設計のレビュー**（09_Learning/LEARNING_CYCLE_V2.md。承認で実装Sprint開始・Architecture v1.4へ） | 09_Learning/ | 高 |
| 8 | 催事データの投入（07_Data/events/raw/へExcel/CSV。置くだけで取込可能） | CEO作業 | 高 |
| 9 | ~~FOS-data.json配置~~ ✅ 2026-07-07 配置完了→FOS Connector v1.0稼働（TaskRecord34件・Brief接続済み） | — | 完了 |

| 10 | **so u発注量の判断材料（Brief#3判断3・Hold）**: ①前回と今回の販売条件の比較（会場・時期・広告・在庫リスク）②上限予算額の確認 → 揃い次第B案方向で再判断。**FOS側にも確認タスクの追加を推奨（CEO操作）** | CEO確認 → 次回Brief | 高 |
| 11 | ~~工場打ち合わせResult初号~~ → **RES-0001として記録済み（2026-07-07・継続観察）**。残: 打ち合わせメモ受領でEvidence補完+納期/品質/生産結果が出た時点で最終判定（成功/失敗） | CEO任意 | 低 |

## 未確定事項（データ不足TODO）

- COMPANY_PROFILE: 従業員数・決算期・財務数値・顧客データ・知財登録番号
- ~~COMPANY_PROFILE: MIRAI UPの位置づけ~~ ✅ 2026-07-06解消（所有者=株式会社ベルタ・NOMADOは支援プロジェクト。3-B分類へ記載済み）
- CORE_PRINCIPLES: 数値基準（現金化日数・粗利率最低ライン・投資上限）
- BUSINESS_PHILOSOPHY: 各ブランド哲学の詳細・10年後/30年後の会社像

## 保留事項

- **Gitロックファイルの削除（要CEO作業）**: サンドボックスはマウントフォルダ内のファイル削除ができず、gitの一時ロックが残留。v1.0.0タグとコミット(f838519)は正常だが、以後のコミットがブロックされている。CEOのMacでターミナルから以下を実行すると解消する:
  ```
  cd ~/Claude/Projects/FUKUDA\ AI
  rm .git/HEAD.lock .git/index.lock .git/index-v2.lock
  git add -A && git commit -m "docs: v1.0.0リリース記録・FUKUDA AI誕生日"
  ```
  （CHANGELOG・IDENTITYへの誕生日記録はファイルとして保存済み。未コミットなだけ）

- Brand Constitution原本（docx）のプロジェクト内保存場所の指定（現状アップロード領域のみ）
- 憲法第9条【内部限定】事項のAgent参照可否ルール化
- 定型文対策の強化（PTN-003は定型文疑い。Pattern Analyzerの意味解析化と合わせて検討）
