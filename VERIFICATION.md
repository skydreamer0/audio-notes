# Verification status

Date: 2026-11-01. Scope: initial source prototype, Linux / Python 3.12.

## Executed

| Check | Result | What it establishes |
| --- | --- | --- |
| `python -m unittest discover -s tests -v` | 17 / 17 pass | API contracts and listed edge cases |
| `node tests/test_ui.js` | Pass | Old summary/status responses cannot overwrite a newer job in a DOM stub |
| `node --check app/static/app.js` | Pass | JavaScript parses |
| Python compileall | Pass | Python modules compile |
| Actual FFprobe/FFmpeg with generated silence WAV | Pass | Valid media probes and converts; absent ASR engine is reported honestly |
| Actual subprocess cancellation | Pass | Long-running test child is stopped and temporary directory removed |
| Uvicorn loopback HTTP request | HTTP 200 | Server starts, serves the interface and shuts down normally |

Automated boundary coverage includes token/Origin/Host checks, empty and oversized bodies, fake audio MIME, unsafe supplied filenames, duration overflow/NaN, video streams, busy state, unfinished export, timestamp formatting, missing tokenizer, summary consent and rejection of remote model metadata before transcript delivery.

Independent source review identified three issues: stale UI responses, missing-tokenizer fallback risk and loopback-versus-cloud summary assumptions. All three were fixed and regression-tested. The source was accepted **with limits**, not certified as a finished product.

## Not verified

- Real Whisper inference, recognition accuracy or silence hallucination rate: no engine/model was installed in the test environment.
- Real Ollama inference or summary quality: no Ollama service/model was available.
- Windows, macOS, CUDA/GPU and performance.
- Real browser rendering, uploads, drag/drop, mobile layout and accessibility. The separate browser could not reach the test server; HTTP 200 is not browser acceptance.
- Long-running or adversarial media fuzzing and internet-facing security.

The completed-transcript API test uses the literal `TEST STUB ONLY`; it is not an audio transcript. `tests/test_ui.js` uses a small fake DOM, not a browser. README's SRT example is hand-written. `PREVIEW.html` is a static preview, not a live demo.

There is no CI workflow in this initial repository. Local checks are not presented as GitHub CI or a release certification. No hosted deployment or packaged desktop release is included.
