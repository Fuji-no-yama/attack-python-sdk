from typing import Literal

from .technique import AttackTechnique


class AttackTactic:
    def __init__(
        self,
        tactic_id: str,
        name: str,
        domain: Literal["enterprise", "mobile", "ics"],
        description: str,
        technique_list: list[AttackTechnique],
    ) -> None:
        self.id: str = tactic_id
        self.name: str = name
        self.domain: Literal["enterprise", "mobile", "ics"] = domain
        self.description: str = description
        self.technique_list: list[AttackTechnique] = technique_list  # list[AttackTechnique]の形を保持したリスト
