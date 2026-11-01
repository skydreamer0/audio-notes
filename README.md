# Audio Notes

**Turn recordings into timestamped notes — with a local-first workflow you can inspect.**

Import an audio file, run a local Whisper model, export a transcript, and optionally ask a local Ollama model to summarize it with links back to the source segments.

[繁體中文快速開始](README.zh-TW.md) · [Architecture & scope](SPEC.md) · [Verification](VERIFICATION.md) · [Contributing](CONTRIBUTING.md)

> **Early source prototype.** The upload, validation, job lifecycle, export and safety boundaries have automated tests. Real Whisper transcription accuracy, real Ollama inference, Windows/GPU execution and browser interaction have **not yet been validated**. No models or desktop installer are bundled. This is not a production-ready transcription service.

## Why this project?

Audio Notes keeps the first workflow small: **one recording → one transcript → notes you can take elsewhere**. It is intended for people who want to run a readable, self-hosted tool on their own computer rather than send recordings to a hosted transcription service.

The interface currently uses Traditional Chinese. Open [`PREVIEW.html`](PREVIEW.html) from your downloaded copy for an offline **static layout preview**. It does not transcribe files or display fabricated results. For a working interface, start the server below.

## What is implemented?

| Capability | Current implementation |
| --- | --- |
| Import | MP3, M4A and WAV; actual media probing, not extension-only checks |
| Transcription | Local `faster-whisper` adapter, timestamped segments; requires your own compatible model |
| Job control | One transcription at a time; status, cancel and delete |
| Export | Plain text, Markdown and SRT subtitles |
| Optional summary | Explicit action, local Ollama model preflight, segment references |
| Data retention | Original audio removed after processing; transcripts kept in server memory until deleted or server shutdown |
| Dependencies | No external frontend CDN, telemetry, accounts or paid API integration |

**Not included:** live microphone capture, speaker diarization, transcript editing, video import, batch queues, cloud sync, automatic model downloads or unofficial ChatGPT/Codex endpoints. A supported API adapter is not proof of successful real-model validation; see [verification](VERIFICATION.md).

## Quick start

### Prerequisites

