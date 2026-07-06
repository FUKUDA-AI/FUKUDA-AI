# PRINCIPLE_REVIEW_QUEUE — Principle レビューキュー

作成日: 2026-07-06（Principle Review Sprint v1.0）
対象: Principle 10件（PRN-001〜010・全件draft）
入力: 01_Knowledge/08_Decision_Log/principle_log.json

> **使い方**: CEOは「CEO判断」欄に approve / reject / hold を、必要なら「CEOコメント」欄に修正指示を記入する。
> AIは承認・反映を行っていない。**承認されたものだけ**が次Sprintで EVOLVING_PRINCIPLES.md（EP-xxx）へ登録される。CORE_PRINCIPLESへの昇格はEVOLVINGでの検証後にCEOのみが行う。
> AI推奨の集計: approve 8件 / hold 1件 / reject 1件
> **CEO判断（2026-07-06記入済み）: Approve 8件（PRN-001〜008）/ Hold 2件（PRN-009・010）**。承認8件は次SprintでEVOLVING_PRINCIPLESへ登録する。
> 判定基準（前回CEO指示より）: **「事実」だけでは原則にならない。どんな場面でも使える判断原則であること。**

---

| # | ID | タイトル | 内容（summary） | 根拠Lesson | 根拠Pattern | AI推奨 | AI推奨理由 | 反映先候補 | CEO判断 | CEOコメント |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | PRN-001 | ブランドは売るものではなく、人の歩みを豊かにするために存在する | 全ブランド・商品・発信は「歩みゆたかに」を最上位思想とし、作り手の情熱とストーリーを形にする | LSN-001 (released) | PTN-001 (released) | **approve** | CEO承認済みの最多反復思想（6会話）の原則化。憲法第1・2条と完全整合。CEOコメント「会社・ブランド・AIすべての最上位思想」を反映済み | EVOLVING（将来のCORE候補） | ✅ Approve |  |
| 2 | PRN-002 | お客様の想いは、必ず作り手まで届ける | お客様の手紙・言葉を職人まで共有した上でものづくりをする | LSN-002 (released) | PTN-002 (released) | **approve** | 5会話反復+CEO「so uの標準対応として残す」。場面を問わず使える行動原則 | EVOLVING + SOP（so u標準対応） | ✅ Approve |  |
| 3 | PRN-003 | 一人のお客様のために、通常を超える対応を惜しまない | 必要なら通常外の特別製作体制を整える。数ではなく一人に向かう | LSN-005 (released) | PTN-004 (released) | **approve** | 3会話反復・憲法第3条「迎える」の実践原則 | EVOLVING | ✅ Approve |  |
| 4 | PRN-004 | 安くするのではなく、工夫によってお客様へ還元する | 値引きでなくDX・改善によるコスト削減分をお客様へ還元する | LSN-016 (released) / LSN-004 (hold) | PTN-003 (hold) | **approve** | CEOコメント2件（「工夫でお客さんに還元」「DX還元思想として再整理」）をそのまま原則化。承認によりhold中のLSN-004/PTN-003も解消できる | EVOLVING（将来のCORE候補・CORE第4条の実践形） | ✅ Approve |  |
| 5 | PRN-005 | 判断は過去実績の数値を基準に持ちつつ、今年の条件・環境・在庫・市場変化を含めて行う | 実績数値（駅系催事平均30万等）を土台に、今年の条件を重ねて判断する | LSN-003 (released) | — | **approve** | CEO提示の例（前年売上だけで判断しない）と同型。催事AIの中核判断原則になる。数値そのものはKnowledge側で管理 | EVOLVING + Knowledge（実績数値は催事Knowledgeへ） | ✅ Approve |  |
| 6 | PRN-006 | 失敗は謝罪で終わらせず、プロセスの見直しへ昇華させる | 事故・失敗は必ずチェックリスト・プロセス見直しへつなげる | LSN-023 (released) | — | **approve** | CEOコメント「継続するために、未然の防止」の原則化。全部門で再利用可能 | EVOLVING + SOP（催事設営チェックリスト） | ✅ Approve |  |
| 7 | PRN-007 | 品質は時間と反復で確保し、確保できるまで世に出さない・価格を約束しない | 試作と修正を惜しまず、品質確定前に価格を約束しない | LSN-018 / LSN-014 (released) | — | **approve** | 2つの承認済みLessonを統合。CORE第9条・憲法第8条と整合 | EVOLVING | ✅ Approve |  |
| 8 | PRN-008 | 商品は、使い手の身体と課題の観察から設計する | 「何が売れるか」でなく「使い手のどんな課題を解決するか」から開発を始める | LSN-009 (released) | — | **approve** | Dr.Nomado開発判断の原則化。単一根拠だが判断理由が明確で、商品企画AIの前提になる | EVOLVING | ✅ Approve |  |
| 9 | PRN-009 | 仕上がりの良し悪しは、職人の目と実物の雰囲気で決める | 仕様・データだけで決めず職人の美的判断を基準にする | LSN-007 (released) | — | **hold** | 憲法第6条と整合するが、根拠が単発の商品仕様知見（点彫り）のみ。「事実だけでは原則にならない」基準に照らすと反復根拠が不足。追加事例が出るまでhold、事実はso u Knowledgeへ、が無難 | hold（事実はKnowledgeへ）or EVOLVING | ⏸ Hold | 方向性は賛成。反復実績不足のため継続観察（SUNNY NOMADO / so u / MIRAI UP / 今後のブランドで反復を確認）。将来は「最終品質は数値だけでなく職人の経験・感性・実物確認を含めて判断する」全社Principleへ成長させる |
| 10 | PRN-010 | 出店・企画の判断には、売上見込みだけでなく付帯コストを含める | 採算判断にスペース費・作業費等を織り込む | LSN-011 (hold) | — | **reject** | 根拠のLSN-011をCEOが「事実だけでは原則にならない」としてholdへ修正済み。原則としては却下し、付帯コストの事実は催事Knowledgeで管理することを推奨 | Archive（事実は催事Knowledgeへ） | ⏸ Hold | 抽象度不足。「経営判断は売上だけでなく利益・ブランド価値・運営負荷・将来性を総合的に判断する」へ再整理し次回再提案 |

---

## 反映先の意味

| 反映先 | 内容 | 実施 |
|---|---|---|
| EVOLVING | EVOLVING_PRINCIPLES.mdへEP-xxxとして登録（検証中の判断原則） | 承認後、次Sprint |
| CORE | CORE_PRINCIPLES.mdへの昇格（**EVOLVINGでの検証後・CEOのみ**。今回の直接昇格は不可） | 将来 |
| Knowledge | 事実・数値情報を01_Knowledge該当カテゴリへ | Phase 6 |
| SOP | 04_SOPへ手順書化 | 承認後 |
| Archive | 却下理由つき保存 | 承認後 |

**注意: AIはEVOLVING / CORE / Knowledgeへ一切反映していない。全10件はdraftのまま。承認分の登録は次Sprint（EVOLVING登録Sprint）で行う。**
