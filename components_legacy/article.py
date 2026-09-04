import datetime
import os
import re
import pathlib
import bs4

import server



def format_datetime_as_human_readable(p_datetime: datetime.datetime) -> str:
    return p_datetime.strftime("%B %d, %Y at %I:%M %p")


class Article:
    article_id: str = ""
    last_edit_datetime: datetime.datetime = datetime.datetime.fromtimestamp(0)
    title: str = ""
    body: str = ""

    @classmethod
    def from_html(self, p_path: str):
        article = Article()
        
        # NOTE(vanya): File name without extension
        file_name: str = os.path.splitext(os.path.basename(p_path))[0]

        article.article_id: str = file_name
        article.last_edit_datetime = datetime.datetime.fromtimestamp(pathlib.Path(p_path).stat().st_mtime)

        # NOTE(vanya): Parse from the .html file
        html_data: str = ""
        with open(p_path, "r", encoding="utf-8") as f:
            html_data = f.read()
        
        found_title = re.search(r"<title>(.*?)<\/title>", html_data, re.DOTALL)
        if found_title:
            article.title = found_title.group(1)
    
        found_body = re.search(r"<body>(.*?)<\/body>", html_data, re.DOTALL)
        if found_body:
            article.body = found_body.group(1).strip()
        
        return article
    

    def render(self) -> str:
        body_soup = bs4.BeautifulSoup(self.body, "html.parser")

        # NOTE(vanya): Generate Table of Contents
        toc_soup = bs4.BeautifulSoup("", "html.parser")
        
        server.soup_push_element(toc_soup, "h2", id="toc")

        ul = server.soup_push_element(toc_soup, "ul")
        for header_index, h2 in enumerate(body_soup.find_all("h2")):
            section_name: str = h2.get_text()
            # section_id: str = "section-" + section_name.lower().replace(" ", "-")
            section_id: str = f"section-{ header_index }"

            h2.attrs["id"] = section_id

            server.soup_push_element(
                ul,
                "li",
                p_content=server.soup_push_element(
                    None,
                    "a",
                    p_content=section_name,
                    href=f"#{ section_id }"
                )
            )

        return f"""
            <article class="article">
                <table>
                    <tr>
                        <th>
                            <img src="/public/pictures/pfp.png" class="pfp">
                        </th>
                        <td>
                            { f"<h3>{ self.title }</h3>" if self.title else "" }
                            <p style="margin: 0">
                                Last edited on
                                <time datetime="{ self.last_edit_datetime.isoformat() }">{ format_datetime_as_human_readable(self.last_edit_datetime) }</time>
                            </p>
                        </td>
                    </tr>
                </table>

                { str(toc_soup) }
                
                { str(body_soup) }
            </article>
        """
