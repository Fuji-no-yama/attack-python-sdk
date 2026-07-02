"""Attackインスタンスの基本プロパティに関するテスト。"""

import pytest

from attack import Attack
from attack.entities import (
    AttackAbstractMitigation,
    AttackCampaign,
    AttackGroup,
    AttackSoftware,
    AttackTactic,
    AttackTechnique,
)


class TestAttackProperties:
    """各バージョンでAttackが正しく初期化され、リストが空でないことを確認する。"""

    def test_version_is_set(self, attack_default: Attack) -> None:
        assert attack_default.version is not None
        assert attack_default.version != ""

    def test_domain_is_set(self, attack_default: Attack) -> None:
        assert attack_default.domain == "enterprise"

    def test_technique_list_not_empty(self, attack_default: Attack) -> None:
        assert isinstance(attack_default.technique_list, list)
        assert len(attack_default.technique_list) > 0

    def test_tactic_list_not_empty(self, attack_default: Attack) -> None:
        assert isinstance(attack_default.tactic_list, list)
        assert len(attack_default.tactic_list) > 0

    def test_mitigation_list_not_empty(self, attack_default: Attack) -> None:
        assert isinstance(attack_default.mitigation_list, list)
        assert len(attack_default.mitigation_list) > 0

    def test_campaign_list_not_empty(self, attack_default: Attack) -> None:
        assert isinstance(attack_default.campaign_list, list)
        assert len(attack_default.campaign_list) > 0

    def test_group_list_not_empty(self, attack_default: Attack) -> None:
        assert isinstance(attack_default.group_list, list)
        assert len(attack_default.group_list) > 0

    def test_software_list_not_empty(self, attack_default: Attack) -> None:
        assert isinstance(attack_default.software_list, list)
        assert len(attack_default.software_list) > 0


class TestTechniqueProperties:
    """テクニックオブジェクトのプロパティを確認する。"""

    def test_technique_has_required_fields(self, attack_default: Attack) -> None:
        for tec in attack_default.technique_list:
            assert isinstance(tec, AttackTechnique)
            assert tec.id is not None
            assert tec.id != ""
            assert tec.name is not None
            assert tec.name != ""
            assert tec.description is not None
            assert tec.description != ""

    def test_technique_id_format(self, attack_default: Attack) -> None:
        for tec in attack_default.technique_list:
            assert tec.id.startswith("T"), f"Unexpected technique id format: {tec.id}"

    def test_child_technique_has_parent(self, attack_default: Attack) -> None:
        for tec in attack_default.technique_list:
            if tec.have_parent:
                assert tec.parent_id is not None, f"Child technique {tec.id} has no parent_id"

    def test_technique_has_tactics(self, attack_default: Attack) -> None:
        for tec in attack_default.technique_list:
            assert isinstance(tec.tactics, list)
            assert len(tec.tactics) > 0, f"Technique {tec.id} has no tactics"


class TestTacticProperties:
    """タクティックオブジェクトのプロパティを確認する。"""

    def test_tactic_has_required_fields(self, attack_default: Attack) -> None:
        for tac in attack_default.tactic_list:
            assert isinstance(tac, AttackTactic)
            assert tac.id is not None
            assert tac.id != ""
            assert tac.name is not None
            assert tac.name != ""

    def test_tactic_id_format(self, attack_default: Attack) -> None:
        for tac in attack_default.tactic_list:
            assert tac.id.startswith("TA"), f"Unexpected tactic id format: {tac.id}"

    def test_tactic_has_techniques(self, attack_default: Attack) -> None:
        for tac in attack_default.tactic_list:
            assert isinstance(tac.technique_list, list)
            assert len(tac.technique_list) > 0, f"Tactic {tac.id} has no techniques"


class TestMitigationProperties:
    """緩和策オブジェクトのプロパティを確認する。"""

    def test_mitigation_has_required_fields(self, attack_default: Attack) -> None:
        for mit in attack_default.mitigation_list:
            assert isinstance(mit, AttackAbstractMitigation)
            assert mit.id is not None
            assert mit.id != ""
            assert mit.name is not None
            assert mit.name != ""
            assert mit.description is not None
            assert mit.description != ""

    def test_mitigation_id_format(self, attack_default: Attack) -> None:
        for mit in attack_default.mitigation_list:
            assert mit.id.startswith("M"), f"Unexpected mitigation id format: {mit.id}"

    def test_mitigation_has_concrete_mitigations(self, attack_default: Attack) -> None:
        for mit in attack_default.mitigation_list:
            assert isinstance(mit.concrete_mitigation_list, list)


class TestCampaignProperties:
    """キャンペーンオブジェクトのプロパティを確認する。"""

    def test_campaign_has_required_fields(self, attack_default: Attack) -> None:
        for campaign in attack_default.campaign_list:
            assert isinstance(campaign, AttackCampaign)
            assert campaign.id is not None
            assert campaign.id != ""
            assert campaign.name is not None
            assert campaign.name != ""
            assert campaign.description is not None
            assert campaign.description != ""

    def test_campaign_id_format(self, attack_default: Attack) -> None:
        for campaign in attack_default.campaign_list:
            assert campaign.id.startswith("C"), f"Unexpected campaign id format: {campaign.id}"

    def test_campaign_has_procedures(self, attack_default: Attack) -> None:
        for campaign in attack_default.campaign_list:
            assert isinstance(campaign.procedure_list, list)


