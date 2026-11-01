# Audio Notes｜錄音變成筆記

[English / 完整文件](README.md)

匯入自己的 MP3、M4A 或 WAV，由本機 Whisper 轉成有時間戳的逐字稿，匯出 TXT、Markdown、SRT。可另外主動使用本機 Ollama 產生附段落引用的摘要。

**目前是開源原型，不是已通過真實語音辨識驗收的成品。** 程式與邊界測試已完成；實際 Whisper／Ollama 推論、Windows／GPU、真實瀏覽器互動尚未驗證。沒有附模型或 EXE，也不會自己下載模型。

## Windows 快速開始

需要 Python 3.11+；辨識另外需要 PATH 裡有 FFmpeg／ffprobe。

```powershell
git clone https://github.com/skydreamer0/audio-notes.git
cd audio-notes
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

開啟 http://127.0.0.1:8765 。先看版面可直接開下載後的 `PREVIEW.html`，但它只是靜態預覽，不會轉錄。

### 啟用辨識

先停止服務，在同一個虛擬環境安裝引擎，指向你已取得且有權使用的 CTranslate2 Whisper 模型目錄：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-asr.txt
$env:AUDIO_MODEL_PATH = 'D:\Models\faster-whisper-small'
$env:AUDIO_DEVICE = 'cpu'
$env:AUDIO_COMPUTE_TYPE = 'int8'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

模型需要 `model.bin`、`config.json`、`tokenizer.json` 及該模型所需的其他檔案，不是單一 `.pt` 檔。先從 CPU/int8 確認；GPU 相容性依 upstream 文件，這個專案尚未實測。

### 選配摘要

先把 **Ollama 服務本身**設成 `OLLAMA_NO_CLOUD=1` 並重啟，確認日誌顯示 cloud disabled。再設定 `AUDIO_OLLAMA_MODEL` 為已安裝的本機模型名稱，重啟 Audio Notes。按「同意使用本機 Ollama 整理」才傳逐字稿。

程式會先檢查模型資訊，拒絕遠端模型及未知引用。`localhost` 不等於絕對離線：不要配置轉送代理。AI 摘要仍可能錯，請回查原文。

## 使用與資料

- 一次一個音檔，最多 100 MiB／2 小時；目前只接受純音訊。
- 確認有權使用錄音後再開始。沒有麥克風錄製、不讀聊天室、不送付費 API。
- 原音於處理完成、失敗或取消後移除；逐字稿只在記憶體，請先匯出再關閉服務。重新整理頁面不會恢復目前工作。
- 非正常終止可能留下 OS 暫存；刪除不是磁碟安全抹除。
- 只給本機單人使用，不要開放對外連線。
- 尚無逐字稿編輯、音訊播放、語者辨識、影片、批次或雲端同步。

[完整設定與疑難排解](README.md) · [已跑與未跑驗證](VERIFICATION.md) · [貢獻方式](CONTRIBUTING.md)
