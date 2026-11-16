# 內容網站交接檔

用問題型教學文章替三個 App 帶 Google 搜尋流量。專案總交接檔：lawrence124875/english-app-builds 分支 promo-videos 的 promo-videos/HANDOFF.md。

## 結構
- `build.py`：產生 `_site/`。原有手寫頁面（`index.html`、`tarot-cards/`、`terms/`、`app-ads.txt`）原樣複製，網址不變
- `src/langs.json`：每種語言的介面文字、App 名稱與介紹；`dir` 可設 `rtl`（阿拉伯文）
- `src/content/<語言>/<app>/<slug>.md`：文章。app 只能是 `iching`、`tarot`、`english`
  - 前置欄位：`title`、`description`（必填）、`order`（排序）
  - 不同語言用相同的 `<app>/<slug>` 配對，自動產生 hreflang
  - 塔羅、易經文章自動加「供自我反思與娛樂」；內文出現 NGSL 時自動加出處
  - 文末下載按鈕與延伸閱讀自動產生
- `src/style.css`：共用樣式，內嵌進每頁，不放追蹤碼
- `.github/workflows/site.yml`：PR 只建置並檢查 title、description、canonical、hreflang、sitemap；推到 main 後部署 Pages

## 原則
- 文章全部重新撰寫，不用 App 內的牌義、卦辭、爻辭、單字清單；只談方法與觀念
- 每種語言各自撰寫，標題用當地搜尋句型，不逐字翻譯
- 開新分支發 PR，不直接推 main

## 進度
- 繁中、英文：19 篇 × 2 語完成（謙卦 6、光穗塔羅 7、智慧聽覺巡航 6），PR #13

## 待辦：其餘 9 語（每批 3 語，每種語言各自發 PR，一批審完再做下一批）
1. 日文 ja、韓文 ko、簡中 zh-CN
2. 西班牙文 es、葡萄牙文 pt、印尼文 id
3. 泰文 th、越南文 vi、阿拉伯文 ar（`dir: rtl`）

每種語言的做法：在 `src/langs.json` 加一筆，寫 19 篇到 `src/content/<語言>/`，slug 與繁中、英文相同；自審用語、事實與手機版面。

## 使用者手動事項
1. **Pages 來源**：repo Settings → Pages → Build and deployment → Source 改成「GitHub Actions」（合併 PR 前做）
2. **Search Console 驗證**：到 https://search.google.com/search-console 新增資源，選「網址前置字元」填 `https://lawrence124875.github.io/`，驗證方式選「HTML 標記」，把 meta 標籤內容交給 Claude 加進 `build.py`（或選「HTML 檔案」，把檔案放到 repo 根目錄）
3. **提交 sitemap**：驗證後在 Search Console →「Sitemap」提交 `sitemap.xml`
4. 約 4–6 週後看「成效」報表，各國家的曝光可作為後續語言優先順序的參考
