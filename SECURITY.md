# Security and privacy

Do not expose the Rust bridge outside loopback. Use a separate local REST API key; never use an upstream access token as the local key. The desktop sends only to configured literal loopback and does not read Codex authentication files. The original Rust server does read its explicitly configured/login authentication when started and transmits audio to an unofficial ChatGPT endpoint. Starting it is a deliberate operator action; this repository does not start it for you.

Record/transcribe only content you have permission to process. Both native send paths ask for cloud transmission confirmation. Cancelling local work cannot retract uploaded data. History persists locally without application-layer encryption. Temporary microphone recordings may survive a forced crash; imported originals are never removed. Clipboard export makes text available to other clipboard consumers.

Never include recordings, transcripts, login files, keys, environment dumps or local logs in public reports. First report only a non-sensitive description and affected source revision. No private disclosure mailbox or guaranteed security response SLA is configured. If a report requires secrets, do not post it publicly; ask for a secure channel without attaching the material.

No claims of official OpenAI API compatibility, guaranteed access, service-policy approval or independent security audit are made. Dependency/build and Windows runtime verification are still outstanding.
