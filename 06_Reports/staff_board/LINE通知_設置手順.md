# スタッフ相談 LINEボット — 設置手順 v2（LINE完結型・所要40分・無料）

**v2変更（2026-07-11 CEO指示）**: スタッフの入力はシートではなく**LINEで完結**。「相談」と送る→選択肢をタップしていくだけで相談が送信される対話ボット型。

```
スタッフ: LINEで「相談」→ ボタンをタップ（ブランド→カテゴリ→内容→A案/B案→おすすめ→期限）
   ↓ 自動でシートに記録（スタッフはシートを開かない）
FUKUDA AI: 毎朝Briefの判断候補に掲載 ／「今日中」の相談はCEOのLINEに即時通知
   ↓
CEO: シートの「CEO回答」列に記入＋状態=回答済み
   ↓ 5分以内
スタッフのLINE: 「【福田より回答】…」が自動で届く
```

---

## STEP 1. シート（記録用・スタッフは触らない）

1. **スタッフ相談ボード_雛形.xlsx** をGoogleドライブへ→「Googleスプレッドシートとして保存」
2. 共有は**CEOのみでOK**（スタッフに共有不要になりました）

## STEP 2. LINE公式アカウント（10分）

1. https://developers.line.biz/ → プロバイダー「NOMADO」→ チャネル作成 → **Messaging API**
2. チャネル名: **NOMADO 福田**（スタッフに見える名前）
3. 「Messaging API設定」→ **チャネルアクセストークン（長期）発行** → コピー
4. LINE Official Account Manager: あいさつメッセージON（文面:「NOMADOの相談窓口です。①最初に『登録 お名前』と送信 ②相談したい時は『相談』と送ってください」）・**応答メッセージOFF・Webhook ON**

## STEP 3. スクリプト（15分）

シートの「拡張機能 > Apps Script」に以下を**全文**貼り付け:

```javascript
const PROPS = PropertiesService.getScriptProperties();
const TOKEN = PROPS.getProperty("LINE_TOKEN");
const CEO_UID = PROPS.getProperty("CEO_USER_ID"); // 任意（今日中相談の即時通知先）
const CACHE = CacheService.getScriptCache();      // 対話の途中状態（6時間保持）

const BRANDS = ["so u", "SUNNY NOMADO", "催事", "EC", "その他"];
const CATS = ["発注・数量", "在庫", "価格", "催事対応", "顧客対応", "出荷・納期", "その他"];
const TEMPLATES = ["再入荷の数量を決めたい", "追加発注の可否", "価格を確認したい",
                   "納期・出荷日を確認したい", "不良・破損の対応", "✏️自由に入力する"];
const RECS = ["A案", "B案", "どちらでも", "CEOにお任せ"];
const DUES = ["今日中", "明日中", "今週中", "急ぎではない"];

function doPost(e) {
  const body = JSON.parse(e.postData.contents);
  (body.events || []).forEach(handleEvent);
  return ContentService.createTextOutput("OK");
}

function handleEvent(ev) {
  if (ev.type !== "message" || ev.message.type !== "text") return;
  const uid = ev.source.userId, text = ev.message.text.trim();

  if (text.indexOf("登録") === 0) {                       // ---- 初回登録 ----
    const name = text.replace(/^登録[ 　]*/, "");
    if (!name) return reply(ev.replyToken, "「登録 お名前」の形で送ってください（例: 登録 山田）");
    SpreadsheetApp.getActive().getSheetByName("スタッフマスタ").appendRow([name, uid, new Date()]);
    return reply(ev.replyToken, name + "さんを登録しました。相談したい時は「相談」と送ってください。");
  }
  if (text === "相談" || text === "相談する") {            // ---- 相談開始 ----
    CACHE.put(uid, JSON.stringify({ step: "brand", d: {} }), 21600);
    return ask(ev.replyToken, "どのブランド・案件ですか？（タップで選択）", BRANDS);
  }
  if (text === "キャンセル") { CACHE.remove(uid); return reply(ev.replyToken, "相談を中止しました。"); }

  const raw = CACHE.get(uid);
  if (!raw) return reply(ev.replyToken, "相談を始めるには「相談」、名前の登録は「登録 お名前」と送ってください。");
  const s = JSON.parse(raw);
  const save = function () { CACHE.put(uid, JSON.stringify(s), 21600); };

  switch (s.step) {                                       // ---- 対話フロー ----
    case "brand":
      s.d.brand = text; s.step = "cat"; save();
      return ask(ev.replyToken, "相談のカテゴリは？", CATS);
    case "cat":
      s.d.cat = text; s.step = "content"; save();
      return ask(ev.replyToken, "相談内容を選ぶか、自由入力を選んでください", TEMPLATES);
    case "content":
      if (text === "✏️自由に入力する") { s.step = "content_free"; save();
        return reply(ev.replyToken, "相談内容を一言で入力してください"); }
      s.d.content = text; s.step = "optA"; save();
      return reply(ev.replyToken, "A案があれば入力してください（なければ「なし」と送信）");
    case "content_free":
      s.d.content = text; s.step = "optA"; save();
      return reply(ev.replyToken, "A案があれば入力してください（なければ「なし」と送信）");
    case "optA":
      s.d.a = (text === "なし") ? "" : text; s.step = "optB"; save();
      return reply(ev.replyToken, "B案があれば入力してください（なければ「なし」と送信）");
    case "optB":
      s.d.b = (text === "なし") ? "" : text; s.step = "rec"; save();
      return ask(ev.replyToken, "あなたのおすすめは？", RECS);
    case "rec":
      s.d.rec = text; s.step = "due"; save();
      return ask(ev.replyToken, "いつまでに回答が必要ですか？", DUES);
    case "due":
      s.d.due = text; CACHE.remove(uid);
      return finalize(uid, ev.replyToken, s.d);
  }
}

function finalize(uid, replyToken, d) {
  const ss = SpreadsheetApp.getActive();
  const name = lookupName(uid) || ("未登録(" + uid.slice(-6) + ")");
  ss.getSheetByName("相談受付").appendRow([new Date(), name, d.brand, d.cat, d.content,
    d.a, d.b, d.rec, d.due, "未回答", "", ""]);
  reply(replyToken, "✅ 受け付けました。回答が決まり次第このトークにお送りします。\n――――\n" +
    d.brand + " / " + d.cat + "\n相談: " + d.content + "\nA案: " + (d.a || "-") +
    " / B案: " + (d.b || "-") + "\nおすすめ: " + d.rec + " / 希望: " + d.due);
  if (d.due === "今日中" && CEO_UID) {
    push(CEO_UID, "🚨 今日中の相談が届きました\n" + name + "さん / " + d.brand + " / " + d.cat +
      "\n" + d.content + "\nA: " + (d.a || "-") + " / B: " + (d.b || "-") + "（推奨: " + d.rec + "）");
  }
}

// ---- CEO回答 → スタッフLINEへ（5分ごと自動実行） ----
function notifyAnswers() {
  const ss = SpreadsheetApp.getActive();
  const sh = ss.getSheetByName("相談受付");
  const data = sh.getDataRange().getValues();
  const H = data[0];
  const col = function (n) { return H.indexOf(n); };
  const cContent = H.findIndex(function(h){ return String(h).indexOf("相談内容") === 0; });
  for (let i = 1; i < data.length; i++) {
    const r = data[i];
    if (r[col("CEO回答")] && r[col("状態")] === "回答済み" && !r[col("LINE通知")]) {
      const uid = lookupUid(String(r[col("名前")]).trim());
      if (!uid) { sh.getRange(i + 1, col("LINE通知") + 1).setValue("⚠LINE未登録"); continue; }
      push(uid, "【福田より回答】\n相談: " + r[cContent] + "\n回答: " + r[col("CEO回答")]);
      sh.getRange(i + 1, col("LINE通知") + 1).setValue("通知済み " + new Date().toLocaleString("ja-JP"));
    }
  }
}

// ---- 共通 ----
function lookupName(uid) { return lookupStaff(1, uid, 0); }
function lookupUid(name) { return lookupStaff(0, name, 1); }
function lookupStaff(keyCol, key, valCol) {
  const rows = SpreadsheetApp.getActive().getSheetByName("スタッフマスタ").getDataRange().getValues().slice(1);
  for (const r of rows) if (String(r[keyCol]).trim() === key) return r[valCol];
  return null;
}
function ask(replyToken, text, options) {
  line("reply", { replyToken: replyToken, messages: [{ type: "text", text: text,
    quickReply: { items: options.map(function (o) {
      return { type: "action", action: { type: "message", label: o.slice(0, 20), text: o } }; }) } }] });
}
function reply(replyToken, text) { line("reply", { replyToken: replyToken, messages: [{ type: "text", text: text }] }); }
function push(to, text) { line("push", { to: to, messages: [{ type: "text", text: text }] }); }
function line(ep, payload) {
  UrlFetchApp.fetch("https://api.line.me/v2/bot/message/" + ep, { method: "post",
    contentType: "application/json", headers: { Authorization: "Bearer " + TOKEN },
    payload: JSON.stringify(payload), muteHttpExceptions: true });
}
```

