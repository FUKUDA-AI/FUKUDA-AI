# CEO_REVIEW_QUEUE — Pattern / Lesson レビューキュー

作成日: 2026-07-06（CEO Review Sprint v1.0）
対象: Pattern 4件 + Lesson 23件 = **27件**
入力: 01_Knowledge/08_Decision_Log/pattern_log.json / lesson_log.json

> **使い方**: CEOは「CEO判断」欄に approve / reject / hold を、必要なら「CEOコメント」欄に修正指示・却下理由を記入するだけでよい。
> AI推奨は参考であり、**AIは承認していない**。全27件は draft のまま。正式反映（EVOLVING_PRINCIPLES / Knowledge / SOP）はCEO判断の記入後、次Sprintで実施する。
> AI推奨の集計: **approve 13件 / reject 11件 / hold 3件**

---

## 優先レビュー（TOP10 — ここだけ見れば主要判断が完了する）

| 優先 | ID | 種別 | タイトル | 要約 | カテゴリ | ブランド | conf | AI推奨 | AI推奨理由 | 反映先候補 | CEO判断 | CEOコメント |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | LSN-001 (根拠: PTN-001) | Lesson | 歩みゆたかに×作り手の情熱・ストーリー | ブランド発信の核として6会話で反復。今後も一貫適用 | ブランド | 全社 | high | **approve** | 憲法第2条・第4条と完全整合。最多反復（2024-08〜2026-04・6会話）。EVOLVING仮説EP-001の第一号候補 | EVOLVING_PRINCIPLES | | |
| 2 | PTN-001 | Pattern | 職人との考え: 情熱・ストーリー・大切 | LSN-001の根拠Pattern | ブランド | 全社 | high | **approve** | 同上（LSN-001とセットで承認するとEVOLVINGの根拠リンクが成立する） | EVOLVING_PRINCIPLES（根拠） | | |
| 3 | LSN-003 | Lesson | 駅系催事の売上実績（平均30万） | 駅催事場の判断理由に実績数値つき。類似判断の基準に再利用 | 催事 | 全社 | medium | **approve** | 唯一の実績数値つき判断理由。催事AIの判断基準の種になる | Knowledge Draft（催事） | | |
| 4 | LSN-023 | Lesson | 設営事故→事前準備プロセス見直し | 事故を教訓に設営の事前準備プロセスを徹底見直し | 催事 | 全社 | low | **approve** | 実際に起きた事故の教訓。催事設営チェックリストとしてSOP化できる | SOP（催事設営） | | |
| 5 | LSN-019〜022 | Lesson×4 | 設営事故の謝罪文4件 | 同一事故に関する謝罪定型文 | 催事/経営 | 全社 | low | **reject** | LSN-023と同一事象の重複。謝罪文自体に学びはない（教訓はLSN-023に集約済み） | Archive（却下理由つき保存） | | |
| 6 | LSN-002 (根拠: PTN-002) | Lesson | 職人への手紙共有・最速でお手元へ | 顧客の手紙を職人と共有し心を込めて最速納品（5会話反復） | so u | 全社 | medium | **approve** | 反復あり・so uの顧客対応プロセスとしてSOP化できる。憲法第3条（迎える・支える・送り出す）と整合 | SOP + Knowledge Draft（so u） | | |
| 7 | LSN-016 | Lesson | JR浦和駅催事の好反応 | 最近反応が良かった場所=JR浦和駅催事 | 催事 | 全社 | low | **approve** | 実績のある成功要因。催事場選定の判断材料（LSN-003と合わせて催事Knowledgeの核） | Knowledge Draft（催事） | | |
| 8 | PTN-003 / LSN-004 | Pattern+Lesson | DX化→送料無料条件の引き下げ | nomado.shop導入で1配送下代15,000円以上送料無料へ変更 | 在庫・発注 | 全社 | low | **hold** | 定型文由来疑いだが、卸EC送料条件の「事実」としては記録価値あり。学びとしてでなく事実情報として残すかCEO判断 | Knowledge Draft（事実として）or Archive | | |
| 9 | LSN-009 | Lesson | 足圧矯正=高硬度インソールの開発判断 | かかと+三点固定で足圧を正常化する高硬度インソールが必要と判断 | 在庫・発注 | 全社 | low | **approve** | Dr.Nomadoの商品開発思想（判断理由つき）。商品企画AIの判断材料に再利用可 | Knowledge Draft（商品企画） | | |
| 10 | LSN-014 | Lesson | 試作反復と価格提示の関係 | 試作を経ないと品質・デザイン確保できず価格提示は困難 | 商品企画 | 全社 | low | **approve** | ODM見積対応の標準話法・判断基準としてSOP化できる | SOP（営業・見積） | | |

