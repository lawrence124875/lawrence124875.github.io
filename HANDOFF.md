# 內容網站交接檔

用問題型教學文章替三個 App 帶 Google 搜尋流量。專案總交接檔：lawrence124875/english-app-builds 分支 promo-videos 的 promo-videos/HANDOFF.md。

## 結構
- `build.py`：產生 `_site/`。原有手寫頁面（`index.html`、`tarot-cards/`、`terms/`、`app-ads.txt`）原樣複製，網址不變
- `src/langs/<語言>.json`：每種語言一檔，介面文字、App 名稱與介紹；`order` 決定語言列表順序，`dir` 可設 `rtl`（阿拉伯文）。各語言分檔，平行的語言 PR 不會互相衝突
- `src/style.css` 依 `lang` 切換中日韓泰阿字型
- `src/content/<語言>/<app>/<slug>.md`：文章。app 只能是 `iching`、`tarot`、`english`
  - 前置欄位：`title`、`description`（必填）、`order`（排序）
  - 不同語言用相同的 `<app>/<slug>` 配對，自動產生 hreflang
  - 塔羅、易經文章自動加「供自我反思與娛樂」；內文出現 NGSL 時自動加出處
  - 文末下載按鈕與延伸閱讀自動產生
- `src/style.css`：共用樣式，內嵌進每頁，不放追蹤碼
- `tools/og.py`：產生 `og/` 分享預覽圖（不複製進 `_site`，`og/` 會）
- `.github/workflows/site.yml`：PR 只建置並檢查 title、description、canonical、hreflang、sitemap；推到 main 後部署 Pages

## 原則
- 文章全部重新撰寫，不用 App 內的牌義、卦辭、爻辭、單字清單；只談方法與觀念
- 每種語言各自撰寫，標題用當地搜尋句型，不逐字翻譯
- 開新分支發 PR，不直接推 main

## 進度
- 已上線：11 語 × 19 篇，推到 main 後由 Actions 部署 Pages
- Search Console 已驗證並提交 sitemap；Bing 從 Search Console 匯入；Naver 已驗證。驗證 meta 放在根目錄 `index.html` 的 head
- 分享預覽圖：`og/<home|iching|tarot|english>.png`（1200×630，英文字，各語言共用），由 `python tools/og.py` 產生；`build.py` 依文章分類自動帶 og:image 與 twitter:card，語言首頁用 home

## 後續可做
- 約 4–6 週後看 Search Console「成效」報表，依各國曝光補文章或調整標題，並作為語言優先順序參考
