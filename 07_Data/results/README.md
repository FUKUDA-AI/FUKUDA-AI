# 07_Data/results — Result Record（Result Layer・Data Layer）

## 目的
Decision Logの判断が「どうなったか」の記録庫。判断→期待→期日→結果→差分を閉じる（Result Layer v1.0初実装・Sprint 15）。

## Version
Result Recorder v1.0 [Experimental]（2026-07-07〜稼働）

## 構成

| ファイル | 内容 | ルール |
|---|---|---|
| `result_draft_log.json` | Result Draft（Action Record + CEO記入欄） | Recorderが生成。**判定（成功/失敗/継続観察）はCEOのみ・AIは推測しない** |
| `result_log.json` | 確定Result（CEO判定済みのみ） | **CEO確認後の確定操作でのみ追記**。AIは勝手に書かない |
| `index.json` | 確認待ちサマリー | Morning Brief「⏰ 結果確認待ち」の参照元。Recorderのみ再生成 |

## 使用方法

```
python3 result_recorder.py          # 結果待ちDecision抽出 + Draft生成 + index更新
python3 result_recorder.py --check  # 抽出確認のみ（書き込みなし）
```

## Result Draftの主項目

result_id / decision_fingerprint（冪等キー・Decision遡及リンク）/ action（date・actor・what=事実のみ）/
decision_type_main・sub / decision_importance / expected_result / review_after_days（引き継ぎ・無ければnull）/
check_due_date / status（**CEO判定待ち**）/ outcome / 数値結果 / 成功・失敗要因 / 想定との差異 /
evidence（**必須。無ければlearning_ready不可**）/ learning_ready / record_status

## ルール（RESULT_LAYER_DESIGN.md準拠・CEO指示 Sprint 15）

- AIはResultを推測しない。機械が書けるのは事実（日付・出典・引き継ぎ）だけ
- 成功/失敗/継続観察の判定・要因分析はCEOのみ
- Decision Log本体は書き換えない（読み取りのみ）
- 書き込み先は本フォルダのみ（コードで強制）・既存ファイル削除禁止・冪等
- learning_ready=trueのResultだけがInsight Generator v1.1（将来）の学習対象になる