class TestGroupProperties:
    """グループオブジェクトのプロパティを確認する。"""

    def test_group_has_required_fields(self, attack_default: Attack) -> None:
        for group in attack_default.group_list:
            assert isinstance(group, AttackGroup)
            assert group.id is not None
            assert group.id != ""
            assert group.name is not None
            assert group.name != ""
            assert group.description is not None
            assert group.description != ""

    def test_group_id_format(self, attack_default: Attack) -> None:
        for group in attack_default.group_list:
            assert group.id.startswith("G"), f"Unexpected group id format: {group.id}"

    def test_group_has_procedures(self, attack_default: Attack) -> None:
        for group in attack_default.group_list:
            assert isinstance(group.procedure_list, list)


class TestSoftwareProperties:
    """ソフトウェアオブジェクトのプロパティを確認する。"""

    def test_software_has_required_fields(self, attack_default: Attack) -> None:
        for software in attack_default.software_list:
            assert isinstance(software, AttackSoftware)
            assert software.id is not None
            assert software.id != ""
            assert software.name is not None
            assert software.name != ""
            assert software.description is not None
            assert software.description != ""

    def test_software_id_format(self, attack_default: Attack) -> None:
        for software in attack_default.software_list:
            assert software.id.startswith("S"), f"Unexpected software id format: {software.id}"

    def test_software_has_procedures(self, attack_default: Attack) -> None:
        for software in attack_default.software_list:
            assert isinstance(software.procedure_list, list)


class TestProcedureProperties:
    """プロシージャオブジェクトのプロパティを確認する。"""

    def test_procedure_in_campaign(self, attack_default: Attack) -> None:
        for campaign in attack_default.campaign_list:
            for proc in campaign.procedure_list:
                assert proc.parent_id == campaign.id
                assert proc.parent_name == campaign.name
                assert proc.parent_type == "campaign"
                assert proc.technique_id is not None
                assert proc.description is not None

    def test_procedure_in_group(self, attack_default: Attack) -> None:
        for group in attack_default.group_list:
            for proc in group.procedure_list:
                assert proc.parent_id == group.id
                assert proc.parent_name == group.name
                assert proc.parent_type == "group"

    def test_procedure_in_software(self, attack_default: Attack) -> None:
        for software in attack_default.software_list:
            for proc in software.procedure_list:
                assert proc.parent_id == software.id
                assert proc.parent_name == software.name
                assert proc.parent_type == "software"


class TestReferenceProperties:
    """参照オブジェクトのプロパティを確認する。"""

    def test_external_reference_list_not_empty(self, attack_default: Attack) -> None:
        assert isinstance(attack_default.external_reference_list, list)
        assert len(attack_default.external_reference_list) > 0

    def test_technique_has_references(self, attack_default: Attack) -> None:
        techniques_with_refs = [t for t in attack_default.technique_list if t.reference_list]
        assert len(techniques_with_refs) > 0


class TestAllVersions:
    """全バージョンでAttackが正常に初期化されることを確認する。"""

    def test_all_versions_loadable(self, all_versions: list[str]) -> None:
        for version in all_versions:
            attack = Attack(version=version)
            assert attack.version == f"v{version}"
            assert len(attack.technique_list) > 0
            assert len(attack.tactic_list) > 0
            assert len(attack.mitigation_list) > 0

    def test_default_version_is_latest(self, all_versions: list[str]) -> None:
        attack = Attack()
        latest = sorted(all_versions)[-1]
        assert attack.version == f"v{latest}", f"Default version {attack.version} is not latest v{latest}"

    def test_invalid_version_raises(self) -> None:
        with pytest.raises(ValueError, match="version must be one of"):
            Attack(version="99.9")

    def test_invalid_domain_raises(self) -> None:
        with pytest.raises(ValueError, match="domain must be one of"):
            Attack(domain="invalid")


class TestDomains:
    """enterprise以外のドメイン(mobile, ics)が正常に読み込めることを確認する。"""

    def test_mobile_domain_loadable(self, attack_mobile: Attack) -> None:
        assert attack_mobile.domain == "mobile"
        assert len(attack_mobile.technique_list) > 0
        assert len(attack_mobile.tactic_list) > 0

    def test_ics_domain_loadable(self, attack_ics: Attack) -> None:
        # ICSデータには外部参照リストに存在しない引用名(N/A等)が含まれるため、
        # 参照解決で例外を出さずに読み込めることの回帰テストを兼ねる
        assert attack_ics.domain == "ics"
        assert len(attack_ics.technique_list) > 0
        assert len(attack_ics.tactic_list) > 0
