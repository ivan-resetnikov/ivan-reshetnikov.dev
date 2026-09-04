from __future__ import annotations

import datetime
import os
import re
import pathlib

import core



def format_datetime_as_human_readable(p_datetime: datetime.datetime) -> str:
    return p_datetime.strftime("%B %d, %Y at %I:%M %p")



class Thought:
    def __init__(self) -> None:
        self.name: str = ""
        self.creation_datetime: datetime.datetime = datetime.datetime.fromtimestamp(0)
        self.is_personal: bool = False
        self.body: str = ""


    @staticmethod
    def from_html(p_path: str) -> Thought:
        thought = Thought()
        
        # NOTE(vanya): File name without extension
        file_name: str = os.path.splitext(os.path.basename(p_path))[0]

        # NOTE(vanya): Defaults
        thought.name = file_name
        
        thought.creation_datetime = datetime.datetime.fromtimestamp(pathlib.Path(p_path).stat().st_ctime)
        # NOTE(vanya): Default timezone
        timezone_offset = datetime.timezone(datetime.timedelta(hours=0))
        thought.creation_datetime = thought.creation_datetime.replace(tzinfo=timezone_offset)

        thought.is_personal = False

        # NOTE(vanya): Load the .html file
        with open(p_path, "r", encoding="utf-8") as f:
            html_data: str = f.read()

        # NOTE(vanya): Parse, while handling and excluding atttributes
        body: str = ""
        for line in html_data.split("\n"):
            if line.startswith("@"):
                thought.parse_attribure(line.split(" "))
            else:
                body += line + "\n"
    
        thought.body = body
        
        return thought
    

    def parse_attribure(self, p_tokens: list[str]) -> None:
        def next_token() -> str|None:
            if p_tokens:
                return p_tokens.pop(0)
            else:
                return None
        
        match next_token():
            case "@personal":
                self.is_personal = True
            case "@override_creation_time":
                self.creation_datetime = datetime.datetime.fromisoformat(next_token() or "")
            case _:
                print("Unhandled post attribute")
    

    def render_html(self) -> str:
        #{ f"<h3>{ self.title }</h3>" if self.title else "" }

        if self.is_personal:
            return f"""
                <article class="thought" id="thought-{ self.name }">
                    <p>This thought is too personal to show on the Internet (⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄ </p>
                </article>
            """
        else:
            return f"""
                <article class="thought" id="thought-{ self.name }">
                    <table>
                        <tr>
                            <th>
                                <img src="/public/pictures/pfp.png" class="pfp">
                            </th>
                            <td>
                                <p style="margin: 0">
                                    <b>@vanya</b><br>
                                    thought on
                                    <time datetime="{ self.creation_datetime.isoformat() }">{ format_datetime_as_human_readable(self.creation_datetime) }</time>
                                </p>
                            </td>
                        </tr>
                    </table>
                    { self.body }
                </article>
            """


def register_components(p_template_renderer: core.HTMLTemplateRenderer) -> None:
    @p_template_renderer.component("post")
    def _(name: str) -> str:
        return Thought.from_html("./thoughts/" + name + ".html").render_html()