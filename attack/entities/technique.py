from typing import TYPE_CHECKING, Literal

from .reference import AttackExternalReference, AttackInternalReference

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
        tactics: list["AttackTactic"],
        reference_list: list[AttackExternalReference | AttackInternalReference],
    ) -> None:
        self.name: str = name
        self.id: str = technique_id
        self.domain: Literal["enterprise", "mobile", "ics"] = domain
        self.description: str = description  # リンク系統を清掃する
        self.mitigation_list: list[AttackConcreteMitigation] = mitigation_list if mitigation_list is not None else []
        self.have_parent: bool = have_parent
        self.parent_id: str | None = parent_id
        self.tactics: list[AttackTactic] = tactics
        self.reference_list: list[AttackExternalReference | AttackInternalReference] = reference_list
