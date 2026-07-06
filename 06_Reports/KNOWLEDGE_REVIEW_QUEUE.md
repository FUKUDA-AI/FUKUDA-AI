# KNOWLEDGE_REVIEW_QUEUE — Knowledge Draft レビューキュー

作成日: 2026-07-06（Knowledge Review Sprint v1.0）
対象: Knowledge Draft 10件 + SOP Draft 3件 = **13件**（全件 status: draft）
入力: 01_Knowledge/knowledge_index.json / 01_Knowledge/_drafts/ / 04_SOP/_drafts/

> **使い方**: CEOは「CEO判断」欄に approve / reject / hold を記入する。
> AIはReleased化・ファイル移動を行っていない。承認分は次Sprintでカテゴリフォルダへ移動しreleased化する（そこで初めてAgentが参照可能になる）。
> AI推奨の集計: approve 12件 / hold 1件 / reject 0件
> **CEO判断（2026-07-06記入済み・反映済み）: Approve 12件 → released化完了 / Hold 1件（KN-SOP-0003: 実運用で成熟後にReleased昇格）**
> ※全13件はCEO承認済みLesson由来のため大半がapprove推奨。reject候補はLessonレビュー時点で既に除外済み。

---

| 優先 | ID | 種別 | タイトル | カテゴリ | ブランド | 要約 | 根拠EP | 根拠Lesson | 根拠Pattern | Evidence | AI推奨 | AI推奨理由 | 反映先 | CEO判断 | CEOコメント |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | KN-BRD-0001 | Knowledge | ブランド発信の核 — 歩みゆたかに×作り手の情熱・ストーリー | BRD | 全社 | 全ブランドの発信は「歩みゆたかに」と情熱・ストーリーを軸に語る | EP-001 | LSN-001 | PTN-001 | 6会話（2024-08〜2026-04）+CEO承認 | **approve** | EP-001と完全整合・最多Evidence。全AgentQが参照すべきブランド発信の基準 | 01_Brands（released化） | ✅ Approve |  |
| 2 | KN-EVT-0001 | Knowledge | 駅系催事の売上実績 — 平均30万円 | EVT | 全社 | 駅系催事場の平均売上30万円。出店判断の土台数値 | EP-005 | LSN-003 | — | Conversation記録+CEO「催事AIの判断基準として利用」 | **approve** | 唯一の実績数値つきKnowledge。催事AIの中核参照データ | 05_Events（released化） | ✅ Approve |  |
| 3 | KN-CS-0001 | Knowledge | so u標準対応 — 手紙を職人と共有し最速でお手元へ | CS | so u | お客様の想いを職人へ共有し心を込めて最速納品 | EP-002 | LSN-002 | PTN-002 | 5会話（2023-06〜2026-07）+CEO承認 | **approve** | EP-002の実務展開。so u対応の一貫性を支える | 03_Customers（released化） | ✅ Approve |  |
| 4 | KN-SOP-0001 | SOP | so u顧客対応プロセス — 手紙共有・最速納品 | SOP | so u | 手紙受領→職人共有→製作→丁寧な連絡の4段階 | EP-002 | LSN-002 | PTN-002 | 同上 | **approve** | KN-CS-0001の手順化。SOP化できる（CEO「標準対応として残す」） | 04_SOP（released化） | ✅ Approve |  |
| 5 | KN-EVT-0003 | Knowledge | 催事設営の教訓 — 事故を受けた事前準備見直し | EVT | 全社 | 事故教訓を個別対応で終わらせずプロセス見直しへ | EP-006 | LSN-023 | — | 実際の事故記録+CEO承認 | **approve** | EP-006の実例。再発防止の根拠記録 | 05_Events（released化） | ✅ Approve |  |
| 6 | KN-SOP-0003 | SOP | 催事設営チェックリスト（事前準備） | SOP | 全社 | 会場条件確認・手順文書化・安全確認・更新ルールの4項目 | EP-006 | LSN-023 | — | 同上 | **hold** | 方向はEP-006と整合するが、**手順詳細に現場確認TODOが残っている**。CEO・現場の確認で具体化してからreleased化を推奨 | 04_SOP（現場確認後にreleased化） | ⏸ Hold | 現場確認TODO残。実際の催事設営で数回運用し成熟した段階でReleasedへ |
| 7 | KN-CS-0002 | Knowledge | so u特別製作体制 — 一人のための通常外対応 | CS | so u | 通常外の特別製作体制を整えた実績 | EP-003 | LSN-005 | PTN-004 | 3会話+CEO承認 | **approve** | EP-003の実践記録。特別対応の判断前例になる | 03_Customers（released化） | ✅ Approve |  |
| 8 | KN-PRD-0002 | Knowledge | Dr.Nomadoインソール設計思想 — 足圧の正常化 | PRD | Dr.Nomado | かかと+三点固定で足圧正常化。高硬度設計の理由 | EP-008 | LSN-009 | — | 開発判断記録+CEO承認 | **approve** | EP-008の実例。商品企画AIの設計判断の参照元 | 02_Products（released化） | ✅ Approve |  |
| 9 | KN-SLS-0001 | Knowledge | ODM見積対応 — 試作を経ない価格提示はしない | SLS | 全社 | 品質確保に試作が必要なため試作前に確定価格を出さない | EP-007 | LSN-014 | — | 商談記録+CEO承認 | **approve** | EP-007の営業実務への展開。見積トラブル防止 | 10_Sales（released化・フォルダ新設） | ✅ Approve |  |
| 10 | KN-SOP-0002 | SOP | ODM見積対応プロセス — 試作と価格提示 | SOP | 全社 | ヒアリング→試作説明→概算条件明記→品質確定後見積の4段階 | EP-007 | LSN-014 | — | 同上 | **approve** | KN-SLS-0001の手順化。SOP化できる | 04_SOP（released化） | ✅ Approve |  |
| 11 | KN-PRD-0003 | Knowledge | マルチカラーシリーズ開発 — 修正反復による品質確保 | PRD | SUNNY NOMADO | 何度もの修正・時間をかけ自信ある品質へ到達 | EP-007 | LSN-018 | — | 開発記録+CEO承認 | **approve** | EP-007の実例（商品開発側）。開発期間見積りの参考 | 02_Products（released化） | ✅ Approve |  |
| 12 | KN-EVT-0002 | Knowledge | 催事場実績 — JR浦和駅の反応が良好 | EVT | 全社 | 最近反応が良かった催事場所の実績 | EP-004 | LSN-016 | — | 会話記録+CEO承認 | **approve** | 実績ある成功要因。ただし「最近」の時期が経過すると鮮度が落ちるため、催事データ取込後に定量更新を推奨（注記つきapprove） | 05_Events（released化） | ✅ Approve |  |
| 13 | KN-PRD-0001 | Knowledge | so u彫刻仕様 — 点彫りの方が良い雰囲気 | PRD | so u | 点彫刻のほうが良い仕上がりという職人知見 | —（PRN-009はhold中） | LSN-007 | — | 実物確認記録+CEO承認 | **approve** | 原則化は保留中（PRN-009）だが、**商品仕様の事実Knowledge**としては有効。so u製作の参照知見 | 02_Products（released化） | ✅ Approve |  |

---

## 反映先の意味

| 反映先 | 内容 |
|---|---|
| カテゴリフォルダ（released化） | 承認後、次Sprintで_draftsから該当フォルダへ移動しstatus: releasedへ。**ここで初めてAgentの参照対象になる** |
| 現場確認後にreleased化 | TODOを解消してから再レビュー |
| Archive | 却下理由つき保存 |

**【2026-07-06 反映完了】** CEO判断に基づき、Approve 12件をカテゴリフォルダへ移動しreleased化。KN-SOP-0003はin_review（hold）として04_SOP/_draftsに保持。knowledge_index.json再生成済み（released 12 / in_review 1）。元Draftは移動記録スタブとして保持（Archiveしていない）。
