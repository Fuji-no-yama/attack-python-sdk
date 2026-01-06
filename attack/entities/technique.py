import re
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .mitigation import AttackConcreteMitigation
    from .tactic import AttackTactic


class AttackTechnique:
    def __init__(  # noqa: PLR0913 (引数総数警告)
        self,
        name: str,
        technique_id: str,
        domain: Literal["enterprise", "mobile", "ics"],
        description: str,
        *,
        mitigation_list: list["AttackConcreteMitigation"] | None = None,
        have_parent: bool = False,
        parent_id: str | None = None,
        tactics: list["AttackTactic"] | None = None,
    ) -> None:
        self.name: str = name
        self.id: str = technique_id
        self.domain: Literal["enterprise", "mobile", "ics"] = domain
        self.description: str = self.clean_description(description)  # リンク系統を清掃する
        self.mitigation_list: list[AttackConcreteMitigation] = mitigation_list if mitigation_list is not None else []
        self.have_parent: bool = have_parent
        self.parent_id: str | None = parent_id
        self.tactics: list[AttackTactic] | None = tactics  # tacticオブジェクト

    def clean_description(self, desc: str) -> str:  # リンクなどのノイズのみを削除する関数
        pattern1 = r"\(https?://[^\s]+\)"  # MarkdownのURLを削除
        pattern2 = r"\(Citation:.*?\)"  # Markdownの引用リンクを削除
        pattern3 = r"<code>"
        pattern4 = r"</code>"
        return re.sub(rf"{pattern1}|{pattern2}|{pattern3}|{pattern4}", "", desc)
