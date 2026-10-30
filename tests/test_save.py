import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


class FakeVideo:
    def save_to(self, stream, **kwargs):
        if kwargs != {"format": "mp4", "codec": "auto"}:
            raise AssertionError(kwargs)
        stream.write(b"test video with audio")


class SaveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.preview = self.root / "preview"
        folders = types.SimpleNamespace(get_output_directory=lambda: str(self.root), get_temp_directory=lambda: str(self.preview))
        api = types.SimpleNamespace(Types=types.SimpleNamespace(VideoContainer=types.SimpleNamespace(MP4="mp4"), VideoCodec=types.SimpleNamespace(AUTO="auto")))
        with patch.dict(sys.modules, {"folder_paths": folders, "comfy_api.latest": api}):
            spec = importlib.util.spec_from_file_location("saver_test", Path(__file__).resolve().parents[1] / "__init__.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        self.node = module.SaveVideoLocalPath()

    def test_save_and_preview(self):
        result = self.node.save(FakeVideo(), str(self.root / "nested"), "clip.mp4")
        path = Path(result["result"][0])
        item = result["ui"]["images"][0]
        self.assertEqual(path.read_bytes(), (self.preview / item["filename"]).read_bytes())
        self.assertEqual(item["type"], "temp")
        self.assertEqual(result["ui"]["animated"], (True,))

    def test_collision_and_default_folder(self):
        first = self.node.save(FakeVideo(), "", "clip.mp4")
        second = self.node.save(FakeVideo(), "", "clip.mp4")
        self.assertEqual(Path(first["result"][0]).parent, self.root)
        self.assertEqual(Path(second["result"][0]).name, "clip_00001.mp4")
        self.assertEqual(Path(first["result"][0]).read_bytes(), b"test video with audio")

    def test_invalid_filename(self):
        for name in ("../clip.mp4", "clip.webm", "", "nested/clip.mp4"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.node.save(FakeVideo(), str(self.root), name)

    def test_encoding_failure_propagates(self):
        video = FakeVideo()
        with patch.object(video, "save_to", side_effect=RuntimeError("encode failed")):
            with self.assertRaisesRegex(RuntimeError, "encode failed"):
                self.node.save(video, str(self.root), "clip.mp4")
        self.assertFalse(self.preview.exists())


if __name__ == "__main__":
    unittest.main()
