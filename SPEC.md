# Codex source integration specification

## User-requested direction
Directly reuse A3Boy/codex-voice-input and Wangnov/codex-asr source, not a new independently implemented UI/ASR backend. Supersedes the first Python/Whisper/Ollama prototype at main `7b300569e158c183dab8e1d62cbf6df0c6bd48c7`.

## Source boundary
38 unmodified text source/build/license files are pinned in UPSTREAM.json. Original C# application copied into desktop; only integration-related files patched, with a complete reproducible INTEGRATION.patch. Rust source remains unchanged. Original upstream workflows, installers, screenshots and binary branding assets are excluded. Missing icon compile references are removed; the existing Windows tray fallback is retained.

## Integration
Reuse original recording, capsule, controller, settings and history. Adapt original C# engine from direct auth/upstream HTTP to user-configured literal-loopback Wangnov REST. Remove desktop auth discovery/JWT parsing/direct upstream fallback; no script autostarts bridge. Separate app data/mutex avoids modifying upstream installation data. Global hotkeys opt-in; ready click copies instead of injecting.

Add native Settings file import and latest-result TXT/Markdown/Codex-prompt export. Import is size/duration checked with NAudio; originals never deleted. Recording reuses upstream cleanup and auto-stops around 10 minutes. Each recording/import requires a modal cloud-consent confirmation before engine invocation. API key is a separate local REST key, environment only. Server login remains Wangnov's existing implementation and must be configured/run explicitly by the user.

## Contract / limits
MP3/M4A/WAV import, 50 MiB, 10 minutes. Loopback HTTP path /v1/audio/transcriptions only; no proxy inheritance/redirects/DNS host/userinfo/query/fragment. JSON text only, response 1 MiB and 5-minute deadline; no retries. Missing/empty/invalid text has visible failure, not fabricated output. No timestamps/SRT/diarization; summary is prompt export only, not an AI service. Cancel local work cannot retract remote processing. Native history persists to 200 entries; user may clear it, no encryption promised.

## Verification and release gates
Before source publication: provenance/git hashes, exact source set, reproducible diff, static XML/contract checks, independent source review. Provide no-network .NET mock harness but do not claim it passed without executing it. Windows compilation/UI, dependency restore, actual Rust server operation/login and actual transcription each remain separate NOT_VERIFIED gates. No EXE/release/deployment until required gates and authorization are satisfied.
