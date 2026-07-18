# FOSアプリ改修スペック — スタッフ相談（staffRequests）画面の追加

作成: 2026-07-11（FUKUDA AI）/ 対象: FOSアプリ（FOS.html等・CEO側で運用中のアプリ）
背景: FOS-data.jsonの`staffRequests`配列がアプリ画面に表示されず、CEOが相談を確認・解決できない。

## 要件（最小）

1. **一覧表示**: `staffRequests` のうち `status` が `resolved`/`done` 以外を一覧表示
2. **表示項目**: projectName / problem / staffProposal / optionA / optionB / recommended / decisionNeeded / createdAt（日付表示）
3. **解決操作**: 各行に「✅ 解決」ボタン → `status: "resolved"` + `resolvedAt`（epoch ms）+ `ceoDecision`（任意入力: 選んだ案と一言）を書き込み、FOS-data.jsonへ保存（既存の保存処理と同じ経路で）
4. **新規追加（任意）**: スタッフが相談を追加するフォーム（problem/optionA/optionB/recommended/decisionNeeded）
5. データ構造は現状のまま（キー追加のみ・削除しない）。解決済みは配列から消さずstatusで管理（FUKUDA AIの学習履歴になる）

## そのまま貼れるコード例（バニラJS・アプリの保存関数に合わせて`saveData()`を差し替え）

```html
<section id="staff-requests">
  <h2>🙋 スタッフ相談（CEO判断待ち）</h2>
  <div id="sr-list"></div>
</section>
<script>
function renderStaffRequests(data) {
  const wrap = document.getElementById("sr-list");
  const open = (data.staffRequests || []).filter(s => !["resolved","done"].includes(s.status));
  wrap.innerHTML = open.length ? "" : "<p>判断待ちの相談はありません</p>";
  open.forEach(s => {
    const d = document.createElement("div");
    d.className = "sr-card";
    d.innerHTML = `
      <b>${s.projectName}</b>: ${s.problem}
      <br>提案: ${s.staffProposal || "-"}
      <br>A案: ${s.optionA || "-"} / B案: ${s.optionB || "-"}（推奨: ${s.recommended || "-"}）
      <br>要判断: <b>${s.decisionNeeded || "-"}</b>
      <br><small>${new Date(Number(s.createdAt)).toLocaleDateString("ja-JP")} 起票</small>
      <br><input placeholder="CEO判断メモ（例: B案・上限◯円）" id="sr-memo-${s.id}">
      <button onclick="resolveStaffRequest('${s.id}')">✅ 解決</button>`;
    wrap.appendChild(d);
  });
}
function resolveStaffRequest(id) {
  const s = fosData.staffRequests.find(x => x.id === id);
  if (!s) return;
  s.status = "resolved";
  s.resolvedAt = Date.now();
  s.ceoDecision = document.getElementById("sr-memo-" + id).value || "";
  saveData();              // ← アプリ既存の保存関数に合わせる
  renderStaffRequests(fosData);
}
</script>
```

## FUKUDA AI側の対応（実装済み・アプリ改修不要で今日から動く分）

- fos_importer v1.2.2: `status: resolved` の相談は自動で候補から外れる（既存動作）
- 暫定運用: 相談画面ができるまで、**新規相談はtasksに「【相談】」プレフィックス**で書けばスタッフ相談として扱う（FOS/README.md v1.3運用）
