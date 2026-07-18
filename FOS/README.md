# FOS Operating Rule v1.2 — FOS運用ルール + Decision Metadata

Version: v1.2（Sprint 14.2・設計。v1.1に decision_importance / expected_result / review_after_days を追加 = **Result Layer接続の前提設計**）
最終更新日: 2026-07-07
状態: **Released（CEO一括承認 2026-07-07・Sprint 14系）** — CEOの入力習慣として運用開始
正本: FOS-data.json（Source of Truth・FOS.htmlは表示用補助）

> **FUKUDA AIはFOSに映るものしか見えない。**
> FOSに入っていない重要タスクは、Briefに上がらず、判断されず、学習もされない。
> このルールは「何をFOSに入れるか」を決める — 入れた瞬間、AIの視界に入る。

---

## 1. FOSに必ず入れるもの

| 種類 | 例 | 理由 |
|---|---|---|
| **CEO判断が必要なもの** | 発注量の承認・出店可否・価格・コラボ可否 | Briefの判断候補になる（staffRequests推奨） |
| **人が返事を待っているもの** | スタッフ相談・職人への回答・取引先への返事 | 憲法: 人を待たせない。優先加点される |
| **期限があるもの** | 締切・納期・打ち合わせ・搬入 | 期限切れ検知が働く（events推奨） |
| **お金が動くもの** | 発注・支払い・請求・投資 | CORE第2条①現金化スピードの監視対象 |
| **発注・支払い・納期・契約・催事・顧客対応** | 全般 | 会社の現場そのもの |
| **Morning Briefに出したいもの** | 「明日CEOに判断させたい」こと | 入れれば翌朝のBriefに乗る |

**迷ったら入れる。** 入れすぎのコストは低い（Briefは3件に絞るので溢れない）が、入れ忘れのコストは高い（AIから見えない）。

### スタッフ相談の書き方（v1.3運用・2026-07-11 CEO決定）

- **新規の相談はtasksにタイトル先頭「【相談】」で書く**（例:「【相談】so u: 再入荷数量を決めたい。A=同数/B=1.5倍。推奨B」）。FUKUDA AIが自動でスタッフ相談として扱い、Brief判断候補・スタッフ待ちに載せる（priority 90=人を待たせない）
- 理由: **staffRequests配列はFOSアプリの画面に表示されず、CEOがアプリから解決操作できない**ため（2026-07-11判明）。既存のstaffRequestsはチャット経由で判断→CEO承認のもとAIがstatusを更新する
- アプリに相談画面が追加されたら（[STAFF_REQUESTS_UI_SPEC.md](STAFF_REQUESTS_UI_SPEC.md)参照）staffRequests運用へ戻してよい

## 2. FOSに入れなくてよいもの

- ただのメモ・思いつき（→ Briefの「AIへの気付き」欄 or thought欄へ）
- 完了済みで学習価値がないもの
- 単発の雑務（5分で終わり・判断も期限も金額もないもの）
- **AI Memoryだけで足りるもの**（FUKUDA AIの開発タスク・レビューキュー等はPENDINGが持つ。二重入力は不要）

## 3. FOSとPENDINGの役割分担

| | **FOS = CEOの操作面** | **PENDING = AIの記録面** |
|---|---|---|
| 誰が書くか | **CEO（スタッフ）のみ** | AIのみ |
| 中身 | 会社の現場のタスク・判断・期限 | FUKUDA AI開発のレビュー待ち・保留・観察 |
| AIの扱い | 読み取り専用（変更・完了化・削除はCEO確認後=CEO操作） | AIが直接更新 |
| Briefへの流れ | FOS Importer→TaskRecord→判断候補 | PENDING Reader→判断候補 |
| 同期 | Briefでの判断結果をAIがPENDINGに記録し、**FOS側の更新（完了化等）はCEOへ依頼する** | 同左 |

**原則**: 同じ案件を両方に書かない。会社の現場=FOS、AI開発=PENDING。境界例はFOS優先（CEOの目に入る場所が正）。