## 残りのレビュー対象（11〜27）

| 優先 | ID | 種別 | タイトル | 要約 | カテゴリ | ブランド | conf | AI推奨 | AI推奨理由 | 反映先候補 | CEO判断 | CEOコメント |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11 | PTN-002 | Pattern | 職人・手元・一日 | LSN-002の根拠Pattern（5会話・2023-06〜2026-07） | so u | 全社 | medium | **approve** | LSN-002とセットで承認（根拠リンク成立） | Knowledge Draft（根拠） | | |
| 12 | PTN-004 / LSN-005 | Pattern+Lesson | so u特別製作体制 | 顧客のために通常外の特別製作体制を整え心を込めて作る（3会話） | so u | 全社 | low | **approve** | so uの顧客対応方針として反復・憲法第3条（一人に向かう）と整合 | Knowledge Draft（so u） | | |
| 13 | LSN-018 | Lesson | マルチカラー: 修正反復→品質確保 | 何度もの修正に時間をかけた結果、自信を持てる品質に到達 | 商品企画 | SUNNY NOMADO | low | **approve** | 「品質で妥協しない」（CORE第9条）の実例。商品開発の学びとして再利用可 | Knowledge Draft（商品企画） | | |
| 14 | LSN-010 | Lesson | 中国工場・旧正月前の準備 | 旧正月前はサンプルと並行して版下も早急に進行が必要 | 商品企画 | 全社 | low | **approve** | 発注リードタイムの運用知識。発注・在庫AIのSOP化できる | SOP（発注カレンダー） | | |
| 15 | LSN-007 | Lesson | 彫刻は「点」が良い雰囲気 | so uの彫刻は点彫りのほうが良い仕上がり | 在庫・発注 | 全社 | low | **hold** | 商品仕様の知見だが単発・文脈不足。so u商品知識として残すか要確認 | Knowledge Draft（so u）or Archive | | |
| 16 | LSN-006 | Lesson | メール自動送信の技術メモ | 自動送信はサーバー側スケジューラが必要 | 経営 | 全社 | low | **reject** | 技術メモであり経営の学びではない。判断基準として弱い | Archive | | |
| 17 | LSN-008 | Lesson | 「次回は是非お取組みを」 | 取引先からの社交的な申し出 | 催事 | 全社 | low | **reject** | 予定連絡・社交辞令。学びなし | Archive | | |
| 18 | LSN-011 | Lesson | 作業スペースの費用発生 | スペース用意には費用が発生する旨の断片 | 催事 | 全社 | low | **reject** | 文脈のない断片。判断基準として弱い | Archive | | |
| 19 | LSN-012 | Lesson | 訪問日調整のメール | 訪問日の調整連絡 | so u | 全社 | low | **reject** | 予定連絡。学びなし | Archive | | |
| 20 | LSN-013 | Lesson | 搬出時のお礼・次回出店連絡 | お礼と次回11月出店の連絡文作成 | 催事 | 全社 | low | **reject** | 予定連絡が主。学びが薄い | Archive | | |
| 21 | LSN-015 | Lesson | 品川駅催事の開催予定 | 2023年6月の開催予定連絡 | 催事 | 全社 | low | **reject** | 過去の予定連絡。学びなし（催事出店履歴は将来の催事データ取込で管理すべき） | Archive | | |
| 22 | LSN-017 | Lesson | スケジュール過密で再調整 | 条件で再調整するが過密でうまくいかない可能性の連絡 | 営業 | 全社 | low | **reject** | 社交的な断り文。失敗要因としての実体なし | Archive | | |

※ 優先5（LSN-019〜022）と優先8・12は複数IDを1行に統合して表記。個別判断が必要な場合はコメント欄に記載してください。

---

## 反映先候補の意味

| 反映先 | 内容 | 実施Sprint |
|---|---|---|
| EVOLVING_PRINCIPLES | 判断基準の仮説（EP-xxx）として登録 | 承認後、次Sprint |
| Knowledge Draft | 01_Knowledge該当カテゴリへdraftとして転記（Knowledge Builder） | Phase 6 |
| SOP | 04_SOPへ手順書化 | 承認後、次Sprint |
| Archive | 却下理由つきで保存（Generator改善の学習データ） | 承認後、次Sprint |

## AI推奨の適用ルール（参考）

- approve: 憲法/CORE整合・複数会話反復・再利用可能・数値/実績あり・SOP化可能
- reject: 定型文由来・予定連絡/謝罪文・重複・判断基準として弱い
- hold: 価値はあるが追加情報が必要・統合したほうがよい・CEO判断が必要

**注意: 本キューはAIの推奨であり、正式判断はすべてCEOが行う。CEO判断の記入前は全件draftのまま変更しない。**
