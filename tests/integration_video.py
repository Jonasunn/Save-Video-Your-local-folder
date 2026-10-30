import argparse
from fractions import Fraction
import importlib.util
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

parser = argparse.ArgumentParser()
parser.add_argument("--comfyui", required=True)
args = parser.parse_args()
sys.path.insert(0, str(Path(args.comfyui).resolve()))
# ComfyUI parses process arguments when its API is imported.
sys.argv = [sys.argv[0], "--cpu"]

import av
import torch
import folder_paths
from comfy_api.latest import InputImpl, Types

spec = importlib.util.spec_from_file_location("local_video_saver", Path(__file__).resolve().parents[1] / "__init__.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

frames = torch.zeros((12, 64, 64, 3))
frames[:, :, :, 0] = torch.linspace(0, 1, 12)[:, None, None]
rate = 48000
tone = 0.1 * torch.sin(2 * torch.pi * 440 * torch.arange(rate) / rate)
audio = {"waveform": tone.reshape(1, 1, -1), "sample_rate": rate}
video = InputImpl.VideoFromComponents(Types.VideoComponents(images=frames, frame_rate=Fraction(12), audio=audio))

with tempfile.TemporaryDirectory() as root:
    preview = str(Path(root) / "preview")
    with patch.object(folder_paths, "get_temp_directory", return_value=preview):
        first = module.SaveVideoLocalPath().save(video, root, "test.mp4")
        second = module.SaveVideoLocalPath().save(video, root, "test.mp4")
    assert first["result"] != second["result"]
    path = first["result"][0]
    preview_path = Path(preview) / first["ui"]["images"][0]["filename"]
    assert Path(path).read_bytes() == preview_path.read_bytes()
    with av.open(path) as container:
        stream = container.streams.video[0]
        assert (stream.width, stream.height) == (64, 64)
        assert stream.average_rate == Fraction(12)
        assert len(list(container.decode(video=0))) == 12
    with av.open(path) as container:
        assert container.streams.audio
        assert sum(frame.samples for frame in container.decode(audio=0)) >= rate
print("PASS: real MP4 encode/decode, 12 fps, 12 frames, 64x64, audio, preview bytes, collision handling")
