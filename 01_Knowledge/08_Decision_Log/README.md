# 08_Decision_Log — 経営判断・知見・パターンの正式保存先

## 目的
Decision（経営判断）・Insight（経営知見）・Pattern（反復検証された思想・判断）の**正式保存先**。CEO決定（2026-07-06）により、ルート直下の `08_Decision_Log/` は今後使用しない（既存データは削除せず存置）。

## Version
- Decision Extractor v2.0 [Experimental] → `decision_log.json`（20件・出力先を本フォルダへ変更済み）
- Insight Extractor v2.0 [Experimental] → `insight_log.json`（382件・同上）
- Pattern Analyzer v1.0 [Experimental] → `pattern_log.json`（4件）
- Lesson Generator v1.0 [Experimental] → `lesson_log.json`（23件・CEOレビュー済み 2026-07-06）
- Principle Generator v1.0 [Experimental] → `principle_log.json`（10件・全draft・CEOレビュー待ち）

## 最終更新日
2026-07-06

## 関連機能
プロジェクトルートの pattern_analyzer.py / decision_extractor.py / insight_extractor.py

## 依存関係
- pattern_log.json の入力: 本フォルダの insight_log.json + decision_log.json
- 学習サイクル上の位置: Insight / Decision → **Pattern** → Lesson → EVOLVING_PRINCIPLES → CEO Review → CORE_PRINCIPLES

## 使用方法
```
python3 pattern_analyzer.py
```

## 重要ルール
- pattern_log.json の全Patternは `status: draft` / `needs_ceo_review: true`
- CEOレビュー前に CORE_PRINCIPLES / EVOLVING_PRINCIPLES / Knowledge Released へ反映しない
- Experimentalの出力を経営判断に直接使わない（Development Standard §4）

## 今後のTODO
- Pattern 4件のCEOレビュー（承認分はEVOLVING_PRINCIPLESへ）
- 意味解析ベースのグルーピング強化（現状は文字n-gram TF-IDF）
- ルート08_Decision_Log/の99_Archive移動（CEO承認待ち）
