# Save Video to Local Path for ComfyUI

Save a native ComfyUI `VIDEO` to an editable local folder, with an in-node video preview.

## Install

Copy this repository into `ComfyUI/custom_nodes/comfyui-save-video-local-path`, restart ComfyUI, and add **Save Video to Local Path** from the video category. Do not install a second copy if the original `save_video_local_path` folder is already installed: both register `SaveVideoLocalPath`.

No additional Python packages or model downloads are required beyond ComfyUI's existing video support. Requires a ComfyUI version exposing `comfy_api.latest.Types` and native `VIDEO.save_to`. Tested against ComfyUI 0.43.1 on Windows; other platforms are not yet verified.

## Use

Connect a native `VIDEO` output to `video`.

- `output_folder`: destination folder on the computer running ComfyUI. Blank uses ComfyUI's output directory. A relative path resolves from the server working directory. A network share must be accessible to the server account.
- `filename`: MP4 filename only, for example `my_clip.mp4`. Existing files are not overwritten; numbered suffixes are added.
- `saved_path`: absolute path of the saved file.

The node delegates MP4 encoding to ComfyUI and uses the input video's frame rate and audio. It does not resize frames or generate new content. Encoding is not necessarily lossless; codec selection is ComfyUI's automatic selection. MP4 is not an alpha-preserving export format.

After execution, a player appears below the node's fields. The preview is a byte-identical copy of the saved MP4 in ComfyUI's temporary directory, not a second encode. This consumes additional disk space; temporary preview files can be removed when no longer needed.

The example in `examples/save-video.json` is an API-format wiring example using `LoadVideo`. Replace the input filename and destination before running it. It does not require MiniMax.

## Security and limitations

This node intentionally permits saving outside ComfyUI's output directory. Review destination fields in untrusted workflows. It runs with the server account's filesystem permissions and has no network requests, telemetry, subprocess calls, or runtime installs. A network filesystem path still uses the operating system's file-sharing access.

An interrupted/failed encode may leave a partial file; the next run preserves it and chooses a new filename. If preview copying fails after encoding, the exported video remains at its destination, but execution reports the copy error.

## Development

Run isolated tests with `python -m unittest discover -s tests -p "test_*.py"`.

For a real CPU-only encode/decode test using an existing ComfyUI Python environment:

```text
python tests/integration_video.py --comfyui /path/to/ComfyUI
```

This creates synthetic frames and a tone, saves two MP4s, checks frame count, dimensions, frame rate, audio decoding, collision handling, and identical preview bytes. All generated files stay inside a temporary test directory.

See `RELEASE.md` for remaining publishing steps. This directory is a local release draft, not a published Registry package.
