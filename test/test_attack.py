"""
Attackクラスの包括的なテスト
APIキーを使用する検索機能（get_relevant_technique, get_relevant_procedure）はテストしない
"""

import os
import re

import pytest

from attack import Attack
from attack.entities import (
    AttackAbstractMitigation,
    AttackCampaign,
    AttackConcreteMitigation,
    AttackExternalReference,
    AttackGroup,
    AttackInternalReference,
    AttackProcedure,
    AttackSoftware,
    AttackTactic,
    AttackTechnique,
)


@pytest.fixture(scope="module")
def attack_default() -> Attack:
    """デフォルト設定のAttackインスタンス（モジュール全体で1回だけ初期化）"""
    return Attack()


@pytest.fixture(scope="module")
def attack_enterprise_v18() -> Attack:
    """Enterprise v18.1のAttackインスタンス"""
    return Attack(domain="enterprise", version="18.1")


class TestCheckEnvironment:
    def test_check_mode(self) -> None:
        """テストモードであることを確認"""
        if os.getenv("ATTACK_TEST_MODE") == "False":
            pytest.exit("ATTACK_TEST_MODE 環境変数が設定されていません。テストモードで実行してください。")
        else:
            pytest.skip("テストモードで実行中です。ベクトルDB検索はスキップされます。")


class TestAttackInitialization:
    """初期化とバージョン・ドメイン管理のテスト"""

    def test_default_initialization(self, attack_default: Attack) -> None:
        """デフォルト設定での初期化"""
        assert attack_default.version == "v18.1"
        assert attack_default.domain == "enterprise"
        assert attack_default.technique_list is not None
        assert len(attack_default.technique_list) > 0

    def test_available_versions(self, attack_default: Attack) -> None:
        """利用可能なバージョン一覧の取得"""
        versions = attack_default.get_available_versions()
        assert isinstance(versions, list)
        assert len(versions) > 0
        assert all(re.match(r"\d{2}\.\d", v) for v in versions)

    def test_domain_selection(self, attack_enterprise_v18: Attack) -> None:
        """ドメインでの初期化（enterpriseのみテスト）"""
        assert attack_enterprise_v18.domain == "enterprise"
        assert len(attack_enterprise_v18.technique_list) > 0

    def test_invalid_version(self) -> None:
        """無効なバージョンでエラーが発生することを確認"""
        with pytest.raises(ValueError, match="version must be one of"):
            Attack(version="99.9")

    def test_invalid_domain(self) -> None:
        """無効なドメインでエラーが発生することを確認"""
        with pytest.raises(ValueError, match="domain must be one of"):
            Attack(domain="invalid")


class TestAttackTactics:
    """タクティック関連のテスト"""

    def test_tactic_list_exists(self, attack_default: Attack) -> None:
        """タクティックリストが存在することを確認"""
        assert attack_default.tactic_list is not None
        assert isinstance(attack_default.tactic_list, list)
        assert len(attack_default.tactic_list) > 0

    def test_tactic_properties(self, attack_default: Attack) -> None:
        """タクティックオブジェクトの基本プロパティを確認"""
        for tactic in attack_default.tactic_list:
            assert isinstance(tactic, AttackTactic)
            assert tactic.id is not None
            assert tactic.id.startswith("TA")
            assert tactic.name is not None
            assert tactic.description is not None
            assert isinstance(tactic.technique_list, list)

    def test_get_tactic_by_id(self, attack_default: Attack) -> None:
        """IDによるタクティック取得"""
        first_tactic = attack_default.tactic_list[0]
        retrieved_tactic = attack_default.get_tactic_by_id(first_tactic.id)
        assert retrieved_tactic.id == first_tactic.id
        assert retrieved_tactic.name == first_tactic.name

    def test_get_tactic_by_id_invalid(self, attack_default: Attack) -> None:
        """無効なIDでエラーが発生することを確認"""
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_tactic_by_id("TA9999")

    def test_get_tactic_by_name(self, attack_default: Attack) -> None:
        """名前によるタクティック取得"""
        first_tactic = attack_default.tactic_list[0]
        retrieved_tactic = attack_default.get_tactic_by_name(first_tactic.name)
        assert retrieved_tactic.id == first_tactic.id
        assert retrieved_tactic.name == first_tactic.name

    def test_get_tactic_by_name_invalid(self, attack_default: Attack) -> None:
        """無効な名前でエラーが発生することを確認"""
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_tactic_by_name("InvalidTacticName")