## 4. Decision Metadata（v1.1〜v1.2・判断の分類と結果追跡）

### 4-1. decision_needed（CEO判断が必要か: YES / NO）

| **YESになる条件（1つでも該当すればYES）** | **NOになる条件** |
|---|---|
| 5万円以上のお金が動く | 定型作業 |
| 人が返事を待っている | 完了報告 |
| 会社方針に影響する | 既存ルールどおり |
| ブランドに影響する | 単なるメモ |
| 契約・法務に関係する | AI Memoryだけで十分なもの |
| 在庫・発注に関係する | |
| 催事・出店に関係する | |
| 例外対応である | |
| 後から変更コストが高い | |

- **decision_needed=YES は Morning Brief候補として優先される**（§6の判定条件1）
- 迷ったらYES（NOの誤りはBriefが3件に絞るので吸収されるが、YESの入れ忘れは判断漏れになる）

### 4-2. decision_type_main / decision_type_sub（2階層の判断分類）

**分類一覧（main・subとも同じ13分類から選ぶ）**:
経営戦略 / 予算・資金 / 売上・営業 / マーケティング / 商品・ブランド / 在庫・発注 / 催事・イベント / 顧客対応 / 取引先・仕入先 / 契約・法務 / 人事・組織 / AI・システム / その他

- **decision_type_main: 必須**（判断の主たる領域）
- **decision_type_sub: 任意**（副次的に影響する領域。不要なら **null**）

| 例 | main | sub |
|---|---|---|
| 催事の出店在庫を決める | 催事・イベント | 在庫・発注 |
| 新商品の発信方法 | 商品・ブランド | マーケティング |
| 仕入先への前払い条件 | 予算・資金 | 取引先・仕入先 |
| so u発注量の上限予算（Brief#3の実例） | 在庫・発注 | 予算・資金 |

**共通利用ルール**: mainはMorning Briefで優先表示（subは必要時のみ）→ Decision Logへmain/sub両方保存 → Result Recordへ引き継ぎ → **Knowledge化時はRelated Decision Metadata（main / sub / importance / expected_result）として保持**（v1.2）。**同じ分類が判断の入口（FOS）から学びの出口（Knowledge)まで一気通貫**することで、「催事の判断は何勝何敗か」「S判断の成功率は」「予算判断の傾向は」が重要度別・分類別に後から集計できる。

**AIの制約**: AIはdecision_typeを**推測して確定しない**。未入力は「未分類」として扱い、BriefでCEOへ分類を確認する（1タップで答えられる形で提示）。

### 4-3. decision_importance（経営重要度: S / A / B / C・v1.2追加）

**priorityと分離する**: priority = 作業の急ぎ度 / decision_importance = **経営判断としての重要度**。「急ぎだが軽い判断」（priority=high・importance=B）も「急がないが重い判断」（priority=low・importance=S）も存在する。

| ランク | 該当するもの |
|---|---|
| **S** | 会社方針に影響 / 数十万〜数百万円以上の影響 / 新ブランド / 人事・組織 / 契約・法務 / 大きな投資 / 撤退判断 / **後戻りしにくい判断** |
| **A** | 発注 / 在庫 / 催事 / 取引先対応 / 価格 / 売上に影響 / 顧客対応方針 / 広告予算 |
| **B** | 商品改善 / 小規模な広告 / 軽微な運用変更 / 既存ルール内の判断 / 確認すれば進められるもの |
| **C** | 軽微な確認 / 完了報告 / メモ / AI Memoryだけで足りるもの / Decision Logに残す必要が薄いもの |

- **Sランクは原則としてBrief候補に必ず入れる**（3件枠を消費してでも載せる）
- **AIはdecision_importanceを勝手に確定しない**。未入力は「未設定」として扱い、CEOへ確認する

### 4-4. expected_result（判断時に期待する結果・v1.2追加）

