from __future__ import annotations

import mimetypes
import os
import subprocess
import tempfile

from pathlib import Path

import moe.server as server

from .image import Image



class Video:
    videos = Path("./public/videos/")
    thumbnails = videos / "thumbnails"
    video_thumbnails: dict[str, Path] = {}
    
    
    thumbnails.mkdir(exist_ok=True)


    @classmethod
    def prepare_all_video_thumbnails(cls) -> None:
        for video_path in Path(".").rglob("*.mp4"):
            print(f"Generating thumbnail for {video_path}")

            image_path = cls.video_thumbnails["/" + str(video_path.relative_to(Path(".")))] = cls.thumbnails / (str(video_path.relative_to(cls.videos)) + ".png")
            image_path.parent.mkdir(exist_ok=True)

            try:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-loglevel", "error",
                        "-i", str(video_path.resolve()),
                        "-frames:v", "1",
                        "-c:v", "libwebp",
                        "-f", "webp",
                        str(image_path.resolve()),
                    ],
                    check=True,
                )
            except subprocess.CalledProcessError:
                print(f"FFmpeg failed to extract the first frame! {video_path}")
                continue

        print(cls.video_thumbnails)


    def __init__(self, p_path: str, mute: bool=False, captions: list[dict]=[]) -> None:
        self.path = p_path
        self.captions = captions
        self.thumbnail_url = str(self.video_thumbnails[self.path].relative_to(Path(".")))
    

    def render_html(self) -> str:
        track_html: str = ""
        for stream_idx, stream in enumerate(self.captions):
            vtt_path = stream.get("path", "")
            if not vtt_path:
                print(f"VTT file was not found at {vtt_path}")
                continue

            track_html += f"""\
                <track
                    {"default" if stream_idx == 0 else ""}
                    kind="captions"
                    label="{stream.get("label", f"Stream {stream_idx}")}"
                    src="{vtt_path}" />
                """

        return f"""\
        <video controls preload="none" loading="lazy" poster="{self.thumbnail_url}">
            <source src="{self.path}" type="{ mimetypes.guess_type(self.path)[0] }"/>
            {track_html}
        </video>
        """


def register_components(p_template_renderer: server.HTMLTemplateRenderer) -> None:
    @p_template_renderer.component("video")
    def _(
            path: str,
            mute: bool=False,
            # TODO(vanya): Add support for multiple languages and labels 
            captions: str="",
    ) -> str:
        return Video(path, mute, [
            {"label": "Default", "path": captions}
        ]).render_html()
