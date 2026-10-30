from pathlib import Path
import shutil
import uuid

import folder_paths
from comfy_api.latest import Types


class SaveVideoLocalPath:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "video": ("VIDEO",),
            "output_folder": ("STRING", {"default": "", "tooltip": "Local destination folder. Blank uses ComfyUI's output folder."}),
            "filename": ("STRING", {"default": "MiniMax_H3.mp4", "tooltip": "MP4 filename. Existing files are kept; a numbered suffix is added."}),
        }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_path",)
    FUNCTION = "save"
    CATEGORY = "video"
    OUTPUT_NODE = True

    def save(self, video, output_folder, filename):
        folder = Path(output_folder.strip().strip('"') or folder_paths.get_output_directory()).resolve()
        name = Path(filename.strip())
        if name.name != str(name) or name.suffix.lower() != ".mp4":
            raise ValueError("Enter an MP4 filename without a folder; set the folder in output_folder.")
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / name
        counter = 1
        while True:
            try:
                stream = target.open("xb")
                break
            except FileExistsError:
                target = folder / f"{name.stem}_{counter:05d}.mp4"
                counter += 1
        with stream:
            video.save_to(stream, format=Types.VideoContainer.MP4, codec=Types.VideoCodec.AUTO)
        preview_folder = Path(folder_paths.get_temp_directory())
        preview_folder.mkdir(parents=True, exist_ok=True)
        preview_name = f"local_video_preview_{uuid.uuid4().hex}.mp4"
        shutil.copyfile(target, preview_folder / preview_name)
        return {
            "ui": {
                "images": [{"filename": preview_name, "subfolder": "", "type": "temp"}],
                "animated": (True,),
            },
            "result": (str(target),),
        }


NODE_CLASS_MAPPINGS = {"SaveVideoLocalPath": SaveVideoLocalPath}
NODE_DISPLAY_NAME_MAPPINGS = {"SaveVideoLocalPath": "Save Video to Local Path"}
