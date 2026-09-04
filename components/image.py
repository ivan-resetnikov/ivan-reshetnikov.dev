from __future__ import annotations

import io
import os

import PIL.Image

import core



class Image:
    path: str = ""
    width: int = 0
    height: int = 0
    alt: str = ""

    @classmethod
    def from_file(self, p_path: str, p_alt: str="") -> Image|None:
        if not os.path.exists(p_path):
            print(f"Tried to load an image that does not exist: `{p_path}`")
            return None
        
        image = Image()
        
        if not os.path.exists(p_path):
            return image
        
        pil_image: PIL.Image = PIL.Image.open(p_path)

        image.path = p_path
        image.width = pil_image.width
        image.height = pil_image.height
        image.alt = p_alt

        return image
    

    def resize_and_get_webp_buffer(self, p_width: int) -> bytes:
        pil_image: PIL.Image = PIL.Image.open(self.path)
        buffer: io.BytesIO = io.BytesIO()

        if p_width > 0 and p_width < pil_image.width:
            aspect_factor: float = p_width / float(pil_image.width)
            new_height: int = round(pil_image.height * aspect_factor)

            new_size: tuple[int, int] = (p_width, new_height)

            img_resized = pil_image.resize(new_size)

            img_resized.save(buffer, format="WEBP")
        
        else:
            pil_image.save(buffer, format="WEBP")

        return buffer.getvalue()
    

    def render_html(self, p_very_lazy: bool=False) -> str:
        if p_very_lazy:
            alt_attr: str = f'alt="The image did not load ( yet (т人т) ), the description says: { self.alt }"' if self.alt else ""
            
            return f"""
                <img class="very-lazy-img" loading="lazy" decoding="async" { alt_attr } width="{ self.width }" height="{ self.height }" path="{ self.path.removeprefix(".") }">
                <noscript><img loading="lazy" decoding="async" { alt_attr } src="{ self.path.removeprefix(".") }"></noscript>
            """
        
        else:
            alt_attr: str = f'alt="{ self.alt }"' if self.alt else ""

            return f"""
                <img loading="lazy" decoding="async" { alt_attr } src="{ self.path.removeprefix(".") }">
            """


def register_components(p_template_renderer: core.HTMLTemplateRenderer) -> None:
    @p_template_renderer.component("image")
    def _(
            path: str,
            alt: str="",
            very_lazy: bool=False,
    ) -> str:
        return Image.from_file("./public" + path, alt).render_html(very_lazy)
