# Contributing

Thanks for helping make a small, understandable local audio workflow better.

## Before coding

For substantial behavior changes, open an issue describing the user problem, proposed scope and data flow. Small documentation fixes can go straight to a pull request. Do not include private recordings, transcripts, tokens or machine-specific logs.

## Development

1. Create a Python 3.11+ virtual environment and install `requirements.txt`.
2. Install FFmpeg/ffprobe for media tests; optional ASR models are not needed for the baseline tests.
3. Use Node.js 18+ for the frontend contract test.
4. Run:

```bash
python -m unittest discover -s tests -v
node tests/test_ui.js
node --check app/static/app.js
```

Use your venv's Python executable if it is not activated. Tests marked with a stub verify contracts, not actual model behavior.

## Pull request checklist

- Explain the change, regression test and any unverified behavior.
- Keep unrelated code and dependencies out of the diff.
- Preserve local-only defaults, consent and cleanup; disclose any new network request.
- Use synthetic or redistributable fixtures with clear provenance. Never commit user audio or models.
- Keep both README entry points accurate when setup or privacy behavior changes.
- For UI work, test repeated actions, interrupted requests, cancellation and narrow screens. State when real-browser checks were unavailable.
- Submit as a Draft until tests and review are ready. A passing unit test does not establish ASR accuracy or release readiness.

Contributions must be compatible with the MIT license. Do not copy incompatible third-party code, fonts or artwork without an appropriate license and attribution. By submitting a contribution, you confirm you have the right to contribute it under the project license.
