# Audio Notes · Codex integration

**A Windows recording-and-transcription workspace built directly from two existing MIT projects—not another Whisper/Ollama rewrite.**

[繁體中文](README.zh-TW.md) · [Specification](SPEC.md) · [Verification](VERIFICATION.md) · [Source provenance](UPSTREAM.json)

> **Development source, not a tested Windows release.** Source integrity and static contract checks pass. This environment has no .NET/Rust/Windows toolchain: compilation, native UI, mock .NET execution and actual transcription are **not verified**. No EXE is published.

## What is actually reused?

| Upstream | Pinned revision | Used here |
|---|---|---|
| [A3Boy/codex-voice-input](https://github.com/A3Boy/codex-voice-input) | `f892017aeac3c122b41bc53a3b77c492d505bdc4` | Original WinUI/Win32 capsule, microphone recorder, waveform, controller, settings and history code |
| [Wangnov/codex-asr](https://github.com/Wangnov/codex-asr) | `479f6a7a3db81fe2a23d4755b0ccbeb4400317d4` | Original Rust CLI, HTTP server, authentication and upstream transcription implementation |

The unmodified source is in `vendor/`. `desktop/` contains the actual A3Boy-based application with a small, reviewable [integration patch](INTEGRATION.patch). This is a two-process integration, not a claim that C# and Rust can be pasted into one executable.

```text
A3Boy-based Windows capsule / file picker
    → adapted original recognition engine (loopback HTTP)
    → Wangnov codex-asr REST server
    → unofficial ChatGPT transcription service
    → original preview/history UI → TXT / Markdown / Codex prompt
```

The earlier Python/Whisper/Ollama prototype is superseded by this direction. It remains in Git history; it is not the current implementation or a required dependency.

## Intended workflow

- Record with the original capsule, or import WAV/MP3/M4A from Settings.
- Confirm recording rights and cloud transmission **before each transcription**.
- Preview recognized text. Clicking the ready capsule copies text; this integration does not automatically inject it into another application's input.
- Export the latest result as TXT, Markdown, or a prompt containing the transcript for your normal Codex workflow.
- Existing local history is retained (up to 200 entries). Clear it in Settings when no longer needed.

**No timestamps are supplied by this backend.** There is no SRT, speaker diarization, sentence timeline or automatic summary. The Codex prompt is an export—not a completed AI summary or an automatic Codex invocation.

## Requirements

Windows 10 version 2004 or later / Windows 11, x64; .NET 8 SDK with the required Windows build tools; Rust 1.82+ with an MSVC toolchain. NuGet/Cargo dependencies are resolved during build. WAV/MP3/M4A import uses upstream NAudio and Windows codec support; unsupported files must fail rather than fake a transcript.

No Whisper model, GPU, Ollama or paid API key is required by this integration. This does **not** mean upstream service availability or account eligibility is guaranteed.

## Build from source

These are instructions, **not commands executed during development verification**. Review the code before building. Build tools download third-party dependencies; do not run build steps in an environment where that is disallowed.

```powershell
# From the repository root, on a prepared Windows development machine:
cargo build --locked --release --manifest-path vendor/codex-asr/Cargo.toml
dotnet build desktop/CodexVoiceInput.sln -c Release -p:Platform=x64
```

The desktop assembly is named `AudioNotes`. There is no installer, autostart setup or prebuilt EXE in this repository. Original branding assets were intentionally excluded; compile-time references were removed and the original tray code falls back to a Windows icon.

## Configure and run deliberately

**Launching the Rust server reads its configured Codex/ChatGPT authentication. Transcribing sends audio to ChatGPT.** This is an unofficial endpoint, not an official OpenAI audio API. Review upstream authentication behavior and applicable service rules first. Audio Notes does not discover or copy authentication files in the desktop process and does not start the bridge automatically.

1. Separately configure your existing authorized Codex/ChatGPT login for the upstream bridge. Never paste access tokens into Issues, the UI or command-line arguments.
2. Create a separate local REST key in your own environment. Set `CODEX_ASR_SERVER_KEY` for the server and the same value as `AUDIO_CODEX_ASR_KEY` for the desktop. This is **not** your upstream login token. No key is provided in this repository.
3. In the desktop launch environment, set only the local endpoint:

```powershell
$env:AUDIO_CODEX_ASR_URL = 'http://127.0.0.1:8788/v1/audio/transcriptions'
# AUDIO_CODEX_ASR_KEY must already be set to your separate local server key.
```

4. When you intend to enable cloud transcription, run your reviewed build of the server:

```powershell
.\vendor\codex-asr\target\release\codex-asr.exe serve --host 127.0.0.1 --port 8788 --concurrency 1 --max-upload-mb 50
```

5. Launch the built `AudioNotes.exe` from its build output. Open Settings to import a file. No audio is sent until a transcription is requested and its confirmation is accepted.

The desktop adapter accepts only HTTP literal loopback (`127.0.0.1` or `[::1]`) and the exact `/v1/audio/transcriptions` path. It rejects arbitrary hosts, userinfo, query/fragment, redirects and inherited HTTP proxies. It does not fall back to direct upstream requests or another engine. Other local processes remain part of your trust boundary.

Global hotkeys are disabled by default. Explicitly set `AUDIO_NOTES_ENABLE_HOTKEY=1` before launch if you want the upstream hotkey registration. There is no automatic startup installation.

## Limits and privacy

- File import: ≤50 MiB, ≤10 minutes. Recording automatically stops around 10 minutes, then still asks permission before sending. The upstream author's guidance is under 11 minutes, not a service guarantee.
- One UI transcription at a time. The adapter has a five-minute deadline, bounded response size and no automatic retry.
- Cancel stops local waiting; it **cannot promise** to stop already-uploaded upstream processing or erase remote copies.
- Microphone temporary files are removed by the upstream recorder cleanup path. Imported originals are never deleted. Forced termination can leave temporary recordings.
- Config, text history and diagnostics are stored under `%LOCALAPPDATA%\AudioNotesCodex`, separate from the original upstream app. History persists across exits; it is not encrypted by this app. Do not share that directory as a bug report.
- Local REST keys stay in process configuration, not the UI or source. Raw HTTP response bodies are not displayed in adapter errors. Upstream server logging and storage behavior have their own trust boundary.
- Third-party endpoint/auth changes, account restrictions and transcription quality remain risks. This project is not affiliated with or endorsed by OpenAI or the upstream authors.

## Verification

Offline checks (Python standard library only):

```sh
python tools/verify_sources.py
python -m unittest discover -s tests -v
```

The verifier checks 38 original source blobs against pinned Git hashes, confirms the desktop file set, regenerates the integration diff in memory and parses project/XAML XML. Static checks do **not** establish C# compilation or runtime behavior.

A no-network .NET contract harness is included for a prepared .NET 8 environment:

```powershell
dotnet run --project tests/BridgeContract/BridgeContract.csproj
```

It injects a fake HTTP handler and synthetic bytes to check the multipart contract, safe errors, cancellation and invalid endpoints. It never reads a Codex login file or makes a real transcription call. This harness has **not run in the development environment**.

## Troubleshooting

- **Endpoint not configured:** set the exact loopback URL in the desktop's launch environment, then restart the desktop.
- **Authorization failure:** inspect the separate bridge login/local key configuration yourself; do not send us your token.
- **Import fails:** check duration, file size and Windows decoder support. A renamed extension does not make a valid audio file.
- **No text:** silence/recognition failure is not converted into an invented transcript.
- **Can't build WinUI here:** Linux source checks are not a substitute for Windows build tools; see the unverified items above.

## Contributing and licensing

Keep upstream source immutable; changes belong in `desktop/` and the reproducible integration patch. Run the offline verifier and record Windows/runtime evidence separately. Never submit recordings, authentication files or local logs. See [CONTRIBUTING](CONTRIBUTING.md) and [SECURITY](SECURITY.md).

Both upstream projects are MIT licensed, with their full original licenses/notices retained. [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES.md) explains the source mapping. The root MIT license covers original integration work; it does not erase upstream copyright or license their service access, dependencies or trademarks.