判断した時点で「何が良くなるはずか」を1行で書く。例:
売上増加 / 利益改善 / 在庫リスク低減 / 納期安定 / 顧客満足向上 / ブランド価値向上 / 作業時間短縮 / 再発防止 / 判断材料の明確化

- **Result Recordへ引き継ぎ、結果確認時に expected_result と actual_result の差分を比較する**（当たった判断・外れた判断が事実で残る）
- **AIはexpected_resultを推測しない**（CEO・スタッフの入力のみ。未入力ならBriefで確認）

### 4-5. review_after_days（何日後に結果確認するか・v1.2追加）

| importance | 初期値の目安 |
|---|---|
| S | 30日 |
| A | 14日 |
| B | 7日 |
| C | 原則なし |

- **催事・発注・広告などは実務に合わせて変更可**（例: 催事=会期終了+3日、発注=納品+7日、広告=配信終了時）
- **review_after_days が設定された判断は、経過後にMorning Briefの「結果確認待ち」へ自動的に上がる**（Result Layerの入口。CEOが成功/失敗/継続観察を判定）
- 未入力の場合、AIはimportanceに応じた初期値を**提案してよいが、確定はCEO確認後**

> **v1.2の狙い**: この3項目で「判断→期待→期日→結果→差分」が閉じる。Result Recorder v1.0・Evidence Scorer・Verified昇格条件は本メタデータへ接続する前提で実装する。

## 5. FOS入力テンプレート（v1.2・14項目）

```
title:               何をするか1行（動詞で終える: 「〜を承認する」「〜を確認する」）
category:            催事 / 発注 / 顧客対応 / 営業 / ブランド / 資金 / その他
deadline:            YYYY-MM-DD（あれば必ず。期限切れ検知が働く）
priority:            high / mid / low（迷ったらmid）
waiting_person:      返事を待っている人（いればBrief優先度が上がる）
decision_needed:     YES / NO（§4-1の基準。迷ったらYES）
decision_type_main:  13分類から1つ（必須）
decision_type_sub:   13分類から1つ or null（任意）
options:             A案 / B案（+スタッフ推奨があれば明記 → Briefがほぼ完成形になる）
recommendation:      スタッフの推奨案と理由
memo:                背景・補足（前回実績・数値があると判断が速い）
decision_importance: S / A / B / C（§4-3の基準。priorityとは別物・迷ったら1つ上）
expected_result:     この判断で何が良くなるはずか1行（§4-4の例から。Resultと比較される）
review_after_days:   結果確認までの日数（S30/A14/B7/C原則なし。催事・発注・広告は実務に合わせ変更可）
```

**良い入力の実例（Brief#3判断3）**: so u発注の相談は options（A=同数/B=1.5倍）+ recommendation（B案・前回完売のため）まで入っていたため、Briefがそのまま判断材料になった。**この形が模範。**

**惜しかった実例**: 期限切れイベント2件は「済んだかどうか」がFOS上で分からずBriefで確認が必要だった。→ 済んだらFOSで完了化する習慣が価値を生む。

## 6. Morning Briefへ上げる条件（機械が自動判定・v1.2）

**候補になる条件**: decision_needed = YES は必ず判断候補（mainを見出しに表示・subは必要時のみ）。

**並び順（v1.2・上から優先）**:

1. **期限切れ**（deadline超過）→ 緊急として最上位
2. **decision_importance = S** → **原則必ずBrief候補に入れる**（3件枠を消費してでも）
3. **waiting_person がいる**（人を待たせない・憲法）
4. **decision_importance = A**
5. **期限3日以内**
6. **priority = high** または プロジェクトのtodayScore/urgencyが高い

- 完了済み（done）・importance=C/priority=lowで期限なし → Briefには載せない（索引には残る）
- **結果確認待ち（v1.2新設）**: review_after_days が経過した判断は、Briefの「結果確認待ち」セクションへ自動掲載（CEOが成功/失敗/継続観察を判定 → Result Record化）

## 7. Decision Logへ送る条件

