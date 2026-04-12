"""ID検索機能のテスト(ベクトル検索を除く)。"""

import pytest

from attack import Attack
from attack.entities import (
    AttackAbstractMitigation,
    AttackCampaign,
    AttackConcreteMitigation,
    AttackExternalReference,
    AttackGroup,
    AttackProcedure,
    AttackSoftware,
    AttackTactic,
    AttackTechnique,
)


class TestSearchTechniqueById:
    """テクニックID検索のテスト。"""

    def test_search_existing_technique(self, attack_default: Attack) -> None:
        first = attack_default.technique_list[0]
        result = attack_default.get_technique_by_id(first.id)
        assert isinstance(result, AttackTechnique)
        assert result.id == first.id
        assert result.name == first.name

    def test_search_nonexistent_technique_raises(self, attack_default: Attack) -> None:
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_technique_by_id("T9999")


class TestSearchTacticById:
    """タクティックID検索のテスト。"""

    def test_search_existing_tactic_by_id(self, attack_default: Attack) -> None:
        first = attack_default.tactic_list[0]
        result = attack_default.get_tactic_by_id(first.id)
        assert isinstance(result, AttackTactic)
        assert result.id == first.id

    def test_search_existing_tactic_by_name(self, attack_default: Attack) -> None:
        first = attack_default.tactic_list[0]
        result = attack_default.get_tactic_by_name(first.name)
        assert result.id == first.id
        assert result.name == first.name

    def test_search_nonexistent_tactic_by_id_raises(self, attack_default: Attack) -> None:
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_tactic_by_id("TA9999")

    def test_search_nonexistent_tactic_by_name_raises(self, attack_default: Attack) -> None:
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_tactic_by_name("InvalidTacticName")


class TestSearchMitigationById:
    """緩和策ID検索のテスト。"""

    def test_search_existing_mitigation(self, attack_default: Attack) -> None:
        first = attack_default.mitigation_list[0]
        result = attack_default.get_mitigation_by_id(first.id)
        assert isinstance(result, AttackAbstractMitigation)
        assert result.id == first.id

    def test_search_nonexistent_mitigation_raises(self, attack_default: Attack) -> None:
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_mitigation_by_id("M9999")


class TestSearchConcreteMitigationByTechniqueId:
    """テクニックIDによる具体緩和策検索のテスト。"""

    def test_search_concrete_mitigation(self, attack_default: Attack) -> None:
        first_technique = attack_default.technique_list[0]
        results = attack_default.get_concrete_mitigation_by_technique_id(first_technique.id)
        assert isinstance(results, list)
        for mit in results:
            assert isinstance(mit, AttackConcreteMitigation)
            assert mit.technique_id == first_technique.id


class TestSearchCampaignById:
    """キャンペーンID検索のテスト。"""

    def test_search_existing_campaign(self, attack_default: Attack) -> None:
        first = attack_default.campaign_list[0]
        result = attack_default.get_campaign_by_id(first.id)
        assert isinstance(result, AttackCampaign)
        assert result.id == first.id

    def test_search_nonexistent_campaign_raises(self, attack_default: Attack) -> None:
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_campaign_by_id("C9999")


class TestSearchGroupById:
    """グループID検索のテスト。"""

    def test_search_existing_group(self, attack_default: Attack) -> None:
        first = attack_default.group_list[0]
        result = attack_default.get_group_by_id(first.id)
        assert isinstance(result, AttackGroup)
        assert result.id == first.id

    def test_search_nonexistent_group_raises(self, attack_default: Attack) -> None:
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_group_by_id("G9999")


class TestSearchSoftwareById:
    """ソフトウェアID検索のテスト。"""

    def test_search_existing_software(self, attack_default: Attack) -> None:
        first = attack_default.software_list[0]
        result = attack_default.get_software_by_id(first.id)
        assert isinstance(result, AttackSoftware)
        assert result.id == first.id

    def test_search_nonexistent_software_raises(self, attack_default: Attack) -> None:
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_software_by_id("S9999")


class TestSearchProcedureById:
    """プロシージャID検索のテスト。"""

    def test_search_existing_procedure(self, attack_default: Attack) -> None:
        first_procedure = None
        for campaign in attack_default.campaign_list:
            if campaign.procedure_list:
                first_procedure = campaign.procedure_list[0]
                break
        assert first_procedure is not None, "テスト用のプロシージャが見つかりません"
        result = attack_default.get_procedure_by_id(first_procedure.original_id)
        assert isinstance(result, AttackProcedure)
        assert result.original_id == first_procedure.original_id

    def test_search_nonexistent_procedure_raises(self, attack_default: Attack) -> None:
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_procedure_by_id("P999999")

    def test_search_procedure_by_technique_id(self, attack_default: Attack) -> None:
        first_technique = attack_default.technique_list[0]
        results = attack_default.get_procedure_by_technique_id(first_technique.id)
        assert isinstance(results, list)
        for proc in results:
            assert isinstance(proc, AttackProcedure)
            assert proc.technique_id == first_technique.id


class TestSearchExternalReferenceByName:
    """外部参照名検索のテスト。"""

    def test_search_existing_reference(self, attack_default: Attack) -> None:
        first = attack_default.external_reference_list[0]
        result = attack_default.get_external_reference_by_name(first.name)
        assert isinstance(result, AttackExternalReference)
        assert result.name == first.name
        assert result.url == first.url

    def test_search_nonexistent_reference_raises(self, attack_default: Attack) -> None:
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_external_reference_by_name("NonExistentReference")
