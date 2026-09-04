import logging
import os
import datetime

from server import App
from html_factory import HTMLFactory


class AppError:
    SUCCESS: int = 0
    FILE_NOT_FOUND: int = 1


class Post:
    def __init__(self):
        self.html_source: str = ""
        self.creation_datetime: datetime = datetime.datetime.fromtimestamp(0)
        self.is_personal = False

    @classmethod
    def from_html(self, p_path: str):
        p = Post()

        if not os.path.exists(p_path):
            logging.error(f"Cannot load Post from an .html file `{p_path}` - file does not exist.")
            return (p, AppError.FILE_NOT_FOUND)

        with open(p_path, "r", encoding="utf-8") as f:
            raw_html_source: str = f.read()
        
        html_source: str = ""
        for line in raw_html_source.split("\n"):
            if line.startswith("@"):
                attribute_tokens: list[str] = line.split(" ")
                match attribute_tokens[0]:
                    case "@personal":
                        p.is_personal = True
            else:
                html_source += line + "\n"
        
        p.html_source = html_source

        return (p, AppError.SUCCESS)
    

    def render_html(self) -> str:
        head: str = f"""
                <table>
                    <tr>
                        <th>
                            <img src="/public/pictures/pfp.png" class="pfp">
                        </th>
                        <td>
                            <p style="margin: 0">
                                <b>@vanya</b><br>
                                yapped on
                                <time datetime="{ self.creation_datetime.isoformat() }">{ self.format_datetime_as_human_readable(self.creation_datetime) }</time>
                            </p>
                        </td>
                    </tr>
                </table>
            """
        
        return head + self.html_source
    

    def format_datetime_as_human_readable(self, p_datetime: datetime.datetime) -> str:
        return p_datetime.strftime("%B %d, %Y at %I:%M %p")



def register_components_for_app(p_app: App) -> None:

    @p_app.component("posts_timeline")
    def render_posts_timeline() -> str:
        html_source = HTMLFactory()
        
        # NOTE(vanya): Go over every .html file in ./posts/
        posts: list[Post] = []

        for file_name in reversed(os.listdir("./posts/")):
            file_path: str = os.path.join("./posts/", file_name)

            if (
                not os.path.isfile(file_path)
                or not file_path.endswith(".html")
            ):
                continue

            # NOTE(vanya): Load the post HTML data
            loaded_post, error = Post.from_html(file_path)
            match error:
                case AppError.SUCCESS:
                    posts.append(loaded_post)
                case AppError.FILE_NOT_FOUND:
                    logging.warning(f"Post `{file_name}` will not be loaded - file not found.")
                    continue

        for post in posts:
            if not post.is_personal:
                html_source.push_element(None, "article", post.render_html(), class_="post", id_=f"post-{file_name[:file_name.rfind(".")]}")

        return html_source.render_html()