設定3つ:
1. ⚙プロジェクトの設定 > スクリプトプロパティ → `LINE_TOKEN` = STEP2のトークン。（任意）`CEO_USER_ID` = CEOも友だち追加して「登録 福田」と送るとスタッフマスタに自分のIDが記録されるので、それをコピーして設定 → **「今日中」相談が即あなたのLINEに飛びます**
2. デプロイ > 新しいデプロイ > 「ウェブアプリ」→ アクセス「全員」→ URLをLINE DevelopersのWebhook URLへ（検証で成功を確認）
3. トリガー: `notifyAnswers` を時間主導型・**5分おき**

## STEP 4. スタッフへの案内（これだけ）

「①QRコードから友だち追加 → ②『登録 自分の名前』と送信 → ③相談したい時は『相談』と送ってボタンを選ぶだけ」

## STEP 5. FUKUDA AIへの接続（私の作業・シートURL共有後）

未回答の相談を毎朝Briefの判断候補へ自動掲載（staff_requests_importer実装）。CEOはBriefで判断→シートに一言記入→LINEへ自動返信、で一巡します。

---

### スタッフから見た画面イメージ

```
スタッフ: 相談
ボット: どのブランド・案件ですか？ [so u][SUNNY NOMADO][催事][EC][その他]
スタッフ: （so u をタップ）
ボット: 相談のカテゴリは？ [発注・数量][在庫][価格]…
スタッフ: （発注・数量 をタップ）
ボット: 相談内容を選ぶか、自由入力を選んでください [再入荷の数量を決めたい]…
スタッフ: （再入荷の数量を決めたい をタップ）
ボット: A案があれば入力してください（なければ「なし」）
スタッフ: 前回と同数
ボット: B案は？
スタッフ: 1.5倍に増やす
ボット: あなたのおすすめは？ [A案][B案][どちらでも][CEOにお任せ]
スタッフ: （B案 をタップ）
ボット: いつまでに回答が必要ですか？ [今日中][明日中][今週中][急ぎではない]
スタッフ: （今週中 をタップ）
ボット: ✅ 受け付けました。回答が決まり次第このトークにお送りします。
```
タップ6回+入力2回（A案/B案のみ）・約30秒です。