- BriefでCEOが判断（承認/却下/保留/完了）を記入したもの → **Decision Log Draft経由で本体へ**。記録時に **decision_type_main / sub / decision_importance / expected_result / review_after_days の5項目を保存**（v1.2）
- FOS上でCEOが直接大きな判断をした場合（Briefを経ない判断）→ 次回Briefの「Decision Log候補」欄で確認してから記録
- 記録対象は「判断」のみ。作業完了の事実だけならDecision Logに送らない（それはResult/タスク完了）

## 8. Result Recordへ送る条件（Result Layer実装後）

- Decision Logに記録された判断のうち **trackable（実行系）** のもの: 発注・出店・価格・企画開始など
- **確認時期はreview_after_daysが決める**（v1.2。未設定はimportance初期値S30/A14/B7を提案・確定はCEO）。経過後、Briefの「結果確認待ち」でCEOが 成功/失敗/継続観察 を記入 → Result Record化
- **Result Recordへは decision_type main/sub + expected_result + review_after_days を引き継ぐ**（v1.2）。結果確認時に **expected_result vs actual_result** を並べて比較 → 差分がInsightの種になる（分類別・重要度別の成功率が集計可能に）
- FOSのevents（催事等）は実施後、07_Data/events/の実績データと照合して数値を自動転記（判定はCEOのみ）
- 例: 「工場打ち合わせ（済み・結果メモ後日）」→ メモ受領時にResult Record初号

## 9. 運用の1日（この形に慣れる）

```
朝  : fos_importer.py → Morning Brief発行 → CEOが3件判断（5分）
日中: 新しい判断事項・期限・相談が発生したらFOSへ入力（テンプレート§5・14項目）
夕方: 済んだタスクをFOSで完了化（1分。翌朝のBriefが正確になる）
```

## 10. FOSアプリのデータ保存構造（CEO提供情報 2026-07-10・連携の前提）

| 項目 | 内容 |
|---|---|
| アプリの正本 | **ChromeのLocalStorage**（キー `fos_state_v2`・FOS.htmlのfile://オリジン紐づけ） |
| FOS-data.json | アプリの**自動同期先**（自動保存オン時・変更の約0.8秒後に全状態を書込）。**FUKUDA AIの読取元はこのJSONのまま** |
| 同期の注意 | **ブラウザ再起動後は「自動保存を再開」ボタンを押すまでJSONが更新されない**（それまで古いまま）。**毎朝Brief前にCEOがFOSを開いて再開を押す運用**で鮮度を保つ |
| スキーマ | トップキー: projects / tasks / improvements / staffRequests / chatImports / learningLogs / events。projects.scores 9項目+thought / tasks.done / staffRequests.status（pending・approved・rejected・later） |
| **AI側への影響（重要）** | アプリの自動保存は**JSONを全置換**する。AIがJSONへ直接書いた変更（例: 2026-07-10のevents完了フラグ）はアプリのLocalStorageに存在しないため**次回同期で消える**。→ **FOSの内容変更は必ずアプリ側で行う**（AIのJSON直接編集は原則禁止の再確認。緊急時もアプリ側への反映をセットにする） |

## 変更履歴

| 日付 | 版 | 内容 |
|---|---|---|
| 2026-07-07 | v1.0 | 初版作成（Sprint 14・設計のみ。Brief#3後のCEO指摘「FOS外の重要タスク存在」を受けて） |
| 2026-07-10 | v1.2追補 | §10 FOSアプリのデータ保存構造を記録（CEO提供情報: LocalStorage正本・自動同期・再開ボタン運用・全置換上書きの注意） |
| 2026-07-07 | v1.1 | Decision Metadata追加（decision_needed YES/NO基準・decision_type main/sub 2階層13分類・共通利用ルール。Sprint 14.1・設計のみ） |
| 2026-07-07 | v1.2 | Result Layer接続の前提設計（decision_importance S/A/B/C・expected_result・review_after_days S30/A14/B7。テンプレート14項目化・Brief並び順・結果確認待ち新設。Sprint 14.2・設計のみ） |
