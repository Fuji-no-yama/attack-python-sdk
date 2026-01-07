from typing import Literal

from .reference import AttackExternalReference, AttackInternalReference


class AttackAbstractMitigation:  # 1つの抽象緩和策を表すクラス(具体緩和策を保有)
    def __init__(
        self,
        mitigation_id: str,
        description: str,
        domain: Literal["enterprise", "mobile", "ics"],
        concrete_mitigation_list: list["AttackConcreteMitigation"],
        reference_list: list[AttackExternalReference | AttackInternalReference],
    ) -> None:
        self.id: str = mitigation_id
        self.domain: Literal["enterprise", "mobile", "ics"] = domain
        self.description: str = description  # リンク系統を清掃する
        self.concrete_mitigation_list: list[AttackConcreteMitigation] = concrete_mitigation_list
        self.reference_list: list[AttackExternalReference | AttackInternalReference] = reference_list


class AttackConcreteMitigation:  # 1つの具体緩和策を表すクラス
    def __init__(
        self,
        abstract_mitigation_id: str,
        description: str,
        domain: Literal["enterprise", "mobile", "ics"],
        reference_list: list[AttackExternalReference | AttackInternalReference],
    ) -> None:
        self.abstract_mitigation_id: str = abstract_mitigation_id
        self.domain: Literal["enterprise", "mobile", "ics"] = domain
        self.description: str = description  # リンク系統を清掃する
        self.reference_list: list[AttackExternalReference | AttackInternalReference] = reference_list
