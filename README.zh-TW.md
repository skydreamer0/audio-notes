# Audio Notes · Codex 原碼整合版

**直接整合兩個既有 MIT 專案，不再另寫 Whisper／Ollama 主線。**

[English](README.md) · [SPEC](SPEC.md) · [驗證紀錄](VERIFICATION.md) · [原始碼對照](UPSTREAM.json)

> 目前交付開發原始碼，不是已驗收的 Windows 版本。來源雜湊及靜態契約檢查通過；這個環境沒有 .NET／Rust／Windows 工具鏈，因此編譯、Windows GUI、.NET mock 執行及真實轉錄都尚未驗證。沒有發布 EXE。

## 直接用了哪些程式？

- **[A3Boy/codex-voice-input](https://github.com/A3Boy/codex-voice-input)**：固定 `f892017aeac3c122b41bc53a3b77c492d505bdc4`，沿用原本 WinUI／Win32 膠囊、麥克風錄音、波形、狀態控制器、設定及歷史記錄。
- **[Wangnov/codex-asr](https://github.com/Wangnov/codex-asr)**：固定 `479f6a7a3db81fe2a23d4755b0ccbeb4400317d4`，沿用 Rust CLI、REST server、登入與上游轉錄程式。

`vendor/` 保留原始碼不修改；`desktop/` 是套用最小接線修改的原生程式。[INTEGRATION.patch](INTEGRATION.patch) 列出所有修改。這是兩個程序透過本機 HTTP 整合，不是假稱 Rust 與 C# 貼在一起就能成為單一 EXE。

```text
原生膠囊錄音／檔案匯入 → 修改後的原辨識 engine
→ 本機 codex-asr → ChatGPT 非官方雲端辨識
→ 原預覽與歷史介面 → TXT／Markdown／Codex 整理提示稿
```

先前 Python／Whisper／Ollama 原型不再是目前方向，也不是必要依賴；舊版仍留在 Git 歷史。

## 使用流程

1. 用原膠囊錄音，或從設定匯入 WAV／MP3／M4A。
2. 每次送出前，確認錄音使用權與雲端傳輸同意。
3. 預覽文字；點擊完成的膠囊只複製文字，不自動注入別的程式輸入框。
4. 從設定匯出最新一筆 TXT、Markdown 或交給你自己的 Codex 使用的整理提示稿。
5. 原有歷史功能保留，最多 200 筆；不需要時在設定清空。

**後端沒有提供時間戳。** 不顯示假時間線，也沒有 SRT、語者分離或自動摘要。Codex 提示稿是匯出功能，不是已執行的 AI 摘要，也不會自行啟動 Codex。

## 建置需求與步驟

Windows 10 2004 以上／Windows 11，x64；.NET 8 SDK 與 Windows 建置工具；Rust 1.82 以上與 MSVC 工具鏈。建置會透過 NuGet／Cargo 下載相依套件。匯入使用原專案 NAudio 與 Windows 解碼能力，格式不支援時應失敗，不產生假逐字稿。

不需要 Whisper 模型、GPU、Ollama 或付費 API key；這不代表上游服務永遠可用或所有帳戶皆可用。

以下是供已備妥 Windows 開發環境使用的指令，本輪沒有執行；請先審閱原始碼：

```powershell
cargo build --locked --release --manifest-path vendor/codex-asr/Cargo.toml
dotnet build desktop/CodexVoiceInput.sln -c Release -p:Platform=x64
```

組件名稱為 `AudioNotes`，不提供安裝程式、開機啟動或預建 EXE。未攜入上游品牌圖片；編譯引用已移除，托盤沿用原程式的 Windows 預設圖示備援。

## 明確配置後才啟動

**啟動 Rust server 會讀取它配置的 Codex／ChatGPT 登入資料；轉錄會將音檔傳至 ChatGPT。** 這不是官方 OpenAI audio API。請先核對上游登入行為與服務規則。桌面程式不搜尋／複製登入檔，也不自動啟動 bridge。

1. 自行為上游 bridge 配置已授權的既有登入。不要把 access token 貼進 Issue、UI 或命令列。
2. 自行配置獨立的本機 REST key：server 的 `CODEX_ASR_SERVER_KEY` 與桌面的 `AUDIO_CODEX_ASR_KEY` 要一致。這不是你的上游登入 token；專案沒有附任何密鑰。
3. 桌面啟動環境設定：

```powershell
$env:AUDIO_CODEX_ASR_URL = 'http://127.0.0.1:8788/v1/audio/transcriptions'
# AUDIO_CODEX_ASR_KEY 應已設定為你自己的本機 REST key。
```

4. 確定要啟用雲端辨識後，才執行已審閱的 bridge 建置產物：

```powershell
.\vendor\codex-asr\target\release\codex-asr.exe serve --host 127.0.0.1 --port 8788 --concurrency 1 --max-upload-mb 50
```

5. 從建置輸出啟動 `AudioNotes.exe`，開設定匯入音檔。要求轉錄並同意前不會外送。

桌面 adapter 僅接受 HTTP 的 `127.0.0.1`／`[::1]` 與固定 `/v1/audio/transcriptions` 路徑；拒絕任意網域、userinfo、query／fragment、重新導向與環境代理。不會偷偷改走其他引擎或直接呼叫上游。同機其他程序仍屬於你必須信任的範圍。

全域快捷鍵預設不註冊；需要時自行在啟動前設定 `AUDIO_NOTES_ENABLE_HOTKEY=1`。不會自動設定開機啟動。

## 限制與資料保存

- 匯入最多 50 MiB、10 分鐘；錄音約 10 分鐘自動停止，之後仍需同意才送出。上游作者的 11 分鐘建議不是服務保證。
- UI 同時一個轉錄；adapter 五分鐘期限、回應大小上限、不自動重試。
- 取消只能停止本機等待，不能保證停止已送出的遠端運算或刪除遠端副本。
- 麥克風暫存沿用原錄音器清理；匯入的原檔不刪除。強制結束可能留下暫存錄音。
- 設定、文字歷史、診斷位於 `%LOCALAPPDATA%\AudioNotesCodex`，與原版分開。歷史退出後仍保存，未由本程式加密；不要直接上傳該目錄回報問題。
- 本機 REST key 不放 UI／程式碼；adapter 不顯示 HTTP 原始錯誤本文。Rust server 的紀錄與資料處理另有自己的信任邊界。
- 非官方端點、登入格式、帳戶限制與辨識品質皆有風險。專案不代表 OpenAI 或原作者背書。

## 驗證與排錯

```sh
python tools/verify_sources.py
python -m unittest discover -s tests -v
```

以上只需 Python 標準函式庫，核對 38 個 upstream blob、desktop 清單、可重現 diff 與 XML／靜態契約，**不是 C# 編譯或 GUI 驗收**。

另附不連網的 .NET mock handler 契約測試：

```powershell
dotnet run --project tests/BridgeContract/BridgeContract.csproj
```

測試僅用假 HTTP handler 與合成 bytes，不讀登入、不錄音、不呼叫真實轉錄。此環境尚未執行它。

常見問題：未設 URL 要先設定並重啟；授權錯誤自行檢查 bridge 登入與本機 key，不要寄 token；匯入失敗核對格式／長度／大小及 Windows decoder；空白辨識不會補造文字。Linux 靜態檢查不能取代 Windows 建置。

## 貢獻與授權

保留 vendor 不變，改動置於 desktop 與可重現 patch。不要提交錄音、登入檔或本機 log。詳見 [CONTRIBUTING](CONTRIBUTING.md)、[SECURITY](SECURITY.md)、[THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES.md)。兩庫 MIT 原文與著作權完整保留；根目錄 MIT 只涵蓋本專案新增接線，不抹去原作者權利，也不授權上游服務、相依套件或商標。
