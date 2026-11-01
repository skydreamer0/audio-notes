# Third-party source notices

This integration directly redistributes source under the MIT License:

- **A3Boy/codex-voice-input**, commit `f892017aeac3c122b41bc53a3b77c492d505bdc4`: original files in `vendor/codex-voice-input/`, adapted application in `desktop/`. Original [LICENSE](vendor/codex-voice-input/LICENSE) and [THIRD_PARTY_NOTICES](vendor/codex-voice-input/THIRD_PARTY_NOTICES.md) retained in both copies. The adapted original recognition engine changes transport, not ownership.
- **Wangnov/codex-asr**, commit `479f6a7a3db81fe2a23d4755b0ccbeb4400317d4`: original Rust files in `vendor/codex-asr/`, including [LICENSE-MIT](vendor/codex-asr/LICENSE-MIT).

UPSTREAM.json maps each redistributed original file to its upstream repository, revision, path and Git blob hash. INTEGRATION.patch records the complete modifications to the desktop copy. No upstream installers/workflows or branding images are redistributed. The Rust README retains upstream references for provenance; those external assets are not included.

Dependencies retain their own licenses (see Cargo.lock and C# PackageReference entries). Root LICENSE covers original integration glue and documentation, not a replacement for upstream notices. Source licenses do not confer permission to use third-party accounts/services/trademarks or guarantee unofficial endpoint access. No affiliation or endorsement is implied.
