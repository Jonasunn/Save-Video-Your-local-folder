# Test status — 2026-10-30

Local Windows verification used the existing ComfyUI 0.43.1 environment (Python 3.12.9).

- PASS: four isolated unit tests covering saved-path output, preview payload and bytes, default/nested folders, collision protection, invalid filenames, and encoding error propagation.
- PASS: real synthetic MP4 encode/decode, 64x64 pixels, 12 frames at 12 fps, with decoded audio.
- PASS: preview bytes equal the exported MP4; repeated saves use different paths.
- PASS: TOML metadata and JSON example parse successfully.
- NOT VERIFIED: macOS/Linux execution and encoding. The supplied CI workflow tests isolated logic on all three platforms, not real ComfyUI encoding.
- NOT VERIFIED: browser player interaction for this packaged release.
- NOT VERIFIED: Registry acceptance or clean Manager installation; nothing has been published.

Tests use temporary directories and synthetic media. No user media, generation jobs, or destination-folder contents are needed.