class TestAttackTechniques:
    """テクニック関連のテスト"""

    def test_technique_list_exists(self, attack_default: Attack) -> None:
        """テクニックリストが存在することを確認"""
        assert attack_default.technique_list is not None
        assert isinstance(attack_default.technique_list, list)
        assert len(attack_default.technique_list) > 0

    def test_technique_properties(self, attack_default: Attack) -> None:
        """テクニックオブジェクトの基本プロパティを確認"""
        for technique in attack_default.technique_list[:10]:  # 最初の10件をサンプル確認
            assert isinstance(technique, AttackTechnique)
            assert technique.id is not None
            assert technique.id.startswith("T")
            assert technique.name is not None
            assert technique.description is not None
            assert isinstance(technique.tactics, list)
            assert len(technique.tactics) > 0

    def test_technique_description_cleaned(self, attack_default: Attack) -> None:
        """テクニックの説明文が適切にクリーニングされていることを確認"""
        for technique in attack_default.technique_list:
            self._check_description_cleaned(technique.description)

    def test_get_technique_by_id(self, attack_default: Attack) -> None:
        """IDによるテクニック取得"""
        first_technique = attack_default.technique_list[0]
        retrieved_technique = attack_default.get_technique_by_id(first_technique.id)
        assert retrieved_technique.id == first_technique.id
        assert retrieved_technique.name == first_technique.name

    def test_get_technique_by_id_invalid(self, attack_default: Attack) -> None:
        """無効なIDでエラーが発生することを確認"""
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_technique_by_id("T9999")

    def test_subtechniques_have_parent(self, attack_default: Attack) -> None:
        """サブテクニックが存在することを確認"""
        subtechniques = [t for t in attack_default.technique_list if "." in t.id]
        assert len(subtechniques) > 0  # サブテクニックが少なくとも1つは存在する

        # parent_idが設定されているサブテクニックのみ検証
        subtechniques_with_parent = [t for t in subtechniques if t.parent_id is not None]
        for technique in subtechniques_with_parent[:5]:  # 最初の5件をサンプル検証
            parent = attack_default.get_technique_by_id(technique.parent_id)  # ty:ignore[invalid-argument-type]
            assert parent is not None
            assert "." not in parent.id

    def _check_description_cleaned(self, description: str) -> None:
        """説明文が適切にクリーニングされていることを確認"""
        # Citation表記が残っていないことを確認
        pattern = r"\(Citation: .*?\)"
        match = re.search(pattern, description)
        assert match is None, f"引用表記が残っています: {match.group() if match else ''} in {description[:100]}"

        # 内部参照のマークダウン表記が残っていないことを確認
        pattern = r"\[.*?\]\(https://attack.mitre.org/.*?\)"
        match = re.search(pattern, description)
        assert match is None, f"内部参照のマークダウン表記が残っています: {match.group() if match else ''} in {description[:100]}"


