# Verification — Codex source integration

## Passed in this cloud workspace
- 38 vendored originals match upstream Git blob SHA-1 and fixed revisions in UPSTREAM.json.
- Desktop copy has a complete source-file mapping and reproducible INTEGRATION.patch.
- 8 Python static source-contract checks pass, including XML parsing, no desktop auth discovery, loopback/redirect/proxy constraints in source, consent guards for both sending paths, omitted asset build references, default injection disabled and no fake timestamp export.

## Included but NOT_RUN
- `tests/BridgeContract`: .NET 8 fake-handler contract harness (no actual HTTP/auth/audio). This workspace has no dotnet executable.
- Rust/C# compilation, dependency restore and Rust unit tests: no cargo/rustc/.NET/Windows toolchain available.

## NOT_VERIFIED
Native Windows recording, file-picker/decoder support, UI interaction/cleanup under actual Windows failures, real cancellation semantics, upstream account compatibility, true transcription completeness/accuracy and any actual Codex summarization. No EXE was built, no upstream server was launched, no auth file read, and no real audio sent. Static source tests are not runtime evidence.

The first prototype's Python ASR-stub tests and the abandoned independently-written REST adapter tests are NOT validation of this integration and are not counted here. Independent review results belong to the exact reviewed snapshot, not a future edit.
