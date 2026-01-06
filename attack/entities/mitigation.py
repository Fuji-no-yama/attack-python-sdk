import re
from typing import Literal


class AttackAbstractMitigation:  # 1つの抽象緩和策を表すクラス(具体緩和策を保有)
    def __init__(
        self,
        mitigation_id: str,
        description: str,
        domain: Literal["enterprise", "mobile", "ics"],
        concrete_mitigation_list: list["AttackConcreteMitigation"],
    ) -> None:
        self.id: str = mitigation_id
        self.domain: Literal["enterprise", "mobile", "ics"] = domain
        self.description: str = self.clean_description(description)  # リンク系統を清掃する
        self.concrete_mitigation_list: list[AttackConcreteMitigation] = concrete_mitigation_list

    def clean_description(self, desc: str) -> str:
        pattern1 = r"\(https?://[^\s]+\)"  # MarkdownのURLを削除
        pattern2 = r"\(Citation:.*?\)"  # Markdownの引用リンクを削除
        pattern3 = r"<code>"
        pattern4 = r"</code>"
        return re.sub(rf"{pattern1}|{pattern2}|{pattern3}|{pattern4}", "", desc)


class AttackConcreteMitigation:  # 1つの具体緩和策を表すクラス
    def __init__(self, abstract_mitigation_id: str, description: str, domain: Literal["enterprise", "mobile", "ics"]) -> None:
        self.abstract_mitigation_id: str = abstract_mitigation_id
        self.domain: Literal["enterprise", "mobile", "ics"] = domain
        self.description: str = self.clean_description(description)  # リンク系統を清掃する

    def clean_description(self, desc: str) -> str:
        pattern1 = r"\(https?://[^\s]+\)"  # MarkdownのURLを削除
        pattern2 = r"\(Citation:.*?\)"  # Markdownの引用リンクを削除
        pattern3 = r"<code>"
        pattern4 = r"</code>"
        return re.sub(rf"{pattern1}|{pattern2}|{pattern3}|{pattern4}", "", desc)
