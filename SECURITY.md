# Security and privacy

Audio Notes is an experimental, single-user localhost tool. No production hardening or independent penetration test is claimed. There is no supported hosted or internet-facing mode.

## Safe use

- Bind only to `127.0.0.1`; do not expose it through a public tunnel or reverse proxy.
- Keep Python dependencies, FFmpeg and local inference software current. Parsing media is a security boundary.
- Only process recordings you have permission to use.
- Use trusted local model files. Do not place a forwarding proxy at the Ollama endpoint; disable Ollama cloud features explicitly.
- Keep recordings, transcripts, credentials and temporary data out of Git and public issues.
- Normal deletion does not securely erase storage; crashes may leave temporary directories.

## Reporting a concern

Do not publish an exploit, recording, transcript, credential or private path in a public issue. If GitHub shows a private **Report a vulnerability** option for this repository, use it. Otherwise open a minimal issue asking for a private reporting channel without technical exploitation details or sensitive data. No private channel or response-time SLA is currently guaranteed.

Report the affected revision, a sanitized description and the smallest synthetic reproduction once an appropriate channel is available. Do not test against anyone else's installation without permission.