- Python **3.11 or newer**. The initial test environment used Python 3.12 on Linux.
- [FFmpeg and ffprobe](https://ffmpeg.org/download.html) on `PATH` for media validation and conversion. Although faster-whisper itself uses PyAV, **this app also needs the FFmpeg command-line tools**.
- A modern browser. The server is intended for **one local user**, bound to `127.0.0.1` only.
- For real transcription: `faster-whisper` and an already downloaded, compatible CTranslate2 Whisper model directory.
- Optional: a local-only Ollama installation with an already installed model.

### 1. Get the source and start the interface

```bash
git clone https://github.com/skydreamer0/audio-notes.git
cd audio-notes
python -m venv .venv
```

**Windows PowerShell** — no activation or execution-policy changes needed:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

**Linux / macOS:**

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Open **http://127.0.0.1:8765**. The interface reports whether an ASR model is configured. Without it, the app does **not** generate pretend transcripts.

### 2. Enable local transcription

Stop the server, install the optional engine, and point the app at a model you obtained from a trusted source. Check the model's own license and the [faster-whisper model instructions](https://github.com/SYSTRAN/faster-whisper#model-conversion). A model directory needs `model.bin`, `config.json`, `tokenizer.json` and any vocabulary/preprocessor files required by that model. An OpenAI Whisper `.pt` file alone is not compatible.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-asr.txt
$env:AUDIO_MODEL_PATH = 'D:\Models\faster-whisper-small'
$env:AUDIO_DEVICE = 'cpu'
$env:AUDIO_COMPUTE_TYPE = 'int8'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

**Linux / macOS:**

```bash
.venv/bin/python -m pip install -r requirements-asr.txt
export AUDIO_MODEL_PATH="$HOME/Models/faster-whisper-small"
export AUDIO_DEVICE=cpu
export AUDIO_COMPUTE_TYPE=int8
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Choose a short recording you have permission to process, confirm consent, then select **開始轉錄** (Start transcription). When it finishes, export before closing the server. Language detection is automatic; recognition quality depends on the model and recording.

The app refuses incomplete model directories, requests local files only and sets offline flags in the worker. It never downloads a model automatically. The first inference loads the model and may take time.

### 3. Optional local AI summary

1. Configure the **Ollama server itself** with `OLLAMA_NO_CLOUD=1`, restart it and verify its log reports cloud disabled. Follow the [official local-only instructions](https://github.com/ollama/ollama/blob/main/docs/faq.mdx#how-do-i-disable-ollamas-cloud-features).
2. Install a suitable local model yourself. No model is selected or downloaded by this app.
3. Set `AUDIO_OLLAMA_MODEL` to its exact local model name before starting Audio Notes.
4. After transcription, select **同意使用本機 Ollama 整理** (Consent to local Ollama summary).

For example, in PowerShell:

```powershell
$env:AUDIO_OLLAMA_MODEL = 'your-installed-local-model'
```

Only the transcript is sent, to the fixed `http://127.0.0.1:11434` endpoint. Proxy environment settings and redirects are not used. Before sending transcript text, `/api/show` must return local model metadata and no `remote_host` or `remote_model`. Unknown segment references are rejected.

**A loopback address alone does not guarantee local inference.** Do not put a forwarding proxy at that address. The app cannot attest to arbitrary software running on your computer. AI summaries can still misrepresent a passage even when their references are valid: review the original text.

## Configuration

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `AUDIO_MODEL_PATH` | unset | Existing local CTranslate2 model directory |
| `AUDIO_DEVICE` | `cpu` | faster-whisper device; e.g. `cpu` or `cuda` |
| `AUDIO_COMPUTE_TYPE` | `int8` | Engine compute type; must fit the chosen device/model |
| `AUDIO_OLLAMA_MODEL` | unset | Installed local Ollama model; summaries unavailable when unset |

Start with CPU/int8. GPU setup depends on the installed CTranslate2, CUDA and cuDNN versions; consult the [upstream GPU requirements](https://github.com/SYSTRAN/faster-whisper#gpu). Windows and GPU configuration have not been tested by this project. There are no speed or memory-use promises.

## Example output

**Hand-written format example — not a model result or a real recording:**

```srt
1
00:00:00,000 --> 00:00:02,400
We will review the draft on Friday.

2
00:00:02,400 --> 00:00:05,000
Please bring the updated checklist.
```

Transcript exports preserve segment timing. The summary view links back to segment IDs; summaries are not currently included in exports. There is no built-in audio playback or seek control yet.

## Privacy and boundaries

- The intended execution environment is **your own computer**, not a hosted demo. A cloud-hosted copy would receive any files uploaded to it.
- Process only recordings you have the right to use, including any required participant consent.
- The app does not access microphones, meeting apps, chats or browser sessions.
- Uploads use random temporary directories and fixed internal filenames. Size is checked while streaming. Media tools run with argument arrays, timeouts and a restricted protocol list.
- Original uploads and converted audio are removed after completion, failure or cancellation. Transcripts and summaries stay in RAM; browser exports remain wherever you save them.
- Normal shutdown cleans active jobs. A crash or forced termination may leave OS temporary directories named `audio-notes-*`. Remove those only after confirming no job is active. Deletion is **not secure disk erasure**.
- API calls require a per-process token; Host and Origin checks are enforced. This is not multi-user authentication. **Do not bind to `0.0.0.0`, expose ports publicly or treat it as an internet service.**
- No recordings, model weights, API keys or personal transcripts belong in this repository.

## Limits

- At most **100 MiB** per upload and **2 hours** per recording.
- One active transcription and up to 20 in-memory job records.
- Audio-only media: video and cover-art streams are currently rejected.
- Upload cancellation is unavailable in the UI until a job ID is returned; closing the page can interrupt the request.
- Transcription cancellation stops the worker; summary requests do not have hard cancellation.
- Summary input is limited to 50,000 JSON-serialized characters; no long-document chunking yet.
- Reloading the page does not restore the current job in the UI. Export first; restarting the server clears its memory.
- Real recognition quality, silence hallucinations, very long recordings, Windows/GPU and browser behavior need further validation.

## Development and tests

```bash
python -m unittest discover -s tests -v
node tests/test_ui.js
node --check app/static/app.js
```

Use your virtual environment's Python executable if it is not activated. Node.js 18+ is needed only for the UI contract test. Tests use generated silence and explicitly marked stubs, not private recordings. A passing stub test does **not** mean speech recognition works. [VERIFICATION.md](VERIFICATION.md) separates executed checks from untested integration stages.

```text
Browser UI ── same-origin, token-protected requests ── FastAPI
                                                        │
                                   validate → convert → local ASR subprocess
                                                        │
                                            in-memory transcript → exports
                                                        │
                                      explicit consent → local Ollama preflight
                                                        └─ referenced summary
```

`app/main.py` owns uploads, jobs and export; `app/worker.py` loads local models in a cancellable process; `app/static/` has the dependency-free UI. There is no database or persistent background daemon installed by this project.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| “Engine not ready” / 本機辨識引擎未就緒 | Install optional requirements in the same venv; verify `AUDIO_MODEL_PATH` and required files; restart the server |
| Media processing fails | Run `ffmpeg -version` and `ffprobe -version`; confirm the file is valid audio-only MP3/M4A/WAV |
| Summary unavailable | Set the exact installed local model name, start Ollama locally with cloud disabled, then restart Audio Notes |
| Summary rejected | A remote model, missing local metadata, invalid references or an unreachable server is rejected; transcript is retained |
| GPU errors | Return to CPU/int8, then check upstream CUDA/CTranslate2 compatibility separately |
| Port already used | Choose another local port, such as `--port 8766`, and open that URL |
| Directly opened HTML does nothing | `PREVIEW.html` is static; launch the Python server for functionality |

Do not paste recordings, full transcripts, private paths or credentials into public bug reports. See [SECURITY.md](SECURITY.md).

## Roadmap

- [ ] Real, consented short-audio acceptance fixtures and accuracy review
- [ ] Windows CPU and GPU setup validation
- [ ] Real-browser accessibility and interrupted-flow tests
- [ ] Transcript editing and audio playback/seek
- [ ] Grounded long-transcript summarization with summary export
- [ ] Additional adapters, only with explicit data-flow consent

These are planned directions, not shipped features or delivery commitments.

## Contributing

Small, tested improvements are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md), describe the behavior and keep privacy boundaries intact. For security concerns, follow [SECURITY.md](SECURITY.md). There is no guaranteed support response time.

## Acknowledgments and license

The documentation organization and workflow research were informed by [Vibe](https://github.com/thewh1teagle/vibe), [Scriberr](https://github.com/rishikanthc/Scriberr) and [LocalScribe](https://github.com/imnotwallace/LocalScribe). They are independent projects, not dependencies, sponsors or endorsements. No UI code, artwork, README prose or model assets were copied from them.

The optional ASR integration uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper); [whisper.cpp](https://github.com/ggml-org/whisper.cpp) is a potential future alternative. Summaries use the [Ollama chat API](https://docs.ollama.com/api/chat).

Original Audio Notes code is available under the [MIT License](LICENSE). Dependencies, model weights and FFmpeg distributions have **their own licenses**; this repository does not relicense or bundle them. Check the licenses of the exact packages, model and FFmpeg build you install or redistribute.