class TestAttackMitigations:
    """緩和策関連のテスト"""

    def test_mitigation_list_exists(self, attack_default: Attack) -> None:
        """緩和策リストが存在することを確認"""
        assert attack_default.mitigation_list is not None
        assert isinstance(attack_default.mitigation_list, list)
        assert len(attack_default.mitigation_list) > 0

    def test_mitigation_properties(self, attack_default: Attack) -> None:
        """緩和策オブジェクトの基本プロパティを確認"""
        for mitigation in attack_default.mitigation_list:
            assert isinstance(mitigation, AttackAbstractMitigation)
            assert mitigation.id is not None
            assert mitigation.id.startswith("M")
            assert mitigation.name is not None
            assert mitigation.description is not None
            assert isinstance(mitigation.concrete_mitigation_list, list)

    def test_mitigation_description_cleaned(self, attack_default: Attack) -> None:
        """緩和策の説明文が適切にクリーニングされていることを確認"""
        for mitigation in attack_default.mitigation_list:
            self._check_description_cleaned(mitigation.description)

    def test_get_mitigation_by_id(self, attack_default: Attack) -> None:
        """IDによる緩和策取得"""
        first_mitigation = attack_default.mitigation_list[0]
        retrieved_mitigation = attack_default.get_mitigation_by_id(first_mitigation.id)
        assert retrieved_mitigation.id == first_mitigation.id
        assert retrieved_mitigation.name == first_mitigation.name

    def test_get_mitigation_by_id_invalid(self, attack_default: Attack) -> None:
        """無効なIDでエラーが発生することを確認"""
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_mitigation_by_id("M9999")

    def test_concrete_mitigation_properties(self, attack_default: Attack) -> None:
        """具体的緩和策の基本プロパティを確認"""
        for mitigation in attack_default.mitigation_list:
            for concrete_mitigation in mitigation.concrete_mitigation_list:
                assert isinstance(concrete_mitigation, AttackConcreteMitigation)
                assert concrete_mitigation.abstract_mitigation_id == mitigation.id
                assert concrete_mitigation.abstract_mitigation_name == mitigation.name
                assert concrete_mitigation.technique_id is not None
                assert concrete_mitigation.description is not None

    def test_get_concrete_mitigation_by_technique_id(self, attack_default: Attack) -> None:
        """テクニックIDによる具体的緩和策取得"""
        first_technique = attack_default.technique_list[0]
        concrete_mitigations = attack_default.get_concrete_mitigation_by_technique_id(first_technique.id)
        assert isinstance(concrete_mitigations, list)
        for mitigation in concrete_mitigations:
            assert isinstance(mitigation, AttackConcreteMitigation)
            assert mitigation.technique_id == first_technique.id

    def _check_description_cleaned(self, description: str) -> None:
        """説明文が適切にクリーニングされていることを確認"""
        pattern = r"\(Citation: .*?\)"
        match = re.search(pattern, description)
        assert match is None

        pattern = r"\[.*?\]\(https://attack.mitre.org/.*?\)"
        match = re.search(pattern, description)
        assert match is None


class TestAttackCampaigns:
    """キャンペーン関連のテスト"""

    def test_campaign_list_exists(self, attack_default: Attack) -> None:
        """キャンペーンリストが存在することを確認"""
        assert attack_default.campaign_list is not None
        assert isinstance(attack_default.campaign_list, list)
        assert len(attack_default.campaign_list) > 0

    def test_campaign_properties(self, attack_default: Attack) -> None:
        """キャンペーンオブジェクトの基本プロパティを確認"""
        for campaign in attack_default.campaign_list:
            assert isinstance(campaign, AttackCampaign)
            assert campaign.id is not None
            assert campaign.id.startswith("C")
            assert campaign.name is not None
            assert campaign.description is not None
            assert isinstance(campaign.procedure_list, list)

    def test_get_campaign_by_id(self, attack_default: Attack) -> None:
        """IDによるキャンペーン取得"""
        first_campaign = attack_default.campaign_list[0]
        retrieved_campaign = attack_default.get_campaign_by_id(first_campaign.id)
        assert retrieved_campaign.id == first_campaign.id
        assert retrieved_campaign.name == first_campaign.name

    def test_get_campaign_by_id_invalid(self, attack_default: Attack) -> None:
        """無効なIDでエラーが発生することを確認"""
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_campaign_by_id("C9999")


