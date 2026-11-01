# Audio Notes MVP specification

## Outcome
A local single-user workflow: import a permitted recording → timestamped transcript → TXT/Markdown/SRT; optionally request a source-referenced summary from a local model.

## Architecture
- Independently written FastAPI API plus plain HTML/CSS/JavaScript UI.
- FFprobe checks media; FFmpeg converts audio to mono 16 kHz WAV.
- A separate Python process runs faster-whisper from a configured local model directory. Required model files are checked before loading; no automatic download.
- The API owns job state and temporary-file cleanup. Transcripts stay in process memory.
- An explicit summary request first checks Ollama model metadata, then sends text to the fixed loopback endpoint. Remote metadata is rejected; users must configure Ollama local-only. Reference validation does not establish factual accuracy.

## Boundaries
100 MiB / 2 hours, MP3/M4A/WAV audio-only, one active transcription, 20 retained in-memory jobs. Generated filenames, bounded streaming input, subprocess argument arrays, protocol restrictions, execution timeouts, token/Origin/Host checks and no CORS.

Cancel stops the active transcription process. Original audio is removed after completion, failure or cancellation; graceful shutdown cleans active jobs. Forced termination may leave OS temporary files. The service must not be internet-facing.

## Acceptance evidence
Required tests cover empty/invalid/oversized input, extension spoofing, filename traversal avoidance, duration and stream checks, missing model dependencies, cancellation/cleanup, export timestamps, consent, local-model preflight and stale UI responses. Real ASR and real-browser acceptance remain separate gates; stubs must never be presented as real recognition results.

## Deferred
Microphone capture, diarization, video, editing, playback, batch jobs, persistent storage, cloud APIs and sync. No unofficial ChatGPT/Codex endpoint, cookie or token extraction.

## Reference projects
Workflow and documentation research: Vibe, Scriberr and imnotwallace/LocalScribe. Optional engine: SYSTRAN/faster-whisper. Potential future engine: ggml-org/whisper.cpp. Links and licensing boundaries are in README. No source, artwork or prose was copied from these projects.
