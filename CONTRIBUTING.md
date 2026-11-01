# Contributing

Keep vendor originals immutable and retain their MIT notices. Pin and verify upstream commits rather than pulling floating branches. Make desktop changes only where integration requires them; regenerate `python tools/verify_sources.py --write-patch` and run the verifier/static tests. The generated patch must describe every change.

On a prepared .NET 8 machine, run the fake-handler BridgeContract harness without real auth or network. Windows GUI builds and smoke tests are separate evidence; report exact versions and untested paths. Do not run a real transcription, read an auth file or install dependencies on someone else's device without authorization.

Do not submit recordings, models, binaries, credentials, transcripts, local paths or logs. Do not automate upstream publication, installer execution, login discovery or remote service exposure. No release/merge/deployment is implied by a passing source review.
