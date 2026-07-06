# DEVELOPMENT_STANDARD.md — 開発標準

Version: v1.0
最終更新日: 2026-07-03
状態: Released

本文書は FUKUDA AI / NOMADO AI Operating System の**ソフトウェア開発・保守・運用ルール**を定義する開発標準である。

経営哲学・AI憲法・ブランド思想・CEO判断基準は本文書に含めない。それらは以下で別管理する。

- AI_CHARTER.md
- BUSINESS_PHILOSOPHY.md
- CEO_PRINCIPLES.md

---

## 1. Version管理

すべての機能・Agent・Script・Importer・Extractor・Generator・Writer はVersionを持つ。

表記: `機能名 vX.Y`（例: ChatGPT Importer v1.1、Insight Extractor v1.0）

**Version更新条件**（いずれかに該当したら必ず更新）

- 新機能追加
- アルゴリズム改善
- 分類精度向上
- 処理速度改善
- 互換性に影響する変更
- フォルダ構成変更
- AI判断ロジック変更
- データ構造変更

番号規則: 互換性に影響する変更は X（メジャー）、それ以外は Y（マイナー）を上げる。詳細は [NAMING_CONVENTION.md](NAMING_CONVENTION.md) を参照。

## 2. CHANGELOG

変更履歴は [CHANGELOG.md](CHANGELOG.md) に記録する。

記録項目: Version / 日付 / 対象機能 / 変更内容 / 変更理由 / 互換性 / 担当（AIまたはCEO）

**Version更新時は必ずCHANGELOGも同時更新する。**

## 3. ROADMAP

開発計画は [ROADMAP.md](ROADMAP.md) で管理する。

管理項目: Phase / 目的 / 現在の状態 / 次Sprint / 完了条件 / 依存関係

Phase構成: Phase1 Foundation 〜 Phase10 NOMADO AI Operating System（詳細はROADMAP.md）

## 4. Release管理

各機能は以下のいずれかの状態を持つ。

| 状態 | 意味 |
|---|---|
| Released | 正式運用可。品質検証済み |
| Experimental | 試験運用。結果の検証が必要 |
| Deprecated | 非推奨。後継機能へ移行する |

**正式運用は Released のみ。** Experimentalの出力を経営判断に直接使わない。

## 5. README管理

各フォルダに README.md を配置する。

記載項目: 目的 / Version / 最終更新日 / 関連機能 / 依存関係 / 使用方法 / 今後のTODO

## 6. AI開発ルール

AIは以下を必ず守る。

1. 既存ファイルを勝手に削除しない
2. 既存ファイルを勝手に上書きしない
3. 破壊的変更は必ず事前確認する
4. 既存構造との互換性を最優先する
5. 一時ファイル（temp / sample / test 等、自ら作成したもの）のみ削除可能
6. フォルダ全体削除は禁止
7. READMEとCHANGELOGを同期更新する
8. 完成後は必ずレビュー可能な状態にする（実行結果・統計を提示）

## 7. 命名規則

フォルダ / Python / JSON / Markdown / Agent / Version の命名規則は [NAMING_CONVENTION.md](NAMING_CONVENTION.md) で統一管理する。

## 8. Sprint開発

ウォーターフォールではなくSprint開発を採用する。

**各Sprint終了時に必ず更新するもの**

- 完成物
- Version
- CHANGELOG
- ROADMAP
- 次Sprint
- レビュー結果

## 9. Architecture管理

> **【2026-07-06追記】** 正式Architectureは [ARCHITECTURE.md](ARCHITECTURE.md)（v1.2）を正とする。以下のv1.0図は制定時の記録として保持する。

AIパイプラインを以下のArchitectureとして固定する（Architecture v1.0）。

```
Conversation
    ↓
Conversation Index
    ↓
Insight
    ↓
Decision
    ↓
Lessons Learned
    ↓
CEO Principles
    ↓
Knowledge
    ↓
AI Agents
```

Architecture変更時はVersionを更新し、CHANGELOGに記録する。

## 10. 本文書の位置付け

本文書はソフトウェア開発標準であり、経営哲学・AI憲法・ブランド思想・CEO判断基準は含めない（それらは AI_CHARTER.md / BUSINESS_PHILOSOPHY.md / CEO_PRINCIPLES.md で管理）。

## 11. 今後の運用

新機能を追加する前に必ず確認する。

- 既存Architectureとの整合性
- Version管理
- CHANGELOG
- ROADMAP
- README

**「機能を増やすこと」よりも「長期運用できる品質」を優先する。**