class TestAttackGroups:
    """グループ関連のテスト"""

    def test_group_list_exists(self, attack_default: Attack) -> None:
        """グループリストが存在することを確認"""
        assert attack_default.group_list is not None
        assert isinstance(attack_default.group_list, list)
        assert len(attack_default.group_list) > 0

    def test_group_properties(self, attack_default: Attack) -> None:
        """グループオブジェクトの基本プロパティを確認"""
        for group in attack_default.group_list:
            assert isinstance(group, AttackGroup)
            assert group.id is not None
            assert group.id.startswith("G")
            assert group.name is not None
            assert group.description is not None
            assert isinstance(group.procedure_list, list)

    def test_get_group_by_id(self, attack_default: Attack) -> None:
        """IDによるグループ取得"""
        first_group = attack_default.group_list[0]
        retrieved_group = attack_default.get_group_by_id(first_group.id)
        assert retrieved_group.id == first_group.id
        assert retrieved_group.name == first_group.name

    def test_get_group_by_id_invalid(self, attack_default: Attack) -> None:
        """無効なIDでエラーが発生することを確認"""
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_group_by_id("G9999")


class TestAttackSoftware:
    """ソフトウェア関連のテスト"""

    def test_software_list_exists(self, attack_default: Attack) -> None:
        """ソフトウェアリストが存在することを確認"""
        assert attack_default.software_list is not None
        assert isinstance(attack_default.software_list, list)
        assert len(attack_default.software_list) > 0

    def test_software_properties(self, attack_default: Attack) -> None:
        """ソフトウェアオブジェクトの基本プロパティを確認"""
        for software in attack_default.software_list:
            assert isinstance(software, AttackSoftware)
            assert software.id is not None
            assert software.id.startswith("S")
            assert software.name is not None
            assert software.description is not None
            assert isinstance(software.procedure_list, list)

    def test_get_software_by_id(self, attack_default: Attack) -> None:
        """IDによるソフトウェア取得"""
        first_software = attack_default.software_list[0]
        retrieved_software = attack_default.get_software_by_id(first_software.id)
        assert retrieved_software.id == first_software.id
        assert retrieved_software.name == first_software.name

    def test_get_software_by_id_invalid(self, attack_default: Attack) -> None:
        """無効なIDでエラーが発生することを確認"""
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_software_by_id("S9999")


class TestAttackProcedures:
    """プロシージャ関連のテスト"""

    def test_procedure_in_campaign(self, attack_default: Attack) -> None:
        """キャンペーン内のプロシージャの基本プロパティを確認"""
        for campaign in attack_default.campaign_list:
            for procedure in campaign.procedure_list:
                assert isinstance(procedure, AttackProcedure)
                assert procedure.original_id is not None
                assert procedure.original_id.startswith("P")
                assert procedure.parent_id == campaign.id
                assert procedure.parent_name == campaign.name
                assert procedure.parent_type == "campaign"
                assert procedure.technique_id is not None
                assert procedure.description is not None

    def test_procedure_in_group(self, attack_default: Attack) -> None:
        """グループ内のプロシージャの基本プロパティを確認"""
        for group in attack_default.group_list:
            for procedure in group.procedure_list:
                assert isinstance(procedure, AttackProcedure)
                assert procedure.parent_id == group.id
                assert procedure.parent_name == group.name
                assert procedure.parent_type == "group"

    def test_procedure_in_software(self, attack_default: Attack) -> None:
        """ソフトウェア内のプロシージャの基本プロパティを確認"""
        for software in attack_default.software_list:
            for procedure in software.procedure_list:
                assert isinstance(procedure, AttackProcedure)
                assert procedure.parent_id == software.id
                assert procedure.parent_name == software.name
                assert procedure.parent_type == "software"

    def test_get_procedure_by_technique_id(self, attack_default: Attack) -> None:
        """テクニックIDによるプロシージャ取得"""
        first_technique = attack_default.technique_list[0]
        procedures = attack_default.get_procedure_by_technique_id(first_technique.id)
        assert isinstance(procedures, list)
        for procedure in procedures:
            assert isinstance(procedure, AttackProcedure)
            assert procedure.technique_id == first_technique.id

    def test_get_procedure_by_id(self, attack_default: Attack) -> None:
        """IDによるプロシージャ取得"""
        # キャンペーンから最初のプロシージャを取得
        first_procedure = None
        for campaign in attack_default.campaign_list:
            if campaign.procedure_list:
                first_procedure = campaign.procedure_list[0]
                break

        if first_procedure:
            retrieved_procedure = attack_default.get_procedure_by_id(first_procedure.original_id)
            assert retrieved_procedure.original_id == first_procedure.original_id
            assert retrieved_procedure.parent_id == first_procedure.parent_id

    def test_get_procedure_by_id_invalid(self, attack_default: Attack) -> None:
        """無効なIDでエラーが発生することを確認"""
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_procedure_by_id("P999999")


