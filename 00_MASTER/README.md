# 00_MASTER — 最上位文書群

## 目的
FUKUDA AI（NOMADO AI Operating System）が毎回の判断で参照する最上位文書を管理する。
思想（憲法〜AI規範）と運用（開発標準〜変更履歴）の11文書で構成される。

## Version
v1.0

## 最終更新日
2026-07-06

## AIが毎回読む順番（Session Start Protocol）

セッション全体の参照順は **00_MASTER → AI Memory（10_AI_Memory）→ Knowledge（01_Knowledge）→ Task** とする。
00_MASTER内では、AIは必ずこの順に読み込む。**矛盾がある場合は読込順の小さい文書を正とする。**

| 順 | 文書 | 役割 |
|---|---|---|
| 1 | [00_CONSTITUTION.md](00_CONSTITUTION.md) | 会社・ブランド憲法（House of Hachiemon） |
| 2 | [BUSINESS_PHILOSOPHY.md](BUSINESS_PHILOSOPHY.md) | 経営哲学（会社とは） |
| 3 | [COMPANY_PROFILE.md](COMPANY_PROFILE.md) | 会社の事実情報 |
| 4 | [PROJECT_VISION.md](PROJECT_VISION.md) | FUKUDA AIの目的と未来像 |
| 5 | [IDENTITY.md](IDENTITY.md) | FUKUDA AIとは何者か |
| 6 | [CORE_PRINCIPLES.md](CORE_PRINCIPLES.md) | 不変の経営判断基準 |
| 7 | [EVOLVING_PRINCIPLES.md](EVOLVING_PRINCIPLES.md) | 成長する経営判断基準 |
| 8 | [AI_CHARTER.md](AI_CHARTER.md) | AIの行動規範（AIの法律） |
| 9 | [DEVELOPMENT_STANDARD.md](DEVELOPMENT_STANDARD.md) | 開発標準 |
| 10 | [ROADMAP.md](ROADMAP.md) | 開発計画 |
| 11 | [CHANGELOG.md](CHANGELOG.md) | 変更履歴 |

## 読込順序の対象外（補助文書）

- [ARCHITECTURE.md](ARCHITECTURE.md) — 正式Architecture v1.3（パイプライン・Principle層・5層構造・Memory横断層）。開発作業時に必ず参照
- [NAMING_CONVENTION.md](NAMING_CONVENTION.md) — 命名規則（DEVELOPMENT_STANDARDの下位文書）
- CEO_PRINCIPLES.md — CORE_PRINCIPLES / EVOLVING_PRINCIPLES へ役割分離済み。アーカイブはCEO確認後に実施

## 更新ルール

- 思想文書（読込順1〜8）の改定権限はCEOのみ。AIはEVOLVING_PRINCIPLESへの仮説追記のみ可
- 運用文書（9〜11）は開発標準に従い更新（CHANGELOGはVersion更新時、ROADMAPはSprint終了時に必ず）

## 依存関係
なし（最上位）
