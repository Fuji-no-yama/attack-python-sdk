import re
from typing import Literal

from .technique import AttackTechnique


class AttackTactic:
    def __init__(
        self,
        tactic_id: str,
        name: str,
        domain: Literal["enterprise", "mobile", "ics"],
        description: str,
        tec_lis: list[AttackTechnique],
    ) -> None:
        self.id: str = tactic_id
        self.name: str = name
        self.domain: Literal["enterprise", "mobile", "ics"] = domain
        self.description: str = self.clean_description(description)
        self.technique_list: list[AttackTechnique] = tec_lis  # list[AttackTechnique]の形を保持したリスト

    def clean_description(self, desc: str) -> str:  # リンクなどのノイズのみを削除する関数
        pattern1 = r"\(https?://[^\s]+\)"  # MarkdownのURLを削除
        pattern2 = r"\(Citation:.*?\)"  # Markdownの引用リンクを削除
        pattern3 = r"<code>"
        pattern4 = r"</code>"
        return re.sub(rf"{pattern1}|{pattern2}|{pattern3}|{pattern4}", "", desc)