class TestAttackReferences:
    """参照関連のテスト"""

    def test_external_reference_list_exists(self, attack_default: Attack) -> None:
        """外部参照リストが存在することを確認"""
        assert attack_default.external_reference_list is not None
        assert isinstance(attack_default.external_reference_list, list)
        assert len(attack_default.external_reference_list) > 0

    def test_external_reference_properties(self, attack_default: Attack) -> None:
        """外部参照オブジェクトの基本プロパティを確認"""
        for ref in attack_default.external_reference_list[:10]:  # サンプル確認
            assert isinstance(ref, AttackExternalReference)
            assert ref.id is not None
            assert ref.name is not None
            assert ref.url is not None
            assert ref.description is not None

    def test_get_external_reference_by_name(self, attack_default: Attack) -> None:
        """名前による外部参照取得"""
        first_ref = attack_default.external_reference_list[0]
        retrieved_ref = attack_default.get_external_reference_by_name(first_ref.name)
        assert retrieved_ref.name == first_ref.name
        assert retrieved_ref.url == first_ref.url

    def test_get_external_reference_by_name_invalid(self, attack_default: Attack) -> None:
        """無効な名前でエラーが発生することを確認"""
        with pytest.raises(ValueError, match="は存在しません"):
            attack_default.get_external_reference_by_name("NonExistentReference")

    def test_technique_has_references(self, attack_default: Attack) -> None:
        """テクニックが参照を持つことを確認"""
        techniques_with_refs = [t for t in attack_default.technique_list if t.reference_list]
        assert len(techniques_with_refs) > 0

        for technique in techniques_with_refs[:5]:  # サンプル確認
            for ref in technique.reference_list:
                assert isinstance(ref, (AttackExternalReference, AttackInternalReference))

    def test_mitigation_has_references(self, attack_default: Attack) -> None:
        """緩和策が参照を持つことを確認"""
        mitigations_with_refs = [m for m in attack_default.mitigation_list if m.reference_list]
        assert len(mitigations_with_refs) > 0

        for mitigation in mitigations_with_refs[:5]:  # サンプル確認
            for ref in mitigation.reference_list:
                assert isinstance(ref, (AttackExternalReference, AttackInternalReference))


class TestAttackVectorSearch:
    """ベクトル検索関連のテスト（APIキー不要な部分のみ）"""

    def test_relevant_technique_raises_error_in_test_mode(self, attack_default: Attack) -> None:
        """テストモードではベクトル検索がエラーを発生させることを確認"""
        with pytest.raises(ValueError, match="テストモードのため、ベクトルDB検索は無効化されています"):
            attack_default.get_relevant_technique("test query", top_k=5)

    def test_relevant_procedure_raises_error_in_test_mode(self, attack_default: Attack) -> None:
        """テストモードではプロシージャ検索がエラーを発生させることを確認"""
        with pytest.raises(ValueError, match="テストモードのため、ベクトルDB検索は無効化されています"):
            attack_default.get_relevant_procedure("test query", top_k=5)


class TestAttackMultiVersionDomain:
    """複数バージョン・ドメインの統合テスト"""

    def test_enterprise_version_18(self, attack_enterprise_v18: Attack) -> None:
        """Enterprise v18.1の基本動作を確認"""
        # 基本的なリストが存在することを確認
        assert len(attack_enterprise_v18.technique_list) > 0
        assert len(attack_enterprise_v18.tactic_list) > 0
        assert len(attack_enterprise_v18.mitigation_list) > 0
        assert len(attack_enterprise_v18.campaign_list) >= 0  # キャンペーンは0の可能性もある
        assert len(attack_enterprise_v18.group_list) >= 0
        assert len(attack_enterprise_v18.software_list) >= 0
